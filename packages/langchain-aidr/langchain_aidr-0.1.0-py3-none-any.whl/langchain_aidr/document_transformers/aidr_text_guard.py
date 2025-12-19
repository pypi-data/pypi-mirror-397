from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from crowdstrike_aidr import AIGuard
from langchain_core.documents import BaseDocumentTransformer, Document
from pydantic import SecretStr

if TYPE_CHECKING:
    from collections.abc import Sequence


class CrowdStrikeGuardTransformer(BaseDocumentTransformer):
    """
    Guard documents to monitor, sanitize, and protect sensitive data using
    CrowdStrike AIDR.

    Requirements:
        - Environment variable ``CS_AIDR_TOKEN`` must be set,
          or passed as a named parameter to the constructor.
    """

    _client: AIGuard

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

        self._client = AIGuard(base_url_template=base_url_template, token=token.get_secret_value())

    async def atransform_documents(self, documents: Sequence[Document], **kwargs: Any) -> Sequence[Document]:
        raise NotImplementedError

    def transform_documents(self, documents: Sequence[Document], **kwargs: Any) -> Sequence[Document]:
        """
        Guard documents to monitor, sanitize, and protect sensitive data
        using CrowdStrike AIDR.
        """

        guarded_documents = []
        for document in documents:
            guarded = self._client.guard_chat_completions(
                guard_input={"messages": [{"role": "user", "content": document.page_content}]}
            )

            if not guarded.result:
                raise AssertionError(f"Guard operation failed for document: {document}")

            guarded_content = (
                guarded.result.guard_output["messages"][-1]["content"]
                if guarded.result.guard_output
                else document.page_content
            )
            guarded_documents.append(document.model_copy(update={"page_content": guarded_content}))

        return guarded_documents
