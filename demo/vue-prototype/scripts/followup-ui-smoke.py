#!/usr/bin/env python3
"""Browser smoke test for the report-to-follow-up workflow.

Prerequisites:
- Flask backend is running, default: http://127.0.0.1:5000
- Vue prototype dev server is running, default: http://127.0.0.1:5173
- Python Playwright package and a Chromium browser are available

The script creates a disposable finalized report via backend APIs, verifies
that the Vue UI can manually create the first follow-up task, submits the
public check-in form, confirms the B-side UI sees the reply, and cleans up.
It also validates that the follow tracking page keeps its three-column layout
visible and writes a screenshot for layout regressions.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


USERNAME = "smoke_admin"
PASSWORD = "Smoke@123456"


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.cookie_jar = CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))

    def request(self, method: str, path: str, payload: dict | None = None) -> dict:
        body = None
        headers = {"Content-Type": "application/json"}
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(f"{self.base_url}{path}", data=body, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw or "{}")
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            data = json.loads(raw or "{}")
            raise RuntimeError(data.get("message") or f"{method} {path} failed: HTTP {exc.code}") from exc
        if data.get("success") is False:
            raise RuntimeError(data.get("message") or f"{method} {path} failed")
        return data.get("data") if "data" in data else data

    def login(self) -> None:
        self.request("POST", "/api/auth/login", {"username": USERNAME, "password": PASSWORD})


def create_finalized_report(api: ApiClient) -> tuple[int, int, str]:
    suffix = str(int(time.time()))[-6:]
    patient = api.request(
        "POST",
        "/api/b/patients",
        {
            "name": f"UI联调患者{suffix}",
            "age": 46,
            "gender": "女",
            "phone": f"188{suffix}00",
            "nodule_type": "breast",
            "source_channel": "ui_smoke",
        },
    )
    patient_id = patient["id"]
    record = api.request(
        "POST",
        "/api/b/records",
        {
            "patient_id": patient_id,
            "age": 46,
            "height": 165,
            "weight": 58,
            "phone": patient["phone"],
            "birads_level": "4A",
            "nodule_size": "12x8mm",
            "nodule_quantity": "单发",
            "symptoms": ["疼痛"],
            "family_history": ["无"],
            "breast_discovery_date": "2026-05-01",
        },
    )
    report = api.request("POST", "/api/b/reports/generate", {"record_id": record["id"]})
    report_id = report["report_id"]
    api.request(
        "PUT",
        f"/api/b/reports/{report_id}/advice",
        {
            "content": "UI联调：人工编辑后的健康管理建议。",
            "sections": {
                "imaging_report_advice": "UI联调：影像建议。",
                "overall_assessment": "UI联调：总体评估。",
                "risk_assessment": "UI联调：风险提示。",
            },
        },
    )
    api.request("POST", f"/api/b/reports/{report_id}/advice/submit-review", {})
    api.request("POST", f"/api/b/reports/{report_id}/advice/approve", {})
    return patient_id, report_id, patient["name"]


def assert_follow_tracking_layout(page, screenshot_dir: Path | None = None) -> None:
    columns = {
        "患者列表": page.locator(".follow-patient-col").first,
        "患者聊天记录": page.locator(".tracking-list-col").first,
        "任务执行表": page.locator(".tracking-detail-col").first,
    }
    for name, locator in columns.items():
        expect(locator, f"{name}列不可见").to_be_visible(timeout=10000)
        box = locator.bounding_box()
        if not box or box["width"] < 180 or box["height"] < 300:
            raise AssertionError(f"{name}列尺寸异常：{box}")

    left = columns["患者列表"].bounding_box()
    middle = columns["患者聊天记录"].bounding_box()
    right = columns["任务执行表"].bounding_box()
    if not left or not middle or not right:
        raise AssertionError("执行跟踪列布局缺少可测量区域")
    if not (left["x"] < middle["x"] < right["x"]):
        raise AssertionError(f"执行跟踪三列顺序异常：left={left}, middle={middle}, right={right}")

    if screenshot_dir:
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot_dir / "follow-tracking-layout.png"), full_page=True)


def run_browser_smoke(frontend_url: str, patient_name: str, report_id: int, screenshot_dir: Path | None) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})

        page.goto(f"{frontend_url}/login", wait_until="networkidle")
        page.locator("#loginAccount").fill(USERNAME)
        page.locator("#loginPassword").fill(PASSWORD)
        page.get_by_role("button", name="登录").click()
        page.wait_for_url("**/analytics", timeout=10000)

        page.goto(f"{frontend_url}/patient", wait_until="networkidle")
        expect(page.get_by_text("患者管理").first).to_be_visible(timeout=10000)

        page.goto(f"{frontend_url}/patient?tab=review", wait_until="networkidle")
        expect(page.get_by_text("报告列表").or_(page.get_by_text("体检报告列表")).first).to_be_visible(timeout=10000)
        page.locator("input[placeholder*='姓名'], input[placeholder*='手机号']").first.fill(patient_name)
        expect(page.get_by_text(patient_name).first).to_be_visible(timeout=10000)

        page.goto(f"{frontend_url}/patient?tab=followup-plan", wait_until="networkidle")
        expect(page.get_by_text("随访任务下发").first).to_be_visible(timeout=10000)
        page.locator("input[placeholder*='姓名'], input[placeholder*='手机号']").first.fill(patient_name)
        expect(page.get_by_text(patient_name).first).to_be_visible(timeout=10000)

        page.goto(f"{frontend_url}/patient", wait_until="networkidle")
        search_inputs = page.locator("input[placeholder*='姓名'], input[placeholder*='手机号']")
        search_inputs.first.fill(patient_name)
        page.wait_for_timeout(800)
        page.get_by_role("button", name="查看").first.click(timeout=10000)
        page.wait_for_timeout(2500)

        full_create = page.get_by_role("button", name="创建首次随访任务")
        compact_create = page.get_by_role("button", name="建随访")
        if full_create.count():
            full_create.first.click()
        elif compact_create.count():
            compact_create.first.click()
        else:
            raise AssertionError("没有找到创建首次随访入口")

        expect(page.get_by_text("报告后首次随访").first).to_be_visible(timeout=10000)
        expect(page.get_by_text("已建随访").or_(page.get_by_text("已创建首次随访")).first).to_be_visible(timeout=10000)

        task = page.evaluate(
            """async (reportId) => {
                const res = await fetch(`/api/b/followup/tasks?report_id=${reportId}&source=report&per_page=1`, { credentials: 'include' });
                const data = await res.json();
                if (!data.success || !data.data.items.length) throw new Error('task not found');
                return data.data.items[0];
            }""",
            report_id,
        )
        page.goto(f"{frontend_url}{task['public_checkin_path']}", wait_until="networkidle")
        expect(page.get_by_text("健康管理任务").first).to_be_visible(timeout=10000)
        page.locator("textarea").first.fill("浏览器联调：睡眠正常，饮食清淡，步行20分钟，暂无不适。")
        page.get_by_role("button", name="提交打卡").click()
        expect(page.get_by_text("已完成本次打卡").or_(page.get_by_text("已提醒健康管理师关注")).first).to_be_visible(timeout=10000)

        page.goto(f"{frontend_url}/patient?tab=follow", wait_until="networkidle")
        expect(page.get_by_text("任务执行表").first).to_be_visible(timeout=10000)
        refresh = page.get_by_role("button", name="刷新")
        if refresh.count():
            refresh.first.click()
            page.wait_for_timeout(800)
        assert_follow_tracking_layout(page, screenshot_dir)

        page.goto(f"{frontend_url}/patient", wait_until="networkidle")
        page.locator("input[placeholder*='姓名'], input[placeholder*='手机号']").first.fill(patient_name)
        page.wait_for_timeout(800)
        page.get_by_role("button", name="查看").first.click(timeout=10000)
        expect(page.get_by_text("患者已回复").first).to_be_visible(timeout=10000)
        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend-url", default="http://127.0.0.1:5173")
    parser.add_argument("--backend-url", default="http://127.0.0.1:5000")
    parser.add_argument("--screenshot-dir", default="/tmp/followup-ui-smoke")
    parser.add_argument("--keep", action="store_true", help="保留脚本创建的测试患者")
    args = parser.parse_args()

    api = ApiClient(args.backend_url)
    patient_id = None
    try:
        api.login()
        patient_id, report_id, patient_name = create_finalized_report(api)
        screenshot_dir = Path(args.screenshot_dir) if args.screenshot_dir else None
        run_browser_smoke(args.frontend_url.rstrip("/"), patient_name, report_id, screenshot_dir)
        print("[OK] follow-up UI smoke passed")
    finally:
        if patient_id and not args.keep:
            try:
                api.request("DELETE", f"/api/b/patients/{patient_id}?type=b_end")
                print("[OK] cleaned smoke patient")
            except Exception as exc:
                print(f"[WARN] cleanup failed for patient {patient_id}: {exc}")


if __name__ == "__main__":
    main()
