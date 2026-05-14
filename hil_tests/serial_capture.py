import serial
import time


def capture_uart_log(port, baud_rate=115200, duration_seconds=30, output_file="hil_tests/reports/live_capture.log"):
    print(f"Connecting to {port} at {baud_rate} baud...")
    print(f"Capturing for {duration_seconds} seconds...")

    lines = []

    try:
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            start_time = time.time()
            while (time.time() - start_time) < duration_seconds:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    print(line)
                    lines.append(line)

    except serial.SerialException as e:
        print(f"Serial error: {e}")
        return None

    log_text = "\n".join(lines)

    with open(output_file, "w") as f:
        f.write(log_text)

    print(f"\nLog saved to {output_file}")
    return log_text


if __name__ == "__main__":
    import sys
    port = sys.argv[1] if len(sys.argv) > 1 else "COM7"
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    capture_uart_log(port, duration_seconds=duration)