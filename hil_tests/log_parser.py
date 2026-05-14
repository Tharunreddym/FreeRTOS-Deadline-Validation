import re

PRODUCER_PERIOD_MS = 100
PRODUCER_TOLERANCE_MS = 10
PROCESSOR_DEADLINE_MS = 80


def parse_log(log_text):
    results = {
        "TC_001": None,
        "TC_002": [],
        "TC_003": [],
        "TC_004_pass": 0,
        "TC_004_fail": 0,
        "TC_005": None,
        "TC_006": None,
        "TC_007": None,
        "TC_008": None,
    }

    for line in log_text.splitlines():
        if "RTOS_TC_001 PASS" in line or "Producer running" in line:
            results["TC_001"] = "PASS"

        match = re.search(r"Producer tick: sample=(\d+) tick=(\d+)", line)
        if match:
            results["TC_002"].append({
                "sample": int(match.group(1)),
                "tick": int(match.group(2))
            })

        if "RTOS_TC_003 PASS" in line:
            results["TC_003"].append("PASS")

        if "RTOS_TC_004 PASS" in line:
            results["TC_004_pass"] += 1

        if "RTOS_TC_004 FAIL" in line:
            results["TC_004_fail"] += 1

        if "RTOS_TC_005 PASS" in line:
            results["TC_005"] = "PASS"

        if "RTOS_TC_006 PASS" in line:
            results["TC_006"] = "PASS"

        if "RTOS_TC_007 PASS" in line:
            results["TC_007"] = "PASS"

    required_fields = [
        "RTOS_TC_002", "RTOS_TC_003",
        "RTOS_TC_004", "RTOS_TC_005", "RTOS_TC_006",
        "RTOS_TC_007", "MONITOR"
    ]
    all_present = all(field in log_text for field in required_fields)
    results["TC_008"] = "PASS" if all_present else "FAIL"

    return results


def validate_producer_timing(tc002_results):
    if len(tc002_results) < 2:
        return False, "Not enough samples"

    violations = 0
    total_checked = 0

    for i in range(1, len(tc002_results)):
        prev = tc002_results[i - 1]
        curr = tc002_results[i]

        if curr["sample"] != prev["sample"] + 1:
            continue

        interval = curr["tick"] - prev["tick"]

        if interval > 200 or interval < 0:
            continue

        total_checked += 1
        if abs(interval - PRODUCER_PERIOD_MS) > PRODUCER_TOLERANCE_MS:
            violations += 1

    if total_checked == 0:
        return False, "No valid intervals to check"

    if violations == 0:
        return True, f"All {total_checked} consecutive intervals within tolerance"
    else:
        return False, f"{violations} violations in {total_checked} checked intervals"