import os

from bluer_options.help.functions import get_help
from bluer_objects import file, README

from bluer_agent import NAME, VERSION, ICON, REPO_NAME
from bluer_agent.help.functions import help_functions

items = README.Items(
    [
        {
            "name": "chat",
            "marquee": "https://github.com/kamangir/assets2/raw/main/bluer-agent/icon.jpg?raw=true",
            "url": "./bluer_agent/docs/chat",
        },
        {
            "name": "transcription",
            "marquee": "https://github.com/kamangir/assets2/raw/main/bluer-agent/icon.jpg?raw=true",
            "url": "./bluer_agent/docs/transcription",
        },
    ]
)


def build():
    return all(
        README.build(
            items=readme.get("items", []),
            path=os.path.join(file.path(__file__), readme["path"]),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
            help_function=lambda tokens: get_help(
                tokens,
                help_functions,
                mono=True,
            ),
        )
        for readme in [
            {
                "path": "..",
                "items": items,
            },
            {
                "path": "./docs",
            },
            # aliases
            {
                "path": "./docs/aliases",
            },
            {
                "path": "./docs/aliases/agent.md",
            },
            # features
            {
                "path": "./docs/chat",
            },
            {
                "path": "./docs/chat/validation.md",
            },
            {
                "path": "./docs/transcription",
            },
            {
                "path": "./docs/transcription/validation.md",
            },
        ]
    )
