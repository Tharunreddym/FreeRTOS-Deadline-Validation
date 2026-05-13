#include "rtos_tasks.h"
#include "uart_logger.h"
#include "main.h"
#include <stdio.h>
#include <string.h>

QueueHandle_t xSensorQueue = NULL;
SemaphoreHandle_t xTimingMutex = NULL;

volatile ProcessorTiming_t xProcessorTiming = {0, 0, 0, 1};
volatile uint8_t ucOverloadInject = 0;

void vProducerTask(void *pvParameters)
{
    uint32_t sample_id = 0;
    TickType_t xLastWakeTime = xTaskGetTickCount();
    char log_buf[LOG_MAX_MESSAGE_LEN];

    UART_Log("[RTOS_TC_001 PASS] Scheduler started. Producer running.\r\n");

    for (;;)
    {
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(PRODUCER_PERIOD_MS));

        sample_id++;

        TickType_t now = xTaskGetTickCount();
        snprintf(log_buf, sizeof(log_buf),
            "[RTOS_TC_002] Producer tick: sample=%lu tick=%lu\r\n",
            sample_id, (unsigned long)now);
        UART_Log(log_buf);

        xQueueSend(xSensorQueue, &sample_id, 0);
    }
}

void vProcessorTask(void *pvParameters)
{
    uint32_t received_id;
    char log_buf[LOG_MAX_MESSAGE_LEN];

    for (;;)
    {
        if (xQueueReceive(xSensorQueue, &received_id, portMAX_DELAY) == pdTRUE)
        {
            TickType_t start = xTaskGetTickCount();

            if (xSemaphoreTake(xTimingMutex, pdMS_TO_TICKS(10)) == pdTRUE)
            {
                xProcessorTiming.last_start_tick = start;
                xProcessorTiming.processor_healthy = 1;
                xSemaphoreGive(xTimingMutex);
            }

            snprintf(log_buf, sizeof(log_buf),
                "[RTOS_TC_003 PASS] Processor received sample_id=%lu\r\n",
                received_id);
            UART_Log(log_buf);

            if (ucOverloadInject)
            {
                vTaskDelay(pdMS_TO_TICKS(120));
            }

            TickType_t end = xTaskGetTickCount();
            uint32_t duration = (uint32_t)((end - start) * portTICK_PERIOD_MS);

            if (xSemaphoreTake(xTimingMutex, pdMS_TO_TICKS(10)) == pdTRUE)
            {
                xProcessorTiming.last_end_tick = end;
                xProcessorTiming.last_duration_ms = duration;
                xSemaphoreGive(xTimingMutex);
            }

            if (duration < PROCESSOR_DEADLINE_MS)
            {
                snprintf(log_buf, sizeof(log_buf),
                    "[RTOS_TC_004 PASS] Processing done in %lu ms\r\n",
                    duration);
            }
            else
            {
                snprintf(log_buf, sizeof(log_buf),
                    "[RTOS_TC_004 FAIL] Processing exceeded deadline: %lu ms\r\n",
                    duration);
            }
            UART_Log(log_buf);
        }
    }
}

void vDeadlineMonitorTask(void *pvParameters)
{
    char log_buf[LOG_MAX_MESSAGE_LEN];
    uint8_t was_missed = 0;

    for (;;)
    {
        vTaskDelay(pdMS_TO_TICKS(MONITOR_PERIOD_MS));

        uint32_t duration = 0;

        if (xSemaphoreTake(xTimingMutex, pdMS_TO_TICKS(10)) == pdTRUE)
        {
            duration = xProcessorTiming.last_duration_ms;
            xSemaphoreGive(xTimingMutex);
        }

        if (duration >= PROCESSOR_DEADLINE_MS)
        {
            if (!was_missed)
            {
                UART_Log("[RTOS_TC_005 PASS] Monitor detected deadline miss within cycle.\r\n");
                UART_Log("[RTOS_TC_006 PASS] DEADLINE_MISS detected under overload.\r\n");
                was_missed = 1;
            }
        }
        else
        {
            if (was_missed)
            {
                UART_Log("[RTOS_TC_007 PASS] RECOVERY: Processing returned under deadline.\r\n");
                was_missed = 0;
            }

            snprintf(log_buf, sizeof(log_buf),
                "[MONITOR] System healthy. Last duration: %lu ms\r\n",
                duration);
            UART_Log(log_buf);
        }
    }
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if (GPIO_Pin == B1_Pin)
    {
        ucOverloadInject = !ucOverloadInject;
    }
}
