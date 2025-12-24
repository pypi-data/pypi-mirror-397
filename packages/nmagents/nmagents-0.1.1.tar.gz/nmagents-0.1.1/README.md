# No More Agents - nmagents

## Agentic AI without any Agent Frameworks

There is a deluge of Agentic Frameworks. Actually nothing is needed but just a few python wrappers, and thats what this is. Not another framework

Something you can pip install or copy paste and use! And it has elementary token cost and budgetting which none of the Frameworks have !!

## What is Agentic AI ?

In the simplest sense, it means using AI in your code. For example I give a file and I use an LLM Model to do a Code Review. Instead of me doing this manually in ChatGPT, if I write a program for this then that is Agentic AI.

Here Agent is a automated program that uses AI for a task.

## Why is Model Context Protocol (MCP) needed for Agentic AI ?


MCP is a JSON-RPC based wrapper for API calls. Why ?

Because Generative AI/LLM models can generate the API calls in JSON with parameters,which an Agentic AI program can parse and invoke the actual API.

Example:

Say that I write a program to automate flight ticket booking - an Agentic AI application

User input will be - "Here is a picture of my passport (and credit card). Book me a ticket, economy class to Santiago"

My program will need to translate the above command to an API call with the ticket booking system with the help of LLM. 

I need to tell the LLM to formulate the API call as per how the API expects the parameter. The Ticket Booking System MCP server( assume it exists) will give the methods 

and JSON structure for booking.

I give this format to the LLM and ask it to parse the Passport and user command and create a JSON request for ticket booking

The LLM/AI will repsont with something similar to below and my program will POST this to the Ticket Booking System MCP server for intiating Ticket booking

```
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "book_flight_ticket",
    "arguments": {
      "destination": "Santiago (SCL)",
      "travel_class": "economy",
      "passenger_details": {
        "full_name": "John Doe", 
        "passport_number": "A12345678",
        "nationality": "USA",
        "expiry_date": "2030-05-12"
      },
      "travel_date": "2023-11-27" 
    }
  },
  "id": "call_890s7d6f"
}
```

You will understand while coding MCP the actual deatails


## Which Framework to use for Agentic AI ?

You really do not need a framework like LangChain, LangGraph,CrewAI or AutoGen/Microsoft Agent Framework or all the other hunderds of frameworks for using AI logic in your programming.

Calling LLMs via an API is already exposed by OpenAI APIs. This abstraction is more than enough. All that is needed is just some Software Construction Patterns  like Command Pattern and Chain of Responsibility

This is a simple Command class wrapper for performing LLM-based automation without using Any  frameworks - complex or simple

Just plain MCP and API calls combined with good old-fashioned programming is enough for the most complicated tasks


# How to Use

```
pip install nmagents
from nmagents.command import CallLLM, ToolCall, 
```

## Intailize OpenAI based LLMs (Inlcuding vLLM and ollama models)

```

from openai import OpenAI

# Initialize OpenAI client with OpenAI's official base URL
MODEL_NAME = "gpt-4.1-nano"
#MODEL_NAME = "gpt-5-nano"
openai_client = OpenAI(
    api_key=api_key,
    base_url="https://api.openai.com/v1"
)

# ollama client
# MODEL_NAME= "phi3.5" 
# openai_client = OpenAI(
#     api_key="sk-local",
#     base_url="http://localhost:11434/v1"
#  )

# vllm client
# MODEL_NAME= "gemma"
# openai_client = OpenAI(
#     api_key="sk-local",
#     base_url="http://localhost:8080/v1"
# )
```

## Call the LLM with the Prompt


```
call_llm_command = CallLLM(openai_client, "Call the LLM with the given context",
                               MODEL_NAME, COST_PER_TOKEN_INPUT, COST_PER_TOKEN_OUTPUT, 0.5)

context = main_context + f" Here is the file diff for {file_path}:\n{diff} for review\n" + \
        f"You have access to the following MCP tools to help you with your code review: {tool_schemas_content}"
response = call_llm_command.execute(context)
```


## Call the LLM for invoking an MCP Tool

```
   
async with Client(SOME_MCP_SERVER_URL) as ast_tool_client:

tool_command = ToolCall(
        ast_tool_client, "Call the tool with the given method and params")
 tool_result, succeeded = await tool_command.execute(payload_json)

 ```

 PyPy Repo link

 https://pypi.org/project/nmagents/0.1.0/