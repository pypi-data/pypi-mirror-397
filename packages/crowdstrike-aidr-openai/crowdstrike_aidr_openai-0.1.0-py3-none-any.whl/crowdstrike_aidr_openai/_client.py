from __future__ import annotations

import os
from typing import Any

from crowdstrike_aidr import AIGuard
from openai import AsyncOpenAI, OpenAI
from openai._compat import cached_property
from typing_extensions import override

from crowdstrike_aidr_openai._exceptions import CrowdStrikeError
from crowdstrike_aidr_openai.resources.responses.responses import AsyncCrowdStrikeResponses, CrowdStrikeResponses

__all__ = ("CrowdStrikeOpenAI", "AsyncCrowdStrikeOpenAI")


class CrowdStrikeOpenAI(OpenAI):
    def __init__(
        self,
        *,
        crowdstrike_aidr_api_key: str | None = None,
        crowdstrike_aidr_base_url_template: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        if crowdstrike_aidr_api_key is None:
            crowdstrike_aidr_api_key = os.environ.get("CS_AIDR_API_TOKEN")
        if crowdstrike_aidr_api_key is None:
            raise CrowdStrikeError(
                "The crowdstrike_aidr_api_key client option must be set either by "
                "passing crowdstrike_aidr_api_key to the client or by setting "
                "the CS_AIDR_API_TOKEN environment variable"
            )

        if crowdstrike_aidr_base_url_template is None:
            crowdstrike_aidr_base_url_template = os.environ.get("CS_AIDR_BASE_URL_TEMPLATE")
        if crowdstrike_aidr_base_url_template is None:
            raise CrowdStrikeError(
                "The crowdstrike_aidr_base_url_template client option must be "
                "set either by passing crowdstrike_aidr_base_url_template to "
                "the client or by setting the CS_AIDR_BASE_URL_TEMPLATE "
                "environment variable"
            )

        self.ai_guard_client = AIGuard(
            token=crowdstrike_aidr_api_key, base_url_template=crowdstrike_aidr_base_url_template
        )

    @cached_property
    @override
    def responses(self) -> CrowdStrikeResponses:
        return CrowdStrikeResponses(self)


class AsyncCrowdStrikeOpenAI(AsyncOpenAI):
    def __init__(
        self,
        *,
        crowdstrike_aidr_api_key: str | None = None,
        crowdstrike_aidr_base_url_template: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        if crowdstrike_aidr_api_key is None:
            crowdstrike_aidr_api_key = os.environ.get("CS_AIDR_API_TOKEN")
        if crowdstrike_aidr_api_key is None:
            raise CrowdStrikeError(
                "The crowdstrike_aidr_api_key client option must be set either by "
                "passing crowdstrike_aidr_api_key to the client or by setting "
                "the CS_AIDR_API_TOKEN environment variable"
            )

        if crowdstrike_aidr_base_url_template is None:
            crowdstrike_aidr_base_url_template = os.environ.get("CS_AIDR_BASE_URL_TEMPLATE")
        if crowdstrike_aidr_base_url_template is None:
            raise CrowdStrikeError(
                "The crowdstrike_aidr_base_url_template client option must be "
                "set either by passing crowdstrike_aidr_base_url_template to "
                "the client or by setting the CS_AIDR_BASE_URL_TEMPLATE "
                "environment variable"
            )

        self.ai_guard_client = AIGuard(
            token=crowdstrike_aidr_api_key, base_url_template=crowdstrike_aidr_base_url_template
        )

    @cached_property
    @override
    def responses(self) -> AsyncCrowdStrikeResponses:
        return AsyncCrowdStrikeResponses(self)
