# TripAdvisor 景点抓取（长期可复用）

该项目使用 **Playwright + Python** 自动化访问 TripAdvisor 中国景点列表页，按列表顺序提取景点卡片中的编号与名称，并导出到 Excel。

## 功能

- 示例：生成一个新项目，支持打开浏览器获取景点存到excel
- 目标 URL：https://www.tripadvisor.cn/Attractions-g294211-Activities-China.html及后续页面，每个页面都是通过底部分页按钮进入下一页，直到抓取10个页面后结束，其中初始页面的页码和抓取页面的数量是可以配置的
- 分析页面并按顺序从列表页面的景点卡片中获取编号、景点名称信息
- 输出：仓库里一个 attractionsForAgent.xlsx 存储编号和名称，录制获取数据的视频
- 用法：python3 scrape_tripadvisor_attractions.py --start-page 6 --pages 5 --output attractionsFromPage.xlsx --video attractionsFromPage.webm

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
