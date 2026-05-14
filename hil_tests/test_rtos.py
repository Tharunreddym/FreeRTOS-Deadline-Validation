import pytest
import os
from log_parser import parse_log, validate_producer_timing

LOG_FILE = os.environ.get("RTOS_LOG_FILE", "logs/rtos_uart_log.txt")


def load_log():
    if not os.path.exists(LOG_FILE):
        pytest.skip(f"Log file not found: {LOG_FILE}")
    with open(LOG_FILE, "r") as f:
        return f.read()


def test_TC001_scheduler_starts():
    log = load_log()
    results = parse_log(log)
    assert results["TC_001"] == "PASS", "Scheduler did not start"


def test_TC002_producer_timing():
    log = load_log()
    results = parse_log(log)
    passed, detail = validate_producer_timing(results["TC_002"])
    assert passed, f"Producer timing failed: {detail}"


def test_TC003_queue_transfer():
    log = load_log()
    results = parse_log(log)
    assert len(results["TC_003"]) > 0, "No queue transfers detected"


def test_TC004_normal_deadline():
    log = load_log()
    results = parse_log(log)
    assert results["TC_004_pass"] > 0, "No normal deadline passes found"


def test_TC005_monitor_detection():
    log = load_log()
    results = parse_log(log)
    assert results["TC_005"] == "PASS", "Monitor did not detect deadline miss"


def test_TC006_deadline_miss():
    log = load_log()
    results = parse_log(log)
    assert results["TC_006"] == "PASS", "DEADLINE_MISS not logged"


def test_TC007_recovery():
    log = load_log()
    results = parse_log(log)
    assert results["TC_007"] == "PASS", "RECOVERY not logged"


def test_TC008_log_completeness():
    log = load_log()
    results = parse_log(log)
    assert results["TC_008"] == "PASS", "UART log missing required fields"


if __name__ == "__main__":
    log = load_log()
    results = parse_log(log)
    timing_result = validate_producer_timing(results["TC_002"])

    from report_generator import generate_report
    generate_report(results, timing_result)