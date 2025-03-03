import tkinter as tk
import time

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

if __name__ == "__main__":
    last_content = None
    print("开始循环获取剪贴板内容，按 Ctrl+C 终止程序。")
    while True:
        current_content = get_clipboard_content()
        if current_content and current_content != last_content:
            print(f"检测到新的剪贴板内容: {current_content}")
            last_content = current_content
        time.sleep(1)  # 每隔 1 秒检查一次剪贴板内容

