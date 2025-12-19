from blueness import module
from bluer_objects import file, objects
from bluer_objects.metadata import post_to_object

from bluer_agent import NAME
from bluer_agent.logger import logger


NAME = module.name(__file__, NAME)


def post_process(
    object_name: str,
) -> bool:
    logger.info(f"{NAME}.post_process({object_name})")

    success, content = file.load_json(
        objects.path_of(
            object_name=object_name,
            filename="chat.json",
        ),
        default={},
    )
    if not success:
        return success

    if not isinstance(content, dict):
        logger.error("content is not a dict")
        return False

    if "choices" not in content:
        logger.error("choices not in content")
        return False
    if len(content["choices"]) == 0:
        logger.error("choices is empty")
        return False
    if len(content["choices"]) > 1:
        logger.warning(
            "{} choice(s), will use the first one.".format(content["choices"])
        )

    text = content["choices"][0].get("message", {}).get("content", "")
    logger.info(text)

    return post_to_object(
        object_name,
        "chat",
        text,
    )
