from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langchain_core.messages import BaseMessage, ToolCall
from langchain_core.prompt_values import ChatPromptValue, PromptValue, StringPromptValue
from langchain_core.tools import ArgsSchema, BaseTool
from pydantic import BaseModel

if TYPE_CHECKING:
    from langchain_core.runnables.config import RunnableConfig


class _CrowdStrikeBaseToolInput(BaseModel):
    input_data: str | dict | ToolCall | list[BaseMessage]


class CrowdStrikeBaseTool(BaseTool):
    """
    Base class for CrowdStrike AIDR tools with support for handling multiple
    input types, enabling their seamless integration and transparent use in
    chains.

    To extend this class, implement the `_process_text` method to define
    specific text processing logic.
    """

    args_schema: ArgsSchema = _CrowdStrikeBaseToolInput

    def invoke(
        self,
        input: str | dict | ToolCall | BaseMessage | list[BaseMessage] | PromptValue,
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> Any:
        # Check if the input is a ToolCall.
        if isinstance(input, dict) and "name" in input and "args" in input:
            return super().invoke(input, config, **kwargs)
        else:
            # Process the input data.
            return self._run(input)

    def _run(
        self, input_data: str | dict | ToolCall | BaseMessage | list[BaseMessage] | PromptValue
    ) -> str | dict | ToolCall | BaseMessage | list[BaseMessage] | PromptValue:
        """Process the input data in a subclass using its _process_text method."""
        if isinstance(input_data, str):
            return self._process_text(input_data)
        elif isinstance(input_data, PromptValue):
            return self._process_prompt_value(input_data)
        elif isinstance(input_data, BaseMessage):
            return self._process_single_message(input_data)
        elif isinstance(input_data, list) and all(isinstance(message, BaseMessage) for message in input_data):
            return self._process_messages(input_data)
        else:
            raise TypeError(f"Unsupported input type: {type(input_data)}")

    def _process_text(self, text: str) -> str:
        """Process a string input."""
        # Implement text processing in subclasses.
        raise NotImplementedError("_process_text must be implemented in subclass.")

    def _process_prompt_value(self, prompt_value: PromptValue) -> PromptValue:
        """Process a PromptValue."""
        if isinstance(prompt_value, ChatPromptValue):
            # For ChatPromptValue, process the messages.
            processed_messages = self._process_messages(prompt_value.to_messages())

            # Reconstruct the ChatPromptValue with the processed messages.
            return ChatPromptValue(messages=processed_messages)
        else:
            # For other PromptValue types, process the string representation.
            processed_text = self._process_text(prompt_value.to_string())

            # Reconstruct the PromptValue with the processed content.
            return StringPromptValue(text=processed_text)

    def _process_single_message(self, message: BaseMessage) -> BaseMessage:
        """Process a single message."""
        # Get all the attributes of the message as a dictionary.
        message_dict = message.__dict__.copy()

        # Process the message content.
        message_dict["content"] = self._process_text(message.text())

        # Create a new instance of the message with the processed content.
        return message.__class__(**message_dict)

    def _process_messages(self, messages: list[BaseMessage]) -> list[BaseMessage]:
        """Process a list of messages."""
        return [self._process_single_message(message) for message in messages]
