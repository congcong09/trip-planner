from hello_agents.tools import MCPTool
from ..config import get_settings
from ..models.schemas import WeatherInfo, Location
from typing import Any

_amap_mcp_tool = None


def get_amap_mcp_tool() -> MCPTool:
    """
    获取高德地图的MCP工具实例（单例模式）

    Returns:
      MCPTool 实例
    """

    global _amap_mcp_tool

    if _amap_mcp_tool is None:
        settings = get_settings()

        if not settings.amap_api_key:
            raise ValueError("高德地图API key未配置，请在.env文件中配置 AMAP_API_KEY")

        _amap_mcp_tool = MCPTool(
            name="amap",
            description="高德地图服务，支持POI搜索、路线规划，天气查询等功能",
            server_command=["uvx", "amap-mcp-server"],
            env={"AMAP_MAPS_API_KEY": settings.amap_api_key},
            auto_expand=True,
        )

        print(f"✅ 高德地图MCP工具初始化成功")
        print(f"  工具数量: {len(_amap_mcp_tool._available_tools)}")

        # 打印可用工具列表

        if _amap_mcp_tool._available_tools:
            print("  可用工具：")
            for tool in _amap_mcp_tool._available_tools[:5]:
                print(f"    - {tool.get('name', 'unknow')}")
            if len(_amap_mcp_tool._available_tools) > 5:
                print(f"    ... 还有 {len(_amap_mcp_tool._available_tools) - 5} 个工具")

    return _amap_mcp_tool


class AmapService:
    """高德地图服务封装类"""

    def __init__(self):
        """初始化服务"""
        self.mcp_tool = get_amap_mcp_tool()

    def search_poi(self, keywords: str, city: str, citylimit: bool = True):
        """
        搜索 POI

        Args:
          keywords: 搜索关键词
          city: 城市
          citylimit: 是否限制在城市范围内

        Returns:
          POI信息列表
        """

        try:
            result = self.mcp_tool.run(
                {
                    "action": "call_tool",
                    "tool_name": "maps_text_search",
                    "arguments": {
                        "keywords": keywords,
                        "city": city,
                        "citylimit": citylimit,
                    },
                }
            )

            # 解析结果
            # 注意：mcp工具返回的是字符串，需要解析
            # 这里简化处理，实际应该解析JSON
            print(f"POI搜索结果：{result[:200]}...")

            # TODO: 解析实际的 POI 数据
            return []
        except Exception as e:
            print(e)

    def get_weather(self, city: str) -> list[WeatherInfo]:
        """
        查询天气

        Args:
          city: 城市名称

        Returns:
          天气信息列表
        """
        try:
            # 调用MCP工具
            result = self.mcp_tool.run(
                {
                    "action": "call_tool",
                    "tool_name": "maps_weather",
                    "arguments": {"city": city},
                }
            )

            print(f"天气查询结果：{result[:200]}...")

            # TODO: 解析实际的天气数据
            return []
        except Exception as e:
            print(f"❌ 天气查询失败：{str(e)}")
            return []

    def plan_route(
        self,
        origin_adress: str,
        destination_address: str,
        origin_city: str | None = None,
        destination_city: str | None = None,
        route_type: str = "walking",
    ) -> dict[str, Any]:
        """
        规划路线

        Args:
          origin_address: 起点地址
          destination_address: 终点地址
          origin_city: 起点城市
          destionation_city: 终点城市
          route_type: 路线类型(walking/driving/transit)
        """
        try:
            # 根据路线类型选择工具
            tool_map = {
                "walking": "maps_direction_walking_by_address",
                "driving": "maps_direction_dirving_by_address",
                "transit": "maps_directoin_transit_integrated_by_address",
            }

            tool_name = tool_map.get(route_type, "maps_direction_walking_by_address")

            # 构建参数
            arguments = {
                "origin_address": origin_adress,
                "destination_address": destination_address,
            }

            # 公共交通需要城市参数，其他方式也可以提供城市参数提高准确率
            if origin_city:
                arguments["origin_city"] = origin_city
            if destination_city:
                arguments["destination_city"] = destination_city

            result = self.mcp_tool.run(
                {"action": "call_tool", "tool_name": tool_name, "arguments": arguments}
            )

            print(f"路线规划结果：{result[:200]}...")

            # TODO: 解析实际的路线数据
            return {}

        except Exception as e:
            print(f"❌ 路线规划失败：{str(e)}")
            return {}

    def geocode(self, address: str, city: str | None = None) -> Location | None:
        """
        地理编码(地址转坐标)

        Args:
          address: 地址
          city: 城市

        Returns:
          经纬度坐标
        """

        try:
            arguments = {"address": address}
            if city:
                arguments["city"] = city

            result = self.mcp_tool.run(
                {"action": "call_tool", "tool_name": "maps_geo", "arguments": arguments}
            )

            print(f"地理编码结果：{result[:200]}...")

            # TODO: 解析实际的坐标数据
            return None
        except Exception as e:
            print(f"❌ 地理编码失败：{str(e)}")
            return None

    def get_poi_detail(self, poi_id: str) -> dict[str, Any]:
        """
        获取 POI 详情

        Args:
          poi_id: POI ID

        Returns:
          POI详情信息
        """
        try:
            result = self.mcp_tool.run(
                {
                    "action": "call_tool",
                    "tool_name": "maps_search_detail",
                    "arguments": {"id": poi_id},
                }
            )

            print(f"POI详情结果：{result[:200]}...")

            # 解析结果并提取图片
            import json
            import re

            # 尝试从结果中提取JSON
            json_match = re.search(r"\{.*\}", result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data

            return {"raw": result}
        except Exception as e:
            print(f"❌ 获取POI详情失败：{str(e)}")
            return {}


# 创建全局服务实例
_amap_service = None


def get_amap_service() -> AmapService:
    global _amap_service

    if _amap_service is None:
        _amap_service = AmapService()

    return _amap_service


if __name__ == "__main__":
    service_instance = get_amap_service()
    weather_info = service_instance.get_weather("杭州")
    print(weather_info)
