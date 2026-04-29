# Deploy wzzTest MCP Service

This guide deploys the MCP server as an HTTP endpoint and registers it in Cursor Agent Cloud.

## 1) Run locally first

```bash
cd wzztest_mcp_service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 server.py
```

Default endpoint: `http://127.0.0.1:8000/mcp`

## 2) Choose a public hosting platform

Any platform works as long as it can expose a public HTTPS URL:

- Railway
- Render
- Fly.io
- ECS/VM + reverse proxy

Required runtime command:

```bash
python /app/server.py
```

Required environment variables:

- `HOST=0.0.0.0`
- `PORT=<platform_port>`
- `MCP_PATH=/mcp`
- `WZZTEST_SECURITY_CODE_URL=https://youxuer8.test.xdf.cn/api/sysmanage/securityCode/getSecurityCode`
- `WZZTEST_REQUEST_TIMEOUT_SECONDS=20`
- `WZZTEST_VERIFY_SSL=true`
- `WZZTEST_EXTRA_HEADERS_JSON={"Cookie":"k=v","Authorization":"Bearer x"}`

## 3) Validate deployed endpoint

After deploy, confirm the server is reachable from public internet:

- MCP URL should be like: `https://<your-domain>/mcp`

Then test via FastMCP client from any machine that can reach it:

```python
import asyncio
from fastmcp import Client

async def main():
    async with Client("https://<your-domain>/mcp") as client:
        print([t.name for t in await client.list_tools()])
        print((await client.call_tool("health_check", {})).data)
        result = await client.call_tool("get_security_code_image", {"login_mode": "Front"})
        print(result.data["content_type"], result.data["size_bytes"])

asyncio.run(main())
```

## 4) Register in Cursor Agent Cloud

1. Open `https://cursor.com/agents`
2. Open MCP dropdown
3. Add custom MCP
4. Name: `wzzTest`
5. Transport: `HTTP`
6. URL: `https://<your-domain>/mcp`
7. Save and enable

## 5) Use in Agent prompt or Cloud API run

In your prompt, force tool usage explicitly:

`Use MCP tool wzzTest.get_security_code_image with login_mode='Front' and return JSON fields only.`

If you trigger through Cloud API, send this instruction in `prompt.text` when creating a run.
