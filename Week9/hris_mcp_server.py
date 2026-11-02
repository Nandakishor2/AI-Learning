"""
hris_mcp_server.py
Model Context Protocol (MCP) Server for HRIS (Human Resource Information System)
Standard JSON-RPC 2.0 compliant over stdio and direct programmatic transport.
Exposes employee records and leave balances without embedding any AI or LLM logic.
"""

import sys
import json
from typing import Dict, Any, List, Optional

# Employee Records Database (Track C - HR Policy)
EMPLOYEE_DATABASE = {
    "EMP-1001": {
        "id": "EMP-1001",
        "name": "Alice Chen",
        "jurisdiction": "APAC",
        "tier": "Tier 1 Staff",
        "tenure_months": 4,
        "is_probationary": True,
        "annual_leave_accrued_days": 7.0,
        "annual_leave_taken_days": 2.0,
        "sick_leave_taken_days": 1.0
    },
    "EMP-1002": {
        "id": "EMP-1002",
        "name": "Bob Smith",
        "jurisdiction": "APAC",
        "tier": "Tier 2 Leads",
        "tenure_months": 5,
        "is_probationary": True,
        "annual_leave_accrued_days": 8.75,
        "annual_leave_taken_days": 4.0,
        "sick_leave_taken_days": 0.0
    },
    "EMP-1003": {
        "id": "EMP-1003",
        "name": "Clara Dupont",
        "jurisdiction": "EMEA",
        "tier": "All Tiers",
        "tenure_months": 3,
        "is_probationary": True,
        "annual_leave_accrued_days": 6.25,
        "annual_leave_taken_days": 1.0,
        "sick_leave_taken_days": 0.0
    },
    "EMP-1004": {
        "id": "EMP-1004",
        "name": "David Miller",
        "jurisdiction": "NA",
        "tier": "Standard",
        "tenure_months": 24,
        "is_probationary": False,
        "annual_leave_accrued_days": 20.0,
        "annual_leave_taken_days": 8.0,
        "sick_leave_taken_days": 2.0
    },
    "EMP-1005": {
        "id": "EMP-1005",
        "name": "Elena Gomez",
        "jurisdiction": "LATAM",
        "tier": "Category B",
        "tenure_months": 18,
        "is_probationary": False,
        "annual_leave_accrued_days": 18.0,
        "annual_leave_taken_days": 5.0,
        "sick_leave_taken_days": 0.0
    },
    "EMP-1006": {
        "id": "EMP-1006",
        "name": "Frank Wright",
        "jurisdiction": "UK",
        "tier": "Standard",
        "tenure_months": 36,
        "is_probationary": False,
        "annual_leave_accrued_days": 25.0,
        "annual_leave_taken_days": 12.0,
        "sick_leave_taken_days": 3.0
    },
    "EMP-1007": {
        "id": "EMP-1007",
        "name": "Grace Hopper",
        "jurisdiction": "ANZ",
        "tier": "Year 2+",
        "tenure_months": 28,
        "is_probationary": False,
        "annual_leave_accrued_days": 22.0,
        "annual_leave_taken_days": 7.0,
        "sick_leave_taken_days": 1.0
    }
}

TOOL_DEFINITIONS = [
    {
        "name": "get_employee_record",
        "description": "Fetch verified employee employment record from HRIS database by employee ID. Provides jurisdiction, tier, tenure in months, and probation status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "Employee ID formatted as EMP-XXXX (e.g., EMP-1001)"
                }
            },
            "required": ["employee_id"]
        }
    },
    {
        "name": "get_leave_balance",
        "description": "Retrieve current leave entitlement balance and usage history for an employee.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "Employee ID formatted as EMP-XXXX"
                },
                "leave_type": {
                    "type": "string",
                    "enum": ["annual", "sick", "all"],
                    "description": "The category of leave to inspect (annual, sick, or all)"
                }
            },
            "required": ["employee_id"]
        }
    }
]

class HRISMCPServer:
    """Standard Model Context Protocol (MCP) Server for HRIS."""
    
    def __init__(self, server_name: str = "hris-mcp-server", version: str = "1.0.0"):
        self.server_name = server_name
        self.version = version

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches JSON-RPC 2.0 messages per MCP specification."""
        msg_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": self.server_name,
                        "version": self.version
                    }
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": TOOL_DEFINITIONS
                }
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            try:
                result_content = self.execute_tool(tool_name, tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result_content, indent=2)
                            }
                        ],
                        "isError": False
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({"error": str(e)})
                            }
                        ],
                        "isError": True
                    }
                }

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found."
                }
            }

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Pure backend execution — absolutely no LLM or AI runs on this tool server."""
        if tool_name == "get_employee_record":
            emp_id = args.get("employee_id", "").strip().upper()
            if not emp_id:
                raise ValueError("employee_id parameter is required")
            if emp_id not in EMPLOYEE_DATABASE:
                raise KeyError(f"Employee '{emp_id}' not found in HRIS database.")
            return EMPLOYEE_DATABASE[emp_id]

        elif tool_name == "get_leave_balance":
            emp_id = args.get("employee_id", "").strip().upper()
            leave_type = args.get("leave_type", "all").lower()
            if emp_id not in EMPLOYEE_DATABASE:
                raise KeyError(f"Employee '{emp_id}' not found in HRIS database.")
            
            rec = EMPLOYEE_DATABASE[emp_id]
            accrued = rec["annual_leave_accrued_days"]
            taken = rec["annual_leave_taken_days"]
            remaining = accrued - taken
            
            if leave_type == "annual":
                return {
                    "employee_id": emp_id,
                    "name": rec["name"],
                    "annual_accrued": accrued,
                    "annual_taken": taken,
                    "annual_remaining": remaining
                }
            elif leave_type == "sick":
                return {
                    "employee_id": emp_id,
                    "name": rec["name"],
                    "sick_days_taken": rec["sick_leave_taken_days"]
                }
            else:
                return {
                    "employee_id": emp_id,
                    "name": rec["name"],
                    "annual_accrued": accrued,
                    "annual_taken": taken,
                    "annual_remaining": remaining,
                    "sick_days_taken": rec["sick_leave_taken_days"]
                }
        else:
            raise ValueError(f"Unknown tool '{tool_name}' on HRIS server.")

def run_stdio_server():
    """Run server loop listening on standard input and printing to standard output."""
    server = HRISMCPServer()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = server.handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as ex:
            err_res = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(ex)}"}
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    run_stdio_server()

