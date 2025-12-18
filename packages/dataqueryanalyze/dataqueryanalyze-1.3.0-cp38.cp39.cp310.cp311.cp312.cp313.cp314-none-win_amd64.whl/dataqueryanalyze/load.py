#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import platform
import threading
# 确保当前目录在Python路径中，以便导入app模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入app模块
import app
# 导入add_tok函数
from core.llm import add_tok
# 导入更新检查函数
from dataqueryanalyze import check_for_updates

# 定义main函数，复制app.py中的入口点代码
def main():
    # 检查并创建tok.xml文件
    add_tok()
    
    # 在后台线程中检查更新，不阻塞主程序启动
    update_thread = threading.Thread(target=check_for_updates, daemon=True)
    update_thread.start()
    
    app_instance = app.QApplication(sys.argv)
    app_instance.setStyle('Fusion')  # 使用Fusion风格以获得更好的跨平台一致性
    
    # 设置应用程序字体
    font = app.QFont()
    font.setFamily('Microsoft YaHei')
    font.setPointSize(9)
    app_instance.setFont(font)
    
    window = app.DataAnalysisApp()
    window.show()
    sys.exit(app_instance.exec())

if __name__ == '__main__':
    main()
