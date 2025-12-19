from typing import List

from bluer_options.terminal import show_usage, xtra


def help_validate(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra(
        "upload,verbose",
        mono=mono,
    )

    return show_usage(
        [
            "@agent",
            "chat",
            "validate",
            f"[{options}]",
            "[-|<object-name>]",
        ],
        "validate agent.",
        mono=mono,
    )


help_functions = {
    "validate": help_validate,
}
