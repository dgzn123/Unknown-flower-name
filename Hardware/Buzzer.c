#include "stm32f10x.h"

//蜂鸣器初始化
void Buzzer_Init(void)
{
    //使能GPIOA时钟
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2, ENABLE);

    //GPIO初始化
    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;              // PA0
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;        // 复用推挽输出
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    //配置时钟源
    TIM_InternalClockConfig(TIM2);

    //时基单元初始化
    TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure;
    TIM_TimeBaseStructure.TIM_Prescaler = 72 - 1;
    TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up;
    TIM_TimeBaseStructure.TIM_Period = 1000 - 1;          // 1kHz
    TIM_TimeBaseStructure.TIM_ClockDivision = TIM_CKD_DIV1;
    TIM_TimeBaseStructure.TIM_RepetitionCounter = 0;
    TIM_TimeBaseInit(TIM2, &TIM_TimeBaseStructure);

    //输出比较初始化
    TIM_OCInitTypeDef TIM_OCInitStructure;
    TIM_OCStructInit(&TIM_OCInitStructure);
    TIM_OCInitStructure.TIM_OCMode = TIM_OCMode_PWM1;      // PWM模式1
    TIM_OCInitStructure.TIM_OutputState = TIM_OutputState_Enable;
    TIM_OCInitStructure.TIM_Pulse = 0;                   // 占空比0%
    TIM_OCInitStructure.TIM_OCPolarity = TIM_OCPolarity_High;
    TIM_OC1Init(TIM2, &TIM_OCInitStructure);

    //启动定时器
    TIM_Cmd(TIM2, ENABLE);
}

//设置蜂鸣器频率和占空比
void Buzzer_Set(uint16_t frequency, uint8_t dutyCycle)
{
    if (frequency == 0 || dutyCycle > 100)  // 无声或无效占空比
    {
        // 关闭蜂鸣器
        TIM_SetCompare1(TIM2, 0);
        return;
    }

    // 计时器预分频为72, 定时器时钟为 72MHz / 72 = 1MHz
    // 因此计数单位为 1us，周期应为 (1_000_000 / frequency)
    uint32_t timer_clk = 1000000UL; // 1 MHz
    uint32_t period = timer_clk / frequency; // 计数周期
    if (period == 0) period = 1;  // 防止除零错误
    uint32_t pulse = (period * dutyCycle) / 100; // 占空比对应的比较值

    TIM_SetAutoreload(TIM2, period - 1); // 设置自动重装载寄存器
    TIM_SetCompare1(TIM2, pulse);        // 设置比较寄存器
}
