import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_agent import NAME
from bluer_agent.transcription.post_processing import post_process
from bluer_agent.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="post_process",
)
parser.add_argument(
    "--object_name",
    type=str,
)
parser.add_argument(
    "--filename",
    type=str,
)
parser.add_argument(
    "--language",
    type=str,
    default="fa",
    help="en | fa",
)
args = parser.parse_args()

success = False
if args.task == "post_process":
    success = post_process(
        object_name=args.object_name,
        filename=args.filename,
        language=args.language,
    )
else:
    success = None

sys_exit(logger, NAME, args.task, success)
