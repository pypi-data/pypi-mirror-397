import time
from typing import Optional, Iterator

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import Agent, ToolDefinition, AgentThreadCreationOptions, ThreadMessageOptions, ThreadRun, \
    RunStatus, ThreadMessage, MessageTextContent
from azure.core.credentials import TokenCredential


class Message:
    def __init__(self, _:ThreadMessage):
        self._ = _
    @property
    def text_messages(self) -> list[str]:
        return [content['text']['value'] for content in self._.content if isinstance(content, MessageTextContent)]

class Client:
    def __init__(self, foundry_id, project, credential: TokenCredential) -> None:
        self.agent: Optional[Agent] = None
        self.client = AgentsClient(
            endpoint=f"https://{foundry_id}.services.ai.azure.com/api/projects/{project}",
            credential=credential
        )
        self.project = project

    def as_agent(self, model: str, *,
                 tools: list[ToolDefinition],
                 sys_prompt: str = None,
                 ):
        self.agent = self.client.create_agent(
            model=model,
            instructions=sys_prompt,
            tools=tools,
        )

    def begin_chat(self, *messages: ThreadMessageOptions) -> ThreadRun:
        thread = AgentThreadCreationOptions(
            messages=list(messages)
        )
        return self.client.create_thread_and_run(
            agent_id=self.agent.id,
            thread=thread,
            parallel_tool_calls=True,
        )

    def wait_for_run(self, thread_run: ThreadRun, expected_status: RunStatus, poll_interval=1):

        current_status = self.client.runs.get(thread_run.thread_id, thread_run.id).status

        if current_status == expected_status:
            return None
        time.sleep(poll_interval)
        return self.wait_for_run(thread_run, expected_status, poll_interval)

    def get_messages(self, thread_run: ThreadRun)->Iterator[Message]:
        return (Message(m) for m in self.client.messages.list(thread_run.thread_id, run_id=thread_run.id))


