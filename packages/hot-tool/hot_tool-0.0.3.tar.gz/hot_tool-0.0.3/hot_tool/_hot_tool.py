from typing import Optional


class HotTool:
    def run(
        self, arguments: Optional[str] = None, context: Optional[str] = None
    ) -> str:
        raise NotImplementedError("Subclasses must implement this method")
