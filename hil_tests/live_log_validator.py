import re
import argparse
from pathlib import Path


PRODUCER_PERIOD_MS = 100
PRODUCER_TOLERANCE_MS = 10
PROCESSOR_DEADLINE_MS = 80


def read_log(path: str) -> list[str]:
    log_path = Path(path)

    if not log_path.exists():
        raise FileNotFoundError(f"Log file not found: {log_path}")

    return log_path.read_text(encoding="utf-8", errors="ignore").splitlines()


def extract_producer_ticks(lines: list[str]) -> list[int]:
    ticks = []

    pattern = re.compile(r"Producer tick: sample=\d+ tick=(\d+)")

    for line in lines:
        match = pattern.search(line)
        if match:
            ticks.append(int(match.group(1)))

    return ticks


def check_scheduler_started(lines: list[str]) -> bool:
    return any("[RTOS_TC_001 PASS]" in line for line in lines)


def check_processor_received(lines: list[str]) -> bool:
    return any("[RTOS_TC_003 PASS]" in line for line in lines)


def check_processing_under_deadline(lines: list[str]) -> bool:
    pattern = re.compile(r"Processing done in (\d+) ms")

    for line in lines:
        match = pattern.search(line)
        if match:
            duration = int(match.group(1))
            if duration <= PROCESSOR_DEADLINE_MS:
                return True

    return False


def check_deadline_miss(lines: list[str]) -> bool:
    return any("[RTOS_TC_004 FAIL]" in line for line in lines)


def check_monitor_detected_miss(lines: list[str]) -> bool:
    return any("[RTOS_TC_005 PASS]" in line for line in lines)


def check_overload_detected(lines: list[str]) -> bool:
    return any("[RTOS_TC_006 PASS]" in line for line in lines)


def check_recovery(lines: list[str]) -> bool:
    return any("[RTOS_TC_007 PASS]" in line for line in lines)


def check_producer_period(ticks: list[int]) -> bool:
    if len(ticks) < 2:
        return False

    valid_periods = 0
    total_periods = 0

    for previous_tick, current_tick in zip(ticks, ticks[1:]):
        difference = current_tick - previous_tick

        # Ignore resets/restarts where tick goes backward.
        if difference <= 0:
            continue

        total_periods += 1

        lower_limit = PRODUCER_PERIOD_MS - PRODUCER_TOLERANCE_MS
        upper_limit = PRODUCER_PERIOD_MS + PRODUCER_TOLERANCE_MS

        if lower_limit <= difference <= upper_limit:
            valid_periods += 1

    if total_periods == 0:
        return False

    pass_ratio = valid_periods / total_periods

    return pass_ratio >= 0.90


def validate_log(lines: list[str]) -> dict[str, bool]:
    ticks = extract_producer_ticks(lines)

    results = {
        "RTOS_TC_001 Scheduler started": check_scheduler_started(lines),
        "RTOS_TC_002 Producer 100 ms timing": check_producer_period(ticks),
        "RTOS_TC_003 Processor received samples": check_processor_received(lines),
        "RTOS_TC_004 Processing under deadline": check_processing_under_deadline(lines),
        "RTOS_TC_004 Deadline miss under overload": check_deadline_miss(lines),
        "RTOS_TC_005 Monitor detected deadline miss": check_monitor_detected_miss(lines),
        "RTOS_TC_006 Overload deadline miss detected": check_overload_detected(lines),
        "RTOS_TC_007 Recovery after overload": check_recovery(lines),
    }

    return results


def print_results(results: dict[str, bool]) -> None:
    print("\nFreeRTOS Live HIL Validation Results")
    print("-----------------------------------")

    passed = 0

    for test_name, status in results.items():
        if status:
            print(f"PASS - {test_name}")
            passed += 1
        else:
            print(f"FAIL - {test_name}")

    total = len(results)

    print("-----------------------------------")
    print(f"Summary: {passed}/{total} tests passed")

    if passed == total:
        print("FINAL RESULT: PASS")
    else:
        print("FINAL RESULT: FAIL")


def main():
    parser = argparse.ArgumentParser(description="Validate STM32 FreeRTOS UART log")
    parser.add_argument(
        "--log",
        default="hil_tests/reports/live_capture.log",
        help="Path to captured UART log file",
    )

    args = parser.parse_args()

    lines = read_log(args.log)
    results = validate_log(lines)
    print_results(results)


if __name__ == "__main__":
    main()