#!/usr/bin/env python3
"""
PreToolUse Write|Edit hook — simplify gate (lớp chặn).

Cặp với simplify_gate.py (PostToolUse tracker đếm LOC). Tracker chỉ in
SIMPLIFY_TRIGGERED rồi return — KHÔNG chặn được vì PostToolUse chạy sau tool.
Hook này là lớp PreToolUse: đọc state file của tracker, nếu ngưỡng đã bị vượt
(triggered=true) và simplify.threshold.enabled=true → exit 2, buộc xử lý
simplify trước khi cho phép sửa tiếp.

Mọi exception → log.error() + sys.exit(0) (fail-open có log).
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from ck_config_utils import get_section, get_sessions_dir
from hook_logger import HookLogger


def main() -> None:
    log = HookLogger("simplify-gate-pre")

    try:
        data = json.load(sys.stdin)
    except Exception as e:
        log.error(f"stdin parse failed → fail-open: {e}")
        sys.exit(0)

    # Bỏ qua sub-agent (tracker cũng bỏ qua agent_id)
    if data.get("agent_id"):
        sys.exit(0)

    # Kill switch — dùng chung khóa với tracker: simplify.threshold.enabled
    threshold = get_section("simplify").get("threshold", {})
    if not threshold.get("enabled", True):
        sys.exit(0)

    tool_input = data.get("tool_input", {}) or {}
    target = tool_input.get("file_path", "")
    # Chống bootstrap loop: không chặn thao tác lên session-data
    if "session-data" in target.replace("\\", "/"):
        sys.exit(0)

    session_id = data.get("session_id") or os.environ.get("CLAUDE_SESSION_ID", "default")
    try:
        sp = get_sessions_dir(data.get("cwd")) / f"simplify-tracker-{session_id}.json"
        if not sp.exists():
            sys.exit(0)
        state = json.loads(sp.read_text(encoding="utf-8-sig"))
    except Exception as e:
        log.error(f"tracker read failed → fail-open: {e}")
        sys.exit(0)

    if state.get("triggered"):
        sys.stderr.write(
            "[simplify-gate-pre] Chặn: ngưỡng simplify đã bị vượt trong session này. "
            "Chạy simplify (cook Step 3.S) trên các file đã sửa rồi mới tiếp tục, "
            "hoặc đặt simplify.threshold.enabled=false trong .ck.json.\n"
        )
        sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
