# TripAdvisor 景点抓取（长期可复用）

该项目使用 **Playwright + Python** 自动化访问 TripAdvisor 中国景点列表页，按列表顺序提取景点卡片中的编号与名称，并导出到 Excel。

## 功能

- 从起始页 `https://www.tripadvisor.cn/Attractions-g294211-Activities-China.html` 开始抓取
- 支持指定起始页码，从任意页开始抓取后续数据
- 通过底部分页控件进入下一页
- 默认抓取 10 页（可配置）
- 导出 `编号`、`景点名称` 到 `attractionsForAgent.xlsx`
- 自动录制抓取过程视频（默认 `attractionsForAgent.webm`）

## 环境准备

```bash
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium
```

## 运行

```bash
python3 scrape_tripadvisor_attractions.py
```

默认输出：

- `attractionsForAgent.xlsx`
- `attractionsForAgent.webm`

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