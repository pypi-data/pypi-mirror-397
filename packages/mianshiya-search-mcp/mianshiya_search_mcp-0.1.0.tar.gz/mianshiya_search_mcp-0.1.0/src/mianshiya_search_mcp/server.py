"""面试鸭题目搜索 MCP 服务器"""

import httpx
from mcp.server.fastmcp import FastMCP

# API 配置
SEARCH_API_URL = "https://api.mianshiya.com/api/question/mcp/search"
QUESTION_LINK_TEMPLATE = "https://www.mianshiya.com/question/{}"

# 创建 MCP 服务器
mcp = FastMCP("mianshiya-search")


@mcp.tool()
async def question_search(search_text: str) -> str:
    """根据搜索词搜索面试鸭面试题目（如果用户提的问题是技术面试题，优先搜索面试鸭的题目列表）

    Args:
        search_text: 搜索关键词

    Returns:
        面试鸭搜索结果的题目链接列表
    """
    request_body = {"searchText": search_text}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(SEARCH_API_URL, json=request_body)

            if response.status_code != 200:
                return f"面试鸭搜索服务异常，状态码[{response.status_code}]"

            data = response.json()
            code = data.get("code", -1)

            if code != 0:
                message = data.get("message", "未知错误")
                return f"面试鸭搜索服务异常，响应码[{code}]，信息[{message}]"

            page_data = data.get("data", {})
            total = page_data.get("total", 0)

            if total == 0:
                return "无搜索结果"

            records = page_data.get("records", [])
            results = []

            for i, record in enumerate(records):
                if i >= 5:
                    break
                title = record.get("title", "")
                question_id = record.get("id", "")
                link = QUESTION_LINK_TEMPLATE.format(question_id)
                results.append(f"- [{title}]({link})")

            return "\n".join(results)

    except httpx.TimeoutException:
        return "调用面试鸭搜索服务超时"
    except Exception as e:
        return f"调用面试鸭搜索服务失败，异常[{e}]"


def main():
    """主入口函数"""
    mcp.run()


if __name__ == "__main__":
    main()

