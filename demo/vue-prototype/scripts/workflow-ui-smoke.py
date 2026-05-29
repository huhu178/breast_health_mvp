#!/usr/bin/env python3
"""Browser smoke test for the follow-up workflow configuration page."""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


USERNAME = "smoke_admin"
PASSWORD = "Smoke@123456"


def save_failure_screenshot(page, screenshot_dir: Path | None) -> None:
    if not screenshot_dir:
        return
    try:
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot_dir / "failure.png"), full_page=True)
    except Exception as exc:
        print(f"[WARN] failed to write failure screenshot: {exc}")


def run_workflow_smoke(frontend_url: str, screenshot_dir: Path | None) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(f"{frontend_url}/login", wait_until="networkidle")
            page.locator("#loginAccount").fill(USERNAME)
            page.locator("#loginPassword").fill(PASSWORD)
            page.get_by_role("button", name="登录").click()
            page.wait_for_url("**/analytics", timeout=10000)

            page.goto(f"{frontend_url}/followup-workflow", wait_until="networkidle")
            expect(page.get_by_role("heading", name="随访知识库与模板")).to_be_visible(timeout=10000)
            expect(page.get_by_role("heading", name="随访任务模板")).to_be_visible(timeout=10000)
            expect(page.get_by_text("知识库与模板编辑").first).to_be_visible(timeout=10000)
            expect(page.get_by_text("任务节点").first).to_be_visible(timeout=10000)

            page.get_by_role("button", name="新建随访模板").click()
            expect(page.locator("input[placeholder*='乳腺结节30天随访任务']").first).to_be_visible(timeout=10000)

            add_node = page.get_by_role("button", name="添加节点")
            if add_node.is_enabled():
                add_node.click()
                expect(page.get_by_role("heading", name="新增任务节点")).to_be_visible(timeout=10000)
                page.get_by_role("button", name="取消").click()

            page.get_by_role("button", name="新增知识").click()
            expect(page.get_by_role("heading", name="新增知识")).to_be_visible(timeout=10000)
            page.get_by_role("button", name="取消").click()

            page.get_by_role("button", name="新增AI规则").click()
            expect(page.get_by_role("heading", name="新增AI规则")).to_be_visible(timeout=10000)
            page.get_by_role("button", name="取消").click()

            if screenshot_dir:
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(screenshot_dir / "followup-workflow.png"), full_page=True)
        except Exception:
            save_failure_screenshot(page, screenshot_dir)
            raise
        finally:
            browser.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend-url", default="http://127.0.0.1:5173")
    parser.add_argument("--screenshot-dir", default="/tmp/followup-workflow-ui-smoke")
    args = parser.parse_args()

    screenshot_dir = Path(args.screenshot_dir) if args.screenshot_dir else None
    run_workflow_smoke(args.frontend_url.rstrip("/"), screenshot_dir)
    print("[OK] follow-up workflow UI smoke passed")


if __name__ == "__main__":
    main()
