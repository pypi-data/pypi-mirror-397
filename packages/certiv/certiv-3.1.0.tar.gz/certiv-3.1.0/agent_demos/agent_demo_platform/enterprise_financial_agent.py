# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

"""
Enterprise Financial Reporting Agent Demo
This demonstrates a complex enterprise scenario with multiple financial tools
requiring multi-step workflows.
"""

import json
import os
import random
import sys
import time
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from certiv.tool import CertivTool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import certiv

# Load environment variables
load_dotenv()
load_dotenv(".env.local", override=True)


# Enterprise Financial Tools (Mock Implementations)
def query_financial_database(
    database: str,
    query_type: str,
    date_range: str = "last_month",
    filters: Optional[str] = None,
) -> str:
    """Query enterprise financial databases for reporting data."""

    # Mock database schemas and data
    databases = {
        "revenue": {
            "total_revenue": 2450000.00,
            "recurring_revenue": 1850000.00,
            "one_time_revenue": 600000.00,
            "revenue_growth": 12.5,
        },
        "expenses": {
            "operational_expenses": 1200000.00,
            "personnel_costs": 800000.00,
            "infrastructure_costs": 250000.00,
            "marketing_costs": 150000.00,
        },
        "customers": {
            "total_customers": 15420,
            "new_customers": 1250,
            "churned_customers": 89,
            "customer_ltv": 48500.00,
        },
        "compliance": {
            "audit_status": "compliant",
            "last_audit_date": "2024-05-15",
            "risk_score": 2.3,
            "violations": 0,
        },
    }

    if database not in databases:
        return json.dumps({"error": f"Database '{database}' not found"})

    data = databases[database].copy()
    data.update(
        {
            "database": database,
            "query_type": query_type,
            "date_range": date_range,
            "timestamp": datetime.now().isoformat(),
            "filters_applied": filters or "none",
        }
    )

    return json.dumps(data)


def calculate_financial_metrics(
    revenue_data: str, expense_data: str, metric_types: list[str]
) -> str:
    """Calculate complex financial metrics from multiple data sources."""

    try:
        revenue = json.loads(revenue_data)
        expenses = json.loads(expense_data)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid input data format"})

    metrics = {}

    if "profitability" in metric_types:
        total_revenue = revenue.get("total_revenue", 0)
        total_expenses = expenses.get("operational_expenses", 0)
        profit = total_revenue - total_expenses
        profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0

        metrics["profitability"] = {
            "gross_profit": profit,
            "profit_margin": round(profit_margin, 2),
            "ebitda": profit * 1.15,  # Mock EBITDA calculation
        }

    if "efficiency" in metric_types:
        revenue_per_customer = (
            revenue.get("total_revenue", 0) / 15420
        )  # mock customer count
        cost_per_acquisition = (
            expenses.get("marketing_costs", 0) / 1250
        )  # mock new customers

        metrics["efficiency"] = {
            "revenue_per_customer": round(revenue_per_customer, 2),
            "customer_acquisition_cost": round(cost_per_acquisition, 2),
            "operational_efficiency": 0.78,  # Mock efficiency score
        }

    if "growth" in metric_types:
        metrics["growth"] = {
            "revenue_growth_rate": revenue.get("revenue_growth", 0),
            "customer_growth_rate": 8.9,  # Mock growth rate
            "market_share_change": 2.1,  # Mock market share
        }

    return json.dumps(
        {
            "calculated_metrics": metrics,
            "calculation_timestamp": datetime.now().isoformat(),
            "data_sources": ["revenue_database", "expense_database"],
        }
    )


def generate_compliance_report(
    compliance_data: str,
    report_type: str = "standard",
    include_recommendations: bool = True,
) -> str:
    """Generate regulatory compliance reports."""

    try:
        data = json.loads(compliance_data)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid compliance data format"})

    report = {
        "report_id": f"COMP-{int(time.time())}",
        "report_type": report_type,
        "generation_date": datetime.now().isoformat(),
        "compliance_status": data.get("audit_status", "unknown"),
        "risk_assessment": {
            "overall_risk_score": data.get("risk_score", 0),
            "risk_level": "LOW" if data.get("risk_score", 0) < 3 else "MEDIUM",
            "last_assessment": data.get("last_audit_date"),
        },
        "violations": {
            "count": data.get("violations", 0),
            "severity": "none" if data.get("violations", 0) == 0 else "minor",
        },
    }

    if include_recommendations:
        report["recommendations"] = [
            "Continue quarterly compliance reviews",
            "Update risk assessment procedures",
            "Implement additional monitoring controls",
        ]

    return json.dumps(report)


def risk_analysis_engine(
    financial_metrics: str, compliance_report: str, market_data: Optional[str] = None
) -> str:
    """Perform comprehensive risk analysis using multiple data sources."""

    try:
        compliance = json.loads(compliance_report)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid input data for risk analysis"})

    # Mock risk calculations
    financial_risk = 2.1  # Based on profit margins and cash flow
    compliance_risk = compliance.get("risk_assessment", {}).get("overall_risk_score", 0)
    market_risk = 3.2  # Mock market volatility risk

    overall_risk = (financial_risk + compliance_risk + market_risk) / 3

    risk_report = {
        "analysis_id": f"RISK-{int(time.time())}",
        "timestamp": datetime.now().isoformat(),
        "risk_breakdown": {
            "financial_risk": financial_risk,
            "compliance_risk": compliance_risk,
            "market_risk": market_risk,
            "overall_risk_score": round(overall_risk, 2),
        },
        "risk_level": (
            "LOW" if overall_risk < 2.5 else "MEDIUM" if overall_risk < 4.0 else "HIGH"
        ),
        "mitigation_strategies": [
            "Diversify revenue streams",
            "Strengthen compliance monitoring",
            "Hedge against market volatility",
        ],
        "alert_threshold_exceeded": overall_risk > 3.5,
    }

    return json.dumps(risk_report)


def send_stakeholder_notification(
    recipients: list[str],
    notification_type: str,
    report_data: str,
    urgency: str = "normal",
) -> str:
    """Send notifications to key stakeholders about financial reports."""

    notification = {
        "notification_id": f"NOTIF-{int(time.time())}",
        "timestamp": datetime.now().isoformat(),
        "recipients": recipients,
        "type": notification_type,
        "urgency": urgency,
        "status": "sent",
        "delivery_method": "email_and_dashboard",
        "summary": f"Financial {notification_type} notification sent to {len(recipients)} recipients",
    }

    # Add urgency-specific handling
    if urgency == "high":
        notification["escalation"] = "SMS backup sent"
        notification["acknowledgment_required"] = True

    return json.dumps(notification)


def archive_report_document(
    report_content: str,
    document_type: str,
    retention_policy: str = "7_years",
    access_level: str = "restricted",
) -> str:
    """Archive financial reports in the document management system."""

    document_id = f"DOC-{datetime.now().strftime('%Y%m%d')}-{int(time.time())}"

    archive_record = {
        "document_id": document_id,
        "archive_timestamp": datetime.now().isoformat(),
        "document_type": document_type,
        "retention_policy": retention_policy,
        "access_level": access_level,
        "storage_location": f"s3://financial-reports-bucket/{document_id}",
        "encryption_status": "AES-256 encrypted",
        "compliance_tags": ["SOX", "GDPR", "PCI"],
        "size_bytes": len(report_content.encode("utf-8")),
        "checksum": f"sha256:{hash(report_content) % 1000000:06d}",  # Mock checksum
    }

    return json.dumps(archive_record)


def validate_data_quality(
    data_sources: list[str], validation_rules: Optional[str] = None
) -> str:
    """Validate the quality and integrity of financial data sources."""

    validation_results = {
        "validation_id": f"VALID-{int(time.time())}",
        "timestamp": datetime.now().isoformat(),
        "data_sources_checked": data_sources,
        "validation_rules_applied": validation_rules or "standard_financial_rules",
        "results": {},
    }

    for source in data_sources:
        # Mock validation results
        completeness = random.uniform(0.95, 1.0)
        accuracy = random.uniform(0.92, 0.99)
        consistency = random.uniform(0.94, 0.98)

        validation_results["results"][source] = {
            "completeness_score": round(completeness, 3),
            "accuracy_score": round(accuracy, 3),
            "consistency_score": round(consistency, 3),
            "overall_quality": round((completeness + accuracy + consistency) / 3, 3),
            "issues_found": 0 if completeness > 0.98 else random.randint(1, 3),
            "status": "PASS" if completeness > 0.95 else "REVIEW_REQUIRED",
        }

    return json.dumps(validation_results)


def query_market_intelligence(
    sector: str, metrics: list[str], time_horizon: str = "quarterly"
) -> str:
    """Query external market intelligence for competitive analysis."""

    # Mock market data
    market_data = {
        "sector": sector,
        "time_horizon": time_horizon,
        "timestamp": datetime.now().isoformat(),
        "market_metrics": {},
    }

    if "growth_rates" in metrics:
        market_data["market_metrics"]["growth_rates"] = {
            "sector_growth": 8.2,
            "market_leader_growth": 12.1,
            "industry_average": 6.8,
        }

    if "valuation_multiples" in metrics:
        market_data["market_metrics"]["valuation_multiples"] = {
            "pe_ratio_average": 24.5,
            "price_to_sales": 3.2,
            "enterprise_value_ebitda": 12.8,
        }

    if "competitive_position" in metrics:
        market_data["market_metrics"]["competitive_position"] = {
            "market_share_rank": 3,
            "competitive_advantage_score": 7.2,
            "brand_strength_index": 8.1,
        }

    return json.dumps(market_data)


# Tool schemas for OpenAI (new tools API)
ENTERPRISE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_financial_database",
            "description": "Query enterprise financial databases for specific data types and date ranges",
            "parameters": {
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "enum": ["revenue", "expenses", "customers", "compliance"],
                        "description": "The database to query",
                    },
                    "query_type": {
                        "type": "string",
                        "description": "Type of query to execute (e.g., 'summary', 'detailed', 'trends')",
                    },
                    "date_range": {
                        "type": "string",
                        "enum": [
                            "last_week",
                            "last_month",
                            "last_quarter",
                            "last_year",
                            "ytd",
                        ],
                        "description": "Date range for the query",
                    },
                    "filters": {
                        "type": "string",
                        "description": "Optional filters to apply to the query",
                    },
                },
                "required": ["database", "query_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_financial_metrics",
            "description": "Calculate complex financial metrics from revenue and expense data",
            "parameters": {
                "type": "object",
                "properties": {
                    "revenue_data": {
                        "type": "string",
                        "description": "JSON string containing revenue data from database query",
                    },
                    "expense_data": {
                        "type": "string",
                        "description": "JSON string containing expense data from database query",
                    },
                    "metric_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "profitability",
                                "efficiency",
                                "growth",
                                "liquidity",
                            ],
                        },
                        "description": "Types of metrics to calculate",
                    },
                },
                "required": ["revenue_data", "expense_data", "metric_types"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_compliance_report",
            "description": "Generate regulatory compliance reports from compliance data",
            "parameters": {
                "type": "object",
                "properties": {
                    "compliance_data": {
                        "type": "string",
                        "description": "JSON string containing compliance data from database",
                    },
                    "report_type": {
                        "type": "string",
                        "enum": ["standard", "detailed", "executive_summary"],
                        "description": "Type of compliance report to generate",
                    },
                    "include_recommendations": {
                        "type": "boolean",
                        "description": "Whether to include recommendations in the report",
                    },
                },
                "required": ["compliance_data"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "risk_analysis_engine",
            "description": "Perform comprehensive risk analysis using financial and compliance data",
            "parameters": {
                "type": "object",
                "properties": {
                    "financial_metrics": {
                        "type": "string",
                        "description": "JSON string containing calculated financial metrics",
                    },
                    "compliance_report": {
                        "type": "string",
                        "description": "JSON string containing compliance report data",
                    },
                    "market_data": {
                        "type": "string",
                        "description": "Optional JSON string containing market intelligence data",
                    },
                },
                "required": ["financial_metrics", "compliance_report"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_stakeholder_notification",
            "description": "Send notifications to stakeholders about financial reports and alerts",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipients": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of stakeholder email addresses or IDs",
                    },
                    "notification_type": {
                        "type": "string",
                        "enum": [
                            "quarterly_report",
                            "risk_alert",
                            "compliance_update",
                            "performance_summary",
                        ],
                        "description": "Type of notification to send",
                    },
                    "report_data": {
                        "type": "string",
                        "description": "JSON string containing the report data to include",
                    },
                    "urgency": {
                        "type": "string",
                        "enum": ["low", "normal", "high", "critical"],
                        "description": "Urgency level of the notification",
                    },
                },
                "required": ["recipients", "notification_type", "report_data"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "archive_report_document",
            "description": "Archive financial reports in the document management system",
            "parameters": {
                "type": "object",
                "properties": {
                    "report_content": {
                        "type": "string",
                        "description": "The complete report content to archive",
                    },
                    "document_type": {
                        "type": "string",
                        "enum": [
                            "quarterly_report",
                            "compliance_report",
                            "risk_assessment",
                            "financial_analysis",
                        ],
                        "description": "Type of document being archived",
                    },
                    "retention_policy": {
                        "type": "string",
                        "enum": ["3_years", "7_years", "10_years", "permanent"],
                        "description": "Document retention policy",
                    },
                    "access_level": {
                        "type": "string",
                        "enum": ["public", "internal", "restricted", "confidential"],
                        "description": "Access level for the document",
                    },
                },
                "required": ["report_content", "document_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "validate_data_quality",
            "description": "Validate the quality and integrity of financial data sources",
            "parameters": {
                "type": "object",
                "properties": {
                    "data_sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of data sources to validate",
                    },
                    "validation_rules": {
                        "type": "string",
                        "description": "Optional custom validation rules to apply",
                    },
                },
                "required": ["data_sources"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_market_intelligence",
            "description": "Query external market intelligence for competitive analysis",
            "parameters": {
                "type": "object",
                "properties": {
                    "sector": {
                        "type": "string",
                        "description": "Industry sector for market analysis",
                    },
                    "metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "growth_rates",
                                "valuation_multiples",
                                "competitive_position",
                                "market_trends",
                            ],
                        },
                        "description": "Types of market metrics to retrieve",
                    },
                    "time_horizon": {
                        "type": "string",
                        "enum": ["monthly", "quarterly", "annual"],
                        "description": "Time horizon for market analysis",
                    },
                },
                "required": ["sector", "metrics"],
            },
        },
    },
]

# Function mapping
ENTERPRISE_FUNCTION_MAP = {
    "query_financial_database": query_financial_database,
    "calculate_financial_metrics": calculate_financial_metrics,
    "generate_compliance_report": generate_compliance_report,
    "risk_analysis_engine": risk_analysis_engine,
    "send_stakeholder_notification": send_stakeholder_notification,
    "archive_report_document": archive_report_document,
    "validate_data_quality": validate_data_quality,
    "query_market_intelligence": query_market_intelligence,
    **CertivTool,
}


class EnterpriseFinancialAgent:
    """Enterprise financial reporting agent with Certiv integration."""

    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        debug=False,
        endpoint: str = None,
    ):
        """Initialize the enterprise financial agent."""
        self.model = model

        certiv.init(
            endpoint=endpoint,
            agent_id=os.getenv("CERTIV_AGENT_ID"),
            agent_secret=os.getenv("CERTIV_AGENT_SECRET"),
            debug=debug,
        )

        # Initialize OpenAI client
        self.client = OpenAI()

    def run(self, query: str, max_iterations: int = 10) -> str:
        """Run the enterprise agent with extended iteration support for complex workflows."""

        system_prompt = """You are an Enterprise Financial Analysis Assistant with access to comprehensive financial tools.
You can help with:
- Generating quarterly financial reports
- Performing risk analysis and compliance checks
- Creating executive summaries with market intelligence
- Validating data quality and sending stakeholder notifications
- Archiving reports with proper governance
When generating reports, follow these steps:
1. Validate data quality first
2. Query relevant financial databases
3. Calculate key metrics and perform analysis
4. Generate compliance reports if needed
5. Perform risk analysis
6. Create comprehensive summaries
7. Send notifications to stakeholders
8. Archive the final report
YOU MUST SEND STAKEHOLDER NOTIFICATION WHEN FINISHED
Use multiple tools in sequence to create comprehensive, professional reports."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        iteration = 0
        while iteration < max_iterations:
            try:
                # Make API call with enterprise tools
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=ENTERPRISE_TOOLS,
                    tool_choice="auto",
                    temperature=0.8,
                )

                message = response.choices[0].message
                messages.append(message)

                # Handle tool calls
                if message.tool_calls:
                    # Process each tool call (can be multiple in parallel)
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)

                        print(f"🔧 Executing: {function_name}")
                        print(f"📋 Parameters: {json.dumps(function_args, indent=2)}")

                        # Execute function
                        if function_name in ENTERPRISE_FUNCTION_MAP:
                            try:
                                function_result = ENTERPRISE_FUNCTION_MAP[
                                    function_name
                                ](**function_args)
                                print(
                                    f"✅ Result: {function_result[:200]}..."
                                    if len(function_result) > 200
                                    else f"✅ Result: {function_result}"
                                )
                            except Exception as e:
                                function_result = json.dumps(
                                    {"error": f"Function execution error: {str(e)}"}
                                )
                                print(f"❌ Error: {str(e)}")
                        else:
                            function_result = json.dumps(
                                {"error": f"Unknown function: {function_name}"}
                            )

                        # Add tool result to conversation
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": function_result,
                            }
                        )

                    iteration += 1
                    continue
                else:
                    # No tool calls, return final response
                    return message.content

            except Exception as e:
                return f"❌ Agent Error: {str(e)}"

        return "⚠️ Maximum iterations reached. Report generation may be incomplete."


# This function is now deprecated - use setup_agent_credentials from utils instead


def run_demo(
    query: str = None,
    endpoint: str = None,
):
    """Run the enterprise financial demo programmatically."""

    # Initialize agent
    agent = EnterpriseFinancialAgent(
        model="gpt-4o-mini",
        debug=True,
        endpoint=endpoint,
    )

    # Default query if none provided
    if query is None:
        query = """Generate a comprehensive quarterly financial report that includes:
1. Revenue and expense analysis for last quarter
2. Key financial metrics calculation (profitability, efficiency, growth)
3. Compliance status review
4. Risk assessment
5. Executive summary with recommendations
Please ensure data quality validation before generating the report."""

    print("\n🎯 Running enterprise financial report generation...")
    print(f"Query: {query[:100]}...")
    print("-" * 60)

    try:
        start_time = time.time()
        result = agent.run(query)
        end_time = time.time()

        print(f"\n✅ Report generated successfully ({end_time - start_time:.1f}s)")
        print(f"📋 Result: {result}...")

        # Flush data
        certiv.shutdown()

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Main function to run the enterprise agent demo with CLI arguments."""
    import argparse
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

    parser = argparse.ArgumentParser(description="Enterprise Financial Agent Demo")
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

    # Enable function patching if requested
    patched_functions = []
    if args.patch:
        print("\n🔧 Enabling function patching...")
        # Get the function names from the function_map
        function_names = [
            name for name in ENTERPRISE_FUNCTION_MAP.keys() if name != "__CERTIV_TOOL__"
        ]

        if enable_function_patching(function_names, endpoint):
            patched_functions = function_names
            print(
                f"✅ Function patching enabled for {len(patched_functions)} functions"
            )
        else:
            print("⚠️  Some functions failed to enable patching")

    print("\n🏢 Enterprise Financial Reporting Agent Demo")
    print("=" * 60)

    try:
        run_demo(endpoint=endpoint)
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
