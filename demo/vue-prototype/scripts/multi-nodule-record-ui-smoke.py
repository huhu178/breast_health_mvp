#!/usr/bin/env python3
"""Browser smoke test for multi-nodule patient record saves."""

from __future__ import annotations

import argparse
import time
import urllib.parse
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from smoke_utils import api_fetch_data, browser_login, cleanup_patients_with_page, save_failure_screenshot


CASES = [
    {
        "label": "肺+乳",
        "expected_nodule_type": "breast_lung",
        "organs": ["lung", "breast"],
    },
    {
        "label": "甲+乳",
        "expected_nodule_type": "breast_thyroid",
        "organs": ["thyroid", "breast"],
    },
    {
        "label": "肺+甲",
        "expected_nodule_type": "lung_thyroid",
        "organs": ["lung", "thyroid"],
    },
    {
        "label": "三合并",
        "expected_nodule_type": "triple",
        "organs": ["lung", "thyroid", "breast"],
    },
]


def base_field(page, label: str):
    return page.locator(".field").filter(has_text=label).first


def nodule_section(page, title: str):
    return page.locator(".nodule-mini").filter(has_text=title).first


def section_field(section, label: str):
    return section.locator(".form-field").filter(has_text=label).first


def fill_base(page, label: str, value: str) -> None:
    base_field(page, label).locator("input").first.fill(value)


def select_base(page, label: str, value: str) -> None:
    base_field(page, label).locator("select").first.select_option(label=value)


def fill_section(section, label: str, value: str) -> None:
    section_field(section, label).locator("input").first.fill(value)


def select_section(section, label: str, value: str) -> None:
    section_field(section, label).locator("select").first.select_option(label=value)


def click_section_tag(section, field_label: str, tag_name: str) -> None:
    section_field(section, field_label).get_by_role("button", name=tag_name).click()


def find_patient(page, name: str):
    search = urllib.parse.quote(name)
    data = api_fetch_data(page, f"/api/b/patients?type=b_end&search={search}&per_page=20")
    for item in data.get("items", []):
        if item.get("name") == name:
            return item
    return None


def fill_lung(page) -> None:
    section = nodule_section(page, "肺部结节")
    expect(section).to_be_visible(timeout=10000)
    fill_section(section, "结节发现时间", "2026-05-01")
    select_section(section, "Lung-RADS分级", "4A")
    select_section(section, "数量", "单发")
    fill_section(section, "结节大小", "8.5")
    click_section_tag(section, "肺部症状", "咳嗽")
    click_section_tag(section, "肺部家族史", "无")


def fill_thyroid(page) -> None:
    section = nodule_section(page, "甲状腺结节")
    expect(section).to_be_visible(timeout=10000)
    fill_section(section, "结节发现时间", "2026-05-02")
    select_section(section, "TI-RADS分级", "4A")
    select_section(section, "数量", "单发")
    fill_section(section, "结节大小", "6.2")
    click_section_tag(section, "结节症状", "颈部肿块")
    click_section_tag(section, "甲状腺家族史", "无")


def fill_breast(page) -> None:
    section = nodule_section(page, "乳腺结节")
    expect(section).to_be_visible(timeout=10000)
    fill_section(section, "结节发现时间", "2026-05-03")
    select_section(section, "BI-RADS分级", "4A")
    select_section(section, "数量", "单发")
    fill_section(section, "结节大小", "12.5")
    click_section_tag(section, "结节症状", "乳房疼痛")
    click_section_tag(section, "家族史", "无")


def fill_case_organs(page, organs: list[str]) -> None:
    if "lung" in organs:
        fill_lung(page)
    if "thyroid" in organs:
        fill_thyroid(page)
    if "breast" in organs:
        fill_breast(page)


def assert_record(case: dict, patient: dict, record: dict) -> None:
    if patient.get("nodule_type") != case["expected_nodule_type"]:
        raise AssertionError(f"nodule_type mismatch for {case['label']}: {patient}")
    organs = set(case["organs"])
    if "lung" in organs:
        if record.get("lung_rads_level") != "4A":
            raise AssertionError(f"lung_rads_level mismatch: {record}")
        if str(record.get("lung_nodule_size")) not in {"8.5", "8.5mm"}:
            raise AssertionError(f"lung_nodule_size mismatch: {record}")
    if "thyroid" in organs:
        if record.get("tirads_level") != "4A":
            raise AssertionError(f"tirads_level mismatch: {record}")
        if str(record.get("thyroid_nodule_size")) not in {"6.2", "6.2mm"}:
            raise AssertionError(f"thyroid_nodule_size mismatch: {record}")
    if "breast" in organs:
        if record.get("birads_level") != "4A":
            raise AssertionError(f"birads_level mismatch: {record}")
        if str(record.get("nodule_size")) not in {"12.5", "12.5mm"}:
            raise AssertionError(f"nodule_size mismatch: {record}")


def save_one_case(page, frontend_url: str, case: dict, case_index: int, screenshot_dir: Path | None) -> int:
    suffix = f"{str(int(time.time()))[-5:]}{case_index}"
    patient_name = f"UI多结节{case['label']}{suffix}"
    patient_phone = f"173{suffix}33"

    page.goto(f"{frontend_url}/patient", wait_until="networkidle")
    expect(page.get_by_text("患者管理").first).to_be_visible(timeout=10000)
    page.get_by_role("button", name="+ 新建档案").click()
    expect(page.get_by_text("患者基础信息").first).to_be_visible(timeout=10000)

    fill_base(page, "姓名", patient_name)
    select_base(page, "性别", "女")
    fill_base(page, "出生日期", "1980-06-15")
    fill_base(page, "手机号", patient_phone)
    fill_base(page, "身高", "165")
    fill_base(page, "体重", "58")
    fill_base(page, "联系地址", "上海市浦东新区 UI 多结节验收地址")
    select_base(page, "来源类型", "门诊")
    fill_base(page, "检查日期", "2026-05-28")

    page.get_by_role("button", name=case["label"]).click()
    fill_case_organs(page, case["organs"])

    page.get_by_role("button", name="保存档案").first.click()
    expect(page.get_by_text("档案已保存").first).to_be_visible(timeout=10000)

    patient = find_patient(page, patient_name)
    if not patient:
        raise AssertionError(f"saved patient not found for {case['label']}")
    records = api_fetch_data(page, f"/api/b/patients/{patient['id']}/records")
    if len(records) != 1:
        raise AssertionError(f"expected 1 saved record for {case['label']}, got {len(records)}")
    assert_record(case, patient, records[0])

    page.goto(f"{frontend_url}/patient", wait_until="networkidle")
    page.locator("input[placeholder*='姓名'], input[placeholder*='手机号']").first.fill(patient_name)
    patient_row = page.locator("tbody tr", has_text=patient_name).first
    expect(patient_row).to_be_visible(timeout=10000)
    expect(patient_row.get_by_text(patient_name).first).to_be_visible(timeout=10000)

    if screenshot_dir:
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot_dir / f"multi-nodule-{case['expected_nodule_type']}.png"), full_page=True)
    return patient["id"]


def run_multi_nodule_smoke(frontend_url: str, screenshot_dir: Path | None) -> None:
    patient_ids: list[int] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            browser_login(page, frontend_url)

            for index, case in enumerate(CASES):
                patient_ids.append(save_one_case(page, frontend_url, case, index, screenshot_dir))
                print(f"[OK] multi-nodule save passed: {case['label']}")
        except Exception:
            save_failure_screenshot(page, screenshot_dir)
            raise
        finally:
            cleanup_patients_with_page(page, patient_ids, "multi-nodule")
            browser.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend-url", default="http://127.0.0.1:5173")
    parser.add_argument("--screenshot-dir", default="/tmp/multi-nodule-record-ui-smoke")
    args = parser.parse_args()

    screenshot_dir = Path(args.screenshot_dir) if args.screenshot_dir else None
    run_multi_nodule_smoke(args.frontend_url.rstrip("/"), screenshot_dir)
    print("[OK] multi-nodule record UI smoke passed")


if __name__ == "__main__":
    main()
