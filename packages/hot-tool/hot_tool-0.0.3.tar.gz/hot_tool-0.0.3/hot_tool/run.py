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


def get_all_descendants(base_class: Type) -> list[Type]:
    """
    Recursively get all descendant classes of a base class.
    Returns a flat list of all subclasses at any depth.
    """
    result: list[Type] = []
    for child in base_class.__subclasses__():
        result.append(child)
        # Recursively get descendants of this child
        result.extend(get_all_descendants(child))
    return result


def get_concrete_tool_classes(
    base_class: Type[HotTool], module_name: Optional[str] = None
) -> list[Type[HotTool]]:
    """
    Get concrete tool classes that implement run().
    Optionally filter by module name to get only script-defined classes.
    """
    all_descendants = get_all_descendants(base_class)
    concrete_classes: list[Type[HotTool]] = []

    for cls in all_descendants:
        # Check if this class defines its own run() method
        if "run" in cls.__dict__:
            # If module_name is specified, only include classes from that module
            if module_name is None or cls.__module__ == module_name:
                concrete_classes.append(cls)

    return concrete_classes


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
    # Only get tools defined in the current script (__main__)
    concrete_tools = get_concrete_tool_classes(HotTool, module_name="__main__")

    if len(concrete_tools) == 0:
        # Check if there are any HotTool subclasses at all in the script
        all_script_descendants = [
            cls for cls in get_all_descendants(HotTool) if cls.__module__ == "__main__"
        ]

        if len(all_script_descendants) == 0:
            raise HotToolImplementationNotFoundError(
                "No tool class found in this script. "
                "Please define a class that inherits from HotTool "
                "and implements the run() method."
            )
        else:
            # Found classes but none implement run()
            class_names = [cls.__name__ for cls in all_script_descendants]
            raise HotToolImplementationNotFoundError(
                f"Found tool class(es) {class_names} but none "
                "implement the run() method. "
                "Please add a run(self, arguments=None, context=None) "
                "method to your tool class."
            )
    elif len(concrete_tools) > 1:
        tool_names = [cls.__name__ for cls in concrete_tools]
        raise HotMultipleToolImplementationsFoundError(
            f"Multiple tool implementations found in script: {tool_names}. "
            "Only one concrete tool class is allowed per script."
        )

    tool_class = concrete_tools[0]

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
        result = run_tool(tool_class, arguments=args.arguments, context=args.context)
        logger.info(f"Tool result: {str(result)[:100]}")
        print(result)  # print to stdout for LLM to read

    except Exception as e:
        logger.exception(e)
        logger.error(f"Error running tool: {e}")
        sys.exit(1)

    return None
