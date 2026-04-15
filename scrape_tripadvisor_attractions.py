from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from openpyxl import Workbook
from playwright.sync_api import Page, TimeoutError, sync_playwright

DEFAULT_URL = "https://www.tripadvisor.cn/Attractions-g294211-Activities-China.html"
RANK_NAME_PATTERN = re.compile(r"^(\d+)\.(.+)$")
LATEST_OUTPUT_RECORD = Path(__file__).resolve().parent / ".tripadvisor_latest_outputs.json"


@dataclass(frozen=True)
class AttractionItem:
    rank: int
    name: str


def load_previous_outputs(record_path: Path) -> tuple[Path | None, Path | None]:
    if not record_path.exists():
        return None, None

    try:
        payload = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, None

    excel_raw = payload.get("excel")
    video_raw = payload.get("video")
    excel_path = Path(excel_raw).expanduser() if isinstance(excel_raw, str) else None
    video_path = Path(video_raw).expanduser() if isinstance(video_raw, str) else None
    return excel_path, video_path


def remove_previous_outputs(
    previous_excel: Path | None,
    previous_video: Path | None,
    current_excel: Path,
    current_video: Path,
) -> None:
    current_paths = {current_excel.resolve(), current_video.resolve()}
    for previous_path in (previous_excel, previous_video):
        if previous_path is None:
            continue
        resolved_previous = previous_path.resolve()
        if resolved_previous in current_paths:
            continue
        if previous_path.exists():
            previous_path.unlink()
            print(f"[INFO] 已删除旧输出: {previous_path}")


def persist_latest_outputs(record_path: Path, excel_path: Path, video_path: Path) -> None:
    payload = {
        "excel": str(excel_path.resolve()),
        "video": str(video_path.resolve()),
    }
    record_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="抓取 TripAdvisor 中国景点列表并导出 Excel。"
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="景点列表起始 URL。")
    parser.add_argument(
        "--pages", type=int, default=10, help="抓取页数（默认 10）。"
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="从第几页开始抓取（页码从 1 开始，默认 1）。",
    )
    parser.add_argument(
        "--output",
        default="attractionsForAgent.xlsx",
        help="Excel 输出文件路径。",
    )
    parser.add_argument(
        "--video",
        default="attractionsForAgent.webm",
        help="录屏输出文件路径。",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="是否启用有头浏览器（默认无头）。",
    )
    return parser.parse_args()


def extract_ranked_names(page: Page) -> list[AttractionItem]:
    raw_items = page.evaluate(
        """
        () => {
          const anchors = Array.from(document.querySelectorAll("a"));
          const rankAnchors = anchors
            .map((anchor) => {
              const text = (anchor.textContent || "").replace(/\\s+/g, " ").trim();
              return { text };
            })
            .filter(
              (row) =>
                /^\\d+\\./.test(row.text) &&
                !/条中国景点点评$/.test(row.text)
            );
          return rankAnchors.map((row) => row.text);
        }
        """
    )
    items: list[AttractionItem] = []
    for raw_item in raw_items:
        match = RANK_NAME_PATTERN.match(raw_item)
        if not match:
            continue
        rank = int(match.group(1))
        name = match.group(2).strip()
        if name:
            items.append(AttractionItem(rank=rank, name=name))
    if not items:
        raise RuntimeError("当前页面未提取到景点数据，请检查页面结构。")
    return items


def goto_next_page(page: Page, previous_first_rank: int) -> bool:
    next_button = page.locator("a[aria-label='Next page']")
    if next_button.count() == 0:
        return False

    next_button.first.click()
    try:
        page.wait_for_function(
            """
            (oldRank) => {
              const firstRankAnchor = Array.from(document.querySelectorAll("a"))
                .map((anchor) => {
                  const text = (anchor.textContent || "").replace(/\\s+/g, " ").trim();
                  const isVisible = !!(
                    anchor.offsetWidth ||
                    anchor.offsetHeight ||
                    anchor.getClientRects().length
                  );
                  return { text, isVisible };
                })
                .find((row) => row.isVisible && /^\\d+\\./.test(row.text));

              if (!firstRankAnchor) return false;
              const currentRank = Number(firstRankAnchor.text.split(".")[0]);
              return currentRank !== oldRank;
            }
            """,
            arg=previous_first_rank,
            timeout=60_000,
        )
    except TimeoutError as exc:
        raise RuntimeError("分页后数据未刷新，无法继续抓取下一页。") from exc
    return True


def get_current_page_number(page: Page) -> int:
    current_page = page.evaluate(
        """
        () => {
          const currentPageAnchor = document.querySelector(
            "a[aria-label*='is your current page']"
          );
          if (!currentPageAnchor) return 1;

          const ariaLabel = currentPageAnchor.getAttribute("aria-label") || "";
          const ariaMatch = ariaLabel.match(/Page\\s+(\\d+)\\s+is your current page/i);
          if (ariaMatch) return Number(ariaMatch[1]);

          const text = (currentPageAnchor.textContent || "").trim();
          if (/^\\d+$/.test(text)) return Number(text);
          return 1;
        }
        """
    )
    return int(current_page)


def jump_to_start_page(page: Page, start_page: int) -> None:
    if start_page <= 1:
        return

    current_page = get_current_page_number(page)
    if current_page > start_page:
        raise RuntimeError(
            f"当前已在第 {current_page} 页，无法回退到第 {start_page} 页。"
        )

    while current_page < start_page:
        current_items = extract_ranked_names(page)
        has_next = goto_next_page(page, previous_first_rank=current_items[0].rank)
        if not has_next:
            raise RuntimeError(
                f"无法跳转到第 {start_page} 页：分页在第 {current_page} 页提前结束。"
            )
        page.wait_for_timeout(1_500)
        current_page = get_current_page_number(page)
        print(f"[INFO] 已跳转到站点第 {current_page} 页")


def save_to_excel(items: list[AttractionItem], output_path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "景点"
    sheet.append(["编号", "景点名称"])
    for item in items:
        sheet.append([item.rank, item.name])
    workbook.save(output_path)


def run_scraper(
    url: str,
    pages: int,
    start_page: int,
    output: Path,
    video_output: Path,
    headed: bool,
) -> None:
    if pages <= 0:
        raise ValueError("pages 必须大于 0。")
    if start_page <= 0:
        raise ValueError("start_page 必须大于 0。")

    output = output.resolve()
    video_output = video_output.resolve()
    previous_excel, previous_video = load_previous_outputs(LATEST_OUTPUT_RECORD)

    output.parent.mkdir(parents=True, exist_ok=True)
    video_output.parent.mkdir(parents=True, exist_ok=True)
    temp_video_dir = video_output.parent / ".playwright-video-tmp"
    temp_video_dir.mkdir(parents=True, exist_ok=True)

    all_items: list[AttractionItem] = []
    page = None
    page_video = None
    excel_saved = False
    video_saved = False

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not headed)
        context = browser.new_context(
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            viewport={"width": 1440, "height": 900},
            record_video_dir=str(temp_video_dir),
            record_video_size={"width": 1280, "height": 720},
        )

        try:
            page = context.new_page()
            page_video = page.video
            page.goto(url, wait_until="domcontentloaded", timeout=120_000)
            page.wait_for_timeout(2_500)
            jump_to_start_page(page, start_page=start_page)

            for page_index in range(1, pages + 1):
                page.wait_for_timeout(2_500)
                current_items = extract_ranked_names(page)
                all_items.extend(current_items)
                site_page_number = get_current_page_number(page)
                print(
                    f"[INFO] 进度 {page_index}/{pages}：站点第 {site_page_number} 页抓取完成，"
                    f"{len(current_items)} 条（首条编号 {current_items[0].rank}）"
                )

                if page_index == pages:
                    break

                has_next = goto_next_page(page, previous_first_rank=current_items[0].rank)
                if not has_next:
                    print("[WARN] 未找到下一页按钮，提前结束抓取。")
                    break

            save_to_excel(all_items, output)
            print(f"[INFO] Excel 已保存: {output}")
            excel_saved = True
        finally:
            if page is not None:
                page.close()
            if page_video is not None:
                if video_output.exists():
                    video_output.unlink()
                page_video.save_as(str(video_output))
                print(f"[INFO] 录屏已保存: {video_output}")
                video_saved = True
            context.close()
            browser.close()
            shutil.rmtree(temp_video_dir, ignore_errors=True)

    if excel_saved and video_saved:
        remove_previous_outputs(
            previous_excel=previous_excel,
            previous_video=previous_video,
            current_excel=output,
            current_video=video_output,
        )
        persist_latest_outputs(
            record_path=LATEST_OUTPUT_RECORD,
            excel_path=output,
            video_path=video_output,
        )


def main() -> None:
    args = parse_arguments()
    run_scraper(
        url=args.url,
        pages=args.pages,
        start_page=args.start_page,
        output=Path(args.output),
        video_output=Path(args.video),
        headed=args.headed,
    )


if __name__ == "__main__":
    main()
