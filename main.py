import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
from maindisplay import create_chat_window
from tqdm import tqdm
from ollama import pull

def get_ollama_list_first_column():
    """
    执行 ollama list 命令，获取输出的第一列内容。

    :return: 包含第一列内容的列表
    """
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        if lines and lines[0].startswith('NAME'):
            lines = lines[1:]
        first_column = [line.split()[0] for line in lines if line]
        return first_column
    except subprocess.CalledProcessError as e:
        print(f"执行命令时出错: {e.stderr}")
        return []

def on_confirm():
    global selected_model
    # 获取用户选择的模型
    selected_model = combo_box.get()
    print(f"你选择了: {selected_model}")
    try:
        # 执行 ollama run 命令
        command = ['ollama', 'run', selected_model]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)

        # 创建聊天窗口
        create_chat_window(root, selected_model)

        # 隐藏主窗口而不是销毁
        root.withdraw()

    except subprocess.CalledProcessError as e:
        print(f"执行 ollama run 命令时出错: {e.stderr}")
    except Exception as e:
        print(f"调用 ollama 模型时出错: {e}")

# 新增模型拉取函数
def pull_model(model_name='deepseek-r1:1.5b'):
    """自动拉取指定模型并显示进度条"""
    current_digest, bars = '', {}
    try:
        for progress in pull(model_name, stream=True):
            digest = progress.get('digest', '')
            if digest != current_digest and current_digest in bars:
                bars[current_digest].close()

            if not digest:
                print(progress.get('status'))
                continue

            if digest not in bars and (total := progress.get('total')):
                bars[digest] = tqdm(total=total, desc=f'pulling {digest[7:19]}', unit='B', unit_scale=True)

            if completed := progress.get('completed'):
                bars[digest].update(completed - bars[digest].n)

            current_digest = digest
        return True
    except Exception as e:
        print(f"模型拉取失败: {e}")
        return False

# 修改主程序逻辑
root = tk.Tk()
root.title("下拉列表界面")

# 获取模型列表并自动拉取
options = get_ollama_list_first_column()
if not options:
    if pull_model():  # 默认拉取llama3.2
        options = get_ollama_list_first_column()  # 重新获取列表

# 创建下拉列表
combo_box = ttk.Combobox(root, values=options)
if options:
    combo_box.set(options[0])
else:
    combo_box.set("无可用选项")
combo_box.pack(pady=20, padx=50, anchor=tk.CENTER)

# 创建确定按钮
confirm_button = ttk.Button(root, text="确定", command=on_confirm)
confirm_button.pack(pady=10, padx=50, anchor=tk.CENTER)

# 计算选择界面显示在屏幕中间的位置
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - width) // 2
y = (screen_height - height) // 2
root.geometry(f"{width}x{height}+{x}+{y}")

root.mainloop()
