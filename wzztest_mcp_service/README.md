# wzzTest MCP Service

This service exposes an MCP tool that calls:

`https://youxuer8.test.xdf.cn/api/sysmanage/securityCode/getSecurityCode?loginMode=Front`

and returns the image as base64 so Agent Cloud can consume it.

## 1) Local run

```bash
cd wzztest_mcp_service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 server.py
```

The MCP endpoint defaults to:

- `http://0.0.0.0:8000/mcp`

## 2) Environment variables

- `HOST` (default `0.0.0.0`)
- `PORT` (default `8000`)
- `MCP_PATH` (default `/mcp`)
- `WZZTEST_SECURITY_CODE_URL` (default fixed to the API URL above)
- `WZZTEST_REQUEST_TIMEOUT_SECONDS` (default `20`)
- `WZZTEST_VERIFY_SSL` (default `true`)
- `WZZTEST_EXTRA_HEADERS_JSON` (optional JSON object for extra request headers, example: `{"Cookie":"a=b","Authorization":"Bearer xxx"}`)

## 3) Docker run

```bash
cd wzztest_mcp_service
docker build -t wzztest-mcp:latest .
docker run --rm -p 8000:8000 --name wzztest-mcp wzztest-mcp:latest
```

## 4) Agent Cloud MCP registration

In `https://cursor.com/agents`:

1. Open MCP dropdown
2. Add custom MCP
3. Name: `wzzTest`
4. Transport: `HTTP`
5. URL: `https://<your-domain>/mcp`
6. If needed, configure auth headers or OAuth

## 5) Tool contract

### `health_check`
Returns:

```json
{"ok": true, "service": "wzzTest", "transport": "streamable-http"}
```

### `get_security_code_image`
Input:

- `login_mode` (default `Front`)

Output fields:

- `ok`: bool
- `source`: `"wzzTest"`
- `source_url`: final requested URL
- `login_mode`: echoed input
- `content_type`: image MIME type
- `size_bytes`: image bytes length
- `image_base64`: captcha image base64
- `image_data_url`: `data:<mime>;base64,...` format for direct frontend rendering
