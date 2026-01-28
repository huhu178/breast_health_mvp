"""
项目一致性体检脚本（静态检查）

用途：
1) 快速检查 7 类结节（breast/lung/thyroid/breast_lung/breast_thyroid/lung_thyroid/triple）
   在前端入口、后端模板映射、提示词映射中是否齐全
2) 输出缺失项清单，便于逐条补齐

运行：
  python backend/scripts/audit_nodule_consistency.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_VIEWS = PROJECT_ROOT / "frontend" / "vue-app" / "src" / "views"
FRONTEND_TEMPLATES = PROJECT_ROOT / "frontend" / "templates" / "reports"
BACKEND_REPORT_MANAGER = PROJECT_ROOT / "backend" / "utils" / "report_manager.py"
BACKEND_PROMPT_CONFIG = PROJECT_ROOT / "backend" / "prompt_config.py"
FRONTEND_PATIENTS_VIEW = PROJECT_ROOT / "frontend" / "vue-app" / "src" / "views" / "PatientsView.vue"
FRONTEND_PATIENT_DETAIL = PROJECT_ROOT / "frontend" / "vue-app" / "src" / "views" / "PatientDetailView.vue"


NODULE_TYPES = [
    "breast",
    "lung",
    "thyroid",
    "breast_lung",
    "breast_thyroid",
    "lung_thyroid",
    "triple",
]


@dataclass
class Finding:
    kind: str
    ok: bool
    detail: str


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_template_mapping_keys(report_manager_src: str) -> set[str]:
    # 粗略从 TEMPLATE_MAPPING = { 'breast': '...', ... } 抓 key
    # 允许单双引号
    m = re.search(r"TEMPLATE_MAPPING\s*=\s*\{([\s\S]*?)\}\s*", report_manager_src)
    if not m:
        return set()
    body = m.group(1)
    return set(re.findall(r"['\"]([a-z_]+)['\"]\s*:\s*['\"][^'\"]+['\"]", body))


def _extract_prompts_keys(prompt_config_src: str) -> set[str]:
    m = re.search(r"PROMPTS\s*=\s*\{([\s\S]*?)\n\}\s*\n", prompt_config_src)
    if not m:
        return set()
    body = m.group(1)
    # 顶层 key： 'breast': { ... }
    return set(re.findall(r"^\s*['\"]([a-z_]+)['\"]\s*:\s*\{", body, flags=re.MULTILINE))


def _check_frontend_views_exist() -> list[Finding]:
    # 仅检查关键表单视图是否存在（与 PatientsView/PatientDetailView 的 routeMap 对齐）
    expected = {
        "breast": "RecordFormView_New.vue",
        "lung": "LungRecordFormView.vue",
        "thyroid": "ThyroidRecordFormView.vue",
        "breast_lung": "BreastLungFormView.vue",
        "breast_thyroid": "BreastThyroidFormView.vue",
        "lung_thyroid": "ThyroidLungFormView.vue",  # 页面文件名是 ThyroidLungFormView，但类型是 lung_thyroid
        "triple": "TripleNoduleFormView.vue",
    }
    findings: list[Finding] = []
    for k, filename in expected.items():
        exists = (FRONTEND_VIEWS / filename).exists()
        findings.append(
            Finding(
                kind="frontend.view",
                ok=exists,
                detail=f"{k}: {filename} {'OK' if exists else 'MISSING'}",
            )
        )
    return findings


def _check_frontend_route_maps() -> list[Finding]:
    findings: list[Finding] = []
    src_patients = _read_text(FRONTEND_PATIENTS_VIEW)
    src_detail = _read_text(FRONTEND_PATIENT_DETAIL)

    for t in NODULE_TYPES:
        # routeMap key 出现即可（静态检查）
        in_patients = t in src_patients
        in_detail = t in src_detail
        findings.append(
            Finding(
                kind="frontend.routeMap",
                ok=in_patients and in_detail,
                detail=f"{t}: PatientsView={'OK' if in_patients else 'MISSING'}, PatientDetailView={'OK' if in_detail else 'MISSING'}",
            )
        )
    return findings


def _check_report_templates_exist() -> list[Finding]:
    findings: list[Finding] = []
    # report_manager 中模板映射指向 templates/reports/...，我们直接检查文件是否存在
    report_manager_src = _read_text(BACKEND_REPORT_MANAGER)
    mapping = _extract_template_mapping_keys(report_manager_src)
    for t in NODULE_TYPES:
        ok = t in mapping
        findings.append(Finding(kind="backend.templateMappingKey", ok=ok, detail=f"{t}: {'OK' if ok else 'MISSING'}"))

    # 额外检查 templates/reports/*_report.html 是否存在
    expected_files = {
        "breast": "breast_report.html",
        "lung": "lung_report.html",
        "thyroid": "thyroid_report.html",
        "breast_lung": "breast_lung_report.html",
        "breast_thyroid": "breast_thyroid_report.html",
        "lung_thyroid": "lung_thyroid_report.html",
        "triple": "triple_report.html",
    }
    for t, fn in expected_files.items():
        exists = (FRONTEND_TEMPLATES / fn).exists()
        findings.append(Finding(kind="backend.reportTemplateFile", ok=exists, detail=f"{t}: {fn} {'OK' if exists else 'MISSING'}"))

    return findings


def _check_prompt_templates() -> list[Finding]:
    src = _read_text(BACKEND_PROMPT_CONFIG)
    prompt_keys = _extract_prompts_keys(src)
    findings: list[Finding] = []
    for t in NODULE_TYPES:
        ok = t in prompt_keys
        findings.append(Finding(kind="backend.promptsKey", ok=ok, detail=f"{t}: {'OK' if ok else 'MISSING'}"))
    return findings


def main() -> int:
    findings: list[Finding] = []

    # 基础路径存在性
    for p in [FRONTEND_VIEWS, FRONTEND_TEMPLATES, BACKEND_REPORT_MANAGER, BACKEND_PROMPT_CONFIG]:
        findings.append(Finding(kind="path.exists", ok=p.exists(), detail=str(p)))

    if not all(f.ok for f in findings if f.kind == "path.exists"):
        for f in findings:
            if f.kind == "path.exists" and not f.ok:
                print(f"[FATAL] 缺失路径：{f.detail}")
        return 2

    findings.extend(_check_frontend_views_exist())
    findings.extend(_check_frontend_route_maps())
    findings.extend(_check_report_templates_exist())
    findings.extend(_check_prompt_templates())

    ok_count = sum(1 for f in findings if f.ok)
    fail = [f for f in findings if not f.ok]

    print("\n========== Nodule Consistency Audit ==========")
    print(f"Project: {PROJECT_ROOT}")
    print(f"Checks: {len(findings)} | OK: {ok_count} | FAIL: {len(fail)}")

    if fail:
        print("\n---- FAIL ----")
        for f in fail:
            print(f"[{f.kind}] {f.detail}")

    print("\n---- OK (sample) ----")
    for f in findings[:10]:
        print(f"[{f.kind}] {f.detail} -> {'OK' if f.ok else 'FAIL'}")

    print("\n建议：先修复 FAIL 项，再按结节类型跑一遍手工冒烟流程（建患者→建档案→生成报告→审核编辑→覆盖发布→导出/删除）。")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())







