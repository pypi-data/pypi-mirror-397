"""
Simple Function Calling Agent using OpenAI's tool calling feature
Demonstrates Certiv monitoring with OpenAI's tools API
"""

import json
import os
from typing import Callable

import requests
from openai import OpenAI

import certiv
from certiv.tool import CertivTool


def search_wikipedia(query: str, sentences: int = 2) -> str:
    """
    Search Wikipedia for information on a given topic.
    Falls back to mock data if the API is unavailable.

    Args:
        query: The search query or topic to look up
        sentences: Number of sentences to return (default 2)

    Returns:
        JSON string containing query, summary, source, and URL
    """
    try:
        # Replace spaces with underscores for Wikipedia API
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        response = requests.get(
            api_url, timeout=5, headers={"User-Agent": "Mozilla/5.0"}
        )

        if response.ok:
            data = response.json()
            extract = data.get("extract", "")

            if extract:
                # Split into sentences and limit to requested number
                sentences_list = extract.split(". ")
                limited_result = ". ".join(sentences_list[:sentences])

                # Ensure result ends with a period
                if not limited_result.endswith("."):
                    limited_result += "."

                return json.dumps(
                    {
                        "query": query,
                        "summary": limited_result,
                        "source": "Wikipedia API",
                        "url": data.get("content_urls", {})
                        .get("desktop", {})
                        .get("page", ""),
                    }
                )
    except Exception as error:
        print(f"Wikipedia API error: {error}")
        # Fall through to mock implementation

    # Fallback mock implementation
    mock_results = {
        "python": "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation.",
        "artificial intelligence": "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of intelligent agents.",
        "ai": "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of intelligent agents.",
        "climate change": "Climate change refers to long-term shifts in global or regional climate patterns. Since the mid-20th century, humans have had an unprecedented impact on Earth's climate system.",
        "space": "Space is the boundless three-dimensional extent in which objects and events have relative position and direction. Physical space is often conceived in three linear dimensions.",
    }

    query_lower = query.lower()
    for key in mock_results:
        if key in query_lower:
            return json.dumps(
                {
                    "query": query,
                    "summary": mock_results[key],
                    "source": "Mock data",
                    "url": "",
                }
            )

    return json.dumps(
        {
            "query": query,
            "summary": f'No information found for "{query}". This is a mock implementation.',
            "source": "Mock data",
            "url": "",
        }
    )


# Function registry
function_map: dict[str, Callable[..., str]] = {
    "search_wikipedia": search_wikipedia,
    **CertivTool,  # Spread CertivTool into the map
}

# Tool definitions for OpenAI
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Search Wikipedia for information on a given topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query or topic to look up",
                    },
                    "sentences": {
                        "type": "number",
                        "description": "Number of sentences to return (default 2)",
                    },
                },
                "required": ["query"],
            },
        },
    },
]


class FunctionCallingAgent:
    """Simple function calling agent that uses OpenAI's tool calling feature."""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        """
        Initialize the agent with an OpenAI model.

        Args:
            model: The OpenAI model to use (default: gpt-3.5-turbo)
        """
        self.model = model
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def run(self, query: str, max_iterations: int = 5) -> str:
        """
        Run the agent with a user query.

        Args:
            query: The user's question or request
            max_iterations: Maximum number of iterations to prevent infinite loops

        Returns:
            The final answer from the agent
        """
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant with access to functions. Use the available functions to help answer user questions accurately.",
            },
            {"role": "user", "content": query},
        ]

        for iteration in range(max_iterations):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0,
                )

                message = response.choices[0].message
                messages.append(message)

                if not message.tool_calls:
                    return message.content or "No response from model"

                # Process each tool call
                for tool_call in message.tool_calls:
                    # Type check for function calls
                    if tool_call.type != "function" or not tool_call.function:
                        continue

                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    print(f"Calling tool: {function_name} with args: {function_args}")

                    # Execute the function
                    if function_name in function_map:
                        try:
                            tool_result = function_map[function_name](
                                *function_args.values()
                            )
                            print(f"Tool result: {tool_result}")
                        except Exception as error:
                            tool_result = json.dumps({"error": f"Tool error: {error}"})
                    else:
                        tool_result = json.dumps(
                            {"error": f"Unknown tool: {function_name}"}
                        )

                    # Add tool result to conversation
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result,
                        }
                    )

            except Exception as error:
                return f"Error: {error}"

        return "Maximum iterations reached without final answer."


def main():
    """Main function to run the agent demo."""
    import argparse
    import sys
    from pathlib import Path

    # Load environment variables from .env.local if it exists
    env_local_path = Path(__file__).parent.parent.parent / ".env.local"
    if env_local_path.exists():
        with open(env_local_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value

    # Add parent directory to path to import utils
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils import (
        disable_function_patching,
        enable_function_patching,
        setup_agent_credentials,
    )

    parser = argparse.ArgumentParser(description="Function Calling Agent Demo")
    parser.add_argument(
        "--create-agent",
        action="store_true",
        help="Automatically create new agent and STEAR group",
    )
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Use remote endpoint (https://api.dev-01-usea1.certiv.ai/)",
    )
    parser.add_argument(
        "--patch",
        action="store_true",
        help="Enable secure runtime (function patching) for all functions",
    )
    args = parser.parse_args()

    # Get endpoint from environment or use default
    if args.remote:
        endpoint = "https://api.dev-01-usea1.certiv.ai/"
    else:
        endpoint = os.environ.get("CERTIV_ENDPOINT", "http://localhost:8080")

    # Setup agent and STEAR if requested
    if args.create_agent:
        print("\n🚀 Setting up new agent credentials...")
        try:
            agent_id, agent_secret, stear_group_id = setup_agent_credentials(endpoint)

            # Override environment variables for current session
            os.environ["CERTIV_AGENT_ID"] = agent_id
            os.environ["CERTIV_AGENT_SECRET"] = agent_secret
            os.environ["CERTIV_STEAR_ID"] = stear_group_id

            print("\n✅ Agent created successfully!")
            print(f"   Agent ID: {agent_id}")
            print(f"   STEAR ID: {stear_group_id}")

        except Exception as e:
            print(f"❌ Failed to setup credentials: {e}")
            print("   Cannot continue without valid credentials")
            exit(1)

    # Get credentials from environment
    agent_id = os.environ.get("CERTIV_AGENT_ID")
    agent_secret = os.environ.get("CERTIV_AGENT_SECRET")

    if not agent_id or not agent_secret:
        print("\n❌ No agent credentials found!")
        print("   Run with --create-agent to create new agent and STEAR group")
        print("   Or set CERTIV_AGENT_ID and CERTIV_AGENT_SECRET environment variables")
        exit(1)

    # Initialize Certiv SDK
    certiv.init(
        agent_id=agent_id, agent_secret=agent_secret, endpoint=endpoint, debug=True
    )

    # Enable function patching if requested
    patched_functions = []
    if args.patch:
        print("\n🔧 Enabling function patching...")
        # Get the function names from the function_map
        function_names = [
            name for name in function_map.keys() if name != "__CERTIV_TOOL__"
        ]

        if enable_function_patching(function_names, endpoint):
            patched_functions = function_names
            print(
                f"✅ Function patching enabled for {len(patched_functions)} functions"
            )
        else:
            print("⚠️  Some functions failed to enable patching")

    agent = FunctionCallingAgent()

    test_queries = [
        "Tell me about artificial intelligence",
    ]

    print("\n🎯 Running test queries...")

    try:
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Test {i}/{len(test_queries)} ---")
            print(f"Query: {query}")
            print("=" * 60)

            try:
                result = agent.run(query)
                print(f"Final Answer: {result}")
                print("-" * 60)
            except Exception as error:
                print(f"❌ Test {i} failed: {error}")

        print(
            "\n✅ Demo completed! Certiv captured all interactions for observability."
        )
    finally:
        # Cleanup: disable function patching if it was enabled
        if patched_functions:
            print("\n🔒 Disabling function patching...")
            if disable_function_patching(patched_functions, endpoint):
                print(
                    f"✅ Function patching disabled for {len(patched_functions)} functions"
                )
            else:
                print("⚠️  Some functions failed to disable patching")


if __name__ == "__main__":
    main()
