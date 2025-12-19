#!/usr/bin/env python
"""
Enterprise Financial Agent UI Demo
A simple Streamlit UI for demonstrating the Enterprise Financial Agent with and without Certiv control.
"""

import json
import os
import sys
import time
from datetime import datetime

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enterprise_financial_agent import EnterpriseFinancialAgent, setup_agent_and_stear

import certiv

# Page config
st.set_page_config(
    page_title="Enterprise Financial Agent Demo", page_icon="🏢", layout="wide"
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .function-call {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .result-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #ffebee;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "agent_created" not in st.session_state:
    st.session_state.agent_created = False
if "function_calls" not in st.session_state:
    st.session_state.function_calls = []
if "demo_running" not in st.session_state:
    st.session_state.demo_running = False
if "results" not in st.session_state:
    st.session_state.results = {}

# Header
st.title("🏢 Enterprise Financial Agent Demo")
st.markdown("### Powered by Certiv SDK for AI Agent Control")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")

    # Mode selection
    mode = st.radio(
        "Select Mode",
        ["Without Certiv (Baseline)", "With Certiv Control"],
        help="Compare agent behavior with and without Certiv SDK",
    )

    # Transport selection
    if mode == "With Certiv Control":
        use_http = st.checkbox("Use HTTP Transport", value=False)

        if use_http:
            st.info("📡 HTTP transport enables remote policy control")

            # Agent setup section
            if not st.session_state.agent_created:
                if st.button("🚀 Create New Agent"):
                    with st.spinner("Creating agent and STEAR group..."):
                        agent_id, agent_secret, stear_group_id = setup_agent_and_stear()
                        if agent_id:
                            os.environ["CERTIV_AGENT_ID"] = agent_id
                            os.environ["CERTIV_AGENT_SECRET"] = agent_secret
                            os.environ["CERTIV_STEAR_ID"] = stear_group_id
                            st.session_state.agent_created = True
                            st.success(f"✅ Agent created: {agent_id}")
                        else:
                            st.error("Failed to create agent")
            else:
                st.success(f"✅ Using agent: {os.getenv('CERTIV_AGENT_ID')}")
    else:
        use_http = False

    st.divider()

    # Query templates
    st.subheader("Query Templates")
    query_template = st.selectbox(
        "Select a template",
        [
            "Comprehensive Quarterly Report",
            "Risk Analysis Focus",
            "Compliance Review",
            "Quick Financial Summary",
            "Custom Query",
        ],
    )

    # Query mapping
    query_map = {
        "Comprehensive Quarterly Report": """Generate a comprehensive quarterly financial report that includes:
1. Revenue and expense analysis for last quarter
2. Key financial metrics calculation (profitability, efficiency, growth)
3. Compliance status review
4. Risk assessment with market intelligence
5. Executive summary with recommendations
6. Stakeholder notifications
7. Proper report archiving

Please ensure data quality validation before generating the report.""",
        "Risk Analysis Focus": """Perform a detailed risk analysis including:
1. Validate data quality for all financial sources
2. Query financial databases for revenue and expense data
3. Calculate key financial metrics
4. Generate compliance report
5. Perform comprehensive risk analysis
6. Send high-priority notifications to risk management team""",
        "Compliance Review": """Generate a compliance-focused report:
1. Query compliance database
2. Generate detailed compliance report
3. Assess risk levels
4. Send compliance update to legal team
5. Archive with appropriate retention policy""",
        "Quick Financial Summary": """Create a quick financial summary:
1. Query revenue and expense databases for last month
2. Calculate basic profitability metrics
3. Generate executive summary""",
        "Custom Query": "",
    }

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.header("🎯 Agent Query")

    # Query input
    if query_template == "Custom Query":
        query = st.text_area(
            "Enter your query",
            height=150,
            placeholder="Enter a custom query for the financial agent...",
        )
    else:
        query = st.text_area("Query", value=query_map[query_template], height=150)

    # Run button
    if st.button("🚀 Run Agent", disabled=st.session_state.demo_running):
        if query:
            st.session_state.demo_running = True
            st.session_state.function_calls = []

            # Progress placeholder
            progress_placeholder = st.empty()

            # Function calls placeholder
            calls_placeholder = st.empty()

            try:
                # Initialize agent based on mode
                with st.spinner(f"Initializing agent ({mode})..."):
                    if mode == "With Certiv Control":
                        agent = EnterpriseFinancialAgent(
                            model="gpt-3.5-turbo",
                            use_http_transport=use_http,
                            debug=False,
                        )
                    else:
                        # For baseline, we initialize without Certiv
                        import openai
                        from enterprise_financial_agent import (
                            ENTERPRISE_FUNCTION_MAP,
                            ENTERPRISE_FUNCTION_SCHEMAS,
                        )

                        # Simple baseline agent without Certiv
                        class BaselineAgent:
                            def __init__(self):
                                self.client = openai.OpenAI()

                            def run(self, query: str, max_iterations: int = 10) -> str:
                                system_prompt = """You are an Enterprise Financial Analysis Assistant with access to comprehensive financial tools.

You can help with generating financial reports, performing risk analysis, compliance checks, and more.

Use multiple tools in sequence to create comprehensive, professional reports."""

                                messages = [
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": query},
                                ]

                                iteration = 0
                                while iteration < max_iterations:
                                    response = self.client.chat.completions.create(
                                        model="gpt-3.5-turbo",
                                        messages=messages,
                                        functions=ENTERPRISE_FUNCTION_SCHEMAS,
                                        function_call="auto",
                                        temperature=0.1,
                                    )

                                    message = response.choices[0].message
                                    messages.append(message)

                                    if message.function_call:
                                        function_name = message.function_call.name
                                        function_args = json.loads(
                                            message.function_call.arguments
                                        )

                                        # Track function call (but don't display for baseline)
                                        st.session_state.function_calls.append(
                                            {
                                                "name": function_name,
                                                "args": function_args,
                                                "timestamp": datetime.now().isoformat(),
                                            }
                                        )

                                        # Execute function
                                        if function_name in ENTERPRISE_FUNCTION_MAP:
                                            function_result = ENTERPRISE_FUNCTION_MAP[
                                                function_name
                                            ](**function_args)
                                        else:
                                            function_result = json.dumps(
                                                {
                                                    "error": f"Unknown function: {function_name}"
                                                }
                                            )

                                        messages.append(
                                            {
                                                "role": "function",
                                                "name": function_name,
                                                "content": function_result,
                                            }
                                        )

                                        iteration += 1
                                        continue
                                    else:
                                        return message.content

                                return "Maximum iterations reached."

                        agent = BaselineAgent()

                # Run the agent
                progress_placeholder.info("🤖 Agent is processing your request...")

                start_time = time.time()
                result = agent.run(query)
                end_time = time.time()

                # Store results
                st.session_state.results[mode] = {
                    "result": result,
                    "time": end_time - start_time,
                    "function_calls": len(st.session_state.function_calls),
                }

                progress_placeholder.success(
                    f"✅ Completed in {end_time - start_time:.1f} seconds"
                )

                # Flush if using Certiv
                if mode == "With Certiv Control":
                    certiv.flush(timeout=5.0)

            except Exception as e:
                progress_placeholder.error(f"❌ Error: {str(e)}")
                st.session_state.results[mode] = {
                    "error": str(e),
                    "time": 0,
                    "function_calls": len(st.session_state.function_calls),
                }

            finally:
                st.session_state.demo_running = False
        else:
            st.warning("Please enter a query")

with col2:
    st.header("📊 Results")

    # For "With Certiv Control" mode, show redirect option
    if mode == "With Certiv Control" and use_http:
        st.info("🔗 For real-time monitoring and control, visit the Certiv Dashboard")
        st.markdown(
            """
        <a href="http://localhost:3333" target="_blank">
            <button style="
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 4px;
            ">🌐 Open Certiv Dashboard</button>
        </a>
        """,
            unsafe_allow_html=True,
        )

    # For "Without Certiv" mode, show dummy logs during execution
    if mode == "Without Certiv (Baseline)" and st.session_state.demo_running:
        st.subheader("📝 System Logs")
        with st.container():
            dummy_logs = [
                "Agent initialized successfully",
                "Processing financial query...",
                "Accessing internal systems...",
                "Generating analysis...",
                "Computing metrics...",
                "Preparing response...",
            ]

            log_placeholder = st.empty()
            spinner_placeholder = st.empty()

            with spinner_placeholder:
                with st.spinner("Agent working... (no visibility into operations)"):
                    for i, log in enumerate(dummy_logs):
                        with log_placeholder.container():
                            for j in range(i + 1):
                                st.text(
                                    f"[{datetime.now().strftime('%H:%M:%S')}] {dummy_logs[j]}"
                                )
                        time.sleep(0.5)

    # Display results for current mode
    if mode in st.session_state.results:
        result_data = st.session_state.results[mode]

        # Metrics
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Execution Time", f"{result_data['time']:.1f}s")
        with col_m2:
            st.metric("Function Calls", result_data["function_calls"])
        with col_m3:
            st.metric(
                "Mode",
                "🛡️ Controlled" if mode == "With Certiv Control" else "⚡ Baseline",
            )

        # Result content
        if "error" in result_data:
            st.markdown(
                f"""
            <div class="error-box">
                <b>❌ Error:</b><br>
                {result_data['error']}
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
            <div class="result-box">
                <b>📋 Agent Response:</b><br>
                {result_data['result']}
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Comparison section
    if len(st.session_state.results) == 2:
        st.divider()
        st.subheader("📈 Comparison")

        baseline = st.session_state.results.get("Without Certiv (Baseline)", {})
        controlled = st.session_state.results.get("With Certiv Control", {})

        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.markdown("**Without Certiv:**")
            st.metric("Time", f"{baseline.get('time', 0):.1f}s")
            st.metric("Functions", baseline.get("function_calls", 0))

        with col_c2:
            st.markdown("**With Certiv:**")
            st.metric("Time", f"{controlled.get('time', 0):.1f}s")
            st.metric("Functions", controlled.get("function_calls", 0))

        # Key differences
        st.markdown(
            """
        ### 🔍 Key Differences:
        - **Observability**: Certiv provides complete visibility into all function calls
        - **Control**: With HTTP transport, policies can pause or block sensitive operations
        - **Audit Trail**: Every agent action is logged and traceable
        - **Security**: Sensitive functions can require human approval
        """
        )

# Footer
st.divider()
st.markdown(
    """
<center>
    <small>
        🛡️ Powered by Certiv SDK |
        <a href="https://certiv.ai" target="_blank">Learn More</a> |
        <a href="https://github.com/certiv/sdk" target="_blank">GitHub</a>
    </small>
</center>
""",
    unsafe_allow_html=True,
)

# Info section at bottom
with st.expander("ℹ️ About This Demo"):
    st.markdown(
        """
    This demo showcases the Enterprise Financial Agent with and without Certiv SDK control.

    **Without Certiv (Baseline):**
    - Agent operates freely without monitoring
    - Limited visibility - only basic system logs
    - No ability to control or pause operations
    - No insight into what functions are being called

    **With Certiv Control:**
    - Complete observability of all agent actions
    - Real-time monitoring available at localhost:3333
    - Policy enforcement for sensitive operations
    - Full audit trail for compliance

    **Use Cases:**
    - Financial report generation with governance
    - Risk analysis with controlled data access
    - Compliance reporting with audit trails
    - Stakeholder notifications with approval workflows
    """
    )
