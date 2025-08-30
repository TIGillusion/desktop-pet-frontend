"""
真实的Live2D桌面渲染器
使用PyQt5和OpenGL，集成真正的Live2D模型渲染
"""
import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QOpenGLWidget, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QCursor, QPainter, QPen
import OpenGL.GL as gl
from config import config
from real_live2d_controller import real_live2d_controller

# Windows API 导入（用于真正的鼠标穿透）
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
    
    # Windows 常量
    GWL_EXSTYLE = -20
    WS_EX_TRANSPARENT = 0x00000020
    WS_EX_LAYERED = 0x00080000


class Live2DRenderer(QOpenGLWidget):
    def __init__(self, live2d_model_name = None):
        self.live2d_model_name = live2d_model_name

        super().__init__()
        
        self.setupWindow()
        self.setupTimer()
        self.setupTrayIcon()
        
        # 鼠标拖拽和大小调整
        self.dragging = False
        self.resizing = False
        self.drag_position = QPoint()
        self.resize_edge = None  # 记录正在调整的边缘
        self.resize_start_pos = QPoint()
        self.resize_start_geometry = None
        
        # 调整模式
        self.resize_mode = False  # 是否进入调整大小模式
        
        # 模型状态
        self.current_model = None
        self.parameters = {}
        
        # 边框宽度
        self.border_width = 10
    
    def get_resize_edge(self, pos):
        """检测鼠标位置在哪个边缘"""
        if not self.resize_mode:
            return None
            
        rect = self.rect()
        x, y = pos.x(), pos.y()
        w, h = rect.width(), rect.height()
        
        # 检测边角和边缘
        in_left = x <= self.border_width
        in_right = x >= w - self.border_width
        in_top = y <= self.border_width
        in_bottom = y >= h - self.border_width
        
        # 边角优先
        if in_top and in_left:
            return 'top_left'
        elif in_top and in_right:
            return 'top_right'
        elif in_bottom and in_left:
            return 'bottom_left'
        elif in_bottom and in_right:
            return 'bottom_right'
        # 边缘
        elif in_top:
            return 'top'
        elif in_bottom:
            return 'bottom'
        elif in_left:
            return 'left'
        elif in_right:
            return 'right'
        else:
            return None
    
    def set_cursor_for_edge(self, edge):
        """根据边缘设置光标"""
        if edge == 'top_left' or edge == 'bottom_right':
            self.setCursor(QCursor(Qt.SizeFDiagCursor))
        elif edge == 'top_right' or edge == 'bottom_left':
            self.setCursor(QCursor(Qt.SizeBDiagCursor))
        elif edge == 'top' or edge == 'bottom':
            self.setCursor(QCursor(Qt.SizeVerCursor))
        elif edge == 'left' or edge == 'right':
            self.setCursor(QCursor(Qt.SizeHorCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))
    
    def set_windows_click_through(self, enabled):
        """使用 Windows API 设置真正的鼠标穿透"""
        if sys.platform != "win32":
            return False
            
        try:
            hwnd = int(self.winId())
            
            # 获取当前窗口样式
            current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            
            if enabled:
                # 启用鼠标穿透：添加 WS_EX_TRANSPARENT 和 WS_EX_LAYERED
                new_style = current_style | WS_EX_TRANSPARENT | WS_EX_LAYERED
            else:
                # 禁用鼠标穿透：移除 WS_EX_TRANSPARENT
                new_style = current_style & ~WS_EX_TRANSPARENT
            
            # 应用新样式
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
            return True
            
        except Exception as e:
            print(f"[渲染器] Windows API 鼠标穿透设置失败: {e}")
            return False
        
    def setupWindow(self):
        """设置窗口属性"""
        self.setWindowTitle(config.WINDOW_TITLE)
        self.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        if config.OBS_COMPATIBLE_MODE:
            # OBS 兼容模式：普通窗口，可被 OBS 捕获
            self.setWindowFlags(
                Qt.FramelessWindowHint |      # 无边框
                Qt.WindowStaysOnTopHint       # 置顶
                # 不使用 Qt.Tool，这样窗口可以被 OBS 识别
            )
            
            # OBS 模式下设置不透明度
            self.setWindowOpacity(config.OBS_MODE_OPACITY)
            
            if not config.OBS_MODE_SHOW_IN_TASKBAR:
                # 如果不想在任务栏显示，使用这个属性
                self.setWindowFlags(self.windowFlags() | Qt.Tool)
                
        else:
            # 桌面宠物模式：原有设置
            self.setWindowFlags(
                Qt.FramelessWindowHint |  # 无边框
                Qt.WindowStaysOnTopHint | # 置顶
           Qt.Tool                   # 工具窗口，不在任务栏显示
                 )
            
            # 设置窗口透明
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.setAttribute(Qt.WA_AlwaysStackOnTop, True)
        
        # 设置鼠标穿透（两种模式都可以使用）
        if config.CLICK_THROUGH_ENABLED:
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            # 使用 Windows API 实现真正的鼠标穿透
            self.set_windows_click_through(True)
        else:
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self.set_windows_click_through(False)
        
    def setupTimer(self):
        """设置渲染定时器"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateAnimation)
        self.timer.start(int(1000 / config.FPS))
        
    def setupTrayIcon(self):
        """设置系统托盘图标"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("系统不支持托盘图标")
            return
            
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 设置默认图标
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.blue)
        self.tray_icon.setIcon(QIcon(pixmap))
        
        # 创建右键菜单
        tray_menu = QMenu()
        
        show_action = QAction("显示/隐藏", self)
        show_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(show_action)
        
        obs_action = QAction("切换 OBS 模式", self)
        obs_action.triggered.connect(self.toggle_obs_mode)
        tray_menu.addAction(obs_action)
        
        click_through_action = QAction("切换鼠标穿透", self)
        click_through_action.triggered.connect(self.toggle_click_through)
        tray_menu.addAction(click_through_action)
        
        size_adjust_action = QAction("切换调整模式", self)
        size_adjust_action.triggered.connect(self.toggle_resize_mode)
        tray_menu.addAction(size_adjust_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
        
    def initializeGL(self):
        """初始化OpenGL和Live2D"""
        try:
            # 初始化Live2D引擎（保持与原项目一致的简单方式）
            real_live2d_controller.initialize()
            print("[渲染器] OpenGL 和 Live2D 初始化完成")
            
            # 自动加载第一个可用模型
            self._auto_load_model(self.live2d_model_name)
            
        except Exception as e:
            print(f"[渲染器] 初始化失败: {e}")
        
    def _auto_load_model(self, live2d_model_name = None):
        """指定加载或自动加载第一个可用模型"""
        try:
            if os.path.exists(config.MODELS_DIR):
                if live2d_model_name:
                    model_path = os.path.join(config.MODELS_DIR, live2d_model_name)
                    print(f"[渲染器] 自动加载模型: {live2d_model_name}")
                    real_live2d_controller.load_model(model_path)
                else:
                    models = [d for d in os.listdir(config.MODELS_DIR) 
                            if os.path.isdir(os.path.join(config.MODELS_DIR, d))]
                    if models:
                        first_model = models[0]
                        model_path = os.path.join(config.MODELS_DIR, first_model)
                        print(f"[渲染器] 自动加载模型: {first_model}")
                        real_live2d_controller.load_model(model_path)
                    else:
                        print("[渲染器] 未找到任何模型文件")
            else:
                print(f"[渲染器] 模型目录不存在: {config.MODELS_DIR}")
        except Exception as e:
            print(f"[渲染器] 自动加载模型失败: {e}")
        
    def resizeGL(self, width, height):
        """窗口大小改变时调用"""
        gl.glViewport(0, 0, width, height)
        # 如果有Live2D模型，调整其大小
        if real_live2d_controller.model:
            try:
                real_live2d_controller.model.Resize(width, height)
            except Exception as e:
                print(f"[渲染器] 模型尺寸调整失败: {e}")
        
    def paintGL(self):
        """OpenGL绘制（与原项目保持一致）"""
        try:
            # 清除背景
            gl.glClearColor(*config.BACKGROUND_COLOR)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            
            # 更新和绘制Live2D模型
            real_live2d_controller.update()
            real_live2d_controller.draw()
            
        except Exception as e:
            print(f"[渲染器] 绘制失败: {e}")
    
    def paintEvent(self, event):
        """Qt绘制事件 - 绘制边框"""
        super().paintEvent(event)
        
        # 只在调整大小模式下绘制边框
        if self.resize_mode:
            painter = QPainter(self)
            pen = QPen()
            pen.setColor(Qt.red)
            pen.setWidth(2)
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            
            # 绘制边框
            rect = self.rect()
            painter.drawRect(rect.adjusted(1, 1, -1, -1))
            
            painter.end()
    
    def handle_resize(self, global_pos):
        """处理窗口大小调整"""
        if not self.resize_edge or not self.resize_start_geometry:
            return
            
        # 计算鼠标移动的偏移量
        delta = global_pos - self.resize_start_pos
        dx, dy = delta.x(), delta.y()
        
        # 获取原始几何信息
        orig_rect = self.resize_start_geometry
        new_x = orig_rect.x()
        new_y = orig_rect.y()
        new_width = orig_rect.width()
        new_height = orig_rect.height()
        
        # 根据调整的边缘计算新的大小和位置
        if 'left' in self.resize_edge:
            new_x = orig_rect.x() + dx
            new_width = orig_rect.width() - dx
        if 'right' in self.resize_edge:
            new_width = orig_rect.width() + dx
        if 'top' in self.resize_edge:
            new_y = orig_rect.y() + dy
            new_height = orig_rect.height() - dy
        if 'bottom' in self.resize_edge:
            new_height = orig_rect.height() + dy
        
        # 限制最小大小
        min_width, min_height = 400, 400
        if new_width < min_width:
            if 'left' in self.resize_edge:
                new_x = orig_rect.x() + orig_rect.width() - min_width
            new_width = min_width
        if new_height < min_height:
            if 'top' in self.resize_edge:
                new_y = orig_rect.y() + orig_rect.height() - min_height
            new_height = min_height
            
        # 应用新的几何信息
        self.setGeometry(new_x, new_y, new_width, new_height)
        
        # 更新配置
        config.WINDOW_WIDTH = new_width
        config.WINDOW_HEIGHT = new_height
            
    def updateAnimation(self):
        """更新动画"""
        self.update()  # 触发重绘
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        # 如果启用了鼠标穿透，忽略所有鼠标事件
        if config.CLICK_THROUGH_ENABLED:
            event.ignore()
            return
            
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            edge = self.get_resize_edge(pos)
            
            if edge and self.resize_mode:
                # 开始调整大小
                self.resizing = True
                self.resize_edge = edge
                self.resize_start_pos = event.globalPos()
                self.resize_start_geometry = self.geometry()
            else:
                # 普通拖拽移动
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        # 如果启用了鼠标穿透，忽略所有鼠标事件
        if config.CLICK_THROUGH_ENABLED:
            event.ignore()
            return
        
        pos = event.pos()
        
        if self.resizing and event.buttons() == Qt.LeftButton:
            # 正在调整大小
            self.handle_resize(event.globalPos())
        elif self.dragging and event.buttons() == Qt.LeftButton:
            # 普通拖拽移动
            self.move(event.globalPos() - self.drag_position)
        else:
            # 检测边缘并设置光标
            edge = self.get_resize_edge(pos)
            self.set_cursor_for_edge(edge)
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        # 如果启用了鼠标穿透，忽略所有鼠标事件
        if config.CLICK_THROUGH_ENABLED:
            event.ignore()
            return
            
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        
    def tray_icon_activated(self, reason):
        """托盘图标点击事件"""
        if reason == QSystemTrayIcon.Trigger:
            self.toggle_visibility()
            
    def toggle_visibility(self):
        """切换窗口显示/隐藏"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
            
    def toggle_obs_mode(self):
        """切换 OBS 兼容模式"""
        # 切换模式
        config.OBS_COMPATIBLE_MODE = not config.OBS_COMPATIBLE_MODE
        
        # 重新设置窗口属性
        self.setupWindow()
        
        # 显示当前模式
        mode_text = "OBS 直播模式" if config.OBS_COMPATIBLE_MODE else "桌面宠物模式"
        print(f"[渲染器] 已切换到: {mode_text}")
        
        # 确保窗口可见
        if not self.isVisible():
            self.show()
    
    def toggle_click_through(self):
        """切换鼠标穿透模式"""
        # 切换穿透状态
        config.CLICK_THROUGH_ENABLED = not config.CLICK_THROUGH_ENABLED
        
        # 应用新的穿透设置
        if config.CLICK_THROUGH_ENABLED:
            # 使用 Qt 属性
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            # 使用 Windows API（更可靠）
            success = self.set_windows_click_through(True)
            if success:
                print("[渲染器] 已启用鼠标穿透（Windows API）")
            else:
                print("[渲染器] 已启用鼠标穿透（Qt 方式）")
        else:
            # 禁用穿透
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self.set_windows_click_through(False)
            print("[渲染器] 已禁用鼠标穿透")
        
        # 显示当前状态
        status_text = "启用" if config.CLICK_THROUGH_ENABLED else "禁用"
        print(f"[渲染器] 鼠标穿透: {status_text}")
    
    def toggle_resize_mode(self):
        """切换调整大小模式"""
        self.resize_mode = not self.resize_mode
        
        if self.resize_mode:
            print("[渲染器] 已启用调整模式 - 将鼠标移至窗口边缘拖拽调整大小")
            # 确保窗口可见且在最前
            if not self.isVisible():
                self.show()
            self.raise_()
        else:
            print("[渲染器] 已禁用调整模式")
            # 重置光标
            self.setCursor(QCursor(Qt.ArrowCursor))
        
        # 触发重绘以显示/隐藏边框
        self.update()
        
    def quit_application(self):
        """退出应用程序"""
        QApplication.quit()
        
    def load_model(self, model_path):
        """加载Live2D模型"""
        try:
            success = real_live2d_controller.load_model(model_path)
            if success:
                self.current_model = model_path
                # 获取最新的参数信息
                self.parameters = real_live2d_controller.get_all_parameters()
            return success
        except Exception as e:
            print(f"[渲染器] 加载模型失败: {e}")
            return False
        
    def set_parameter(self, param_name, value):
        """设置模型参数"""
        try:
            success = real_live2d_controller.set_parameter(param_name, value)
            if success and hasattr(self, 'parameters'):
                self.parameters[param_name] = value
            return success
        except Exception as e:
            print(f"[渲染器] 设置参数失败: {e}")
            return False
        
    def play_expression(self, expression_name):
        """播放表情"""
        try:
            return real_live2d_controller.play_expression(expression_name)
        except Exception as e:
            print(f"[渲染器] 播放表情失败: {e}")
            return False
        
    def play_motion(self, motion_name, motion_no, motion_priority):
        """播放动作"""
        try:
            return real_live2d_controller.play_motion(motion_name, motion_no, motion_priority)
        except Exception as e:
            print(f"[渲染器] 播放动作失败: {e}")
            return False
    
    def get_model_info(self):
        """获取模型信息"""
        return real_live2d_controller.get_model_info()
        

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭最后窗口时不退出程序
    
    # 创建渲染器
    renderer = Live2DRenderer()
    renderer.show()
    
    print(f"Live2D桌面渲染器已启动")
    print(f"窗口大小: {config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
    print(f"API端口: {config.API_PORT}")
    
    # 显示当前模式
    current_mode = "OBS 直播模式" if config.OBS_COMPATIBLE_MODE else "桌面宠物模式"
    click_through_status = "启用" if config.CLICK_THROUGH_ENABLED else "禁用"
    
    print(f"当前模式: {current_mode}")
    print(f"鼠标穿透: {click_through_status}")
    print(f"调整模式: 禁用（可通过托盘菜单启用）")
    
    print("右键托盘图标可以:")
    print("  - 显示/隐藏窗口")
    print("  - 切换 OBS 模式")
    print("  - 切换鼠标穿透")
    print("  - 切换调整模式（拖拽边框调整大小）")
    print("  - 退出程序")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()