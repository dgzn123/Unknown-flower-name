import librosa                     # 用于音频处理和分析
import numpy as np                 # 用于数值计算
import sys                         # 用于命令行参数处理

def analyze_audio_to_simple_notes(audio_path, output_txt="notes_output.txt"):
    """
    分析音频文件，将其音高简化为 C4-C5 的八个基本音符，并保存到 txt 文件。
    """
    
    # 1. 定义目标音符及其频率 (Hz)
    # Do(C4), Re(D4), Mi(E4), Fa(F4), So(G4), La(A4), Ti(B4), Do(C5)
    target_notes = {
        'Do (C4)': 261.63,
        'Re (D4)': 293.66,
        'Mi (E4)': 329.63,
        'Fa (F4)': 349.23,
        'So (G4)': 392.00,
        'La (A4)': 440.00,
        'Ti (B4)': 493.88,
        'Do (C5)': 523.25
    }
    
    # 将字典转换为列表以便于计算
    note_names = list(target_notes.keys())
    note_freqs = np.array(list(target_notes.values()))

    print(f"正在加载音频文件: {audio_path} ...")
    try:
        # 加载音频文件
        # sr=None 保持原始采样率
        y, sr = librosa.load(audio_path, sr=None)
    except Exception as e:
        print(f"错误: 无法加载音频文件. {e}")
        return

    print("正在分析音高 (这可能需要几秒钟)...")
    
    # 2. 提取音高 (基频 f0)
    # 使用 pYIN 算法，它对语音和乐器都比较稳健
    # fmin 和 fmax 限制在合理的分析范围内 (例如 C2 到 C7)
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'), sr=sr)

    # 将时间帧转换为时间（秒）
    times = librosa.times_like(f0, sr=sr)

    print("分析完成，正在简化音符...\n")
    
    try:
        with open(output_txt, "w", encoding="utf-8") as f:
            header = f"{'时间 (秒)':<15} | {'原始频率 (Hz)':<15} | {'简化音符'}"
            print(header)
            print("-" * 50)
            
            f.write(header + "\n")
            f.write("-" * 50 + "\n")

            last_note = None
            
            # 3. 遍历每一帧，映射到最近的目标音符
            for i, freq in enumerate(f0):
                # 如果这一帧没有检测到声音 (NaN) 或者是非浊音
                if not voiced_flag[i] or np.isnan(freq):
                    continue

                # 找到与当前频率最接近的目标频率的索引
                # np.abs(note_freqs - freq) 计算差值绝对值
                # argmin 找到最小差值的索引
                closest_idx = (np.abs(note_freqs - freq)).argmin()
                current_note = note_names[closest_idx]
                
                # 简单的去重逻辑：只有当音符发生变化，或者经过了一定时间才输出
                # 这里为了演示，我们打印每一个检测到的新音符片段的开始
                if current_note != last_note:
                    line_content = f"{times[i]:<15.2f} | {freq:<15.2f} | {current_note}"
                    print(line_content)
                    f.write(line_content + "\n")
                    last_note = current_note
        
        print(f"\n结果已成功保存到文件: {output_txt}")
            
    except Exception as e:
        print(f"保存文件时出错: {e}")

if __name__ == "__main__":
    # 检查命令行参数，如果没有提供文件路径，则使用默认提示
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # 这里可以修改为你想要测试的默认音频文件路径
        file_path = "input.wav" 
        print(f"用法: python audio_to_notes.py <音频文件路径>")
        print(f"未提供路径，尝试默认文件: {file_path}")

    import os
    if os.path.exists(file_path):
        analyze_audio_to_simple_notes(file_path)
    else:
        if len(sys.argv) <= 1:
            print("\n请在命令行中运行并指定音频文件，例如:")
            print("python audio_to_notes.py my_song.mp3")
        else:
            print(f"错误: 文件 '{file_path}' 不存在。")
