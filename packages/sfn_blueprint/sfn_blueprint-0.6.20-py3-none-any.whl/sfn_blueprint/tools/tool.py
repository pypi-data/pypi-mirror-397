from langchain.tools import tool

@tool
def tool_name(name: str) -> str:
    """Description of the tool"""
    return ''