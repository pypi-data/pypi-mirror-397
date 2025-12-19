from typing import Callable, TypedDict, Optional

from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import AzCliCommand

class HandlerParam(TypedDict):
    cmd:AzCliCommand

Handler = Callable[[HandlerParam], None]


class COMMAND_LOADER_CLS(AzCommandsLoader):

    def set_command(self, name:str, hanlder:Handler):
        self.command_table[name] = AzCliCommand(
            self, '-', hanlder,
        )
