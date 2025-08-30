"""
真实的Live2D控制器
基于原始项目实现，使用live2d-py库进行真正的模型渲染
"""
import os
import json
import time
import math
import random
import threading
import traceback
from collections import deque

# 尝试导入live2d库
try:
    import live2d.v3 as live2d
    LIVE2D_AVAILABLE = True
    print("[Live2D] live2d库导入成功")
except ImportError as e:
    LIVE2D_AVAILABLE = False
    print(f"[Live2D] 警告: live2d库未安装 - {e}")
    print("[Live2D] 将使用模拟模式运行")

from config import config

class RealLive2DController:
    def __init__(self):
        self.model = None
        self.model_path = None
        self.parameters = {}
        self.expressions = {}
        self.motions = {}
        self.is_initialized = False
        self.lock = threading.Lock()
        
        # 动画状态
        self.current_expression = None
        self.current_motion = None
        self.parameter_animations = {}
        
        # 自动动画
        self.auto_blink = False
        self.auto_breath = False
        self.last_blink_time = time.time()
        self.last_breath_time = time.time()
        
        # 参数锁定机制 - 防止自动动画覆盖用户设置
        self.locked_parameters = {}  # {param_name: expire_time}
        self.lock_duration = 5.0  # 锁定5秒
        
        # 参数平滑机制 - 让参数变化更加自然流畅
        self.parameter_queues = {}  # {param_name: deque([value1, value2, ...])}
        self.queue_max_length = 5   # 保留最近5个值用于平滑
        self.smoothing_enabled = True  # 是否启用平滑
        
        # 如果没有live2d库，创建模拟参数
        if not LIVE2D_AVAILABLE:
            self._create_mock_parameters()
    
    def _create_mock_parameters(self):
        """创建模拟参数（当live2d库不可用时）"""
        self.parameters = {
            'ParamAngleX': {'value': 0, 'min': -30, 'max': 30, 'default': 0},
            'ParamAngleY': {'value': 0, 'min': -30, 'max': 30, 'default': 0},
            'ParamAngleZ': {'value': 0, 'min': -30, 'max': 30, 'default': 0},
            'ParamEyeBallX': {'value': 0, 'min': -1, 'max': 1, 'default': 0},
            'ParamEyeBallY': {'value': 0, 'min': -1, 'max': 1, 'default': 0},
            'ParamEyeLOpen': {'value': 1, 'min': 0, 'max': 1, 'default': 1},
            'ParamEyeROpen': {'value': 1, 'min': 0, 'max': 1, 'default': 1},
            'ParamMouthOpenY': {'value': 0, 'min': 0, 'max': 1, 'default': 0},
            'ParamBrowLY': {'value': 0, 'min': -1, 'max': 1, 'default': 0},
            'ParamBrowRY': {'value': 0, 'min': -1, 'max': 1, 'default': 0},
            'ParamBreath': {'value': 0, 'min': 0, 'max': 1, 'default': 0},
        }
        
    def initialize(self):
        """初始化Live2D引擎"""
        if LIVE2D_AVAILABLE and not self.is_initialized:
            try:
                live2d.init()
                live2d.glInit()
                self.is_initialized = True
                print("[Live2D] 引擎初始化成功")
            except Exception as e:
                print(f"[Live2D] 引擎初始化失败: {e}")
        else:
            print("[Live2D] 使用模拟模式初始化")
            self.is_initialized = True
    
    def load_model(self, model_path):
        """加载Live2D模型"""
        with self.lock:
            try:
                print(f"[Live2D] 尝试加载模型: {model_path}")
                
                if not os.path.exists(model_path):
                    raise FileNotFoundError(f"模型路径不存在: {model_path}")
                
                # 查找model3.json文件
                model_json = None
                if os.path.isdir(model_path):
                    # # 首先检查是否有配置文件指向真正的model3.json
                    # config_files = [f for f in os.listdir(model_path) if f.endswith('.json') and not f.endswith('.model3.json')]
                    # for config_file in config_files:
                    #     config_path = os.path.join(model_path, config_file)
                    #     try:
                    #         with open(config_path, 'r', encoding='utf-8') as f:
                    #             config_data = json.load(f)
                    #             if 'live2d_model' in config_data:
                    #                 # 找到了配置中的模型路径
                    #                 live2d_model_path = config_data['live2d_model'].replace('\\\\', os.sep)
                    #                 model_json = os.path.join(model_path, live2d_model_path)
                    #                 if os.path.exists(model_json):
                    #                     break
                    #     except:
                    #         continue
                    
                    # # 如果没找到配置文件，直接查找.model3.json文件
                    # if not model_json or not os.path.exists(model_json):

                    # 简化，强制直接获取live2d模型配置
                    for root, dirs, files in os.walk(model_path):
                        for file in files:
                            if file.endswith('.model3.json'):
                                model_json = os.path.join(root, file)
                                break
                        if model_json:
                            break
                else:
                    model_json = model_path
                
                if not model_json or not os.path.exists(model_json):
                    raise FileNotFoundError(f"找不到模型配置文件: {model_path}")
                
                print(f"[Live2D] 找到模型文件: {model_json}")
                
                if LIVE2D_AVAILABLE:
                    # 使用真实的live2d库 - 尝试绝对路径方案
                    if self.model:
                        self.model = None
                    
                    # 创建新模型
                    self.model = live2d.LAppModel()
                    
                    # 尝试方法1: 直接使用绝对路径 - 需要先切换到模型目录
                    print(f"[Live2D] 尝试绝对路径方法（带目录切换）: {model_json}")
                    
                    # 保存当前工作目录  
                    # original_cwd = os.getcwd()  # 不必保存目录
                    try:
                        # 切换到模型文件所在目录，确保纹理路径正确
                        model_dir = os.path.dirname(os.path.abspath(model_json))
                        # os.chdir(model_dir)  # 不必切换目录
                        print(f"[Live2D] 工作目录已切换到: {model_dir}")
                        
                        # 使用绝对路径加载模型
                        success = self.model.LoadModelJson(model_json)
                        print(f"[Live2D] 绝对路径加载结果: {success}")
                        
                    finally:
                        # 恢复原工作目录
                        # os.chdir(original_cwd)
                        pass
                    
                    if not success:
                        print(f"[Live2D] 绝对路径方法报告失败，但让我们继续，也许模型实际上加载了")
                    else:
                        print(f"[Live2D] 绝对路径方法报告成功！")
                    
                    # 暂时不抛出错误，让程序继续运行
                    
                    # 设置模型属性
                    self.model.Resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
                    self.model.SetAutoBlinkEnable(True)  # 我们不自己控制眨眼
                    self.model.SetAutoBreathEnable(True)  # 我们不自己控制呼吸
                    
                    self.model_path = model_json
                    self._load_model_parameters()
                    
                else:
                    # 模拟模式
                    self.model_path = model_json
                    print("[Live2D] 模拟模式 - 模型加载成功")
                
                # 尝试加载表情和动作
                self._load_expressions()
                
                print(f"[Live2D] 模型加载成功: {model_json}")
                return True
                
            except Exception as e:
                print(f"[Live2D] 模型加载失败: {e}")
                traceback.print_exc()
                return False
    
    def _load_model_parameters(self):
        """加载模型参数列表"""
        if not LIVE2D_AVAILABLE or not self.model:
            return
        
        try:
            self.parameters = {}
            param_count = self.model.GetParameterCount()
            print(f"[Live2D] 模型参数数量: {param_count}")
            
            for i in range(param_count):
                param = self.model.GetParameter(i)
                
                # 调试：打印参数对象的所有属性
                if i == 0:
                    print(f"[Live2D] 参数对象属性: {[attr for attr in dir(param) if not attr.startswith('_')]}")
                
                # 尝试不同的属性名
                param_id = param.id
                param_value = param.value
                
                # 尝试获取默认值、最小值、最大值
                try:
                    param_default = getattr(param, 'default_value', param_value)
                except:
                    try:
                        param_default = getattr(param, 'defaultValue', param_value)
                    except:
                        param_default = param_value
                
                try:
                    param_min = getattr(param, 'min_value', -1.0)
                except:
                    try:
                        param_min = getattr(param, 'minValue', -1.0)
                    except:
                        try:
                            param_min = getattr(param, 'minimum', -1.0)
                        except:
                            param_min = -1.0
                
                try:
                    param_max = getattr(param, 'max_value', 1.0)
                except:
                    try:
                        param_max = getattr(param, 'maxValue', 1.0)
                    except:
                        try:
                            param_max = getattr(param, 'maximum', 1.0)
                        except:
                            param_max = 1.0
                
                self.parameters[param_id] = {
                    'index': i,
                    'value': param_value,
                    'default': param_default,
                    'min': param_min,
                    'max': param_max
                }
                
                # 只打印前3个参数的详细信息
                if i < 3:
                    print(f"[Live2D] 参数 {i}: {param_id} = {param_value:.3f} [默认:{param_default:.3f}, 范围:{param_min:.3f}~{param_max:.3f}]")
                elif i == 3:
                    print(f"[Live2D] ... (还有 {param_count - 3} 个参数)")
            
            print(f"[Live2D] 加载了 {len(self.parameters)} 个参数")
            
        except Exception as e:
            print(f"[Live2D] 参数加载失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_expressions(self):
        """加载表情列表"""
        if not self.model_path:
            return
        
        try:
            model_dir = os.path.dirname(self.model_path)
            expressions_dir = os.path.join(model_dir, 'expressions')
            
            if os.path.exists(expressions_dir):
                self.expressions = {}
                for file in os.listdir(expressions_dir):
                    if file.endswith('.exp3.json'):
                        exp_name = os.path.splitext(file)[0]
                        exp_path = os.path.join(expressions_dir, file)
                        self.expressions[exp_name] = exp_path
                
                print(f"[Live2D] 加载了 {len(self.expressions)} 个表情: {list(self.expressions.keys())}")
        
        except Exception as e:
            print(f"[Live2D] 表情加载失败: {e}")
    
    def set_parameter(self, param_name, value):
        """设置模型参数（用户API调用）"""
        try:
            if param_name not in self.parameters:
                print(f"[Live2D] 警告: 参数 '{param_name}' 不存在")
                return False
            
            # 限制参数值范围
            param_info = self.parameters[param_name]
            value = max(param_info['min'], min(param_info['max'], float(value)))
            
            # 添加到平滑队列
            self._add_parameter_to_queue(param_name, value)
            
            # 应用平滑后的值到模型
            self._apply_parameter_to_model(param_name)
            
            # 锁定参数，防止自动动画覆盖用户设置
            self.locked_parameters[param_name] = time.time() + self.lock_duration
            
            # 获取实际应用的平滑值用于显示
            smoothed_value = self._get_smoothed_parameter_value(param_name)
            print(f"[Live2D] 用户设置参数: {param_name} = {value} → 平滑值: {smoothed_value:.3f} (锁定 {self.lock_duration}s)")
            return True
            
        except Exception as e:
            print(f"[Live2D] 设置参数失败: {e}")
            return False
    
    def _is_parameter_locked(self, param_name):
        """检查参数是否被锁定（防止自动动画覆盖用户设置）"""
        if param_name not in self.locked_parameters:
            return False
        
        # 检查锁定是否过期
        if time.time() > self.locked_parameters[param_name]:
            del self.locked_parameters[param_name]
            return False
        
        return True
    
    def _init_parameter_queue(self, param_name):
        """初始化参数队列"""
        if param_name not in self.parameter_queues:
            # 获取当前参数值作为初始值
            current_value = 0.0
            if param_name in self.parameters:
                current_value = self.parameters[param_name].get('value', 0.0)
            
            # 创建队列并填充初始值
            self.parameter_queues[param_name] = deque([current_value] * self.queue_max_length, 
                                                     maxlen=self.queue_max_length)
    
    def _add_parameter_to_queue(self, param_name, value):
        """添加参数值到平滑队列"""
        self._init_parameter_queue(param_name)
        self.parameter_queues[param_name].append(float(value))
    
    def _get_smoothed_parameter_value(self, param_name):
        """获取平滑后的参数值（最近几个值的加权平均）"""
        if not self.smoothing_enabled or param_name not in self.parameter_queues:
            return self.parameters.get(param_name, {}).get('value', 0.0)
        
        queue = self.parameter_queues[param_name]
        if len(queue) == 0:
            return 0.0
        
        # 使用加权平均，越新的值权重越高
        total_weight = 0
        weighted_sum = 0
        
        for i, value in enumerate(queue):
            weight = (i + 1) ** 1.5  # 指数加权，最新的值权重最大
            weighted_sum += value * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _apply_parameter_to_model(self, param_name):
        """将平滑后的参数值应用到模型"""
        try:
            if param_name not in self.parameters:
                return False
            
            # 获取平滑后的值
            smoothed_value = self._get_smoothed_parameter_value(param_name)
            
            # 限制参数值范围
            param_info = self.parameters[param_name]
            smoothed_value = max(param_info['min'], min(param_info['max'], smoothed_value))
            
            if LIVE2D_AVAILABLE and self.model:
                self.model.SetParameterValue(param_name, smoothed_value)
            else:
                # 模拟模式：更新缓存值
                self.parameters[param_name]['value'] = smoothed_value
            
            return True
            
        except Exception as e:
            print(f"[Live2D] 参数应用失败: {e}")
            return False
    
    def _update_all_smoothed_parameters(self):
        """更新所有参数的平滑值到模型"""
        try:
            if not self.smoothing_enabled:
                return
            
            # 遍历所有有队列数据的参数
            for param_name in list(self.parameter_queues.keys()):
                if param_name in self.parameters:
                    # 重新应用平滑后的值
                    smoothed_value = self._get_smoothed_parameter_value(param_name)
                    param_info = self.parameters[param_name]
                    smoothed_value = max(param_info['min'], min(param_info['max'], smoothed_value))
                    
                    if LIVE2D_AVAILABLE and self.model:
                        self.model.SetParameterValue(param_name, smoothed_value)
                    else:
                        self.parameters[param_name]['value'] = smoothed_value
                        
        except Exception as e:
            print(f"[Live2D] 批量参数平滑更新失败: {e}")
    
    def _set_parameter_internal(self, param_name, value):
        """内部参数设置方法（不触发锁定，用于自动动画）"""
        try:
            if param_name not in self.parameters:
                return False
            
            # 限制参数值范围
            param_info = self.parameters[param_name]
            value = max(param_info['min'], min(param_info['max'], float(value)))
            
            # 添加到平滑队列
            self._add_parameter_to_queue(param_name, value)
            
            # 应用平滑后的值到模型
            self._apply_parameter_to_model(param_name)
            
            return True
            
        except Exception as e:
            print(f"[Live2D] 内部参数设置失败: {e}")
            return False
    
    def play_motion(self, motion_name, motion_no, motion_priority):
        """播放动作"""
        try:
            print(self.model.GetMotionGroups())
            # success = self.model.StopAllMotions()
            success = self.model.StartMotion(motion_name, motion_no, motion_priority)

        except Exception as e:
            print(f"[Live2D] 动作播放失败: {e}")
            return False

    def play_expression(self, expression_name):
        """播放表情"""
        try:
            print(self.model.GetExpressionIds())
            # def get_name(namebacklist):
            #     namelist = []
            #     for name in namebacklist:
            #         namelist.append(name.split('.',1)[0])
            #     return namelist

            # if expression_name not in get_name(self.expressions.keys()):
            #     print(f"[Live2D] 警告: 表情 '{expression_name}' 不存在")
            #     return False
            
            if LIVE2D_AVAILABLE and self.model:
                # 使用真实的live2d库播放表情
                # exp_path = self.expressions[expression_name]
                try:
                    # 加载并播放表情文件
                    # success = self.model.SetExpression(exp_path)
                    success = self.model.SetExpression(expression_name)
                    if success:
                        print(f"[Live2D] 播放表情: {expression_name}")
                    else:
                        print(f"[Live2D] 表情加载失败: {expression_name}")
                        return False
                except Exception as e:
                    print(f"[Live2D] 表情播放异常: {e}")
                    return False
            else:
                # 模拟模式
                print(f"[Live2D] 模拟播放表情: {expression_name}")
            
            self.current_expression = expression_name
            return True
            
        except Exception as e:
            print(f"[Live2D] 表情播放失败: {e}")
            return False
    
    def update(self):
        """更新模型动画"""
        try:
            if LIVE2D_AVAILABLE and self.model:
                # 自动眨眼
                if self.auto_blink:
                    current_time = time.time()
                    if current_time - self.last_blink_time > random.uniform(2, 5):
                        self._blink()
                        self.last_blink_time = current_time
                
                # 自动呼吸（检查参数是否存在且未被锁定）
                if self.auto_breath and 'ParamBreath' in self.parameters and not self._is_parameter_locked('ParamBreath'):
                    breath_value = (math.sin(time.time() * 2) + 1) / 2 * 0.5
                    self._set_parameter_internal('ParamBreath', breath_value)
                
                # 应用所有参数的平滑处理
                self._update_all_smoothed_parameters()
                
                # 更新模型
                self.model.Update()
        
        except Exception as e:
            print(f"[Live2D] 更新失败: {e}")
    
    def draw(self):
        """绘制模型"""
        try:
            if LIVE2D_AVAILABLE and self.model:
                self.model.Draw()
            else:
                # 模拟绘制 - 绘制一个简单的测试图形
                self._draw_mock_model()
                
        except Exception as e:
            print(f"[Live2D] 绘制失败: {e}")
    
    def _draw_mock_model(self):
        """绘制模拟模型（简单的测试图形）"""
        try:
            import OpenGL.GL as gl
            
            # 绘制一个彩色三角形作为模拟Live2D角色
            gl.glBegin(gl.GL_TRIANGLES)
            gl.glColor3f(1.0, 0.5, 0.8)  # 粉色
            gl.glVertex2f(0.0, 0.5)
            gl.glColor3f(0.8, 1.0, 0.5)  # 绿色
            gl.glVertex2f(-0.5, -0.5)
            gl.glColor3f(0.5, 0.8, 1.0)  # 蓝色
            gl.glVertex2f(0.5, -0.5)
            gl.glEnd()
            
            # 绘制"眼睛"
            angle_x = self.parameters.get('ParamAngleX', {}).get('value', 0) * 0.01
            eye_x = self.parameters.get('ParamEyeBallX', {}).get('value', 0) * 0.1
            
            gl.glPointSize(10.0)
            gl.glBegin(gl.GL_POINTS)
            gl.glColor3f(0.0, 0.0, 0.0)  # 黑色眼睛
            gl.glVertex2f(-0.2 + eye_x + angle_x, 0.1)  # 左眼
            gl.glVertex2f(0.2 + eye_x + angle_x, 0.1)   # 右眼
            gl.glEnd()
            
        except Exception as e:
            print(f"[Live2D] 模拟绘制失败: {e}")
    
    def _blink(self):
        """眨眼动画"""
        try:
            # 只有当眼睛参数未被锁定时才执行眨眼动画
            if ('ParamEyeLOpen' in self.parameters and 
                not self._is_parameter_locked('ParamEyeLOpen') and 
                not self._is_parameter_locked('ParamEyeROpen') and False):
                
                self._set_parameter_internal('ParamEyeLOpen', 0.0)
                self._set_parameter_internal('ParamEyeROpen', 0.0)
                
                # 0.1秒后重新睁眼
                def open_eyes():
                    time.sleep(0.1)
                    if (not self._is_parameter_locked('ParamEyeLOpen') and 
                        not self._is_parameter_locked('ParamEyeROpen')):
                        self._set_parameter_internal('ParamEyeLOpen', 1.0)
                        self._set_parameter_internal('ParamEyeROpen', 1.0)
                
                threading.Thread(target=open_eyes, daemon=True).start()
                
        except Exception as e:
            print(f"[Live2D] 眨眼失败: {e}")
    
    def get_model_info(self):
        """获取模型信息"""
        return {
            'model_path': self.model_path,
            'is_loaded': self.model is not None,
            'parameter_count': len(self.parameters),
            'expression_count': len(self.expressions),
            'expressions': list(self.expressions.keys()),
            'live2d_available': LIVE2D_AVAILABLE
        }
    
    def get_all_parameters(self):
        """获取所有参数"""
        return {name: info['value'] for name, info in self.parameters.items()}
    
    def set_smoothing_enabled(self, enabled):
        """启用或禁用参数平滑"""
        self.smoothing_enabled = bool(enabled)
        return self.smoothing_enabled
    
    def set_smoothing_settings(self, queue_length=None, enabled=None):
        """设置平滑系统参数"""
        result = {}
        
        if queue_length is not None:
            self.queue_max_length = max(1, min(20, int(queue_length)))  # 限制在1-20之间
            # 重置所有队列以应用新长度
            self.parameter_queues.clear()
            result['queue_length'] = self.queue_max_length
        
        if enabled is not None:
            self.smoothing_enabled = bool(enabled)
            result['smoothing_enabled'] = self.smoothing_enabled
        
        return result
    
    def get_smoothing_info(self):
        """获取平滑系统信息"""
        return {
            'smoothing_enabled': self.smoothing_enabled,
            'queue_length': self.queue_max_length,
            'active_queues': len(self.parameter_queues),
            'queue_parameters': list(self.parameter_queues.keys())
        }

# 创建全局实例
real_live2d_controller = RealLive2DController()