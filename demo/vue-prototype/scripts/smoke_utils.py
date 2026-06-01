"""Shared helpers for Vue prototype browser smoke tests."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path


USERNAME = "smoke_admin"
PASSWORD = "Smoke@123456"


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.cookie_jar = CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))

    def request(self, method: str, path: str, payload: dict | None = None, expect_ok: bool = True) -> dict:
        body = None
        headers = {"Content-Type": "application/json"}
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(f"{self.base_url}{path}", data=body, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw or "{}")
                status = resp.status
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            data = json.loads(raw or "{}")
            status = exc.code
        if expect_ok and (status >= 400 or data.get("success") is False):
            raise RuntimeError(data.get("message") or f"{method} {path} failed: HTTP {status}")
        if expect_ok:
            return data.get("data") if "data" in data else data
        return {"status": status, "body": data}

    def login(self) -> None:
        self.request("POST", "/api/auth/login", {"username": USERNAME, "password": PASSWORD})


def save_failure_screenshot(page, screenshot_dir: Path | None, name: str = "failure") -> None:
    if not screenshot_dir:
        return
    try:
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot_dir / f"{name}.png"), full_page=True)
    except Exception as exc:
        print(f"[WARN] failed to write failure screenshot: {exc}")


def browser_login(page, frontend_url: str) -> None:
    page.goto(f"{frontend_url}/login", wait_until="networkidle")
    page.locator("#loginAccount").fill(USERNAME)
    page.locator("#loginPassword").fill(PASSWORD)
    page.get_by_role("button", name="登录").click()
    page.wait_for_url("**/analytics", timeout=10000)


def api_fetch(page, path: str, method: str = "GET", payload: dict | None = None, expect_ok: bool = True):
    return page.evaluate(
        """async ({ path, method, payload, expectOk }) => {
            const res = await fetch(path, {
                method,
                credentials: 'include',
                headers: payload ? { 'Content-Type': 'application/json' } : {},
                body: payload ? JSON.stringify(payload) : undefined,
            });
            const data = await res.json().catch(() => ({}));
            if (expectOk && (!res.ok || data.success === false)) {
                throw new Error(data.message || `${method} ${path} failed: ${res.status}`);
            }
            return { status: res.status, body: data.data ?? data };
        }""",
        {"path": path, "method": method, "payload": payload, "expectOk": expect_ok},
    )


def api_fetch_data(page, path: str, method: str = "GET", payload: dict | None = None):
    return api_fetch(page, path, method, payload, expect_ok=True)["body"]


def cleanup_patient(api: ApiClient, patient_id: int | None, keep: bool, label: str) -> None:
    if keep or not patient_id:
        return
    try:
        api.request("DELETE", f"/api/b/patients/{patient_id}?type=b_end")
        print(f"[OK] cleaned {label} smoke patient")
    except Exception as exc:
        print(f"[WARN] cleanup failed for patient {patient_id}: {exc}")


def cleanup_patients_with_page(page, patient_ids: list[int], label: str) -> None:
    for patient_id in patient_ids:
        try:
            api_fetch_data(page, f"/api/b/patients/{patient_id}?type=b_end", "DELETE")
            print(f"[OK] cleaned {label} smoke patient {patient_id}")
        except Exception as exc:
            print(f"[WARN] cleanup failed for patient {patient_id}: {exc}")


def create_breast_patient_record(api: ApiClient, name_prefix: str, phone_prefix: str) -> tuple[int, int, str]:
    suffix = str(int(time.time()))[-6:]
    patient = api.request(
        "POST",
        "/api/b/patients",
        {
            "name": f"{name_prefix}{suffix}",
            "age": 46,
            "gender": "女",
            "phone": f"{phone_prefix}{suffix}",
            "nodule_type": "breast",
            "source_channel": "ui_smoke",
        },
    )
    record = api.request(
        "POST",
        f"/api/b/patients/{patient['id']}/records",
        {
            "patient_id": patient["id"],
            "age": 46,
            "height": 165,
            "weight": 58,
            "phone": patient["phone"],
            "birads_level": "4A",
            "nodule_size": "12x8mm",
            "nodule_quantity": "单发",
            "symptoms": "乳房疼痛",
            "family_history": "无",
            "breast_discovery_date": "2026-05-01",
        },
    )
    return patient["id"], record["id"], patient["name"]


def create_generated_breast_report(api: ApiClient, name_prefix: str, phone_prefix: str) -> tuple[int, int, str]:
    patient_id, record_id, patient_name = create_breast_patient_record(api, name_prefix, phone_prefix)
    report = api.request("POST", "/api/b/reports/generate", {"record_id": record_id})
    return patient_id, report["report_id"], patient_name


def create_triple_patient_record(api: ApiClient, name_prefix: str, phone_prefix: str) -> tuple[int, int, str]:
    suffix = str(int(time.time()))[-6:]
    patient = api.request(
        "POST",
        "/api/b/patients",
        {
            "name": f"{name_prefix}{suffix}",
            "age": 46,
            "gender": "女",
            "phone": f"{phone_prefix}{suffix}",
            "nodule_type": "triple",
            "source_channel": "ui_smoke",
        },
    )
    record = api.request(
        "POST",
        f"/api/b/patients/{patient['id']}/records",
        {
            "patient_id": patient["id"],
            "age": 46,
            "height": 165,
            "weight": 58,
            "phone": patient["phone"],
            "breast_discovery_date": "2026-05-01",
            "birads_level": "4A",
            "nodule_quantity": "单发",
            "nodule_size": "12.5",
            "symptoms": "乳房疼痛",
            "family_history": "无",
            "thyroid_discovery_date": "2026-05-02",
            "tirads_level": "4A",
            "thyroid_nodule_quantity": "单发",
            "thyroid_nodule_size": "6.2",
            "thyroid_symptoms": "颈部肿块",
            "thyroid_family_history": "无",
            "lung_discovery_date": "2026-05-03",
            "lung_rads_level": "4A",
            "lung_nodule_quantity": "单发",
            "lung_nodule_size": "8.5",
            "lung_symptoms": "咳嗽",
            "lung_family_history": "无",
        },
    )
    return patient["id"], record["id"], patient["name"]


def create_generated_triple_report(api: ApiClient, name_prefix: str, phone_prefix: str) -> tuple[int, int, str]:
    patient_id, record_id, patient_name = create_triple_patient_record(api, name_prefix, phone_prefix)
    report = api.request("POST", "/api/b/reports/generate", {"record_id": record_id})
    return patient_id, report["report_id"], patient_name
