from typing import List

from bluer_options.terminal import show_usage, xtra


def help_validate(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "".join(
        [
            xtra(
                "download,",
                mono=mono,
            ),
            "filename=<filename.wav>",
            xtra(
                ",install,",
                mono=mono,
            ),
            "language=en|fa",
            xtra(
                ",~play,",
                mono=mono,
            ),
            "record",
            xtra(
                ",upload,verbose",
                mono=mono,
            ),
        ]
    )

    return show_usage(
        [
            "@agent",
            "transcription",
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
