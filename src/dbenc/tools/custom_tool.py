from crewai.tools import BaseTool
from typing import Dict, Any, Optional
from pydantic import Field
import json
import logging

logger = logging.getLogger(__name__)

class CustomTool(BaseTool):
    """
    A custom tool that wraps our existing tools to make them compatible with CrewAI 0.108.0
    """
    name: str = Field(description="The name of the tool")
    description: str = Field(description="The description of the tool")
    tool_instance: Any = Field(description="The tool instance to wrap")

    def _run(self, input_str: str) -> Dict[str, Any]:
        """Run the tool with the specified input"""
        logger.info(f"Running CustomTool for {self.name} with input: {input_str}")

        try:
            # Try to parse the input as JSON
            if isinstance(input_str, str):
                try:
                    parsed_input = json.loads(input_str)
                    if isinstance(parsed_input, dict):
                        return self.tool_instance._run(input_str)
                except (json.JSONDecodeError, TypeError):
                    # If not valid JSON, pass as is
                    pass

            # If we get here, just pass the input as is
            return self.tool_instance._run(input_str)
        except Exception as e:
            logger.error(f"Error in CustomTool: {e}")
            return {"error": f"Error processing request: {str(e)}"}
