from typing import Dict, Any, List
from pixelarrayllm.client import AsyncClient


class CosyVoiceV2ManagerAsync:
    """
    CosyVoice V2（阿里云声音复刻）音色管理器（异步）

    仅包含音色/声音管理接口：
    - list/create/query/update/delete
    """

    def __init__(self, api_key: str, base_url: str = "https://llm.pixelarrayai.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.async_client = AsyncClient(api_key, base_url)

    async def list_voices(self, page_index: int = 0, page_size: int = 10) -> List[Dict[str, Any]]:
        data, success = await self.async_client._request(
            "POST",
            "/api/llm/aliyun_voice/list_voices",
            json={"page_index": page_index, "page_size": page_size},
        )
        if not success:
            raise Exception("获取阿里云声音列表失败")
        return data.get("voices", []) if isinstance(data, dict) else []

    async def create_voice(self, voice_name: str, voice_url: str) -> Dict[str, Any]:
        data, success = await self.async_client._request(
            "POST",
            "/api/llm/aliyun_voice/create",
            json={"voice_name": voice_name, "voice_url": voice_url},
        )
        if not success:
            raise Exception("创建阿里云声音失败")
        return data

    async def delete_voice(self, voice_id: str) -> Dict[str, Any]:
        data, success = await self.async_client._request(
            "POST",
            "/api/llm/aliyun_voice/delete",
            json={"voice_id": voice_id},
        )
        if not success:
            raise Exception("删除阿里云声音失败")
        return data

    async def query_voice(self, voice_id: str) -> Dict[str, Any]:
        data, success = await self.async_client._request(
            "POST",
            "/api/llm/aliyun_voice/query",
            json={"voice_id": voice_id},
        )
        if not success:
            raise Exception("查询阿里云声音失败")
        return data

    async def update_voice(self, voice_id: str, voice_url: str) -> Dict[str, Any]:
        data, success = await self.async_client._request(
            "POST",
            "/api/llm/aliyun_voice/update",
            json={"voice_id": voice_id, "voice_url": voice_url},
        )
        if not success:
            raise Exception("更新阿里云声音失败")
        return data


