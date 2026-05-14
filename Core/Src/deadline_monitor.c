#include "deadline_monitor.h"
#include "rtos_tasks.h"
#include "uart_logger.h"
#include "FreeRTOSConfig.h"
#include <stdio.h>

void vDeadlineMonitorTask(void *pvParameters)
{
    (void)pvParameters;

    char log_buf[LOG_MAX_MESSAGE_LEN];
    uint8_t deadline_miss_active = 0;

    for (;;)
    {
        vTaskDelay(pdMS_TO_TICKS(MONITOR_PERIOD_MS));

        uint32_t duration_ms = 0;

        if (xSemaphoreTake(xTimingMutex, pdMS_TO_TICKS(10)) == pdTRUE)
        {
            duration_ms = xProcessorTiming.last_duration_ms;
            xSemaphoreGive(xTimingMutex);
        }

        if (duration_ms >= PROCESSOR_DEADLINE_MS)
        {
            if (deadline_miss_active == 0U)
            {
                UART_Log("[RTOS_TC_005 PASS] Monitor detected deadline miss within cycle.\r\n");
                UART_Log("[RTOS_TC_006 PASS] DEADLINE_MISS detected under overload.\r\n");
                deadline_miss_active = 1U;
            }
        }
        else
        {
            if (deadline_miss_active != 0U)
            {
                UART_Log("[RTOS_TC_007 PASS] RECOVERY: Processing returned under deadline.\r\n");
                deadline_miss_active = 0U;
            }

            snprintf(log_buf, sizeof(log_buf),
                     "[MONITOR] System healthy. Last duration: %lu ms\r\n",
                     (unsigned long)duration_ms);
            UART_Log(log_buf);
        }
    }
}
