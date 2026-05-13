#include "uart_logger.h"
#include "main.h"
#include <string.h>
#include <stdio.h>

extern UART_HandleTypeDef huart2;

QueueHandle_t xLogQueue = NULL;

void UART_Logger_Init(void)
{
    xLogQueue = xQueueCreate(LOG_QUEUE_LENGTH, LOG_MAX_MESSAGE_LEN);
}

void UART_Log(const char *message)
{
    if (xLogQueue == NULL) return;

    char buffer[LOG_MAX_MESSAGE_LEN];
    strncpy(buffer, message, LOG_MAX_MESSAGE_LEN - 1);
    buffer[LOG_MAX_MESSAGE_LEN - 1] = '\0';

    xQueueSend(xLogQueue, buffer, 0);
}

void vUartLoggerTask(void *pvParameters)
{
    char message[LOG_MAX_MESSAGE_LEN];

    for (;;)
    {
        if (xQueueReceive(xLogQueue, message, portMAX_DELAY) == pdTRUE)
        {
            HAL_UART_Transmit(&huart2,
                (uint8_t *)message,
                strlen(message),
                100);
        }
    }
}
