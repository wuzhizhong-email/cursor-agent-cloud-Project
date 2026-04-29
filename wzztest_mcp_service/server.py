import base64
import json
import os
from typing import Any

import httpx
from fastmcp import FastMCP

DEFAULT_SECURITY_CODE_URL = (
    "https://youxuer8.test.xdf.cn/api/sysmanage/securityCode/getSecurityCode"
)
DEFAULT_LOGIN_MODE = "Front"
DEFAULT_TIMEOUT_SECONDS = 20.0

mcp = FastMCP("wzzTest")


def _as_bool(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def _guess_image_content_type(image_bytes: bytes) -> str | None:
    if image_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if image_bytes.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return None


def _load_extra_headers() -> dict[str, str]:
    raw_headers = os.getenv("WZZTEST_EXTRA_HEADERS_JSON", "").strip()
    if not raw_headers:
        return {}

    try:
        loaded = json.loads(raw_headers)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "WZZTEST_EXTRA_HEADERS_JSON is not valid JSON."
        ) from exc

    if not isinstance(loaded, dict):
        raise RuntimeError("WZZTEST_EXTRA_HEADERS_JSON must be a JSON object.")

    normalized: dict[str, str] = {}
    for key, value in loaded.items():
        normalized[str(key)] = str(value)
    return normalized


def _fetch_security_code_image(login_mode: str) -> tuple[bytes, str, str]:
    url = os.getenv("WZZTEST_SECURITY_CODE_URL", DEFAULT_SECURITY_CODE_URL).strip()
    timeout_seconds = float(
        os.getenv("WZZTEST_REQUEST_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
    )
    verify_ssl = _as_bool(os.getenv("WZZTEST_VERIFY_SSL"), default=True)

    headers: dict[str, str] = {
        "Accept": "image/*,*/*;q=0.8",
        "User-Agent": "wzzTest-mcp/1.0",
    }
    headers.update(_load_extra_headers())
    params = {"loginMode": login_mode}

    with httpx.Client(
        timeout=timeout_seconds,
        verify=verify_ssl,
        follow_redirects=True,
    ) as client:
        response = client.get(url, params=params, headers=headers)

    if response.status_code != 200:
        text_preview = response.text[:300] if response.text else ""
        raise RuntimeError(
            f"Security code API returned HTTP {response.status_code}. "
            f"Body preview: {text_preview}"
        )

    if not response.content:
        raise RuntimeError("Security code API returned an empty response body.")

    content_type = (
        response.headers.get("content-type", "application/octet-stream")
        .split(";")[0]
        .strip()
        .lower()
    )
    if not content_type.startswith("image/"):
        guessed = _guess_image_content_type(response.content)
        if guessed is not None:
            content_type = guessed
        else:
            text_preview = response.text[:300] if response.text else ""
            raise RuntimeError(
                f"Expected an image response but got {content_type}. "
                f"Body preview: {text_preview}"
            )

    return response.content, content_type, str(response.url)


@mcp.tool(
    description=(
        "Call the security code API and return the image in base64 format. "
        "Useful when clients need captcha bytes through MCP."
    )
)
def get_security_code_image(login_mode: str = DEFAULT_LOGIN_MODE) -> dict[str, Any]:
    image_bytes, content_type, source_url = _fetch_security_code_image(login_mode)
    image_base64 = base64.b64encode(image_bytes).decode("ascii")
    data_url = f"data:{content_type};base64,{image_base64}"

    return {
        "ok": True,
        "source": "wzzTest",
        "source_url": source_url,
        "login_mode": login_mode,
        "content_type": content_type,
        "size_bytes": len(image_bytes),
        "image_base64": image_base64,
        "image_data_url": data_url,
    }


@mcp.tool(description="Simple health check for MCP deployment validation.")
def health_check() -> dict[str, Any]:
    return {"ok": True, "service": "wzzTest", "transport": "streamable-http"}


def _host() -> str:
    return os.getenv("HOST", "0.0.0.0")


def _port() -> int:
    return int(os.getenv("PORT", "8000"))


def _path() -> str:
    raw_path = os.getenv("MCP_PATH", "/mcp").strip()
    if not raw_path.startswith("/"):
        raw_path = f"/{raw_path}"
    return raw_path


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host=_host(),
        port=_port(),
        path=_path(),
    )
