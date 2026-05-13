#ifndef INC_RTOS_TASKS_H_
#define INC_RTOS_TASKS_H_

#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "semphr.h"

#define SENSOR_QUEUE_LENGTH     10
#define SENSOR_QUEUE_ITEM_SIZE  sizeof(uint32_t)

extern QueueHandle_t xSensorQueue;
extern SemaphoreHandle_t xTimingMutex;

typedef struct {
    TickType_t last_start_tick;
    TickType_t last_end_tick;
    uint32_t   last_duration_ms;
    uint8_t    processor_healthy;
} ProcessorTiming_t;

extern volatile ProcessorTiming_t xProcessorTiming;
extern volatile uint8_t ucOverloadInject;

void vProducerTask(void *pvParameters);
void vProcessorTask(void *pvParameters);
void vDeadlineMonitorTask(void *pvParameters);

#endif /* INC_RTOS_TASKS_H_ */
