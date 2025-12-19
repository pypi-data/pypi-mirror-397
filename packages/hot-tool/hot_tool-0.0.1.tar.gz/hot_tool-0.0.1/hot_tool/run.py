# hot_tool/run.py
import argparse
import logging
import sys
from typing import Optional, Type, Union

from hot_tool import (
    HotMultipleToolImplementationsFoundError,
    HotTool,
    HotToolImplementationNotFoundError,
)

logger = logging.getLogger(__name__)


def run_tool(
    tool: Union[Type[HotTool], HotTool],
    arguments: Optional[str] = None,
    context: Optional[str] = None,
) -> str:
    if isinstance(tool, Type) and issubclass(tool, HotTool):
        tool = tool()
    elif isinstance(tool, HotTool):
        tool = tool
    else:
        raise ValueError(f"Invalid tool type: {type(tool)}")

    return tool.run(arguments=arguments, context=context)


def run_as_executable():
    subclasses = HotTool.__subclasses__()
    if len(subclasses) == 0:
        raise HotToolImplementationNotFoundError("No implementation found for HotTool.")
    elif len(subclasses) > 1:
        raise HotMultipleToolImplementationsFoundError(
            "Multiple implementations found for HotTool, "
            + "only one in script is allowed."
        )

    subclass_cls = subclasses[0]

    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--arguments",
        type=str,
        default=None,
        help="Arguments for the tool. default is None.",
    )
    parser.add_argument(
        "--context",
        type=str,
        default=None,
        help="Context for the tool. default is None.",
    )
    args = parser.parse_args()

    try:
        result = run_tool(subclass_cls, arguments=args.arguments, context=args.context)
        logger.info(f"Tool result: {str(result)[:100]}")
        print(result)  # print to stdout for LLM to read

    except Exception as e:
        logger.exception(e)
        logger.error(f"Error running tool: {e}")
        sys.exit(1)

    return None


def make_script_runnable(script: str) -> str:
    from textwrap import dedent

    return (
        script.strip()
        + "\n\n\n"
        + dedent(
            """
            from hot_tool.run import run_as_executable

            run_as_executable()
            """
        ).strip()
    )
