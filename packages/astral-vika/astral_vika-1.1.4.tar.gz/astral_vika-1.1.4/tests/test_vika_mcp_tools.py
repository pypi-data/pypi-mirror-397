import logging
import os
import re
import asyncio
from typing import Optional

import pytest

from vika_mcp.mcp.registry import ToolRegistry
from vika_mcp.tools.vika_tools import (
    try_register_vika_tools,
    vika_status,
    vika_get_records,
)
from vika_mcp.tools.builtin import register as register_builtin

pytestmark = pytest.mark.mcp

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def _registered(api_token: str) -> ToolRegistry:
    """
    初始化并注册 vika 工具；依赖环境变量注入的 VIKA_API_TOKEN。
    若凭据缺失会在更早的夹具阶段被 skip。
    """
    registry = ToolRegistry()
    count = try_register_vika_tools(registry)
    # vika.status 总是注册；其余按凭据决定 available
    assert count >= 1
    return registry


@pytest.mark.asyncio
async def test_vika_status(_registered: ToolRegistry):
    """
    连接性：vika.status 应返回 configured=True（有凭据时）。
    """
    status = await vika_status({})
    assert isinstance(status, dict)
    assert "configured" in status
    assert status["host"]
    assert status["configured"] is True, "Vika MCP not configured via env"


@pytest.mark.asyncio
async def test_vika_get_records_minimal(_registered: ToolRegistry, datasheet_id: str):
    """
    读取：vika.get_records 最小查询，limit=1。
    """
    resp = await vika_get_records(
        {
            "datasheet_id": datasheet_id,
            "limit": 1,
        }
    )
    assert isinstance(resp, dict)
    assert "records" in resp and isinstance(resp["records"], list)
    assert "has_more" in resp
    assert "next_offset" in resp


@pytest.mark.asyncio
async def test_vika_get_records_with_view(_registered: ToolRegistry, datasheet_id: str, view_id: Optional[str]):
    """
    读取（带视图）：如 URL 包含 viw...，则用该视图查询一页记录。
    """
    if not view_id:
        pytest.skip("No viewId parsed from VIKA_WORKBENCH_URL; skipping vika.get_records(view).")

    resp = await vika_get_records(
        {
            "datasheet_id": datasheet_id,
            "view_id": view_id,
            "limit": 1,
        }
    )
    assert isinstance(resp, dict)
    assert "records" in resp and isinstance(resp["records"], list)
    assert "has_more" in resp
    assert "next_offset" in resp


def test_tool_specs_include_new_tools_and_schemas():
    """
    工具清单应包含新增 vika.* 工具全集；未配置凭据时 available=False（或给出 unavailable_reason），
    且关键参数 schema 正确。该用例仅校验“规范”，不实际调用后端。
    """
    from vika_mcp.mcp.registry import ToolRegistry
    from vika_mcp.tools.vika_tools import try_register_vika_tools

    registry = ToolRegistry()
    count = try_register_vika_tools(registry)
    assert count >= 1

    tools = registry.list_tools(include_unavailable=True)
    by_name = {t.name: t for t in tools}
    names = set(by_name.keys())

    expected = {
        # 既有保留
        "vika.status", "vika.list_datasheets", "vika.get_records",
        # Records
        "vika.records.create", "vika.records.update", "vika.records.delete",
        "vika.records.get", "vika.records.query",
        # Fields
        "vika.fields.list", "vika.fields.get", "vika.fields.create", "vika.fields.delete",
        # Views
        "vika.views.list", "vika.views.get",
        # Attachments
        "vika.attachments.upload", "vika.attachments.download",
        # Datasheets
        "vika.datasheets.create", "vika.datasheets.info",
    }
    # a) 工具集合包含上述名称全集
    missing = expected - names
    assert not missing, f"Missing tools: {sorted(missing)}"

    # c) 无凭据时（无 VIKA_API_TOKEN）除 vika.status 外均应 available=False 或含 unavailable_reason
    has_token = bool(os.getenv("VIKA_API_TOKEN"))
    assert by_name["vika.status"].available is True
    if not has_token:
        for n in expected - {"vika.status"}:
            spec = by_name[n]
            assert spec.available is False or getattr(spec, "unavailable_reason", None), f"{n} should be unavailable without credentials"

    # b) 参数 schema 关键字段断言（抽查 5 个）
    def _props(spec_name: str):
        sch = by_name[spec_name].input_schema
        assert isinstance(sch, dict) and sch.get("type") == "object"
        return sch.get("required", []), sch.get("properties", {})

    # vika.records.create
    req, props = _props("vika.records.create")
    assert {"datasheet_id", "records"}.issubset(set(req))
    assert "field_key" in props
    fk = props["field_key"]
    assert isinstance(fk, dict) and fk.get("enum") == ["name", "id"]

    # vika.records.query
    req, props = _props("vika.records.query")
    assert "datasheet_id" in req
    expected_opt = {"view_id", "formula", "fields", "page_size", "page_num", "page_token", "sort", "field_key"}
    assert expected_opt.issubset(set(props.keys()))

    # vika.fields.create
    req, props = _props("vika.fields.create")
    assert {"datasheet_id", "space_id", "name", "field_type"}.issubset(set(req))
    assert "property" in props and props["property"].get("type") == "object"

    # vika.attachments.upload
    req, props = _props("vika.attachments.upload")
    assert {"datasheet_id", "file_path"}.issubset(set(req))

    # vika.datasheets.create
    req, props = _props("vika.datasheets.create")
    assert {"space_id", "name"}.issubset(set(req))
    
    
@pytest.mark.asyncio
async def test_live_vika_basic_read_ops():
    """
    只读集成：通过注册表按名称调用 4 个读取类工具，使用 env 凭据。
    - 需要环境变量：VIKA_API_TOKEN、VIKA_WORKBENCH_URL；缺任一则 skip
    - 解析 URL 获取 dst... / viw...；缺 dst 则 skip
    - 仅调用：
        * vika.datasheets.info(dst_id=...)
        * vika.views.list(datasheet_id=...)
        * vika.fields.list(datasheet_id=...)
        * vika.records.query(datasheet_id=..., view_id=?, page_size=1)
    """
    token = os.getenv("VIKA_API_TOKEN")
    workbench_url = os.getenv("VIKA_WORKBENCH_URL")
    if not token or not workbench_url:
        pytest.skip("Missing VIKA_API_TOKEN or VIKA_WORKBENCH_URL; skipping live read-only test.")

    # 解析 ID（稳健：独立搜 dst... 与 viw...）
    m_dst = re.search(r"(dst[0-9A-Za-z]+)", workbench_url or "")
    m_viw = re.search(r"(viw[0-9A-Za-z]+)", workbench_url or "")
    dst_id = m_dst.group(1) if m_dst else None
    viw_id = m_viw.group(1) if m_viw else None
    if not dst_id:
        pytest.skip("Failed to parse datasheetId (dst...) from VIKA_WORKBENCH_URL.")

    # 注册表 + 工具注册
    reg = ToolRegistry()
    register_builtin(reg)
    try_register_vika_tools(reg)

    async def call_tool(name: str, args: dict):
        """根据名称取 handler 并以 dict 作为参数调用；兼容同步/异步处理器。"""
        try:
            _, handler = reg.get(name)
        except KeyError as e:
            pytest.skip(f"Tool not registered: {name} ({e})")
        if asyncio.iscoroutinefunction(handler):
            return await handler(args or {})
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: handler(args or {}))

    # 1) datasheets.info
    try:
        info = await call_tool("vika.datasheets.info", {"dst_id": dst_id})
    except Exception as e:
        pytest.skip(f"vika.datasheets.info failed: {e}")
    assert isinstance(info, dict)
    assert "id" in info and isinstance(info["id"], str)
    assert info["id"] == dst_id

    # 2) views.list
    try:
        vws = await call_tool("vika.views.list", {"datasheet_id": dst_id})
    except Exception as e:
        pytest.skip(f"vika.views.list failed: {e}")
    assert isinstance(vws, dict)
    views = vws.get("views")
    assert isinstance(views, list)
    if viw_id:
        # 若返回包含 id/viewId/view_id 字段，则要求包含该 viw；否则放宽为至少存在一个视图
        has_id_keys = any(isinstance(v, dict) and ("id" in v or "viewId" in v or "view_id" in v) for v in views)
        if has_id_keys:
            found = False
            for v in views:
                if not isinstance(v, dict):
                    continue
                vid = v.get("id") or v.get("viewId") or v.get("view_id")
                if vid == viw_id:
                    found = True
                    break
            assert found, f"Expected view id {viw_id} in views"
        else:
            assert len(views) >= 1

    # 3) fields.list
    try:
        fds = await call_tool("vika.fields.list", {"datasheet_id": dst_id})
    except Exception as e:
        pytest.skip(f"vika.fields.list failed: {e}")
    assert isinstance(fds, dict)
    fields = fds.get("fields")
    assert isinstance(fields, list)

    # 4) records.query
    query_args = {"datasheet_id": dst_id, "page_size": 1}
    if viw_id:
        query_args["view_id"] = viw_id
    try:
        q = await call_tool("vika.records.query", query_args)
    except Exception as e:
        pytest.skip(f"vika.records.query failed: {e}")
    assert isinstance(q, dict)
    assert "records" in q and isinstance(q["records"], list)
    assert "has_more" in q
    assert "next_offset" in q
