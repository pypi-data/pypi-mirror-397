from azure.ai.agents.models import Agent
from azure.core.paging import ItemPaged
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from davidkhala.azure.auth import TokenCredential
from azure.ai.projects.models import AgentVersionObject
from openai import OpenAI
from openai.types.responses.response import Response
from azure.ai.projects.models import AgentObject


class Project:
    def __init__(self, foundry_id, project, credential: TokenCredential):
        self.client = AIProjectClient(
            endpoint=f"https://{foundry_id}.services.ai.azure.com/api/projects/{project}",
            credential=credential,
        )
        self.agent: Agent = None
        self.model:str = None

    def as_chat(self, model: str, sys_prompt: str = None, *, agent_name: str) -> AgentVersionObject:
        if agent_name:
            self.agent = self.client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions=sys_prompt
                ),
            )
        else:
            self.model = model

    @property
    def agents(self) -> list[AgentObject]:
        return [*self.client.agents.list()]

    def chat(self, *user_prompt, **kwargs) -> Response:
        openai_client: OpenAI = self.client.get_openai_client()
        options = {}
        if self.agent:
            options["extra_body"] = {
                "agent": {"name": self.agent.name, "type": "agent_reference"}
            }
        else:
            options['model'] = self.model

        response = openai_client.responses.create(
            input=[{"role": "user", "content": _} for _ in user_prompt],
            **options
        )
        return response
