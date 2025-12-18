"""
维格表团队管理

兼容原vika.py库的Team类
"""
from typing import Dict, Any, Optional, List
from ..types.unit_model import UnitTeamCreateRo, UnitTeamUpdateRo
from ..exceptions import ParameterException, NotFoundException
from ..utils import handle_response
import re
from urllib.parse import quote


class Team:
    """
    团队管理类，提供团队相关操作
    
    兼容原vika.py库的Team接口
    """
    
    def __init__(self, space):
        """
        初始化团队管理器
        
        Args:
            space: 空间实例
        """
        self._space = space
    
    async def aget(self, unit_id: str) -> Dict[str, Any]:
        """
        获取团队信息（异步）
        
        Args:
            unit_id: 团队单元ID
            
        Returns:
            团队信息
        """
        try:
            # 优先使用团队信息API
            response = await self._aget_team(unit_id)
            return response.get('data', {})
        except Exception:
            # 如果团队信息API失败（可能是权限问题），降级到使用团队成员接口
            # 注意：此方法返回的数据可能不完整
            response = await self._aget_team_members(unit_id)
            return response.get('data', {})
    
    # 避免误导：之前为空实现，改为显式未实现
    async def alist(self) -> List[Dict[str, Any]]:
        """
        获取团队列表（异步）
        
        Returns:
            团队列表
        """
        raise NotImplementedError("Team.alist 未实现；暂无可靠团队列表API，避免静默返回空列表误导调用方")
    
    async def acreate(self, team_data: UnitTeamCreateRo) -> Dict[str, Any]:
        """
        创建团队（异步）
        
        Args:
            team_data: 团队创建数据
            
        Returns:
            创建结果
        """
        response = await self._acreate_team(team_data.model_dump())
        return response.get('data', {})
    
    async def aupdate(self, unit_id: str, team_data: UnitTeamUpdateRo) -> Dict[str, Any]:
        """
        更新团队信息（异步）
        
        Args:
            unit_id: 团队单元ID
            team_data: 团队更新数据
            
        Returns:
            更新结果
        """
        response = await self._aupdate_team(unit_id, team_data.model_dump())
        return response.get('data', {})
    
    async def adelete(self, unit_id: str) -> bool:
        """
        删除团队（异步）
        
        Args:
            unit_id: 团队单元ID
            
        Returns:
            是否删除成功
        """
        # 依赖统一异常处理：非2xx或success=False将抛异常，避免错误返回True
        resp = await self._adelete_team(unit_id)
        handle_response(resp)
        return True
    
    async def aget_members(self, unit_id: str) -> List[Dict[str, Any]]:
        """
        获取团队成员列表（异步）
        
        Args:
            unit_id: 团队单元ID
            
        Returns:
            团队成员列表
        """
        response = await self._aget_team_members(unit_id)
        members_data = response.get('data', {}).get('members', [])
        return members_data
    
    async def aget_children(self, unit_id: str) -> List[Dict[str, Any]]:
        """
        获取子团队列表（异步）
        
        Args:
            unit_id: 团队单元ID
            
        Returns:
            子团队列表
        """
        response = await self._aget_team_children(unit_id)
        children_data = response.get('data', {}).get('children', [])
        return children_data
    
    async def aexists(self, unit_id: str) -> bool:
        """
        检查团队是否存在（异步）
        
        Args:
            unit_id: 团队单元ID
            
        Returns:
            团队是否存在
        """
        try:
            await self.aget(unit_id)
            return True
        except NotFoundException:
            # 仅在资源确实不存在时返回 False
            return False
    
    # 避免误导：依赖 list()，改为显式未实现
    async def afind_by_name(self, team_name: str) -> Optional[Dict[str, Any]]:
        """
        根据团队名查找团队（异步）
        
        Args:
            team_name: 团队名称
            
        Returns:
            团队信息或None
        """
        raise NotImplementedError("Team.afind_by_name 未实现；依赖 Team.alist()，当前未提供团队列表API")
    
    async def aget_team_by_name(self, team_name: str) -> Dict[str, Any]:
        """
        根据团队名获取团队（异步）
        
        Args:
            team_name: 团队名称
            
        Returns:
            团队信息
            
        Raises:
            ParameterException: 团队不存在时
        """
        team = await self.afind_by_name(team_name)
        if not team:
            raise ParameterException(f"Team '{team_name}' not found")
        return team
    
    async def aadd_member(self, unit_id: str, member_id: str) -> bool:
        """
        向团队添加成员（异步）
        
        Args:
            unit_id: 团队单元ID
            member_id: 成员ID
            
        Returns:
            是否添加成功
        """
        # 这个功能可能需要特定的API，暂时抛出未实现异常
        raise NotImplementedError("Add member to team is not implemented yet")
    
    async def aremove_member(self, unit_id: str, member_id: str) -> bool:
        """
        从团队移除成员（异步）
        
        Args:
            unit_id: 团队单元ID
            member_id: 成员ID
            
        Returns:
            是否移除成功
        """
        # 这个功能可能需要特定的API，暂时抛出未实现异常
        raise NotImplementedError("Remove member from team is not implemented yet")
    
    # 内部API调用方法
    def _normalize_unit_id(self, unit_id: str) -> str:
        """
        校验并URL编码团队unit_id，仅允许字母/数字/_-，长度1-64。
        返回经 quote(..., safe="") 编码后的路径段。
        """
        if not isinstance(unit_id, str) or not unit_id:
            raise ParameterException("unit_id cannot be empty")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", unit_id):
            raise ParameterException("Invalid unit_id format")
        return quote(unit_id, safe="")
    
    async def _aget_team(self, unit_id: str) -> Dict[str, Any]:
        """获取团队信息的内部API调用（异步）"""
        safe_id = self._normalize_unit_id(unit_id)
        endpoint = f"spaces/{self._space._space_id}/teams/{safe_id}"
        return await self._space._apitable.request_adapter.get(endpoint)
    
    async def _aget_team_members(self, unit_id: str) -> Dict[str, Any]:
        """获取团队成员的内部API调用（异步）"""
        safe_id = self._normalize_unit_id(unit_id)
        endpoint = f"spaces/{self._space._space_id}/teams/{safe_id}/members"
        return await self._space._apitable.request_adapter.get(endpoint)
    
    async def _aget_team_children(self, unit_id: str) -> Dict[str, Any]:
        """获取子团队的内部API调用（异步）"""
        safe_id = self._normalize_unit_id(unit_id)
        endpoint = f"spaces/{self._space._space_id}/teams/{safe_id}/children"
        return await self._space._apitable.request_adapter.get(endpoint)
    
    async def _acreate_team(self, team_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建团队的内部API调用（异步）"""
        endpoint = f"spaces/{self._space._space_id}/teams"
        return await self._space._apitable.request_adapter.post(endpoint, json_body=team_data)
    
    async def _aupdate_team(self, unit_id: str, team_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新团队的内部API调用（异步）"""
        safe_id = self._normalize_unit_id(unit_id)
        endpoint = f"spaces/{self._space._space_id}/teams/{safe_id}"
        return await self._space._apitable.request_adapter.put(endpoint, json_body=team_data)
    
    async def _adelete_team(self, unit_id: str) -> Dict[str, Any]:
        """删除团队的内部API调用（异步）"""
        safe_id = self._normalize_unit_id(unit_id)
        endpoint = f"spaces/{self._space._space_id}/teams/{safe_id}"
        return await self._space._apitable.request_adapter.delete(endpoint)
    
    def __str__(self) -> str:
        return f"Team({self._space})"
    
    def __repr__(self) -> str:
        return f"Team(space={self._space._space_id})"


__all__ = ['Team']
