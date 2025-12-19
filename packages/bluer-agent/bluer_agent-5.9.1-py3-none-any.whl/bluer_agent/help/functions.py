from bluer_ai.help.generic import help_functions as generic_help_functions

from bluer_agent import ALIAS
from bluer_agent.help.chat import help_functions as help_chat
from bluer_agent.help.transcription import help_functions as help_transcription

help_functions = generic_help_functions(plugin_name=ALIAS)

help_functions.update(
    {
        "chat": help_chat,
        "transcription": help_transcription,
    }
)
