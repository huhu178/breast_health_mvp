#!/usr/bin/env python3
"""Browser smoke test for creating first follow-up from the audit modal."""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from smoke_utils import (
    ApiClient,
    api_fetch,
    browser_login,
    cleanup_patient,
    create_generated_breast_report,
    save_failure_screenshot,
)


def run_audit_followup_smoke(frontend_url: str, backend_url: str, screenshot_dir: Path | None, keep: bool) -> None:
    api = ApiClient(backend_url)
    patient_id = None
    try:
        api.login()
        patient_id, report_id, patient_name = create_generated_breast_report(api, "UI审核随访", "174")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            try:
                browser_login(page, frontend_url)

                page.goto(f"{frontend_url}/patient?tab=review", wait_until="networkidle")
                expect(page.get_by_text("报告列表").or_(page.get_by_text("体检报告列表")).first).to_be_visible(timeout=10000)
                page.locator("input[placeholder*='姓名'], input[placeholder*='手机号']").first.fill(patient_name)
                report_row = page.locator("tbody tr", has_text=patient_name).filter(has_text="待审核").first
                expect(report_row).to_be_visible(timeout=10000)
                report_row.locator(".rp-row-actions button").nth(1).click()

                modal = page.locator(".rp-modal").last
                expect(modal.get_by_text("审核AI生成内容").first).to_be_visible(timeout=10000)
                modal.locator("textarea.rp-audit-ta").nth(0).fill("UI审核后随访：影像建议已确认。")
                modal.locator("textarea.rp-audit-ta").nth(1).fill("UI审核后随访：总体评估已确认。")
                modal.locator("textarea.rp-audit-ta").nth(2).fill("UI审核后随访：需要首次随访。")
                modal.get_by_role("button", name="审核通过").click()

                expect(modal.get_by_text("下一步：报告后首次随访")).to_be_visible(timeout=15000)
                modal.get_by_role("button", name="创建首次随访任务").click()
                expect(modal.get_by_role("button", name="打开执行跟踪")).to_be_visible(timeout=15000)
                expect(modal.get_by_role("button", name="复制打卡链接")).to_be_visible(timeout=10000)

                tasks = api_fetch(page, f"/api/b/followup/tasks?report_id={report_id}&source=report&per_page=20")["body"]
                if tasks.get("total") != 1:
                    raise AssertionError(f"expected one report follow-up task, got {tasks}")
                task = tasks["items"][0]
                if task.get("source") != "report" or task.get("patient_id") != patient_id:
                    raise AssertionError(f"unexpected task payload: {task}")
                if not task.get("public_checkin_path", "").endswith(task["task_code"]):
                    raise AssertionError(f"missing public checkin path: {task}")

                duplicate = api_fetch(page, f"/api/b/followup/tasks/from-report/{report_id}", "POST", {}, expect_ok=False)
                if duplicate["status"] != 409 or duplicate["body"].get("success") is not False:
                    raise AssertionError(f"expected duplicate create failure, got {duplicate}")

                page.goto(f"{frontend_url}{task['public_checkin_path']}", wait_until="networkidle")
                expect(page.get_by_text("健康管理任务").first).to_be_visible(timeout=10000)

                page.goto(f"{frontend_url}/patient?tab=follow", wait_until="networkidle")
                expect(page.get_by_text("任务执行表").first).to_be_visible(timeout=10000)

                if screenshot_dir:
                    screenshot_dir.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(screenshot_dir / "audit-followup.png"), full_page=True)
            except Exception:
                save_failure_screenshot(page, screenshot_dir)
                raise
            finally:
                browser.close()
    finally:
        cleanup_patient(api, patient_id, keep, "audit-followup")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend-url", default="http://127.0.0.1:5173")
    parser.add_argument("--backend-url", default="http://127.0.0.1:5000")
    parser.add_argument("--screenshot-dir", default="/tmp/audit-followup-ui-smoke")
    parser.add_argument("--keep", action="store_true", help="保留脚本创建的测试患者")
    args = parser.parse_args()

    screenshot_dir = Path(args.screenshot_dir) if args.screenshot_dir else None
    run_audit_followup_smoke(args.frontend_url.rstrip("/"), args.backend_url.rstrip("/"), screenshot_dir, args.keep)
    print("[OK] audit follow-up UI smoke passed")


if __name__ == "__main__":
    main()
