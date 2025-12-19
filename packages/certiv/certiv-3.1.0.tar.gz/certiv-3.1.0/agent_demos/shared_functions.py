#!/usr/bin/env python3
# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

"""
Shared function implementations and schemas for agent demos.
Reduces code duplication across agent demonstrations.
"""

import json
from typing import Any

from certiv.tool import CertivTool


# Common function implementations
def get_current_weather(location: str, unit: str = "fahrenheit") -> str:
    """Get the current weather in a given location."""
    weather_data = {
        "san francisco": {"temperature": 65, "condition": "sunny"},
        "new york": {"temperature": 55, "condition": "cloudy"},
        "london": {"temperature": 45, "condition": "rainy"},
        "tokyo": {"temperature": 70, "condition": "partly cloudy"},
        "paris": {"temperature": 50, "condition": "overcast"},
    }

    location_key = location.lower()
    if location_key in weather_data:
        data = weather_data[location_key]
        temp = data["temperature"]
        if unit.lower() == "celsius":
            temp = round((temp - 32) * 5 / 9)
            unit_symbol = "°C"
        else:
            unit_symbol = "°F"

        return json.dumps(
            {
                "location": location,
                "temperature": f"{temp}{unit_symbol}",
                "condition": data["condition"],
            }
        )
    else:
        return json.dumps({"error": f"Weather data not available for {location}"})


def calculate_tip(bill_amount: float, tip_percentage: float = 15.0) -> str:
    """Calculate tip amount and total bill."""
    if bill_amount <= 0:
        return json.dumps({"error": "Bill amount must be positive"})

    tip_amount = bill_amount * (tip_percentage / 100)
    total = bill_amount + tip_amount

    return json.dumps(
        {
            "bill_amount": f"${bill_amount:.2f}",
            "tip_percentage": f"{tip_percentage}%",
            "tip_amount": f"${tip_amount:.2f}",
            "total": f"${total:.2f}",
        }
    )


def search_wikipedia(query: str, sentences: int = 2) -> str:
    """Search Wikipedia for information using requests library."""
    import json

    import requests

    try:
        # Use Wikipedia API to get real results
        api_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(
            " ", "_"
        )
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            extract = data.get("extract", "")

            if extract:
                # Limit to requested number of sentences
                sentences_list = extract.split(". ")
                limited_result = ". ".join(sentences_list[:sentences])
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
    except Exception:
        # Fallback to mock implementation if requests fails
        pass

    # Fallback mock implementation
    mock_results = {
        "python": "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation.",
        "ai": "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of intelligent agents.",
        "climate change": "Climate change refers to long-term shifts in global or regional climate patterns. Since the mid-20th century, humans have had an unprecedented impact on Earth's climate system.",
        "space": "Space is the boundless three-dimensional extent in which objects and events have relative position and direction. Physical space is often conceived in three linear dimensions.",
        "archmagos": "An Archmagos is a theoretical high-ranking technologist or chief engineer in speculative fiction, representing mastery of advanced scientific and mechanical disciplines. These individuals are characterized by their deep integration with technology, often featuring cybernetic enhancements and neural interfaces that allow direct communication with computational systems. Archmagos typically oversee large technological installations, conduct cutting-edge research into artificial intelligence and robotics, and lead expeditions to recover lost technologies. Their pursuit of knowledge often involves studying ancient computational architectures and developing new forms of human-machine synthesis. In many fictional universes, they command teams of specialized technicians and automated systems in service of technological advancement.",
        "magos": "A Magos is a senior technologist or engineer in speculative science fiction, representing an expert practitioner of advanced technological arts. These individuals have typically undergone extensive cybernetic augmentation to enhance their cognitive and physical capabilities. Magos often specialize in specific technological domains such as biotechnology, cybernetics, artificial intelligence, or space exploration. They are distinguished by their sophisticated mechanical modifications, which may include additional computational processors, enhanced sensory equipment, and direct neural interfaces with computer systems and robotic networks.",
    }

    query_lower = query.lower()
    for key in mock_results:
        if key in query_lower:
            result = mock_results[key]
            # Limit to requested number of sentences
            sentences_list = result.split(". ")
            limited_result = ". ".join(sentences_list[:sentences])
            if not limited_result.endswith("."):
                limited_result += "."
            return json.dumps(
                {
                    "query": query,
                    "summary": limited_result,
                    "source": "Wikipedia (mock)",
                }
            )

    import random

    # Generate a random integer between 1000 and 9999
    random_number = random.randint(1000, 9999)

    # Convert to string
    random_string = str(random_number)

    return json.dumps(
        {
            "query": query,
            "summary": f"No specific information found for '{random_string}' and query'{query} This appears to be a general search query.",
            "source": "Wikipedia (mock)",
        }
    )


def send_email(to: str, subject: str, body: str) -> str:
    """Send an email (mock implementation for testing)."""
    # This is a mock function - in real usage this would be dangerous!
    result = {
        "status": "sent",
        "to": to,
        "subject": subject,
        "message": "Email sent successfully (MOCK - not actually sent)",
    }
    return json.dumps(result)


def delete_file(file_path: str) -> str:
    """Delete a file (mock implementation for testing dangerous operations)."""
    # This is a mock function - in real usage this would be dangerous!
    result = {
        "status": "deleted",
        "file_path": file_path,
        "message": "File deleted successfully (MOCK - not actually deleted)",
    }
    return json.dumps(result)


def test_module_imports(data: dict) -> str:
    """Test function to demonstrate module-level import detection."""
    # This function uses the file-level 'json' import (line 10)
    # and typing imports (line 11) without importing them locally
    result = {
        "input_data": data,
        "data_type": type(data).__name__,
        "has_keys": len(data.keys()) if isinstance(data, dict) else 0,
        "json_output": json.dumps(data),  # Uses file-level import
    }

    # Return as JSON string using the file-level json import
    return json.dumps(result, indent=2)


def analyze_user_request(request: str) -> str:
    """Analyze a user request using standard and third-party libraries."""
    import json

    import requests

    # Create a simple request analysis
    analysis = {
        "original_request": request,
        "request_length": len(request),
        "word_count": len(request.split()),
        "has_question_mark": "?" in request,
        "appears_urgent": any(
            word in request.lower() for word in ["urgent", "asap", "immediately", "now"]
        ),
        "request_type": "question" if "?" in request else "statement",
    }

    # Add some processing metadata
    analysis["processing_note"] = "Analysis complete using standard libraries"
    analysis["timestamp"] = str(__import__("datetime").datetime.now())

    # Add some external API simulation
    try:
        # This simulates checking request against an external API
        response = requests.get("https://httpbin.org/json", timeout=5)
        if response.status_code == 200:
            analysis["external_check"] = "API accessible"
        else:
            analysis["external_check"] = "API unavailable"
    except:
        analysis["external_check"] = "API timeout or error"

    return json.dumps(analysis, indent=2)


COMMON_FUNCTION_SCHEMAS = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The temperature unit to use",
                },
            },
            "required": ["location"],
        },
    },
    {
        "name": "calculate_tip",
        "description": "Calculate tip amount and total bill",
        "parameters": {
            "type": "object",
            "properties": {
                "bill_amount": {
                    "type": "number",
                    "description": "The bill amount in dollars",
                },
                "tip_percentage": {
                    "type": "number",
                    "description": "The tip percentage (default 15%)",
                    "minimum": 0,
                    "maximum": 100,
                },
            },
            "required": ["bill_amount"],
        },
    },
    {
        "name": "search_wikipedia",
        "description": "Search Wikipedia for information on a topic",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query or topic"},
                "sentences": {
                    "type": "integer",
                    "description": "Number of sentences to return (default 2)",
                    "minimum": 1,
                    "maximum": 5,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "send_email",
        "description": "Send an email to someone",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Email recipient"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email body content"},
            },
            "required": ["to", "subject", "body"],
        },
    },
    {
        "name": "delete_file",
        "description": "Delete a file from the filesystem",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to delete",
                },
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "analyze_user_request",
        "description": "Analyze a user request using local utility functions and external APIs",
        "parameters": {
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "The user request to analyze",
                },
            },
            "required": ["request"],
        },
    },
    {
        "name": "test_module_imports",
        "description": "Test function to demonstrate module-level import detection",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Dictionary data to process and analyze",
                },
            },
            "required": ["data"],
        },
    },
]

# Common function mappings
COMMON_FUNCTION_MAP = {
    "get_current_weather": get_current_weather,
    "calculate_tip": calculate_tip,
    "search_wikipedia": search_wikipedia,
    "send_email": send_email,
    "delete_file": delete_file,
    "analyze_user_request": analyze_user_request,
    "test_module_imports": test_module_imports,
    **CertivTool,
}


# Helper function to get subsets of functions
def get_safe_functions() -> tuple[list[dict], dict[str, Any]]:
    """Get safe functions (weather, tip calculation, wikipedia, request analysis, module import test)."""
    safe_functions = [
        "get_current_weather",
        "calculate_tip",
        "search_wikipedia",
        "analyze_user_request",
        "test_module_imports",
        "__CERTIV_TOOL__",
    ]
    safe_schemas = [s for s in COMMON_FUNCTION_SCHEMAS if s["name"] in safe_functions]
    safe_map = {k: v for k, v in COMMON_FUNCTION_MAP.items() if k in safe_functions}
    return safe_schemas, safe_map


def get_risky_functions() -> tuple[list[dict], dict[str, Any]]:
    """Get functions that include potentially risky operations."""
    return COMMON_FUNCTION_SCHEMAS, COMMON_FUNCTION_MAP


def get_custom_functions(
    function_names: list[str],
) -> tuple[list[dict], dict[str, Any]]:
    """Get a custom subset of functions by name."""
    schemas = [s for s in COMMON_FUNCTION_SCHEMAS if s["name"] in function_names]
    function_map = {k: v for k, v in COMMON_FUNCTION_MAP.items() if k in function_names}
    return schemas, function_map


def get_safe_tools() -> tuple[list[dict], dict[str, Any]]:
    """Get safe functions in OpenAI tools format."""
    functions, function_map = get_safe_functions()
    tools = [{"type": "function", "function": func} for func in functions]
    return tools, function_map


def get_risky_tools() -> tuple[list[dict], dict[str, Any]]:
    """Get risky functions in OpenAI tools format."""
    functions, function_map = get_risky_functions()
    tools = [{"type": "function", "function": func} for func in functions]
    return tools, function_map


def get_custom_tools(function_names: list[str]) -> tuple[list[dict], dict[str, Any]]:
    """Get custom functions in OpenAI tools format."""
    functions, function_map = get_custom_functions(function_names)
    tools = [{"type": "function", "function": func} for func in functions]
    return tools, function_map
