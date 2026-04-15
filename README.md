# TripAdvisor 景点抓取（长期可复用）

该项目使用 **Playwright + Python** 自动化访问 TripAdvisor 中国景点列表页，按列表顺序提取景点卡片中的编号与名称，并导出到 Excel。

## 功能

- 示例：生成一个新项目，支持打开浏览器获取景点存到excel
- 目标 URL：https://www.tripadvisor.cn/Attractions-g294211-Activities-China.html及后续页面，每个页面都是通过底部分页按钮进入下一页，直到抓取10个页面后结束，其中初始页面的页码和抓取页面的数量是可以配置的
- 分析页面并按顺序从列表页面的景点卡片中获取编号、景点名称信息
- 输出：仓库里一个 attractionsForAgent.xlsx 存储编号和名称，录制获取数据的视频
- 用法：python3 scrape_tripadvisor_attractions.py --start-page 6 --pages 5 --output attractionsFromPage.xlsx --video attractionsFromPage.webm

## 环境准备

推荐直接使用仓库内脚本完成环境初始化：

```bash
./scripts/setup_env.sh
```

等价手动命令：

```bash
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium
```

> 可选：安装 `ffmpeg` 可获得更好的视频裁剪效果（未安装也不影响主流程）。

## 运行

```bash
python3 scrape_tripadvisor_attractions.py
```

默认输出：

- `attractionsForAgent.xlsx`
- `attractionsForAgent.webm`

## 测试（怎么测）

### 1) 快速回归（推荐每次改动后都执行）

```bash
./scripts/run_tests.sh
```

该命令会依次执行：

- `python3 -m py_compile scrape_tripadvisor_attractions.py`（语法与导入校验）
- `python3 -m unittest discover -s tests -p "test_*.py"`（无网络单元测试）

### 2) 功能烟雾测试（可选，需网络和浏览器）

```bash
./scripts/run_tests.sh --with-smoke
```

会额外执行：

```bash
python3 scrape_tripadvisor_attractions.py --pages 1 --start-page 1
```

用于验证真实页面抓取链路与输出文件生成。

### 3) 在 Cursor onboard 中配置环境

仓库提供了可直接复制的 onboard 提示词：`ONBOARD_PROMPT.md`。  
将其粘贴到 [cursor.com/onboard](https://cursor.com/onboard) 可让后续 cloud agent 默认具备运行与测试环境。

## 常用参数

```bash
python3 scrape_tripadvisor_attractions.py \
  --start-page 5 \
  --pages 10 \
  --output attractionsForAgent.xlsx \
  --video attractionsForAgent.webm
```

可选参数：

- `--url`: 自定义起始页面
- `--start-page`: 起始页码（默认 1），例如 5 表示从第 5 页开始抓取
- `--pages`: 抓取页数
- `--output`: Excel 输出路径
- `--video`: 录屏输出路径
- `--headed`: 启用有头浏览器（默认无头）
