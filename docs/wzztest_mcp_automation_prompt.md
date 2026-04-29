# wzzTest MCP 一键生成/部署/调用描述文档

本文档提供一段可直接复制给 Agent 的标准描述。下次只需把“完整任务描述模板”原文发送给 Agent，即可自动完成：

1. 生成 `wzzTest` MCP 服务代码  
2. 部署 MCP 服务（本机 + 公网可访问）  
3. 在 Agent Cloud 中配置 MCP 并调用工具  
4. 产出可验证的测试证据与操作说明

---

## 使用方式

1. 复制下方 **完整任务描述模板** 全文。
2. 发送给 Agent（Cursor Agent / Cloud Agent）。
3. 等待 Agent 自动完成代码、部署、调用和验证。

---

## 完整任务描述模板（可直接复制）

你是一个可执行代码与部署操作的工程 Agent。请端到端完成以下任务，不要只给方案，要直接落地执行并给出可验证结果。

### 目标

搭建一个名为 `wzzTest` 的 MCP 服务，并提供工具调用接口：

- 上游接口：  
  `https://youxuer8.test.xdf.cn/api/sysmanage/securityCode/getSecurityCode?loginMode=Front`
- 功能：调用该接口，返回验证码图片数据（base64 格式）
- MCP 服务需可被 Agent Cloud 通过 HTTP MCP 访问调用

### 必须完成的工作

1. **生成服务代码**
   - 新建目录：`wzztest_mcp_service`
   - 使用 Python 实现 MCP 服务（推荐 `fastmcp` + `httpx`）
   - 服务名：`wzzTest`
   - 至少提供两个 MCP 工具：
     - `health_check()`: 返回服务状态
     - `get_security_code_image(login_mode: str = "Front")`: 调用上游接口并返回图片信息
   - `get_security_code_image` 的返回字段至少包含：
     - `ok` (bool)
     - `source` (`"wzzTest"`)
     - `source_url`
     - `login_mode`
     - `content_type`
     - `size_bytes`
     - `image_base64`
     - `image_data_url`（形如 `data:<mime>;base64,...`）
   - 支持环境变量：
     - `HOST`（默认 `0.0.0.0`）
     - `PORT`（默认 `8000`）
     - `MCP_PATH`（默认 `/mcp`）
     - `WZZTEST_SECURITY_CODE_URL`（默认上游接口基础地址）
     - `WZZTEST_REQUEST_TIMEOUT_SECONDS`（默认 `20`）
     - `WZZTEST_VERIFY_SSL`（默认 `true`）
     - `WZZTEST_EXTRA_HEADERS_JSON`（可选，JSON 字符串，用于 Cookie/Authorization 等请求头）
   - 对异常做明确报错：HTTP 非 200、空响应体、非图片响应等。

2. **提供部署文件**
   - `requirements.txt`
   - `Dockerfile`
   - `README.md`（本地运行、Docker 运行、工具字段说明）
   - `DEPLOY.md`（公网部署与 Agent Cloud 配置步骤）

3. **在当前机器部署并运行**
   - 以 HTTP 模式启动 MCP 服务（`streamable-http`）
   - MCP 路径默认 `/mcp`
   - 若机器无 Docker，可先用 Python 直接启动；但 Docker 文件仍需提供
   - 使用 `tmux` 保持服务长期运行

4. **暴露公网地址供 Agent Cloud 调用**
   - 若没有固定域名，使用隧道（如 `cloudflared tunnel --url http://127.0.0.1:8000`）
   - 输出一个可访问的公网 MCP URL（`https://.../mcp`）

5. **验证 MCP 可调用**
   - 用 FastMCP Client 做端到端测试：
     - `list_tools`
     - `health_check`
     - `get_security_code_image`
   - 验证 `image_base64` 可解码为图片字节
   - 保存验证产物：
     - 验证码图片文件（如 `/opt/cursor/artifacts/wzztest_captcha.jpg`）
     - 测试日志（如 `/opt/cursor/artifacts/wzztest_mcp_smoketest.log`）

6. **输出 Agent Cloud 配置说明**
   - 告诉我在 `https://cursor.com/agents` 如何添加 MCP：
     - Name: `wzzTest`
     - Transport: `HTTP`
     - URL: `<你的公网MCP地址>`
   - 给出可直接复制的调用提示词，例如：  
     `Use MCP tool wzzTest.get_security_code_image with login_mode='Front' and return JSON only.`

7. **Git 要求**
   - 新建分支：`cursor/<descriptive-name>`
   - 提交代码并推送远端
   - 创建 PR（草稿可）

### 验收标准（必须全部满足）

1. 仓库中存在 `wzztest_mcp_service` 完整代码与文档。  
2. MCP 服务可启动，`/mcp` 可访问。  
3. 通过 MCP 工具成功调用上游验证码接口并返回图片 base64。  
4. 提供可复现的测试命令、日志和图片产物路径。  
5. 提供 Agent Cloud 的可用配置（名称、传输方式、URL）。  
6. 若使用临时隧道，明确说明 URL 失效与重启后的更新方式。

### 最终回复格式要求

请按以下结构回复：

1. `Walkthrough`：放 1 张验证码图片产物 + 关键日志引用  
2. `Summary`：列出新增文件与核心能力  
3. `Testing`：逐条列出执行过的命令与结果（成功/失败/警告）  
4. `Agent Cloud MCP 配置`：给可直接粘贴的配置项和调用提示词

---

## 备注

- 如果你希望“每次都自动稳定部署为固定域名（非临时隧道）”，可在模板中额外增加：
  - 指定部署平台（例如 ECS / K8s / 内网网关）
  - 指定固定域名与 TLS 证书来源
  - 指定监控与重启策略（systemd/supervisor/k8s health check）
