#!/usr/bin/env python3
"""Destructive-but-cleaned browser smoke for workflow save operations."""

from __future__ import annotations

import argparse
import time
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


def modal(page):
    return page.locator(".modal").last


def cancel_modal(page) -> None:
    modal(page).get_by_role("button", name="取消").click()


def api_fetch(page, path: str, method: str = "GET", payload: dict | None = None):
    return page.evaluate(
        """async ({ path, method, payload }) => {
            const res = await fetch(path, {
                method,
                credentials: 'include',
                headers: payload ? { 'Content-Type': 'application/json' } : {},
                body: payload ? JSON.stringify(payload) : undefined,
            });
            const data = await res.json().catch(() => ({}));
            if (!res.ok || data.success === false) {
                throw new Error(data.message || `${method} ${path} failed: ${res.status}`);
            }
            return data.data ?? data;
        }""",
        {"path": path, "method": method, "payload": payload},
    )


def find_template(page, name: str):
    templates = api_fetch(page, "/api/b/followup/templates?include_nodes=1")
    for tpl in templates or []:
        if tpl.get("name") == name:
            return tpl
    return None


def find_item(items, name: str):
    for item in items or []:
        if item.get("title") == name or item.get("name") == name:
            return item
    return None


def cleanup(page, created: dict[str, int | None]) -> None:
    for key, path in [
        ("node_id", "/api/b/followup/nodes/{id}"),
        ("template_id", "/api/b/followup/templates/{id}"),
        ("knowledge_id", "/api/b/followup/knowledge/{id}"),
        ("rule_id", "/api/b/followup/ai-rules/{id}"),
    ]:
        item_id = created.get(key)
        if not item_id:
            continue
        try:
            api_fetch(page, path.format(id=item_id), "DELETE")
        except Exception as exc:
            print(f"[WARN] cleanup failed for {key}={item_id}: {exc}")


def run_workflow_save_smoke(frontend_url: str, screenshot_dir: Path | None) -> None:
    suffix = str(int(time.time()))[-6:]
    template_name = f"UI保存验收模板{suffix}"
    node_name = f"UI保存验收节点{suffix}"
    knowledge_title = f"UI保存验收知识{suffix}"
    rule_name = f"UI保存验收规则{suffix}"
    created = {"template_id": None, "node_id": None, "knowledge_id": None, "rule_id": None}

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

            page.get_by_role("button", name="新建随访模板").click()
            page.locator("label:has-text('模板名称') input").fill(template_name)
            page.locator("label:has-text('适用结节') select").select_option("breast")
            page.locator("label:has-text('风险等级') select").select_option("mid")
            page.locator("label:has-text('状态') select").select_option("draft")
            page.get_by_role("button", name="保存模板").click()
            expect(page.get_by_text("模板已保存")).to_be_visible(timeout=10000)
            expect(page.get_by_text(template_name).first).to_be_visible(timeout=10000)
            tpl = find_template(page, template_name)
            if not tpl:
                raise AssertionError("saved template not found through API")
            created["template_id"] = tpl["id"]

            page.get_by_role("button", name="添加节点").click()
            expect(page.get_by_role("heading", name="新增任务节点")).to_be_visible(timeout=10000)
            modal(page).locator("label:has-text('节点名称') input").fill(node_name)
            modal(page).locator("label:has-text('任务类型') select").select_option("daily_checkin")
            modal(page).locator("label:has-text('患者动作') select").select_option("reply_text")
            modal(page).locator("label:has-text('AI动作') select").select_option("reply")
            modal(page).locator("label:has-text('推送内容') textarea").fill("请回复今日身体状态，本条用于 UI 保存验收。")
            modal(page).get_by_role("button", name="保存任务节点").click()
            expect(page.get_by_text("节点已保存")).to_be_visible(timeout=10000)
            expect(page.get_by_text(node_name).first).to_be_visible(timeout=10000)
            tpl = find_template(page, template_name)
            node = find_item(tpl.get("nodes", []) if tpl else [], node_name)
            if not node:
                raise AssertionError("saved node not found through API")
            created["node_id"] = node["id"]

            page.get_by_role("button", name="新增知识").first.click()
            expect(page.get_by_role("heading", name="新增知识")).to_be_visible(timeout=10000)
            modal(page).locator("label:has-text('标题') input").fill(knowledge_title)
            modal(page).locator("label:has-text('分类') select").select_option("diet")
            modal(page).locator("label:has-text('任务类型') select").select_option("daily_checkin")
            modal(page).locator("label:has-text('触发关键词') input").fill("UI保存验收")
            modal(page).locator("label:has-text('内容') textarea").fill("这是一条 UI 保存验收知识，测试后会自动清理。")
            modal(page).get_by_role("button", name="保存知识").click()
            expect(page.get_by_text("知识库已保存")).to_be_visible(timeout=10000)
            knowledge = api_fetch(page, "/api/b/followup/knowledge?per_page=200")
            knowledge_item = find_item(knowledge.get("items", []), knowledge_title)
            if not knowledge_item:
                raise AssertionError("saved knowledge not found through API")
            created["knowledge_id"] = knowledge_item["id"]
            page.locator("input[placeholder*='搜索知识标题']").fill(knowledge_title)
            expect(page.locator(".knowledge-item", has_text=knowledge_title).first).to_be_visible(timeout=10000)

            page.get_by_role("button", name="新增AI规则").first.click()
            expect(page.get_by_role("heading", name="新增AI规则")).to_be_visible(timeout=10000)
            modal(page).locator("label:has-text('规则名称') input").fill(rule_name)
            modal(page).locator("label:has-text('规则类型') select").select_option("no_reply")
            modal(page).locator("label:has-text('任务类型') select").select_option("daily_checkin")
            modal(page).locator("label:has-text('动作') select").select_option("manual_handoff")
            modal(page).locator("label:has-text('触发关键词') input").fill("UI保存验收")
            modal(page).locator("label:has-text('回复模板') textarea").fill("提醒健康管理师关注 UI 保存验收。")
            modal(page).get_by_role("button", name="保存规则").click()
            expect(page.get_by_text("AI规则已创建")).to_be_visible(timeout=10000)
            rules = api_fetch(page, "/api/b/followup/ai-rules")
            rule = find_item(rules, rule_name)
            if not rule:
                raise AssertionError("saved AI rule not found through API")
            created["rule_id"] = rule["id"]
            expect(page.locator(".rule-item", has_text=rule_name).first).to_be_visible(timeout=10000)

            if screenshot_dir:
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(screenshot_dir / "workflow-save.png"), full_page=True)
        except Exception:
            save_failure_screenshot(page, screenshot_dir)
            raise
        finally:
            cleanup(page, created)
            browser.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend-url", default="http://127.0.0.1:5173")
    parser.add_argument("--screenshot-dir", default="/tmp/followup-workflow-save-ui-smoke")
    args = parser.parse_args()

    screenshot_dir = Path(args.screenshot_dir) if args.screenshot_dir else None
    run_workflow_save_smoke(args.frontend_url.rstrip("/"), screenshot_dir)
    print("[OK] follow-up workflow save UI smoke passed")


if __name__ == "__main__":
    main()
