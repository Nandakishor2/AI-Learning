# Week 9 Practical — Task Set C: Results & Evaluation Report

**Domain:** HR Policy (Multi-Region Leave Addenda & HRIS Data)  
**Module:** M5 — MCP, Multi-Agent & A2A / Model Context Protocol  
**Deliverable:** An agent that discovers tools over MCP, plus your own MCP server another person's agent can call.  
**Track C Assigned Task:** "Bolt on the HRIS server without touching the agent."

---

## 1. Architectural Foundation: Where the AI Runs and Where It Doesn't

| Role | Component Name | Where It Runs | Responsibilities & Boundaries |
|---|---|---|---|
| **Host** | `MCPAgent` | Local Host Application | Houses LLM reasoning, orchestrates dynamic tool calling, maintains conversation context, and synthesizes user-facing answers. **The AI runs strictly here.** |
| **Client** | `MCPClient` | Boundary Adapter | Protocol translation layer. Handles JSON-RPC 2.0 serialization, socket/stdio transport, schema registry, and session handshake. |
| **Server** | `HRISMCPServer` & `PolicyMCPServer` | Tool Backend Provider | Exposes capabilities via `tools/list` and executes functions via `tools/call`. **Zero AI runs on the server.** The server has no knowledge of which model or host calls it. |

> [!IMPORTANT]
> **MCP is plumbing, not intelligence.** MCP provides an open standard (a standardized "socket") for connecting agents to external capabilities and datasets. It decouples tool definition from agent code, enabling frictionless swapping and cross-organization reusability.

---

## 2. MCP JSON-RPC 2.0 Protocol Messages & Handshake

### 2.1 Initialization Handshake (`initialize`)
```json
// Client Request -> Server
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "clientInfo": { "name": "HRPolicyAgentHost", "version": "1.0.0" }
  }
}

// Server Response -> Client
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": { "listChanged": false },
      "resources": {},
      "prompts": {}
    },
    "serverInfo": { "name": "hris-mcp-server", "version": "1.0.0" }
  }
}
```

### 2.2 Dynamic Tool Discovery (`tools/list`)
```json
// Client Request -> Server
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}

// Server Response -> Client
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "get_employee_record",
        "description": "Fetch verified employee employment record from HRIS database by employee ID.",
        "inputSchema": {
          "type": "object",
          "properties": { "employee_id": { "type": "string" } },
          "required": ["employee_id"]
        }
      },
      {
        "name": "get_leave_balance",
        "description": "Retrieve current leave entitlement balance and usage history for an employee.",
        "inputSchema": {
          "type": "object",
          "properties": {
            "employee_id": { "type": "string" },
            "leave_type": { "type": "string", "enum": ["annual", "sick", "all"] }
          },
          "required": ["employee_id"]
        }
      }
    ]
  }
}
```

### 2.3 Remote Tool Execution (`tools/call`)
```json
// Client Request -> Server
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_employee_record",
    "arguments": { "employee_id": "EMP-1001" }
  }
}

// Server Response -> Client
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"id\": \"EMP-1001\",\n  \"name\": \"Alice Chen\",\n  \"jurisdiction\": \"APAC\",\n  \"tier\": \"Tier 1 Staff\",\n  \"tenure_months\": 4,\n  \"is_probationary\": true\n}"
      }
    ],
    "isError": false
  }
}
```

---

## 3. The Bolt-On Experiment: Adding a Second Server Without Changing Agent Code

In conventional agent architectures, adding a new tool requires modifying the agent source code, updating tool dispatcher mappings, and altering prompt definitions. In contrast, our `MCPAgent` contains **zero hardcoded tools**:

1. **Phase 1 (HRIS Server Only):**
   - Discovered Tools: `['get_employee_record', 'get_leave_balance']`
   - Successfully answers employee balance inquiries.
2. **Phase 2 (Bolt-On Policy Server):**
   - Second MCP server (`PolicyMCPServer`) connected to the client.
   - **Zero lines of `MCPAgent` code modified.**
   - Agent dynamically discovers: `['get_employee_record', 'get_leave_balance', 'get_jurisdiction_rules', 'search_policy_clause']`.
   - The agent immediately handles multi-source regional compliance questions across both servers.

---

## 4. Cross-Organization Interoperability (Partner Agent Call)

To prove that our `HRISMCPServer` can be reused by another team's agent without coupling:
- An external client (`external_client`) connects independently to `hris_server`.
- The partner agent lists tools and calls `get_employee_record(employee_id="EMP-1005")`.
- The server responds with verified payload (`Elena Gomez`, `LATAM`, `18 months tenure`) adhering strictly to the MCP specification.

---

## 5. Mentor Review Checklist Verification

- [x] **Does the agent use a tool through MCP, discovered rather than hard-coded?**  
  Yes. Tools are populated exclusively via `tools/list` RPC queries at runtime.
- [x] **Can they add a second tool without changing the agent's code?**  
  Yes. Bolting on `PolicyMCPServer` expanded the tool set from 2 to 4 tools without touching any agent code.
- [x] **Did they build their own server that another person's agent could call?**  
  Yes. `HRISMCPServer` is a standalone JSON-RPC 2.0 server tested against external clients.
- [x] **Can they explain, in plain words, where the AI runs and where it doesn't?**  
  Yes. The AI runs exclusively on the host application. The MCP server runs zero AI models and only provides tool functions and data.

