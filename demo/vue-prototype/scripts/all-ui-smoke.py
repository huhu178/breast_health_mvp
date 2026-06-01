#!/usr/bin/env python3
"""Run all browser UI smoke checks for the Vue prototype."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_step(label: str, command: list[str]) -> None:
    print(f"[RUN] {label}")
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend-url", default="http://127.0.0.1:5173")
    parser.add_argument("--backend-url", default="http://127.0.0.1:5000")
    parser.add_argument("--screenshot-root", default="/tmp/vue-prototype-ui-smoke")
    args = parser.parse_args()

    root = Path(args.screenshot_root)
    run_step("patient record save", [
        sys.executable,
        "scripts/patient-save-ui-smoke.py",
        "--frontend-url",
        args.frontend_url,
        "--screenshot-dir",
        str(root / "patient-save"),
    ])
    run_step("report audit", [
        sys.executable,
        "scripts/report-audit-ui-smoke.py",
        "--frontend-url",
        args.frontend_url,
        "--backend-url",
        args.backend_url,
        "--screenshot-dir",
        str(root / "report-audit"),
    ])
    run_step("imaging upload", [
        sys.executable,
        "scripts/imaging-upload-ui-smoke.py",
        "--frontend-url",
        args.frontend_url,
        "--backend-url",
        args.backend_url,
        "--screenshot-dir",
        str(root / "imaging-upload"),
    ])
    run_step("audit follow-up", [
        sys.executable,
        "scripts/audit-followup-ui-smoke.py",
        "--frontend-url",
        args.frontend_url,
        "--backend-url",
        args.backend_url,
        "--screenshot-dir",
        str(root / "audit-followup"),
    ])
    run_step("multi-nodule record save", [
        sys.executable,
        "scripts/multi-nodule-record-ui-smoke.py",
        "--frontend-url",
        args.frontend_url,
        "--screenshot-dir",
        str(root / "multi-nodule"),
    ])
    run_step("triple report audit", [
        sys.executable,
        "scripts/triple-report-ui-smoke.py",
        "--frontend-url",
        args.frontend_url,
        "--backend-url",
        args.backend_url,
        "--screenshot-dir",
        str(root / "triple-report"),
    ])
    run_step("follow-up workflow", [
        sys.executable,
        "scripts/workflow-ui-smoke.py",
        "--frontend-url",
        args.frontend_url,
        "--screenshot-dir",
        str(root / "workflow"),
    ])
    run_step("follow-up workflow save", [
        sys.executable,
        "scripts/workflow-save-ui-smoke.py",
        "--frontend-url",
        args.frontend_url,
        "--screenshot-dir",
        str(root / "workflow-save"),
    ])
    run_step("report-to-follow-up", [
        sys.executable,
        "scripts/followup-ui-smoke.py",
        "--frontend-url",
        args.frontend_url,
        "--backend-url",
        args.backend_url,
        "--screenshot-dir",
        str(root / "followup"),
    ])
    print("[OK] all UI smoke checks passed")


if __name__ == "__main__":
    main()
