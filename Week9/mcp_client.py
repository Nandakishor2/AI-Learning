"""
mcp_client.py
Model Context Protocol (MCP) Client
Manages connections to MCP servers, handles JSON-RPC 2.0 communication,
performs dynamic tool discovery, and executes remote tool calls.
Supports both in-process server instances and stdio subprocess execution.
"""

import json
import subprocess
import sys
from typing import Dict, Any, List, Optional

class MCPClient:
    """Standard MCP Client capable of attaching to multiple MCP Servers."""

    def __init__(self):
        self.servers: Dict[str, Any] = {} # server_name -> handler/process
        self.server_modes: Dict[str, str] = {} # server_name -> "direct" | "stdio"
        self.discovered_tools: Dict[str, Dict[str, Any]] = {} # tool_name -> tool metadata + server_name
        self.req_counter = 0

    def connect_server(self, server_name: str, server_instance: Any = None, command: Optional[List[str]] = None):
        """Connect an MCP server either via direct protocol handler or stdio subprocess."""
        if server_instance is not None:
            # Direct in-process MCP handler (fast, reliable)
            init_req = {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {"clientInfo": {"name": "HRPolicyAgentHost", "version": "1.0.0"}}
            }
            init_res = server_instance.handle_request(init_req)
            self.servers[server_name] = server_instance
            self.server_modes[server_name] = "direct"
            return init_res
        elif command is not None:
            # Subprocess stdio MCP transport
            proc = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            init_req = {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {"clientInfo": {"name": "HRPolicyAgentHost", "version": "1.0.0"}}
            }
            proc.stdin.write(json.dumps(init_req) + "\n")
            proc.stdin.flush()
            res_line = proc.stdout.readline()
            init_res = json.loads(res_line) if res_line else {}
            self.servers[server_name] = proc
            self.server_modes[server_name] = "stdio"
            return init_res
        else:
            raise ValueError("Either server_instance or command must be provided.")

    def _next_id(self) -> int:
        self.req_counter += 1
        return self.req_counter

    def discover_tools(self) -> List[Dict[str, Any]]:
        """
        Discovers available tools dynamically over MCP protocol via 'tools/list'.
        Zero hardcoded tools in the host!
        """
        all_tools = []
        for s_name, s_ref in self.servers.items():
            mode = self.server_modes[s_name]
            list_req = {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/list",
                "params": {}
            }
            if mode == "direct":
                res = s_ref.handle_request(list_req)
            else:
                s_ref.stdin.write(json.dumps(list_req) + "\n")
                s_ref.stdin.flush()
                res = json.loads(s_ref.stdout.readline())

            tools = res.get("result", {}).get("tools", [])
            for t in tools:
                t_name = t["name"]
                self.discovered_tools[t_name] = {
                    "tool": t,
                    "server_name": s_name
                }
                all_tools.append(t)
        return all_tools

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Routes tool execution through the standard MCP 'tools/call' JSON-RPC method.
        """
        if tool_name not in self.discovered_tools:
            return {"error": f"Tool '{tool_name}' not found among discovered MCP tools."}

        meta = self.discovered_tools[tool_name]
        s_name = meta["server_name"]
        s_ref = self.servers[s_name]
        mode = self.server_modes[s_name]

        call_req = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        if mode == "direct":
            res = s_ref.handle_request(call_req)
        else:
            s_ref.stdin.write(json.dumps(call_req) + "\n")
            s_ref.stdin.flush()
            line = s_ref.stdout.readline()
            res = json.loads(line) if line else {}

        if "error" in res:
            return {"error": res["error"].get("message", "MCP Tool Error")}

        result_obj = res.get("result", {})
        content_items = result_obj.get("content", [])
        if content_items and content_items[0].get("type") == "text":
            try:
                return json.loads(content_items[0]["text"])
            except Exception:
                return {"text": content_items[0]["text"]}
        return result_obj

    def close(self):
        for s_name, mode in self.server_modes.items():
            if mode == "stdio":
                proc = self.servers[s_name]
                try:
                    proc.terminate()
                except Exception:
                    pass

