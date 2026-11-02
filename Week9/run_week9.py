"""
run_week9.py
Executes the Week 9 Model Context Protocol (MCP) Demonstration:
1. Initializes HRIS MCP Server and connects MCP Client.
2. Agent dynamically discovers tools without hard-coding.
3. Demonstrates agent answering HRIS leave balance inquiry.
4. BOLT-ON EXPERIMENT: Attaches second MCP server (Policy & Rules Server)
   WITHOUT modifying a single line of the agent code.
5. Verifies dynamic discovery of new tools and resolves cross-server queries.
6. Simulates an external team's agent calling the HRIS MCP server.
"""

import sys
import json
from pathlib import Path

# Ensure root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from Week9.hris_mcp_server import HRISMCPServer
from Week9.policy_mcp_server import PolicyMCPServer
from Week9.mcp_client import MCPClient
from Week9.mcp_agent import MCPAgent

def run_week9_demo():
    print("=" * 80)
    print("WEEK 9: MODEL CONTEXT PROTOCOL (MCP) INTEROPERABILITY & DISCOVERY")
    print("=" * 80)

    # Step 1: Start MCP Client and Connect ONLY the HRIS Server
    print("\n[Phase 1] Initializing Host Agent with HRIS MCP Server...")
    mcp_client = MCPClient()
    hris_server = HRISMCPServer()
    mcp_client.connect_server("hris_server", server_instance=hris_server)

    agent = MCPAgent(mcp_client=mcp_client)
    print(f"-> Discovered Tools in Host Agent: {agent.sync_tools()}")

    # Step 2: Run Inquiry using HRIS Server Tools
    q1 = "What is the remaining leave balance for Alice Chen (EMP-1001)?"
    print(f"\nQuery 1: '{q1}'")
    res1 = agent.run(q1)
    print(f"Status: {res1['status']}")
    print(f"Tools Used: {[c['tool'] for c in res1['tool_calls_executed']]}")
    print(f"Agent Output: {res1['answer']}")

    # Step 3: BOLT-ON SECOND MCP SERVER WITHOUT CHANGING AGENT CODE
    print("\n" + "=" * 80)
    print("[Phase 2] BOLTING ON SECOND MCP SERVER (Policy & Rules Server)")
    print("CRITICAL CHECK: ZERO lines of agent code will be changed!")
    print("=" * 80)

    policy_server = PolicyMCPServer()
    mcp_client.connect_server("policy_server", server_instance=policy_server)
    
    # Host agent re-syncs tool registry over standard MCP protocol
    newly_discovered = agent.sync_tools()
    print(f"-> Updated Discovered Tools in Host Agent: {newly_discovered}")
    assert "get_jurisdiction_rules" in newly_discovered, "Failed to discover new tool over MCP!"
    print("-> Verification SUCCESS: Second server bolted on seamlessly without touching agent code!")

    # Step 4: Run Cross-Server Entitlement Inquiries
    queries = [
        "What is the annual leave carry-over cap for Alice Chen (EMP-1001) in APAC?",
        "Can Clara Dupont (EMP-1003) in EMEA roll over unused leave during probation?",
        "How many weeks of primary caregiver leave does David Miller (EMP-1004) receive in North America?",
        "What medical certification is required for Frank Wright (EMP-1006) in the UK for sick leave exceeding 8 days?"
    ]

    print("\n[Phase 3] Executing Cross-Server Entitlement Inquiries:")
    for idx, q in enumerate(queries, start=2):
        print(f"\n--- Query {idx}: '{q}' ---")
        res = agent.run(q)
        print(f"Status: {res['status']}")
        print(f"Tools Executed: {[c['tool'] for c in res['tool_calls_executed']]}")
        print(f"Agent Output: {res['answer']}")

    # Step 5: External Client Interoperability Test
    print("\n" + "=" * 80)
    print("[Phase 4] PROVING ANOTHER PERSON'S AGENT CAN CALL OUR MCP SERVER")
    print("=" * 80)
    external_client = MCPClient()
    external_client.connect_server("partner_hris", server_instance=hris_server)
    ext_tools = [t["name"] for t in external_client.discover_tools()]
    print(f"External Agent Discovered Tools: {ext_tools}")
    
    # External agent calls our tool via pure MCP JSON-RPC
    ext_result = external_client.call_tool("get_employee_record", {"employee_id": "EMP-1005"})
    print(f"External Agent Tool Call Response: {json.dumps(ext_result, indent=2)}")
    assert ext_result.get("name") == "Elena Gomez", "External tool call failed!"
    print("\nAll Week 9 MCP criteria successfully validated!")

if __name__ == "__main__":
    run_week9_demo()

