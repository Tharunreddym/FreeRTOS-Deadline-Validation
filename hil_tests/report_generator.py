import csv
import json
from datetime import datetime


def generate_report(results, timing_result, output_prefix="hil_tests/reports/rtos"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    tc_summary = [
        {"id": "RTOS_TC_001", "description": "Scheduler starts",
         "result": results["TC_001"] or "NOT FOUND"},
        {"id": "RTOS_TC_002", "description": "Producer timing within 100ms +/- 10ms",
         "result": "PASS" if timing_result[0] else "FAIL",
         "detail": timing_result[1]},
        {"id": "RTOS_TC_003", "description": "Queue transfer producer to processor",
         "result": "PASS" if len(results["TC_003"]) > 0 else "FAIL"},
        {"id": "RTOS_TC_004", "description": "Normal processing under deadline",
         "result": "PASS" if results["TC_004_pass"] > 0 else "FAIL",
         "detail": f"PASS={results['TC_004_pass']} FAIL={results['TC_004_fail']}"},
        {"id": "RTOS_TC_005", "description": "Monitor detects deadline miss within cycle",
         "result": results["TC_005"] or "NOT TRIGGERED"},
        {"id": "RTOS_TC_006", "description": "DEADLINE_MISS under overload",
         "result": results["TC_006"] or "NOT TRIGGERED"},
        {"id": "RTOS_TC_007", "description": "RECOVERY after overload clears",
         "result": results["TC_007"] or "NOT TRIGGERED"},
        {"id": "RTOS_TC_008", "description": "UART log completeness",
         "result": results["TC_008"] or "FAIL"},
    ]

    passed = sum(1 for tc in tc_summary if tc["result"] == "PASS")
    total = len(tc_summary)

    generate_csv(tc_summary, timestamp, f"{output_prefix}_results.csv")
    generate_html(tc_summary, timestamp, passed, total, f"{output_prefix}_report.html")
    generate_json(tc_summary, timestamp, passed, total, f"{output_prefix}_results.json")

    print(f"\nReports generated:")
    print(f"  {output_prefix}_results.csv")
    print(f"  {output_prefix}_report.html")
    print(f"  {output_prefix}_results.json")
    print(f"\nResult: {passed}/{total} PASSED")


def generate_csv(tc_summary, timestamp, filepath):
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Test ID", "Description", "Result", "Detail", "Timestamp"])
        for tc in tc_summary:
            writer.writerow([
                tc["id"],
                tc["description"],
                tc["result"],
                tc.get("detail", ""),
                timestamp
            ])


def generate_json(tc_summary, timestamp, passed, total, filepath):
    data = {
        "timestamp": timestamp,
        "summary": f"{passed}/{total} PASSED",
        "test_cases": tc_summary
    }
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def generate_html(tc_summary, timestamp, passed, total, filepath):
    rows = ""
    for tc in tc_summary:
        color = "green" if tc["result"] == "PASS" else "red"
        rows += f"""
        <tr>
            <td>{tc['id']}</td>
            <td>{tc['description']}</td>
            <td style='color:{color};font-weight:bold'>{tc['result']}</td>
            <td>{tc.get('detail', '')}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>FreeRTOS Deadline Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .summary {{ font-size: 1.2em; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>FreeRTOS Task Deadline Validation Report</h1>
    <p>Generated: {timestamp}</p>
    <p class='summary'>Result: <strong>{passed}/{total} PASSED</strong></p>
    <table>
        <tr>
            <th>Test ID</th>
            <th>Description</th>
            <th>Result</th>
            <th>Detail</th>
        </tr>
        {rows}
    </table>
</body>
</html>"""

    with open(filepath, "w") as f:
        f.write(html)