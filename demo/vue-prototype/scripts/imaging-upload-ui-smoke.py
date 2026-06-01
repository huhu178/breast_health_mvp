#!/usr/bin/env python3
"""Browser smoke test for imaging report upload and deletion."""

from __future__ import annotations

import argparse
import base64
import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from smoke_utils import (
    ApiClient,
    api_fetch_data,
    browser_login,
    cleanup_patient,
    create_breast_patient_record,
    save_failure_screenshot,
)

TEST_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


def run_imaging_upload_smoke(frontend_url: str, backend_url: str, screenshot_dir: Path | None, keep: bool) -> None:
    api = ApiClient(backend_url)
    patient_id = None
    upload_name = f"ui-imaging-smoke-{int(time.time())}.png"
    upload_path = Path("/tmp") / upload_name
    upload_path.write_bytes(TEST_PNG)

    try:
        api.login()
        patient_id, record_id, patient_name = create_breast_patient_record(api, "UI影像验收", "175")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            try:
                browser_login(page, frontend_url)

                page.goto(f"{frontend_url}/patient", wait_until="networkidle")
                expect(page.get_by_text("患者管理").first).to_be_visible(timeout=10000)
                page.locator("input[placeholder*='姓名'], input[placeholder*='手机号']").first.fill(patient_name)
                patient_row = page.locator("tbody tr", has_text=patient_name).first
                expect(patient_row).to_be_visible(timeout=10000)
                patient_row.get_by_role("button", name="查看").click()

                workspace = page.locator(".patient-workspace").first
                expect(workspace.get_by_text("影像报告").first).to_be_visible(timeout=10000)
                workspace.locator("input[type='file']").first.set_input_files(str(upload_path))
                expect(workspace.get_by_text(upload_name).first).to_be_visible(timeout=10000)

                imaging = api_fetch_data(page, f"/api/b/records/{record_id}/imaging-reports")
                items = imaging.get("items", [])
                matched = [item for item in items if item.get("file_name") == upload_name]
                if len(matched) != 1:
                    raise AssertionError(f"expected uploaded imaging report, got {items}")
                imaging_id = matched[0]["id"]
                if matched[0].get("file_type") != "image":
                    raise AssertionError(f"expected image file type, got {matched[0]}")

                file_row = workspace.locator(".file-row", has_text=upload_name).first
                file_row.get_by_role("button", name="删除").click()
                expect(workspace.locator(".file-row", has_text=upload_name).first).not_to_be_visible(timeout=10000)

                imaging_after = api_fetch_data(page, f"/api/b/records/{record_id}/imaging-reports")
                remaining = [item for item in imaging_after.get("items", []) if item.get("id") == imaging_id]
                if remaining:
                    raise AssertionError(f"expected imaging report deleted, got {remaining}")

                if screenshot_dir:
                    screenshot_dir.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(screenshot_dir / "imaging-upload.png"), full_page=True)
            except Exception:
                save_failure_screenshot(page, screenshot_dir)
                raise
            finally:
                browser.close()
    finally:
        cleanup_patient(api, patient_id, keep, "imaging-upload")
        try:
            upload_path.unlink()
        except FileNotFoundError:
            pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend-url", default="http://127.0.0.1:5173")
    parser.add_argument("--backend-url", default="http://127.0.0.1:5000")
    parser.add_argument("--screenshot-dir", default="/tmp/imaging-upload-ui-smoke")
    parser.add_argument("--keep", action="store_true", help="保留脚本创建的测试患者")
    args = parser.parse_args()

    screenshot_dir = Path(args.screenshot_dir) if args.screenshot_dir else None
    run_imaging_upload_smoke(args.frontend_url.rstrip("/"), args.backend_url.rstrip("/"), screenshot_dir, args.keep)
    print("[OK] imaging upload UI smoke passed")


if __name__ == "__main__":
    main()
