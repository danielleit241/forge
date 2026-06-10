#!/usr/bin/env python3
"""
PreToolUse Write|Edit|Bash|Agent hook — workflow artifact gate.

Chặn (exit 2) khi ck:cook đang ở phase cần artifact nhưng thiếu/sai một trong
5 artifact JSON của pipeline. Đây là guard CỨNG, thay cho "hard gate" text trong
SKILL.md mà model có thể trôi qua.

Cơ chế chặn: sys.exit(2) + stderr (xác nhận hoạt động qua privacy_block.py).
PostToolUse KHÔNG chặn được tool — gate phải là PreToolUse.

Lớp guard (theo thứ tự, fail-open ở mọi điểm không chắc chắn):
  1. Kill switch: .ck.json artifactGate.enabled=false → exit 0 ngay.
  2. Skip session-data writes → exit 0 (chống bootstrap loop: cook ghi marker
     cook-active.json bằng Write, không được tự kích hoạt gate).
  3. Cook-active flag: không có session-data/cook-active.json hoặc phase_active
     != true → exit 0 (luồng bình thường của user, KHÔNG phải lỗi).
  4. Kiểm 5 artifact trong plan_dir → thiếu/sai schema → exit 2.

Mọi exception → log.error() + sys.exit(0) (fail-open có log, KHÔNG exit 2 —
tránh chặn nhầm tool không liên quan khi chính hook lỗi).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from ck_config_utils import is_enabled, get_sessions_dir
from hook_logger import HookLogger

REQUIRED_ARTIFACTS = [
    "context-snippets.json",
    "risk-gate.json",
    "verification.json",
    "review-decision.json",
    "adversarial-validation.json",
]


def _target_path(tool_name: str, tool_input: dict) -> str:
    """Đường dẫn mà tool định ghi/chạy — dùng để skip session-data."""
    if tool_name in ("Write", "Edit"):
        return tool_input.get("file_path", "")
    if tool_name == "Bash":
        return tool_input.get("command", "")
    return ""


def main() -> None:
    log = HookLogger("artifact-gate")

    # Lớp 0 — parse stdin; lỗi parse → fail-open
    try:
        data = json.load(sys.stdin)
    except Exception as e:
        log.error(f"stdin parse failed → fail-open: {e}")
        sys.exit(0)

    # Lớp 1 — kill switch (mặc định false trong .ck.json)
    if not is_enabled("artifactGate"):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {}) or {}

    # Lớp 2a — gate chỉ có nghĩa với thao tác GHI FILE/chạy lệnh tạo artifact.
    # Agent (spawn sub-agent) không ghi gì trực tiếp → không bao giờ chặn,
    # nếu không sẽ chặn nhầm mọi code-reviewer/debugger/... khi cook active.
    if tool_name not in ("Write", "Edit", "Bash"):
        sys.exit(0)

    # Lớp 2b — skip mọi thao tác chạm session-data (chống bootstrap loop)
    target = _target_path(tool_name, tool_input)
    if "session-data" in target.replace("\\", "/"):
        sys.exit(0)

    # Lớp 3 — chỉ kích hoạt khi có bằng chứng cook đang ở phase cần artifact
    try:
        flag_path = get_sessions_dir(data.get("cwd")) / "cook-active.json"
        if not flag_path.exists():
            sys.exit(0)
        flag = json.loads(flag_path.read_text(encoding="utf-8-sig"))
    except Exception as e:
        log.error(f"cook-active read failed → fail-open: {e}")
        sys.exit(0)

    if not flag.get("phase_active"):
        sys.exit(0)

    plan_dir = flag.get("plan_dir", "")
    if not plan_dir or not Path(plan_dir).is_dir():
        log.error(f"plan_dir invalid in cook-active.json → fail-open: {plan_dir!r}")
        sys.exit(0)

    # Lớp 4 — kiểm 5 artifact
    pd = Path(plan_dir)
    missing = []
    invalid = []
    for name in REQUIRED_ARTIFACTS:
        f = pd / name
        if not f.exists():
            missing.append(name)
            continue
        try:
            json.loads(f.read_text(encoding="utf-8-sig"))
        except Exception:
            invalid.append(name)

    if missing or invalid:
        parts = []
        if missing:
            parts.append("thiếu: " + ", ".join(missing))
        if invalid:
            parts.append("schema sai (không phải JSON hợp lệ): " + ", ".join(invalid))
        sys.stderr.write(
            f"[artifact-gate] Chặn {tool_name}: pipeline cook đang active nhưng "
            f"artifact chưa đủ trong {plan_dir} — " + "; ".join(parts) + ".\n"
            f"Hoàn tất bước sinh artifact của phase hiện tại trước khi tiếp tục, "
            f"hoặc đặt artifactGate.enabled=false trong .ck.json để vô hiệu gate."
        )
        sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Backstop: hook không bao giờ được chặn do lỗi nội bộ của chính nó
        sys.exit(0)
