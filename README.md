
# 未闻花名 蜂鸣器演示 (STM32F103 + 无源蜂鸣器)

本工程示例使用 STM32F103 单片机驱动无源蜂鸣器，通过定时器产生 PWM 以播放“未闻花名”乐曲（乐谱见项目中的文本文件）。

**主要目标**：用最小改动在现有代码基础上播放由音频解码得到的音符频率序列。

**工程结构（关键文件）**

- **工程文件**： [Project.uvprojx](Project.uvprojx)（Keil MDK 工程文件，直接在 Keil 打开并构建）
- 驱动与硬件： [Hardware/Buzzer.c](Hardware/Buzzer.c), [Hardware/Buzzer.h](Hardware/Buzzer.h)
- 延时工具： [System/Delay.c](System/Delay.c), [System/Delay.h](System/Delay.h)
- 用户程序： [User/main.c](User/main.c)
- 乐谱（由 Python 解码音频生成）： 未闻花名 简谱  频率.txt（工程目录）

**工作原理概要**

- `Buzzer.c`：使用 TIM2 通道 1（PA0）输出 PWM。定时器预分频为 72，计数时钟为 1MHz（1µs 单位）。函数 `Buzzer_Set(uint16_t frequency, uint8_t dutyCycle)` 通过设置自动重装载寄存器（ARR）和比较寄存器（CCR1）来改变频率与占空比；频率为 0 时关闭蜂鸣器。
- `Delay.c`：使用 SysTick 实现 Delay_us / Delay_ms / Delay_s，主循环中用于控制每个音符的时长。
- `User/main.c`：包含一个 `music[]` 数组（由你提供的音符时间/频率表生成），程序按时间差计算每个音符的持续时间并调用 `Buzzer_Set` 与 `Delay_ms` 来演奏。

**硬件连接**

- 无源蜂鸣器信号线接到 PA0（对应 TIM2 CH1，见 [Hardware/Buzzer.c](Hardware/Buzzer.c)），另一端接电源/地（根据蜂鸣器类型可接 5V 或 3.3V，注意蜂鸣器额定电压）。
- 若蜂鸣器需要更大电流，建议通过 NPN 三极管或 MOSFET 驱动，并在晶体管两端并联保护二极管/限流电阻，避免直接从 MCU 引脚供电。

**构建与烧录**

1. 在 Windows 上使用 Keil MDK-ARM：打开工程文件 [Project.uvprojx](Project.uvprojx)。
2. 选择合适的目标（Target_1），点击 Build（F7）构建工程。
3. 使用 Keil 的下载工具（ULINK）或 ST-Link + STM32CubeProgrammer 将生成的固件（Project.axf / 导出为 .hex）烧录到 STM32。若使用 STM32CubeProgrammer，可先在 Keil 中生成 HEX/BIN（项目选项 -> Output），然后用 STM32CubeProgrammer 烧录。

**快速调试建议**

- 若未听到声音：
	- 确认 `PA0` 未被其他外设占用；查看 [Hardware/Buzzer.c](Hardware/Buzzer.c) 的 GPIO 配置。
	- 检查 `Buzzer_Init()` 是否被调用（在 [User/main.c](User/main.c) 开头）。
	- 使用示波器或耳机检测 PA0 是否有方波输出。
- 调整音量/响度：修改 `Buzzer_Set` 中 `dutyCycle` 参数（0~100）。50% 是常用的起始值；过高占空比可能使音色改变。

**如何修改乐谱/播放内容**

- `User/main.c` 中 `music[]` 数组保存了每个音符的“开始时间（秒）”与“频率（Hz）”。程序通过相邻时间差计算持续时间并播放。若需要替换乐谱，可：
	1. 使用你原先用的 Python 工具把音频解码为时间-频率表（生成 `未闻花名 简谱  频率.txt`）。
	2. 将新表转换为 `music[]` 数组格式并替换 `User/main.c` 中的数组内容。
	3. 重新构建并烧录。

**注意事项与改进建议**

- 长时间的时间间隔（例如歌曲段落之间的空白）在 `main.c` 中被视为休止，会在播放短音后延长静默；你可根据需要调整“长间隔阈值”（当前实现阈值为 2 秒）与“最长播放片段”（当前示例播放 500ms）。
- 如果需要更精确的时间同步（避免主循环阻塞带来的累计误差），建议用定时器中断或 RTOS 定时任务来调度音符开始/停止。
- 若想播放更复杂的多声部或和弦，需在硬件上增加 DAC/外部音频设备或用多个 PWM 通道混音。

---
工程已更新的关键源码位于：
- [User/main.c](User/main.c)
- [Hardware/Buzzer.c](Hardware/Buzzer.c)
- [System/Delay.c](System/Delay.c)
