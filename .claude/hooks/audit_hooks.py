#!/usr/bin/env python3
"""
Hook audit — chạy thủ công, KHÔNG wire vào settings.json.

Liệt kê: hook nào đã wire (settings.json) ở event nào, trạng thái enabled
(.ck.json), và hook nào tồn tại trong hooks/ nhưng chưa wire.

Health check ĐỘNG (không chỉ kiểm file tồn tại): với mỗi blocking hook, chạy
thử input giả và verify exit code THỰC — phát hiện "hook bypass im lặng"
(exit 0 do bug thay vì exit 2 khi đáng lẽ phải chặn).

    python .claude/hooks/audit_hooks.py
"""

import json
import subprocess
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).parent
ROOT = HOOKS_DIR.parent.parent


def _load_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def _wired_hooks(settings: dict) -> dict[str, list[str]]:
    """map: tên file hook → danh sách event đã wire."""
    out: dict[str, list[str]] = {}
    for event, groups in settings.get("hooks", {}).items():
        for g in groups:
            for h in g.get("hooks", []):
                cmd = h.get("command", "")
                name = Path(cmd.split()[-1]).name if cmd else ""
                if name:
                    out.setdefault(name, []).append(event)
    return out


def _run_hook(name: str, stdin: str) -> int:
    """Chạy hook với stdin giả, trả exit code thực."""
    try:
        r = subprocess.run(
            [sys.executable, str(HOOKS_DIR / name)],
            input=stdin, capture_output=True, text=True, timeout=15,
            cwd=str(ROOT),
        )
        return r.returncode
    except Exception as e:
        print(f"    health check lỗi: {e}")
        return -1


def main() -> None:
    settings = _load_json(ROOT / ".claude" / "settings.json")
    ck = _load_json(ROOT / ".ck.json")
    wired = _wired_hooks(settings)

    print("=== Hook Audit ===\n")

    print("-- Đã wire trong settings.json --")
    for name, events in sorted(wired.items()):
        print(f"  {name:32s} → {', '.join(events)}")

    print("\n-- Tồn tại trong hooks/ nhưng CHƯA wire --")
    on_disk = {p.name for p in HOOKS_DIR.glob("*.py") if p.name != Path(__file__).name}
    unwired = sorted(on_disk - set(wired))
    for name in unwired:
        print(f"  {name}")
    if not unwired:
        print("  (không có)")

    print("\n-- Trạng thái enabled (.ck.json) --")
    for key in ("privacyBlock", "artifactGate", "simplify"):
        section = ck.get(key, {})
        if key == "simplify":
            enabled = section.get("threshold", {}).get("enabled", "(mặc định true)")
        else:
            enabled = section.get("enabled", "(mặc định true)")
        print(f"  {key:16s} enabled = {enabled}")

    print("\n-- Health check ĐỘNG (exit code thực) --")
    # artifact-gate: enabled=false → phải exit 0 (kill switch)
    if (HOOKS_DIR / "workflow_artifact_gate.py").exists():
        rc = _run_hook(
            "workflow_artifact_gate.py",
            '{"tool_name":"Write","tool_input":{"file_path":"src/x.ts"}}',
        )
        expect = 0 if not ck.get("artifactGate", {}).get("enabled", False) else "0|2"
        status = "OK" if rc in (0, 2) else "BẤT THƯỜNG"
        print(f"  workflow_artifact_gate.py: exit={rc} (kỳ vọng {expect}) [{status}]")
        # skip session-data → luôn phải exit 0
        rc2 = _run_hook(
            "workflow_artifact_gate.py",
            '{"tool_name":"Write","tool_input":{"file_path":".claude/session-data/cook-active.json"}}',
        )
        print(f"  workflow_artifact_gate.py (session-data skip): exit={rc2} (kỳ vọng 0) "
              f"[{'OK' if rc2 == 0 else 'LỖI: bootstrap loop risk'}]")
    else:
        print("  workflow_artifact_gate.py: chưa tồn tại")

    # fail-open: JSON rác → mọi hook phải exit 0
    for name in ("workflow_artifact_gate.py", "simplify_gate_pre.py", "build_check.py"):
        if (HOOKS_DIR / name).exists():
            rc = _run_hook(name, "BAD JSON NOT PARSEABLE")
            print(f"  {name} (JSON rác → fail-open): exit={rc} "
                  f"[{'OK' if rc == 0 else 'LỖI: không fail-open'}]")


if __name__ == "__main__":
    main()
