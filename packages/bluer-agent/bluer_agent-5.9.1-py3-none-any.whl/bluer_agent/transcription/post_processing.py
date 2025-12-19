from blueness import module
from bluer_objects import file, objects
from bluer_objects.metadata import post_to_object

from bluer_agent import NAME
from bluer_agent.logger import logger


NAME = module.name(__file__, NAME)


def post_process(
    object_name: str,
    filename: str,
    language: str = "fa",
) -> bool:
    logger.info(
        "{}.post_process({}/{}) [{}]".format(
            NAME,
            object_name,
            file.name_and_extension(filename),
            language,
        )
    )

    success, content = file.load_json(
        objects.path_of(
            object_name=object_name,
            filename="transcript.json",
        ),
        default={},
    )
    if not success:
        return success

    if not isinstance(content, dict):
        logger.error("content is not a dict")
        return False

    text = content.get("text", "")

    logger.info(text)

    return post_to_object(
        object_name,
        file.name(filename),
        text,
    )
