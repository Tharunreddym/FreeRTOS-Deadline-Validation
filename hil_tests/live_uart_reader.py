import argparse
import serial
import time
from pathlib import Path


def read_uart(port: str, baudrate: int, duration: int) -> list[str]:
    lines = []

    print(f"Opening {port} at {baudrate} baud...")
    print(f"Reading UART for {duration} seconds...\n")

    with serial.Serial(port, baudrate, timeout=1) as ser:
        start_time = time.time()

        while time.time() - start_time < duration:
            raw_line = ser.readline()

            if not raw_line:
                continue

            try:
                line = raw_line.decode("utf-8", errors="ignore").strip()
            except UnicodeDecodeError:
                continue

            if line:
                print(line)
                lines.append(line)

    return lines


def save_log(lines: list[str], output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for line in lines:
            file.write(line + "\n")

    print(f"\nSaved UART log to: {path}")


def main():
    parser = argparse.ArgumentParser(description="Live UART reader for STM32 FreeRTOS logs")
    parser.add_argument("--port", required=True, help="STM32 COM port, example: COM7")
    parser.add_argument("--baudrate", type=int, default=115200, help="UART baudrate")
    parser.add_argument("--duration", type=int, default=30, help="Capture duration in seconds")
    parser.add_argument(
        "--output",
        default="hil_tests/reports/live_capture.log",
        help="Output log file path",
    )

    args = parser.parse_args()

    lines = read_uart(args.port, args.baudrate, args.duration)
    save_log(lines, args.output)


if __name__ == "__main__":
    main()