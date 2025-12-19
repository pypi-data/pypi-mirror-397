from azure.ai.agents.models import BingGroundingTool


def bing_tools(connection_id: str):
    return BingGroundingTool(connection_id=connection_id).definitions
