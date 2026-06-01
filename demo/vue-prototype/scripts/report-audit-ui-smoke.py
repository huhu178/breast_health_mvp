#!/usr/bin/env python3
"""Browser smoke test for report advice audit and finalization."""

from __future__ import annotations

import argparse
import time
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


def run_report_audit_smoke(frontend_url: str, backend_url: str, screenshot_dir: Path | None, keep: bool) -> None:
    api = ApiClient(backend_url)
    patient_id = None
    try:
        api.login()
        patient_id, report_id, patient_name = create_generated_breast_report(api, "UI审核验收", "176")

        imaging_text = f"UI审核验收影像建议 {int(time.time())}"
        overall_text = "UI审核验收总体评估：按高风险路径管理并保留影像资料。"
        risk_text = "UI审核验收风险建议：7天内完成首次随访。"
        tongue_text = "UI审核验收舌诊内容：暂未见明显异常回流。"

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
                textareas = modal.locator("textarea.rp-audit-ta")
                expect(textareas).to_have_count(4, timeout=10000)
                textareas.nth(0).fill(imaging_text)
                textareas.nth(1).fill(overall_text)
                textareas.nth(2).fill(risk_text)
                textareas.nth(3).fill(tongue_text)
                modal.get_by_role("button", name="审核通过").click()
                expect(modal.get_by_text("下一步：报告后首次随访")).to_be_visible(timeout=15000)

                advice = api_fetch(page, f"/api/b/reports/{report_id}/advice")["body"]["advice"]
                if advice.get("status") != "archived":
                    raise AssertionError(f"expected archived advice, got {advice}")
                sections = advice.get("sections") or {}
                if sections.get("imaging_report_advice") != imaging_text:
                    raise AssertionError(f"saved imaging advice mismatch: {sections}")
                if sections.get("overall_assessment") != overall_text:
                    raise AssertionError(f"saved overall advice mismatch: {sections}")
                if sections.get("risk_assessment") != risk_text:
                    raise AssertionError(f"saved risk advice mismatch: {sections}")

                detail = api_fetch(page, f"/api/b/reports/{report_id}")["body"]
                if detail.get("status") != "finalized":
                    raise AssertionError(f"expected finalized report, got {detail.get('status')}")

                locked = api_fetch(
                    page,
                    f"/api/b/reports/{report_id}/advice",
                    "PUT",
                    {"content": "归档后不应允许再次保存草稿"},
                    expect_ok=False,
                )
                if locked["status"] != 409 or locked["body"].get("success") is not False:
                    raise AssertionError(f"expected locked advice failure, got {locked}")

                if screenshot_dir:
                    screenshot_dir.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(screenshot_dir / "report-audit.png"), full_page=True)
            except Exception:
                save_failure_screenshot(page, screenshot_dir)
                raise
            finally:
                browser.close()
    finally:
        cleanup_patient(api, patient_id, keep, "report-audit")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend-url", default="http://127.0.0.1:5173")
    parser.add_argument("--backend-url", default="http://127.0.0.1:5000")
    parser.add_argument("--screenshot-dir", default="/tmp/report-audit-ui-smoke")
    parser.add_argument("--keep", action="store_true", help="保留脚本创建的测试患者")
    args = parser.parse_args()

    screenshot_dir = Path(args.screenshot_dir) if args.screenshot_dir else None
    run_report_audit_smoke(args.frontend_url.rstrip("/"), args.backend_url.rstrip("/"), screenshot_dir, args.keep)
    print("[OK] report audit UI smoke passed")


if __name__ == "__main__":
    main()
