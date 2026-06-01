#!/usr/bin/env python3
"""Browser smoke test for triple-nodule report generation and audit."""

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
    create_generated_triple_report,
    save_failure_screenshot,
)


def assert_generated_triple_report(page, report_id: int) -> None:
    detail = api_fetch(page, f"/api/b/reports/{report_id}")["body"]
    if detail.get("status") != "generated":
        raise AssertionError(f"expected generated triple report, got {detail.get('status')}")
    if detail.get("risk_level") not in {"高风险", "中风险", "低风险"}:
        raise AssertionError(f"unexpected risk level: {detail.get('risk_level')}")
    html = detail.get("report_html") or ""
    for keyword in ["乳腺", "甲状腺", "肺"]:
        if keyword not in html:
            raise AssertionError(f"triple report html missing keyword {keyword}")


def run_triple_report_smoke(frontend_url: str, backend_url: str, screenshot_dir: Path | None, keep: bool) -> None:
    api = ApiClient(backend_url)
    patient_id = None
    try:
        api.login()
        patient_id, report_id, patient_name = create_generated_triple_report(api, "UI三合并报告", "172")

        imaging_text = f"UI三合并报告影像建议 {int(time.time())}"
        overall_text = "UI三合并报告总体评估：三类结节资料均已进入报告审核。"
        risk_text = "UI三合并报告风险建议：按高风险路径完成首次随访和复查提醒。"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            try:
                browser_login(page, frontend_url)
                assert_generated_triple_report(page, report_id)

                page.goto(f"{frontend_url}/patient?tab=review", wait_until="networkidle")
                expect(page.get_by_text("报告列表").or_(page.get_by_text("体检报告列表")).first).to_be_visible(timeout=10000)
                page.locator("input[placeholder*='姓名'], input[placeholder*='手机号']").first.fill(patient_name)
                report_row = page.locator("tbody tr", has_text=patient_name).filter(has_text="待审核").first
                expect(report_row).to_be_visible(timeout=10000)
                expect(report_row.get_by_text("三合并").or_(report_row.get_by_text("三合并结节")).first).to_be_visible(timeout=10000)
                report_row.locator(".rp-row-actions button").nth(1).click()

                modal = page.locator(".rp-modal").last
                expect(modal.get_by_text("审核AI生成内容").first).to_be_visible(timeout=10000)
                textareas = modal.locator("textarea.rp-audit-ta")
                expect(textareas).to_have_count(4, timeout=10000)
                textareas.nth(0).fill(imaging_text)
                textareas.nth(1).fill(overall_text)
                textareas.nth(2).fill(risk_text)
                modal.get_by_role("button", name="审核通过").click()
                expect(modal.get_by_text("下一步：报告后首次随访")).to_be_visible(timeout=15000)

                advice = api_fetch(page, f"/api/b/reports/{report_id}/advice")["body"]["advice"]
                if advice.get("status") != "archived":
                    raise AssertionError(f"expected archived advice, got {advice}")
                sections = advice.get("sections") or {}
                if sections.get("imaging_report_advice") != imaging_text:
                    raise AssertionError(f"saved triple imaging advice mismatch: {sections}")

                detail = api_fetch(page, f"/api/b/reports/{report_id}")["body"]
                if detail.get("status") != "finalized":
                    raise AssertionError(f"expected finalized triple report, got {detail.get('status')}")
                if detail.get("report_html") and "reviewed-advice-sections" not in detail["report_html"]:
                    raise AssertionError("finalized triple report html missing reviewed advice sections")

                if screenshot_dir:
                    screenshot_dir.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(screenshot_dir / "triple-report.png"), full_page=True)
            except Exception:
                save_failure_screenshot(page, screenshot_dir)
                raise
            finally:
                browser.close()
    finally:
        cleanup_patient(api, patient_id, keep, "triple-report")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend-url", default="http://127.0.0.1:5173")
    parser.add_argument("--backend-url", default="http://127.0.0.1:5000")
    parser.add_argument("--screenshot-dir", default="/tmp/triple-report-ui-smoke")
    parser.add_argument("--keep", action="store_true", help="保留脚本创建的测试患者")
    args = parser.parse_args()

    screenshot_dir = Path(args.screenshot_dir) if args.screenshot_dir else None
    run_triple_report_smoke(args.frontend_url.rstrip("/"), args.backend_url.rstrip("/"), screenshot_dir, args.keep)
    print("[OK] triple report UI smoke passed")


if __name__ == "__main__":
    main()
