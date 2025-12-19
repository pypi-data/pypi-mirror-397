from __future__ import annotations

import os

from crowdstrike_aidr import AIGuard
from pydantic import SecretStr

from langchain_aidr.tools.base import CrowdStrikeBaseTool


class CrowdStrikeAIGuardError(RuntimeError):
    """
    Exception raised for unexpected scenarios or when malicious prompt is detected.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class CrowdStrikeAIGuard(CrowdStrikeBaseTool):
    """
    Use CrowdStrike AIDR to monitor, sanitize, and protect sensitive data.

    Requirements:
        - Environment variable ``CS_AIDR_TOKEN`` must be set,
          or passed as a named parameter to the constructor.
    """  # noqa: E501

    _client: AIGuard
    _recipe: str

    def __init__(self, *, token: SecretStr | None = None, base_url_template: str | None = None) -> None:
        """
        Args:
            token: CrowdStrike AIDR API token.
            base_url_template: CrowdStrike AIDR base URL template.
        """

        if not token:
            token = SecretStr(os.getenv("CS_AIDR_TOKEN", ""))

        if not token or not token.get_secret_value() or token.get_secret_value() == "":
            raise ValueError("Missing CrowdStrike AIDR API token")

        if not base_url_template:
            raise ValueError("Missing CrowdStrike AIDR base URL template")

        super().__init__(
            name="crowdstrike-aidr-aiguard-tool",
            description=(
                "Identifies and redacts PII and sensitive information in AI "
                "prompts, responses, and RAG context data. Detects and blocks "
                "malware submitted by users or ingested via agents or RAG file "
                "ingestion. Flags or hides malicious IP addresses, domains, "
                "and URLs embedded in prompts, responses, or data vectors."
            ),
        )
        self._client = AIGuard(base_url_template=base_url_template, token=token.get_secret_value())

    def _process_text(self, input_text: str) -> str:
        guarded = self._client.guard_chat_completions(
            guard_input={"messages": [{"role": "user", "content": input_text}]}
        )

        if not guarded.result:
            raise CrowdStrikeAIGuardError("Result is invalid or missing")

        if guarded.result.guard_output is None:
            return input_text

        if guarded.result.guard_output["messages"]:
            input_text = guarded.result.guard_output["messages"][-1]["content"]

        return input_text
