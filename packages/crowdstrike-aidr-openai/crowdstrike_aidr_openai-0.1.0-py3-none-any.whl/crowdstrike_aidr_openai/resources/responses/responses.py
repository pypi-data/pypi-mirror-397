from __future__ import annotations

from collections.abc import Iterable
from itertools import chain
from typing import TYPE_CHECKING, List, Literal, Optional, Union, overload

import httpx
from openai import AsyncStream, NotGiven, Omit, Stream, not_given, omit
from openai._types import Body, Headers, Query
from openai.resources.responses import AsyncResponses, Responses
from openai.types.responses import ResponseOutputMessage, ResponseOutputText, response_create_params
from openai.types.responses.easy_input_message_param import EasyInputMessageParam
from openai.types.responses.response import Response
from openai.types.responses.response_code_interpreter_tool_call_param import ResponseCodeInterpreterToolCallParam
from openai.types.responses.response_computer_tool_call_param import ResponseComputerToolCallParam
from openai.types.responses.response_custom_tool_call_output_param import ResponseCustomToolCallOutputParam
from openai.types.responses.response_custom_tool_call_param import ResponseCustomToolCallParam
from openai.types.responses.response_file_search_tool_call_param import ResponseFileSearchToolCallParam
from openai.types.responses.response_function_tool_call_param import ResponseFunctionToolCallParam
from openai.types.responses.response_function_web_search_param import ResponseFunctionWebSearchParam
from openai.types.responses.response_includable import ResponseIncludable
from openai.types.responses.response_input_param import (
    ApplyPatchCall,
    ApplyPatchCallOutput,
    ComputerCallOutput,
    FunctionCallOutput,
    ImageGenerationCall,
    ItemReference,
    LocalShellCall,
    LocalShellCallOutput,
    McpApprovalRequest,
    McpApprovalResponse,
    McpCall,
    McpListTools,
    ResponseInputItemParam,
    ResponseInputParam,
    ShellCall,
    ShellCallOutput,
)
from openai.types.responses.response_input_param import (
    Message as OpenAIMessage,
)
from openai.types.responses.response_output_message_param import ResponseOutputMessageParam
from openai.types.responses.response_prompt_param import ResponsePromptParam
from openai.types.responses.response_reasoning_item_param import ResponseReasoningItemParam
from openai.types.responses.response_stream_event import ResponseStreamEvent
from openai.types.responses.response_text_config_param import ResponseTextConfigParam
from openai.types.responses.tool_param import ToolParam
from openai.types.shared_params.metadata import Metadata
from openai.types.shared_params.reasoning import Reasoning
from openai.types.shared_params.responses_model import ResponsesModel
from pydantic import BaseModel, ConfigDict, TypeAdapter
from pydantic_core import to_jsonable_python
from typing_extensions import assert_never, override

from crowdstrike_aidr_openai._exceptions import CrowdStrikeAIDRBlockedError

if TYPE_CHECKING:
    from crowdstrike_aidr_openai._client import AsyncCrowdStrikeOpenAI, CrowdStrikeOpenAI

__all__ = ("CrowdStrikeResponses", "AsyncCrowdStrikeResponses")


class Message(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Optional[str] = None
    content: str


list_message_adapter: TypeAdapter[list[Message]] = TypeAdapter(list[Message])


def to_pangea_messages(item: ResponseInputItemParam) -> list[Message]:
    match item:
        case EasyInputMessageParam() as msg:
            if isinstance(msg["content"], str):
                return [Message(role=str(msg["role"]), content=msg["content"])]
            elif isinstance(msg["content"], list):
                return [
                    Message(role=str(msg["role"]), content=item["text"])
                    for item in msg["content"]
                    if item["type"] == "input_text"
                ]
            else:
                return []
        case OpenAIMessage() as msg:
            return [
                Message(role=str(msg["role"]), content=item["text"])
                for item in msg["content"]  # type: ignore[attr-defined]
                if item["type"] == "input_text"
            ]
        case ResponseOutputMessageParam() as msg:
            return [
                Message(role=str(msg["role"]), content=item["text"])
                for item in msg["content"]  # type: ignore[attr-defined]
                if item["type"] == "output_text"
            ]
        case ResponseFileSearchToolCallParam() as msg:
            return []
        case ResponseComputerToolCallParam() as msg:
            return []
        case ComputerCallOutput() as msg:
            return []
        case ResponseFunctionWebSearchParam() as msg:
            return []
        case ResponseFunctionToolCallParam() as msg:
            return []
        case FunctionCallOutput() as msg:
            return []
        case ResponseReasoningItemParam() as msg:
            return []
        case ImageGenerationCall() as msg:
            return []
        case ResponseCodeInterpreterToolCallParam() as msg:
            return []
        case LocalShellCall() as msg:
            return []
        case LocalShellCallOutput() as msg:
            return []
        case McpListTools() as msg:
            return []
        case McpApprovalRequest() as msg:
            return []
        case McpApprovalResponse() as msg:
            return []
        case McpCall() as msg:
            return []
        case ResponseCustomToolCallOutputParam() as msg:
            return []
        case ResponseCustomToolCallParam() as msg:
            return []
        case ItemReference() as msg:
            return []
        case ShellCall() as msg:
            return []
        case ShellCallOutput() as msg:
            return []
        case ApplyPatchCall() as msg:
            return []
        case ApplyPatchCallOutput() as msg:
            return []
        case _ as unhandled_item:
            assert_never(unhandled_item)
            return []


class CrowdStrikeResponses(Responses):
    _client: CrowdStrikeOpenAI

    @override
    def __init__(self, client: CrowdStrikeOpenAI) -> None:
        super().__init__(client)
        self._client = client

    @overload
    def create(
        self,
        *,
        background: Optional[bool] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Optional[Literal[False]] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via
        # kwargs. The extra values given here take precedence over values defined on the client or passed to this
        # method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          background: Whether to run the model response in the background.
              [Learn more](https://platform.openai.com/docs/guides/background).

          conversation: The conversation that this response belongs to. Items from this conversation are
              prepended to `input_items` for this response request. Input items and output
              items from this response are automatically added to this conversation after this
              response completes.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `web_search_call.action.sources`: Include the sources of the web search tool
                call.
              - `code_interpreter_call.outputs`: Includes the outputs of python code execution
                in code interpreter tool call items.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.
              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `message.output_text.logprobs`: Include logprobs with assistant messages.
              - `reasoning.encrypted_content`: Includes an encrypted version of reasoning
                tokens in reasoning item outputs. This enables reasoning items to be used in
                multi-turn conversations when using the Responses API statelessly (like when
                the `store` parameter is set to `false`, or when an organization is enrolled
                in the zero data retention program).

          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          instructions: A system (or developer) message inserted into the model's context.

              When using along with `previous_response_id`, the instructions from a previous
              response will not be carried over to the next response. This makes it simple to
              swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          max_tool_calls: The maximum number of total calls to built-in tools that can be processed in a
              response. This maximum number applies across all built-in tool calls, not per
              individual tool. Any further attempts to call a tool by the model will be
              ignored.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          model: Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).
              Cannot be used in conjunction with `conversation`.

          prompt: Reference to a prompt template and its variables.
              [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).

          prompt_cache_key: Used by OpenAI to cache responses for similar requests to optimize your cache
              hit rates. Replaces the `user` field.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching).

          prompt_cache_retention: The retention policy for the prompt cache. Set to `24h` to enable extended
              prompt caching, which keeps cached prefixes active for longer, up to a maximum
              of 24 hours.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching#prompt-cache-retention).

          reasoning: **gpt-5 and o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          safety_identifier: A stable identifier used to help detect users of your application that may be
              violating OpenAI's usage policies. The IDs should be a string that uniquely
              identifies each user. We recommend hashing their username or email address, in
              order to avoid sending us any identifying information.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          service_tier: Specifies the processing type used for serving the request.

              - If set to 'auto', then the request will be processed with the service tier
                configured in the Project settings. Unless otherwise configured, the Project
                will use 'default'.
              - If set to 'default', then the request will be processed with the standard
                pricing and performance for the selected model.
              - If set to '[flex](https://platform.openai.com/docs/guides/flex-processing)' or
                '[priority](https://openai.com/api-priority-processing/)', then the request
                will be processed with the corresponding service tier.
              - When not set, the default behavior is 'auto'.

              When the `service_tier` parameter is set, the response body will include the
              `service_tier` value based on the processing mode actually used to serve the
              request. This response value may be different from the value set in the
              parameter.

          store: Whether to store the generated model response for later retrieval via API.

          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          stream_options: Options for streaming responses. Only set this when you set `stream: true`.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              The two categories of tools you can provide the model are:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code with strongly typed arguments and outputs.
                Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).
                You can also use custom tools to call your own code.

          top_logprobs: An integer between 0 and 20 specifying the number of most likely tokens to
              return at each token position, each with an associated log probability.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the context of this response and previous ones exceeds the model's
                context window size, the model will truncate the response to fit the context
                window by dropping input items in the middle of the conversation.
              - `disabled` (default): If a model response will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: This field is being replaced by `safety_identifier` and `prompt_cache_key`. Use
              `prompt_cache_key` instead to maintain caching optimizations. A stable
              identifier for your end-users. Used to boost cache hit rates by better bucketing
              similar requests and to help OpenAI detect and prevent abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        stream: Literal[True],
        background: Optional[bool] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via
        # kwargs. The extra values given here take precedence over values defined on the client or passed to this
        # method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[ResponseStreamEvent]:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          background: Whether to run the model response in the background.
              [Learn more](https://platform.openai.com/docs/guides/background).

          conversation: The conversation that this response belongs to. Items from this conversation are
              prepended to `input_items` for this response request. Input items and output
              items from this response are automatically added to this conversation after this
              response completes.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `web_search_call.action.sources`: Include the sources of the web search tool
                call.
              - `code_interpreter_call.outputs`: Includes the outputs of python code execution
                in code interpreter tool call items.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.
              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `message.output_text.logprobs`: Include logprobs with assistant messages.
              - `reasoning.encrypted_content`: Includes an encrypted version of reasoning
                tokens in reasoning item outputs. This enables reasoning items to be used in
                multi-turn conversations when using the Responses API statelessly (like when
                the `store` parameter is set to `false`, or when an organization is enrolled
                in the zero data retention program).

          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          instructions: A system (or developer) message inserted into the model's context.

              When using along with `previous_response_id`, the instructions from a previous
              response will not be carried over to the next response. This makes it simple to
              swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          max_tool_calls: The maximum number of total calls to built-in tools that can be processed in a
              response. This maximum number applies across all built-in tool calls, not per
              individual tool. Any further attempts to call a tool by the model will be
              ignored.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          model: Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).
              Cannot be used in conjunction with `conversation`.

          prompt: Reference to a prompt template and its variables.
              [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).

          prompt_cache_key: Used by OpenAI to cache responses for similar requests to optimize your cache
              hit rates. Replaces the `user` field.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching).

          prompt_cache_retention: The retention policy for the prompt cache. Set to `24h` to enable extended
              prompt caching, which keeps cached prefixes active for longer, up to a maximum
              of 24 hours.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching#prompt-cache-retention).

          reasoning: **gpt-5 and o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          safety_identifier: A stable identifier used to help detect users of your application that may be
              violating OpenAI's usage policies. The IDs should be a string that uniquely
              identifies each user. We recommend hashing their username or email address, in
              order to avoid sending us any identifying information.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          service_tier: Specifies the processing type used for serving the request.

              - If set to 'auto', then the request will be processed with the service tier
                configured in the Project settings. Unless otherwise configured, the Project
                will use 'default'.
              - If set to 'default', then the request will be processed with the standard
                pricing and performance for the selected model.
              - If set to '[flex](https://platform.openai.com/docs/guides/flex-processing)' or
                '[priority](https://openai.com/api-priority-processing/)', then the request
                will be processed with the corresponding service tier.
              - When not set, the default behavior is 'auto'.

              When the `service_tier` parameter is set, the response body will include the
              `service_tier` value based on the processing mode actually used to serve the
              request. This response value may be different from the value set in the
              parameter.

          store: Whether to store the generated model response for later retrieval via API.

          stream_options: Options for streaming responses. Only set this when you set `stream: true`.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              The two categories of tools you can provide the model are:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code with strongly typed arguments and outputs.
                Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).
                You can also use custom tools to call your own code.

          top_logprobs: An integer between 0 and 20 specifying the number of most likely tokens to
              return at each token position, each with an associated log probability.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the context of this response and previous ones exceeds the model's
                context window size, the model will truncate the response to fit the context
                window by dropping input items in the middle of the conversation.
              - `disabled` (default): If a model response will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: This field is being replaced by `safety_identifier` and `prompt_cache_key`. Use
              `prompt_cache_key` instead to maintain caching optimizations. A stable
              identifier for your end-users. Used to boost cache hit rates by better bucketing
              similar requests and to help OpenAI detect and prevent abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        stream: bool,
        background: Optional[bool] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via
        # kwargs. The extra values given here take precedence over values defined on the client or passed to this
        # method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response | Stream[ResponseStreamEvent]:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          background: Whether to run the model response in the background.
              [Learn more](https://platform.openai.com/docs/guides/background).

          conversation: The conversation that this response belongs to. Items from this conversation are
              prepended to `input_items` for this response request. Input items and output
              items from this response are automatically added to this conversation after this
              response completes.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `web_search_call.action.sources`: Include the sources of the web search tool
                call.
              - `code_interpreter_call.outputs`: Includes the outputs of python code execution
                in code interpreter tool call items.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.
              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `message.output_text.logprobs`: Include logprobs with assistant messages.
              - `reasoning.encrypted_content`: Includes an encrypted version of reasoning
                tokens in reasoning item outputs. This enables reasoning items to be used in
                multi-turn conversations when using the Responses API statelessly (like when
                the `store` parameter is set to `false`, or when an organization is enrolled
                in the zero data retention program).

          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          instructions: A system (or developer) message inserted into the model's context.

              When using along with `previous_response_id`, the instructions from a previous
              response will not be carried over to the next response. This makes it simple to
              swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          max_tool_calls: The maximum number of total calls to built-in tools that can be processed in a
              response. This maximum number applies across all built-in tool calls, not per
              individual tool. Any further attempts to call a tool by the model will be
              ignored.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          model: Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).
              Cannot be used in conjunction with `conversation`.

          prompt: Reference to a prompt template and its variables.
              [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).

          prompt_cache_key: Used by OpenAI to cache responses for similar requests to optimize your cache
              hit rates. Replaces the `user` field.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching).

          prompt_cache_retention: The retention policy for the prompt cache. Set to `24h` to enable extended
              prompt caching, which keeps cached prefixes active for longer, up to a maximum
              of 24 hours.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching#prompt-cache-retention).

          reasoning: **gpt-5 and o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          safety_identifier: A stable identifier used to help detect users of your application that may be
              violating OpenAI's usage policies. The IDs should be a string that uniquely
              identifies each user. We recommend hashing their username or email address, in
              order to avoid sending us any identifying information.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          service_tier: Specifies the processing type used for serving the request.

              - If set to 'auto', then the request will be processed with the service tier
                configured in the Project settings. Unless otherwise configured, the Project
                will use 'default'.
              - If set to 'default', then the request will be processed with the standard
                pricing and performance for the selected model.
              - If set to '[flex](https://platform.openai.com/docs/guides/flex-processing)' or
                '[priority](https://openai.com/api-priority-processing/)', then the request
                will be processed with the corresponding service tier.
              - When not set, the default behavior is 'auto'.

              When the `service_tier` parameter is set, the response body will include the
              `service_tier` value based on the processing mode actually used to serve the
              request. This response value may be different from the value set in the
              parameter.

          store: Whether to store the generated model response for later retrieval via API.

          stream_options: Options for streaming responses. Only set this when you set `stream: true`.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              The two categories of tools you can provide the model are:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code with strongly typed arguments and outputs.
                Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).
                You can also use custom tools to call your own code.

          top_logprobs: An integer between 0 and 20 specifying the number of most likely tokens to
              return at each token position, each with an associated log probability.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the context of this response and previous ones exceeds the model's
                context window size, the model will truncate the response to fit the context
                window by dropping input items in the middle of the conversation.
              - `disabled` (default): If a model response will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: This field is being replaced by `safety_identifier` and `prompt_cache_key`. Use
              `prompt_cache_key` instead to maintain caching optimizations. A stable
              identifier for your end-users. Used to boost cache hit rates by better bucketing
              similar requests and to help OpenAI detect and prevent abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @override
    def create(
        self,
        *,
        background: Optional[bool] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Optional[Literal[False]] | Literal[True] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via
        # kwargs. The extra values given here take precedence over values defined on the client or passed to this
        # method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response | Stream[ResponseStreamEvent]:
        messages: list[Message] = []

        if isinstance(instructions, str):
            messages.append(Message(role="system", content=instructions))

        if isinstance(input, str):
            messages.append(Message(role="user", content=input))
        elif input:
            messages.extend(chain.from_iterable(to_pangea_messages(item) for item in input))

        guard_input_response = self._client.ai_guard_client.guard_chat_completions(
            guard_input={"messages": messages}, event_type="input"
        )

        assert guard_input_response.result is not None

        if guard_input_response.result.blocked:
            raise CrowdStrikeAIDRBlockedError()

        if guard_input_response.result.transformed and guard_input_response.result.guard_output is not None:
            input = to_jsonable_python(guard_input_response.result.guard_output["messages"])

        openai_response: Response = super().create(  # type: ignore[misc]
            background=background,
            conversation=conversation,
            include=include,
            input=input,
            instructions=instructions,
            max_output_tokens=max_output_tokens,
            max_tool_calls=max_tool_calls,
            metadata=metadata,
            model=model,
            parallel_tool_calls=parallel_tool_calls,
            previous_response_id=previous_response_id,
            prompt=prompt,
            prompt_cache_key=prompt_cache_key,
            reasoning=reasoning,
            safety_identifier=safety_identifier,
            service_tier=service_tier,
            store=store,
            stream=stream,  # type: ignore[arg-type]
            stream_options=stream_options,
            temperature=temperature,
            text=text,
            tool_choice=tool_choice,
            tools=tools,
            top_logprobs=top_logprobs,
            top_p=top_p,
            truncation=truncation,
            user=user,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

        output_messages = [
            Message(role=o.role, content=c.text)
            for o in openai_response.output
            if o.type == "message"
            for c in o.content
            if c.type == "output_text"
        ]

        # TODO: reintroduce.
        # FPE unredact.
        # if guard_input_response.result.fpe_context is not None:
        #     redact_response = self._client.redact_client.unredact(
        #         output_messages,
        #         fpe_context=guard_input_response.result.fpe_context,
        #     )
        #     assert redact_response.result is not None
        #     output_messages = list_message_adapter.validate_python(redact_response.result.data)

        guard_output_response = self._client.ai_guard_client.guard_chat_completions(
            guard_input={"messages": messages + output_messages},
            event_type="output",
        )

        assert guard_output_response.result is not None

        if guard_output_response.result.blocked:
            raise CrowdStrikeAIDRBlockedError()

        if guard_output_response.result.transformed and guard_output_response.result.guard_output is not None:
            openai_response.output = [
                ResponseOutputMessage(
                    type="message",
                    role="assistant",
                    status="completed",
                    id="",
                    content=[ResponseOutputText(type="output_text", text=x.content, annotations=[])],
                )
                for x in guard_output_response.result.guard_output["messages"]
                if x.role == "assistant"
            ]
        elif guard_input_response.result.fpe_context is not None:
            openai_response.output = [
                ResponseOutputMessage(
                    type="message",
                    role="assistant",
                    status="completed",
                    id="",
                    content=[ResponseOutputText(type="output_text", text=x.content, annotations=[])],
                )
                for x in output_messages
                if x.role == "assistant"
            ]

        return openai_response


class AsyncCrowdStrikeResponses(AsyncResponses):
    _client: AsyncCrowdStrikeOpenAI

    @overload
    async def create(
        self,
        *,
        background: Optional[bool] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Optional[Literal[False]] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via
        # kwargs. The extra values given here take precedence over values defined on the client or passed to this
        # method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          background: Whether to run the model response in the background.
              [Learn more](https://platform.openai.com/docs/guides/background).

          conversation: The conversation that this response belongs to. Items from this conversation are
              prepended to `input_items` for this response request. Input items and output
              items from this response are automatically added to this conversation after this
              response completes.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `web_search_call.action.sources`: Include the sources of the web search tool
                call.
              - `code_interpreter_call.outputs`: Includes the outputs of python code execution
                in code interpreter tool call items.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.
              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `message.output_text.logprobs`: Include logprobs with assistant messages.
              - `reasoning.encrypted_content`: Includes an encrypted version of reasoning
                tokens in reasoning item outputs. This enables reasoning items to be used in
                multi-turn conversations when using the Responses API statelessly (like when
                the `store` parameter is set to `false`, or when an organization is enrolled
                in the zero data retention program).

          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          instructions: A system (or developer) message inserted into the model's context.

              When using along with `previous_response_id`, the instructions from a previous
              response will not be carried over to the next response. This makes it simple to
              swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          max_tool_calls: The maximum number of total calls to built-in tools that can be processed in a
              response. This maximum number applies across all built-in tool calls, not per
              individual tool. Any further attempts to call a tool by the model will be
              ignored.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          model: Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).
              Cannot be used in conjunction with `conversation`.

          prompt: Reference to a prompt template and its variables.
              [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).

          prompt_cache_key: Used by OpenAI to cache responses for similar requests to optimize your cache
              hit rates. Replaces the `user` field.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching).

          prompt_cache_retention: The retention policy for the prompt cache. Set to `24h` to enable extended
              prompt caching, which keeps cached prefixes active for longer, up to a maximum
              of 24 hours.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching#prompt-cache-retention).

          reasoning: **gpt-5 and o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          safety_identifier: A stable identifier used to help detect users of your application that may be
              violating OpenAI's usage policies. The IDs should be a string that uniquely
              identifies each user. We recommend hashing their username or email address, in
              order to avoid sending us any identifying information.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          service_tier: Specifies the processing type used for serving the request.

              - If set to 'auto', then the request will be processed with the service tier
                configured in the Project settings. Unless otherwise configured, the Project
                will use 'default'.
              - If set to 'default', then the request will be processed with the standard
                pricing and performance for the selected model.
              - If set to '[flex](https://platform.openai.com/docs/guides/flex-processing)' or
                '[priority](https://openai.com/api-priority-processing/)', then the request
                will be processed with the corresponding service tier.
              - When not set, the default behavior is 'auto'.

              When the `service_tier` parameter is set, the response body will include the
              `service_tier` value based on the processing mode actually used to serve the
              request. This response value may be different from the value set in the
              parameter.

          store: Whether to store the generated model response for later retrieval via API.

          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          stream_options: Options for streaming responses. Only set this when you set `stream: true`.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              The two categories of tools you can provide the model are:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code with strongly typed arguments and outputs.
                Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).
                You can also use custom tools to call your own code.

          top_logprobs: An integer between 0 and 20 specifying the number of most likely tokens to
              return at each token position, each with an associated log probability.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the context of this response and previous ones exceeds the model's
                context window size, the model will truncate the response to fit the context
                window by dropping input items in the middle of the conversation.
              - `disabled` (default): If a model response will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: This field is being replaced by `safety_identifier` and `prompt_cache_key`. Use
              `prompt_cache_key` instead to maintain caching optimizations. A stable
              identifier for your end-users. Used to boost cache hit rates by better bucketing
              similar requests and to help OpenAI detect and prevent abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        stream: Literal[True],
        background: Optional[bool] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via
        # kwargs. The extra values given here take precedence over values defined on the client or passed to this
        # method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[ResponseStreamEvent]:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          background: Whether to run the model response in the background.
              [Learn more](https://platform.openai.com/docs/guides/background).

          conversation: The conversation that this response belongs to. Items from this conversation are
              prepended to `input_items` for this response request. Input items and output
              items from this response are automatically added to this conversation after this
              response completes.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `web_search_call.action.sources`: Include the sources of the web search tool
                call.
              - `code_interpreter_call.outputs`: Includes the outputs of python code execution
                in code interpreter tool call items.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.
              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `message.output_text.logprobs`: Include logprobs with assistant messages.
              - `reasoning.encrypted_content`: Includes an encrypted version of reasoning
                tokens in reasoning item outputs. This enables reasoning items to be used in
                multi-turn conversations when using the Responses API statelessly (like when
                the `store` parameter is set to `false`, or when an organization is enrolled
                in the zero data retention program).

          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          instructions: A system (or developer) message inserted into the model's context.

              When using along with `previous_response_id`, the instructions from a previous
              response will not be carried over to the next response. This makes it simple to
              swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          max_tool_calls: The maximum number of total calls to built-in tools that can be processed in a
              response. This maximum number applies across all built-in tool calls, not per
              individual tool. Any further attempts to call a tool by the model will be
              ignored.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          model: Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).
              Cannot be used in conjunction with `conversation`.

          prompt: Reference to a prompt template and its variables.
              [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).

          prompt_cache_key: Used by OpenAI to cache responses for similar requests to optimize your cache
              hit rates. Replaces the `user` field.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching).

          prompt_cache_retention: The retention policy for the prompt cache. Set to `24h` to enable extended
              prompt caching, which keeps cached prefixes active for longer, up to a maximum
              of 24 hours.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching#prompt-cache-retention).

          reasoning: **gpt-5 and o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          safety_identifier: A stable identifier used to help detect users of your application that may be
              violating OpenAI's usage policies. The IDs should be a string that uniquely
              identifies each user. We recommend hashing their username or email address, in
              order to avoid sending us any identifying information.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          service_tier: Specifies the processing type used for serving the request.

              - If set to 'auto', then the request will be processed with the service tier
                configured in the Project settings. Unless otherwise configured, the Project
                will use 'default'.
              - If set to 'default', then the request will be processed with the standard
                pricing and performance for the selected model.
              - If set to '[flex](https://platform.openai.com/docs/guides/flex-processing)' or
                '[priority](https://openai.com/api-priority-processing/)', then the request
                will be processed with the corresponding service tier.
              - When not set, the default behavior is 'auto'.

              When the `service_tier` parameter is set, the response body will include the
              `service_tier` value based on the processing mode actually used to serve the
              request. This response value may be different from the value set in the
              parameter.

          store: Whether to store the generated model response for later retrieval via API.

          stream_options: Options for streaming responses. Only set this when you set `stream: true`.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              The two categories of tools you can provide the model are:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code with strongly typed arguments and outputs.
                Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).
                You can also use custom tools to call your own code.

          top_logprobs: An integer between 0 and 20 specifying the number of most likely tokens to
              return at each token position, each with an associated log probability.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the context of this response and previous ones exceeds the model's
                context window size, the model will truncate the response to fit the context
                window by dropping input items in the middle of the conversation.
              - `disabled` (default): If a model response will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: This field is being replaced by `safety_identifier` and `prompt_cache_key`. Use
              `prompt_cache_key` instead to maintain caching optimizations. A stable
              identifier for your end-users. Used to boost cache hit rates by better bucketing
              similar requests and to help OpenAI detect and prevent abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        stream: bool,
        background: Optional[bool] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via
        # kwargs. The extra values given here take precedence over values defined on the client or passed to this
        # method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response | AsyncStream[ResponseStreamEvent]:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          background: Whether to run the model response in the background.
              [Learn more](https://platform.openai.com/docs/guides/background).

          conversation: The conversation that this response belongs to. Items from this conversation are
              prepended to `input_items` for this response request. Input items and output
              items from this response are automatically added to this conversation after this
              response completes.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `web_search_call.action.sources`: Include the sources of the web search tool
                call.
              - `code_interpreter_call.outputs`: Includes the outputs of python code execution
                in code interpreter tool call items.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.
              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `message.output_text.logprobs`: Include logprobs with assistant messages.
              - `reasoning.encrypted_content`: Includes an encrypted version of reasoning
                tokens in reasoning item outputs. This enables reasoning items to be used in
                multi-turn conversations when using the Responses API statelessly (like when
                the `store` parameter is set to `false`, or when an organization is enrolled
                in the zero data retention program).

          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          instructions: A system (or developer) message inserted into the model's context.

              When using along with `previous_response_id`, the instructions from a previous
              response will not be carried over to the next response. This makes it simple to
              swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          max_tool_calls: The maximum number of total calls to built-in tools that can be processed in a
              response. This maximum number applies across all built-in tool calls, not per
              individual tool. Any further attempts to call a tool by the model will be
              ignored.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          model: Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).
              Cannot be used in conjunction with `conversation`.

          prompt: Reference to a prompt template and its variables.
              [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).

          prompt_cache_key: Used by OpenAI to cache responses for similar requests to optimize your cache
              hit rates. Replaces the `user` field.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching).

          prompt_cache_retention: The retention policy for the prompt cache. Set to `24h` to enable extended
              prompt caching, which keeps cached prefixes active for longer, up to a maximum
              of 24 hours.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching#prompt-cache-retention).

          reasoning: **gpt-5 and o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          safety_identifier: A stable identifier used to help detect users of your application that may be
              violating OpenAI's usage policies. The IDs should be a string that uniquely
              identifies each user. We recommend hashing their username or email address, in
              order to avoid sending us any identifying information.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          service_tier: Specifies the processing type used for serving the request.

              - If set to 'auto', then the request will be processed with the service tier
                configured in the Project settings. Unless otherwise configured, the Project
                will use 'default'.
              - If set to 'default', then the request will be processed with the standard
                pricing and performance for the selected model.
              - If set to '[flex](https://platform.openai.com/docs/guides/flex-processing)' or
                '[priority](https://openai.com/api-priority-processing/)', then the request
                will be processed with the corresponding service tier.
              - When not set, the default behavior is 'auto'.

              When the `service_tier` parameter is set, the response body will include the
              `service_tier` value based on the processing mode actually used to serve the
              request. This response value may be different from the value set in the
              parameter.

          store: Whether to store the generated model response for later retrieval via API.

          stream_options: Options for streaming responses. Only set this when you set `stream: true`.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              The two categories of tools you can provide the model are:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code with strongly typed arguments and outputs.
                Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).
                You can also use custom tools to call your own code.

          top_logprobs: An integer between 0 and 20 specifying the number of most likely tokens to
              return at each token position, each with an associated log probability.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the context of this response and previous ones exceeds the model's
                context window size, the model will truncate the response to fit the context
                window by dropping input items in the middle of the conversation.
              - `disabled` (default): If a model response will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: This field is being replaced by `safety_identifier` and `prompt_cache_key`. Use
              `prompt_cache_key` instead to maintain caching optimizations. A stable
              identifier for your end-users. Used to boost cache hit rates by better bucketing
              similar requests and to help OpenAI detect and prevent abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @override
    async def create(
        self,
        *,
        background: Optional[bool] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Optional[Literal[False]] | Literal[True] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via
        # kwargs. The extra values given here take precedence over values defined on the client or passed to this
        # method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response | AsyncStream[ResponseStreamEvent]:
        messages: list[Message] = []

        if isinstance(instructions, str):
            messages.append(Message(role="system", content=instructions))

        if isinstance(input, str):
            messages.append(Message(role="user", content=input))
        elif input:
            messages.extend(chain.from_iterable(to_pangea_messages(item) for item in input))

        guard_input_response = self._client.ai_guard_client.guard_chat_completions(
            guard_input={"messages": messages}, event_type="input"
        )

        assert guard_input_response.result is not None

        if guard_input_response.result.blocked:
            raise CrowdStrikeAIDRBlockedError()

        if guard_input_response.result.transformed and guard_input_response.result.guard_output is not None:
            input = to_jsonable_python(guard_input_response.result.guard_output["messages"])

        openai_response = await super().create(  # type: ignore[misc]
            background=background,
            conversation=conversation,
            include=include,
            input=input,
            instructions=instructions,
            max_output_tokens=max_output_tokens,
            max_tool_calls=max_tool_calls,
            metadata=metadata,
            model=model,
            parallel_tool_calls=parallel_tool_calls,
            previous_response_id=previous_response_id,
            prompt=prompt,
            prompt_cache_key=prompt_cache_key,
            reasoning=reasoning,
            safety_identifier=safety_identifier,
            service_tier=service_tier,
            store=store,
            stream=stream,  # type: ignore[arg-type]
            stream_options=stream_options,
            temperature=temperature,
            text=text,
            tool_choice=tool_choice,
            tools=tools,
            top_logprobs=top_logprobs,
            top_p=top_p,
            truncation=truncation,
            user=user,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

        output_messages = [
            Message(role=o.role, content=c.text)
            for o in openai_response.output
            if o.type == "message"
            for c in o.content
            if c.type == "output_text"
        ]

        # TODO: reintroduce.
        # FPE unredact.
        # if guard_input_response.result.fpe_context is not None:
        #     redact_response = await self._client.redact_client.unredact(
        #         output_messages,
        #         fpe_context=guard_input_response.result.fpe_context,
        #     )
        #     assert redact_response.result is not None
        #     output_messages = list_message_adapter.validate_python(redact_response.result.data)

        guard_output_response = self._client.ai_guard_client.guard_chat_completions(
            guard_input={"messages": messages + output_messages}, event_type="output"
        )

        assert guard_output_response.result is not None

        if guard_output_response.result.blocked:
            raise CrowdStrikeAIDRBlockedError()

        if guard_output_response.result.transformed and guard_output_response.result.guard_output is not None:
            openai_response.output = [
                ResponseOutputMessage(
                    type="message",
                    role="assistant",
                    status="completed",
                    id="",
                    content=[ResponseOutputText(type="output_text", text=x.content, annotations=[])],
                )
                for x in guard_output_response.result.guard_output["messages"]
                if x.role == "assistant"
            ]
        elif guard_input_response.result.fpe_context is not None:
            openai_response.output = [
                ResponseOutputMessage(
                    type="message",
                    role="assistant",
                    status="completed",
                    id="",
                    content=[ResponseOutputText(type="output_text", text=x.content, annotations=[])],
                )
                for x in output_messages
                if x.role == "assistant"
            ]

        return openai_response
