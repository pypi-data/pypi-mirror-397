from __future__ import annotations

from typing import override

from langchain_tests.unit_tests import ToolsUnitTests
from pydantic import SecretStr

from langchain_aidr import CrowdStrikeAIGuard


class TestAIGuard(ToolsUnitTests):
    @override
    @property
    def tool_constructor(self) -> type[CrowdStrikeAIGuard]:
        return CrowdStrikeAIGuard

    @override
    @property
    def tool_constructor_params(self) -> dict:
        return {
            "token": SecretStr("my_api_token"),
            "base_url_template": "https://api.crowdstrike.com/aidr/{SERVICE_NAME}",
        }

    @override
    @property
    def tool_invoke_params_example(self) -> dict:
        return {"input_data": "foo"}
