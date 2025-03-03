import tkinter as tk
from tkinter import ttk
from ollama import chat
import time
import threading

def get_clipboard_content():
    """
    此函数用于获取剪贴板的内容。
    使用 tkinter 创建一个隐藏的主窗口来访问剪贴板。
    如果获取剪贴板内容时出现异常（如剪贴板为空），则返回 None。
    :return: 剪贴板内容，如果获取失败则返回 None
    """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    try:
        content = root.clipboard_get()
        return content
    except tk.TclError:
        return None
    finally:
        root.destroy()  # 销毁窗口，避免资源泄漏

def monitor_clipboard(input_entry):
    """
    循环监测剪贴板内容，若有新内容则填充到输入框
    :param input_entry: 输入框对象
    """
    last_content = None
    while True:
        try:
            current_content = get_clipboard_content()
            if current_content and current_content != last_content:
                input_entry.delete(0, tk.END)  # 清空输入框
                input_entry.insert(0, current_content + " 中文详细讲解")  # 填充新内容
                last_content = current_content
        except Exception as e:
            print(f"监测剪贴板时出错: {e}")
        time.sleep(1)  # 每隔 1 秒检查一次

def send_message(chat_text_widget, input_entry_widget, selected_model):
    """
    此函数用于处理消息发送逻辑，获取用户输入，调用 ollama 模型获取回复，并将对话内容显示在聊天窗口中
    :param chat_text_widget: 用于显示聊天内容的文本框
    :param input_entry_widget: 用户输入消息的输入框
    :param selected_model: 用户选择的 ollama 模型
    """
    message = input_entry_widget.get()
    input_entry_widget.delete(0, tk.END)
    chat_text_widget.insert(tk.END, f"你: {message}\n\n")  # 增加换行符
    try:
        stream = chat(
            model=selected_model,
            messages=[{'role': 'user', 'content': message}],
            stream=True,
        )
        response = ""
        for chunk in stream:
            response += chunk['message']['content']
        chat_text_widget.insert(tk.END, f"模型: {response}\n\n")  # 增加换行符
    except Exception as e:
        chat_text_widget.insert(tk.END, f"调用 ollama 模型时出错: {e}\n\n")  # 增加换行符
    # 滚动到文本框底部
    chat_text_widget.see(tk.END)

def on_chat_window_close(root, chat_window):
    """
    处理聊天窗口关闭事件，销毁主窗口以退出程序
    :param root: 主窗口对象
    :param chat_window: 聊天窗口对象
    """
    chat_window.destroy()
    root.destroy()

def create_chat_window(root, selected_model):
    """
    创建聊天窗口，包含文本显示框、输入框和发送按钮
    :param root: 主窗口
    :param selected_model: 用户选择的 ollama 模型
    :return: 聊天窗口对象
    """
    chat_window = tk.Toplevel(root)
    chat_window.title("聊天界面")
    # 设置窗口始终显示在最上层
    chat_window.attributes('-topmost', True)

    # 创建一个框架来包含文本框和滚动条
    chat_frame = tk.Frame(chat_window)
    chat_frame.pack(pady=10)

    chat_text = tk.Text(chat_frame, height=20, width=50)
    chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 创建垂直滚动条
    scrollbar = tk.Scrollbar(chat_frame, command=chat_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_text.config(yscrollcommand=scrollbar.set)

    input_frame = tk.Frame(chat_window)
    input_frame.pack(pady=10)

    input_entry = tk.Entry(input_frame, width=40)
    input_entry.pack(side=tk.LEFT, padx=5)
    input_entry.bind("<Return>", lambda event: send_message(chat_text, input_entry, selected_model))

    # 创建样式对象
    style = ttk.Style()
    # 设置主题
    style.theme_use('default')
    # 定义圆角按钮样式
    style.configure('RoundedButton.TButton',
                    background='#ADD8E6',  # 浅蓝色背景
                    foreground='white',
                    font=('Arial', 12),
                    borderwidth=0,
                    focuscolor=style.configure(".")["background"])
    style.map('RoundedButton.TButton',
              background=[('active', '#73A6FF'), ('pressed', '#73A6FF')])
    # 创建自定义布局元素
    style.element_create('RoundedButton', 'from', 'clam')
    style.layout('RoundedButton.TButton',
                 [('RoundedButton.padding',
                   {'sticky': 'nswe',
                    'children': [('RoundedButton.label', {'sticky': 'nswe'})]})])

    # 创建圆角按钮
    send_button = ttk.Button(input_frame, text="发送",
                             command=lambda: send_message(chat_text, input_entry, selected_model),
                             style='RoundedButton.TButton')
    send_button.pack(side=tk.LEFT, padx=5)

    # 启动剪贴板监测线程
    try:
        clipboard_thread = threading.Thread(target=monitor_clipboard, args=(input_entry,))
        clipboard_thread.daemon = True
        clipboard_thread.start()
    except Exception as e:
        print(f"启动剪贴板监测线程时出错: {e}")

    # 绑定聊天窗口关闭事件
    chat_window.protocol("WM_DELETE_WINDOW", lambda: on_chat_window_close(root, chat_window))

    # 计算聊天界面显示在屏幕中间的位置
    chat_window.update_idletasks()
    width = chat_window.winfo_width()
    height = chat_window.winfo_height()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    chat_window.geometry(f"{width}x{height}+{x}+{y}")

    return chat_window

