# Cursor Onboard Prompt

请基于当前仓库生成 cloud agent 的默认环境配置，目标是让 agent 开箱即可运行与测试该项目。

## 需要在环境中完成

1. 安装 Python 3 与 pip（如果镜像未内置）。
2. 在仓库根目录执行：
   - `python3 -m pip install --upgrade pip`
   - `python3 -m pip install -r requirements.txt`
   - `python3 -m playwright install chromium`
3. 可选安装 `ffmpeg`（用于更优视频裁剪；缺失不应导致任务失败）。

## 验收命令（必须可通过）

在仓库根目录执行：

```bash
./scripts/run_tests.sh
```

如果网络可用，可额外执行：

```bash
./scripts/run_tests.sh --with-smoke
```

## 约束

- 不要修改脚本 CLI 参数契约。
- 不要改动 Excel 输出数据契约（sheet: `景点`，列：`编号`, `景点名称`）。
