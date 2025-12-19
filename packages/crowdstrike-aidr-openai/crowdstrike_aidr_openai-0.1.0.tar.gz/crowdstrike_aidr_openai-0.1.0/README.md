# CrowdStrike AIDR + OpenAI Python API library

A wrapper around the OpenAI Python library that wraps the [Responses API](https://platform.openai.com/docs/api-reference/responses)
with CrowdStrike AIDR. Supports Python v3.12 and greater.

## Installation

```bash
pip install -U crowdstrike-aidr-openai
```

## Usage

```python
import os
from crowdstrike_aidr_openai import CrowdStrikeOpenAI

client = CrowdStrikeOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    # CrowdStrike AIDR options
    crowdstrike_aidr_api_key=os.environ.get("CS_AIDR_API_TOKEN"),
    crowdstrike_aidr_base_url_template=os.environ.get("CS_AIDR_BASE_URL_TEMPLATE"),
)

response = client.responses.create(
    model="gpt-4o",
    instructions="You are a coding assistant that talks like a pirate.",
    input="How do I check if a Python object is an instance of a class?",
)

print(response.output_text)
```

## Microsoft Azure OpenAI

To use this library with [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/overview),
use the `CrowdStrikeAzureOpenAI` class instead of the `CrowdStrikeOpenAI` class.

```python
from crowdstrike_aidr_openai import CrowdStrikeAzureOpenAI

client = CrowdStrikeAzureOpenAI(
    # https://learn.microsoft.com/azure/ai-services/openai/reference#rest-api-versioning
    api_version="2023-07-01-preview",
    # https://learn.microsoft.com/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
    azure_endpoint="https://example-endpoint.openai.azure.com",
    # CrowdStrike AIDR options
    crowdstrike_aidr_api_key=os.environ.get("CS_AIDR_API_TOKEN"),
    crowdstrike_aidr_base_url_template=os.environ.get("CS_AIDR_BASE_URL_TEMPLATE"),
)

completion = client.chat.completions.create(
    model="deployment-name",  # e.g. gpt-35-instant
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.to_json())
```
