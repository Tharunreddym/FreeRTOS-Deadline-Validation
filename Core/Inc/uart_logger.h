#ifndef INC_UART_LOGGER_H_
#define INC_UART_LOGGER_H_

#include "FreeRTOS.h"
#include "queue.h"

#define LOG_QUEUE_LENGTH     20
#define LOG_MAX_MESSAGE_LEN  128

extern QueueHandle_t xLogQueue;

void UART_Logger_Init(void);
void UART_Log(const char *message);
void vUartLoggerTask(void *pvParameters);

#endif /* INC_UART_LOGGER_H_ */
