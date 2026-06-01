#!/usr/bin/env python3
"""Browser smoke test for patient record save operations.

Prerequisites:
- Flask backend is running, default: http://127.0.0.1:5000
- Vue prototype dev server is running, default: http://127.0.0.1:5173
- Python Playwright package and a Chromium browser are available

The script creates a disposable patient through the Vue record form, verifies
the saved patient and record through backend APIs, checks that the patient
appears in the patient queue, and cleans up the created patient.
"""

from __future__ import annotations

import argparse
import time
import urllib.parse
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from smoke_utils import api_fetch_data, browser_login, cleanup_patients_with_page, save_failure_screenshot


def field(page, label: str):
    return page.locator(".field, .form-field").filter(has_text=label).first


def fill_field(page, label: str, value: str) -> None:
    field(page, label).locator("input").first.fill(value)


def select_field(page, label: str, value: str) -> None:
    field(page, label).locator("select").first.select_option(label=value)


def find_patient(page, name: str):
    search = urllib.parse.quote(name)
    data = api_fetch_data(page, f"/api/b/patients?type=b_end&search={search}&per_page=20")
    for item in data.get("items", []):
        if item.get("name") == name:
            return item
    return None


def run_patient_save_smoke(frontend_url: str, screenshot_dir: Path | None) -> None:
    suffix = str(int(time.time()))[-6:]
    patient_name = f"UI建档验收{suffix}"
    patient_phone = f"177{suffix}88"
    patient_id = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            browser_login(page, frontend_url)

            page.goto(f"{frontend_url}/patient", wait_until="networkidle")
            expect(page.get_by_text("患者管理").first).to_be_visible(timeout=10000)
            page.get_by_role("button", name="+ 新建档案").click()
            expect(page.get_by_text("患者基础信息").first).to_be_visible(timeout=10000)

            fill_field(page, "姓名", patient_name)
            select_field(page, "性别", "女")
            fill_field(page, "出生日期", "1980-06-15")
            fill_field(page, "手机号", patient_phone)
            fill_field(page, "身高", "165")
            fill_field(page, "体重", "58")
            fill_field(page, "联系地址", "上海市浦东新区 UI 验收地址")
            select_field(page, "来源类型", "门诊")
            fill_field(page, "检查日期", "2026-05-28")

            breast_tag = page.get_by_role("button", name="乳腺结节").first
            expect(breast_tag).to_be_visible(timeout=10000)
            if "active" not in (breast_tag.get_attribute("class") or ""):
                breast_tag.click()
            fill_field(page, "结节发现时间", "2026-05-01")
            select_field(page, "BI-RADS分级", "4A")
            select_field(page, "数量", "单发")
            fill_field(page, "结节大小", "12.5")
            page.locator(".form-field", has_text="结节症状").get_by_role("button", name="乳房疼痛").click()
            page.locator(".form-field", has_text="家族史").get_by_role("button", name="无").click()

            page.get_by_role("button", name="保存档案").first.click()
            expect(page.get_by_text("档案已保存").first).to_be_visible(timeout=10000)
            expect(page.get_by_text("已保存").first).to_be_visible(timeout=10000)

            patient = find_patient(page, patient_name)
            if not patient:
                raise AssertionError("saved patient not found through API")
            patient_id = patient["id"]
            if patient.get("phone") != patient_phone:
                raise AssertionError(f"saved patient phone mismatch: {patient}")
            if patient.get("nodule_type") != "breast":
                raise AssertionError(f"saved patient nodule_type mismatch: {patient}")

            records = api_fetch_data(page, f"/api/b/patients/{patient_id}/records")
            if len(records) != 1:
                raise AssertionError(f"expected 1 saved record, got {len(records)}")
            record = records[0]
            if record.get("birads_level") != "4A":
                raise AssertionError(f"saved record birads_level mismatch: {record}")
            if str(record.get("nodule_size")) not in {"12.5", "12.5mm"}:
                raise AssertionError(f"saved record nodule_size mismatch: {record}")
            if "乳房疼痛" not in str(record.get("symptoms") or ""):
                raise AssertionError(f"saved record symptoms mismatch: {record}")

            page.goto(f"{frontend_url}/patient", wait_until="networkidle")
            page.locator("input[placeholder*='姓名'], input[placeholder*='手机号']").first.fill(patient_name)
            patient_row = page.locator("tbody tr", has_text=patient_name).first
            expect(patient_row).to_be_visible(timeout=10000)
            expect(patient_row.locator(".status-tag").first).to_be_visible(timeout=10000)

            if screenshot_dir:
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(screenshot_dir / "patient-save.png"), full_page=True)
        except Exception:
            save_failure_screenshot(page, screenshot_dir)
            raise
        finally:
            cleanup_patients_with_page(page, [patient_id] if patient_id else [], "patient-save")
            browser.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend-url", default="http://127.0.0.1:5173")
    parser.add_argument("--screenshot-dir", default="/tmp/patient-save-ui-smoke")
    args = parser.parse_args()

    screenshot_dir = Path(args.screenshot_dir) if args.screenshot_dir else None
    run_patient_save_smoke(args.frontend_url.rstrip("/"), screenshot_dir)
    print("[OK] patient save UI smoke passed")


if __name__ == "__main__":
    main()
