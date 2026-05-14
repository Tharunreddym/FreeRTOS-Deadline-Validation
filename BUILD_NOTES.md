# FreeRTOS Task Deadline Validation System on STM32

## Locked timing constants

```c
#define PROCESSOR_DEADLINE_MS 80
#define PRODUCER_PERIOD_MS 100
#define PRODUCER_TOLERANCE_MS 10
#define MONITOR_PERIOD_MS 500
```

## Interview explanation

The processor deadline is 80 ms because the producer generates data every 100 ms. That leaves 20 ms of headroom for scheduling jitter, queue handling, logging, and system overhead before the next sample arrives.

## Firmware modules

- `Core/Src/main.c`
- `Core/Src/rtos_tasks.c`
- `Core/Inc/rtos_tasks.h`
- `Core/Src/uart_logger.c`
- `Core/Inc/uart_logger.h`
- `Core/Src/deadline_monitor.c`
- `Core/Inc/deadline_monitor.h`

## Python HIL automation

- `hil_tests/serial_capture.py`
- `hil_tests/log_parser.py`
- `hil_tests/test_rtos.py`
- `hil_tests/report_generator.py`
- `hil_tests/reports/`

## Stack overflow protection

`Core/Inc/FreeRTOSConfig.h` contains:

```c
#define configCHECK_FOR_STACK_OVERFLOW 2
```

`Core/Src/freertos.c` contains:

```c
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName)
{
    taskDISABLE_INTERRUPTS();
    while (1) {}
}
```

## Local validation performed

Python HIL parser validation was run against the included UART log with:

```bash
RTOS_LOG_FILE=logs/rtos_uart_log.txt pytest -q hil_tests/test_rtos.py
```

Result:

```text
8 passed
```

A native firmware build was not completed in this environment because `arm-none-eabi-gcc` is not installed. The STM32CubeIDE/GNU Arm toolchain is required for firmware compilation.
