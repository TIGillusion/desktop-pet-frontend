"""
简化的Flask API服务
提供HTTP接口用于控制Live2D模型
"""
import os
import json
import threading
import traceback
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import config

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局渲染器引用（将由主程序设置）
renderer = None

@app.errorhandler(500)
def handle_500(e):
    """处理内部服务器错误"""
    return jsonify({
        'success': False,
        'error': '内部服务器错误',
        'timestamp': datetime.now().isoformat()
    }), 500

@app.errorhandler(404)
def handle_404(e):
    """处理资源未找到错误"""
    return jsonify({
        'success': False,
        'error': '资源未找到',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.route('/')
def index():
    """API首页"""
    return jsonify({
        'name': 'Live2D Desktop API',
        'version': '1.0.0',
        'status': 'running',
        'renderer_connected': renderer is not None,
        'api_port': config.API_PORT,
        'endpoints': {
            # 基础功能
            'GET /': '获取API信息',
            'GET /models': '获取可用模型列表',
            'POST /load_model': '加载指定模型',
            'GET /model/info': '获取当前模型信息',
            
            # 参数控制
            'POST /model/parameter': '设置单个参数',
            'POST /model/parameters': '批量设置参数',
            'POST /model/parameter_detailed': '设置参数（包含权重）',
            'POST /model/parameter/add': '添加参数值',
            'POST /model/parameter/by_index': '通过索引设置参数',
            'POST /model/parameter/add_by_index': '通过索引添加参数值',
            'GET /model/parameters/info': '获取所有参数信息',
            
            # 表情控制
            'POST /model/expression': '播放表情',
            'POST /model/expression/random': '设置随机表情',
            'POST /model/expression/add': '添加表情',
            'POST /model/expression/remove': '移除表情',
            'GET /model/expressions/info': '获取表情信息',
            
            # 动作控制
            'POST /model/motion': '播放动作',
            'POST /model/motion/random': '开始随机动作',
            'GET /model/motion/finished': '检查动作是否完成',
            'POST /model/motions/stop': '停止所有动作',
            'GET /model/motions/info': '获取动作信息',
            
            # 模型变换
            'POST /model/resize': '调整模型画布大小',
            'POST /model/offset': '设置模型偏移',
            'POST /model/offset_x': '设置X轴偏移',
            'POST /model/offset_y': '设置Y轴偏移',
            'POST /model/scale': '设置模型缩放',
            'POST /model/rotate': '旋转模型',
            
            # 交互功能
            'POST /model/hit_test': '点击测试',
            'POST /model/drag': '拖拽模型',
            'POST /model/part/hit': '点击部件测试',
            
            # 部件控制
            'GET /model/parts/info': '获取部件信息',
            'POST /model/part/opacity': '设置部件透明度',
            'POST /model/part/screen_color': '设置部件屏幕颜色',
            'POST /model/part/multiply_color': '设置部件乘法颜色',
            'POST /model/part/screen_color/get': '获取部件屏幕颜色',
            'POST /model/part/multiply_color/get': '获取部件乘法颜色',
            
            # 可绘制对象
            'GET /model/drawable/info': '获取可绘制对象信息',
            'POST /model/drawable/multiply_color': '设置可绘制对象乘法颜色',
            'POST /model/drawable/screen_color': '设置可绘制对象屏幕颜色',
            
            # 自动功能
            'POST /model/auto_breath': '设置自动呼吸',
            'POST /model/auto_blink': '设置自动眨眼',
            'POST /model/mouth': '设置嘴部开合',
            
            # 重置功能
            'POST /model/reset/expression': '重置表情',
            'POST /model/reset/expressions': '重置所有表情',
            'POST /model/reset/parameters': '重置参数',
            'POST /model/reset/pose': '重置姿态',
            
            # 信息查询
            'GET /model/canvas/info': '获取画布信息',
            'POST /model/sound_path': '获取音频文件路径',
            'POST /model/moc_consistency': '检查MOC文件一致性',
            
            # 平滑系统
            'GET /model/smoothing': '获取参数平滑系统信息',
            'POST /model/smoothing': '设置平滑参数',
        }
    })

@app.route('/models', methods=['GET'])
def get_models():
    """获取可用模型列表"""
    try:
        models = []
        models_dir = config.MODELS_DIR
        
        if os.path.exists(models_dir):
            for item in os.listdir(models_dir):
                model_path = os.path.join(models_dir, item)
                if os.path.isdir(model_path):
                    # 查找model3.json文件
                    for file in os.listdir(model_path):
                        if file.endswith('.json'):
                            json_path = os.path.join(model_path, file)
                            try:
                                with open(json_path, 'r', encoding='utf-8') as f:
                                    model_info = json.load(f)
                                    models.append({
                                        'name': item,
                                        'path': model_path,
                                        'json_file': file,
                                        'info': model_info
                                    })
                                    break
                            except Exception as e:
                                print(f"读取模型信息失败: {json_path}, 错误: {e}")
        
        return jsonify({
            'success': True,
            'models': models,
            'count': len(models)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/load_model', methods=['POST'])
def load_model():
    """加载指定模型"""
    return jsonify({
                'success': False,
                'error': f'此路由已停止服务（有bug）'
            }), 200
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        
        if not model_name:
            return jsonify({
                'success': False,
                'error': '缺少model_name参数'
            }), 400
        
        model_path = os.path.join(config.MODELS_DIR, model_name)
        
        if not os.path.exists(model_path):
            return jsonify({
                'success': False,
                'error': f'模型不存在: {model_name}'
            }), 404
        
        # 调用渲染器加载模型
        if renderer:
            success = renderer.load_model(model_path)
            return jsonify({
                'success': success,
                'model_name': model_name,
                'model_path': model_path
            })
        else:
            return jsonify({
                'success': False,
                'error': '渲染器未连接'
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/model/info', methods=['GET'])
def get_model_info():
    """获取当前模型信息"""
    try:
        if renderer and hasattr(renderer, 'current_model') and renderer.current_model:
            return jsonify({
                'success': True,
                'current_model': renderer.current_model,
                'parameters': getattr(renderer, 'parameters', {})
            })
        else:
            return jsonify({
                'success': False,
                'error': '未加载模型'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/model/parameter', methods=['POST'])
def set_parameter():
    """设置单个参数"""
    try:
        data = request.get_json()
        param_name = data.get('name')
        value = data.get('value')
        
        if param_name is None or value is None:
            return jsonify({
                'success': False,
                'error': '缺少name或value参数'
            }), 400
        
        if renderer:
            renderer.set_parameter(param_name, value)
            return jsonify({
                'success': True,
                'parameter': param_name,
                'value': value
            })
        else:
            return jsonify({
                'success': False,
                'error': '渲染器未连接'
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/model/parameters', methods=['POST'])
def set_parameters():
    """批量设置参数"""
    try:
        data = request.get_json()
        parameters = data.get('parameters', {})
        
        if not isinstance(parameters, dict):
            return jsonify({
                'success': False,
                'error': 'parameters必须是字典格式'
            }), 400
        
        if renderer:
            for param_name, value in parameters.items():
                renderer.set_parameter(param_name, value)
            
            return jsonify({
                'success': True,
                'parameters_set': len(parameters),
                'parameters': parameters
            })
        else:
            return jsonify({
                'success': False,
                'error': '渲染器未连接'
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/model/motion', methods=['POST'])
def play_motion():
    """播放动作"""
    try:
        data = request.get_json()
        motion_name = data.get('motion')
        motion_no = data.get("no")
        motion_priority = data.get("priority")
        
        if not motion_name:
            return jsonify({
                'success': False,
                'error': '缺少motion参数'
            }), 400
        
        if renderer:
            renderer.play_motion(motion_name, motion_no, motion_priority)
            return jsonify({
                'success': True,
                'motion': motion_name,
                'no':motion_no,
                "priority": motion_priority
            })
        else:
            return jsonify({
                'success': False,
                'error': '渲染器未连接'
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/model/expression', methods=['POST'])
def play_expression():
    """播放表情"""
    try:
        data = request.get_json()
        expression_name = data.get('expression')
        
        if not expression_name:
            return jsonify({
                'success': False,
                'error': '缺少expression参数'
            }), 400
        
        if renderer:
            renderer.play_expression(expression_name)
            return jsonify({
                'success': True,
                'expression': expression_name
            })
        else:
            return jsonify({
                'success': False,
                'error': '渲染器未连接'
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/model/mouth', methods=['POST'])
def set_mouth():
    """设置嘴部开合"""
    try:
        data = request.get_json()
        mouth_open = data.get('open', 0.0)
        
        if renderer:
            renderer.set_parameter('ParamMouthOpenY', mouth_open)
            return jsonify({
                'success': True,
                'mouth_open': mouth_open
            })
        else:
            return jsonify({
                'success': False,
                'error': '渲染器未连接'
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def set_renderer(renderer_instance):
    """设置渲染器引用"""
    global renderer
    renderer = renderer_instance

def start_api_server(live2d_model_name):
    """启动API服务器"""
    print(f"启动API服务器: http://{config.API_HOST}:{config.API_PORT}")

    # 临时保存端口信息用于后期需要；出于分布式部署考虑，可能需要http传递相关信息
    data = {
        "name":live2d_model_name,
        "port":config.API_PORT,
        "host":config.API_HOST
    }
    with open(f"temp/running/{live2d_model_name}.json", "w", encoding='utf-8') as f: # 此文件用于后期偶尔数据交换 
        json.dump(data, f, indent=4)

    app.run(
        host=config.API_HOST,
        port=config.API_PORT,
        debug=config.API_DEBUG,
        use_reloader=False,  # 禁用重载器以避免多线程问题
        threaded=True
    )

def start_api_server_thread(live2d_model_name):
    """在后台线程中启动API服务器"""
    api_thread = threading.Thread(target=start_api_server, args=live2d_model_name, daemon=True)
    api_thread.start()
    return api_thread

@app.route('/model/smoothing', methods=['GET'])
def get_smoothing_info():
    """获取参数平滑系统信息"""
    try:
        if renderer is None or not hasattr(renderer, 'controller'):
            return jsonify({'success': False, 'error': '渲染器未连接'})
        
        smoothing_info = renderer.controller.get_smoothing_info()
        return jsonify({
            'success': True,
            'smoothing_info': smoothing_info
        })
        
    except Exception as e:
        print(f"[API] 获取平滑信息失败: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)})

@app.route('/model/smoothing', methods=['POST'])
def set_smoothing_settings():
    """设置参数平滑系统"""
    try:
        if renderer is None or not hasattr(renderer, 'controller'):
            return jsonify({'success': False, 'error': '渲染器未连接'})
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '无效的JSON数据'})
        
        # 获取参数
        enabled = data.get('enabled')
        queue_length = data.get('queue_length')
        
        # 应用设置
        result = renderer.controller.set_smoothing_settings(
            enabled=enabled,
            queue_length=queue_length
        )
        
        return jsonify({
            'success': True,
            'settings': result,
            'current_info': renderer.controller.get_smoothing_info()
        })
        
    except Exception as e:
        print(f"[API] 设置平滑参数失败: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)})

# ========== LAppModel 接口实现 ==========

def get_model():
    """获取 LAppModel 实例的辅助函数"""
    if renderer is None:
        return None
    
    # 方式1: 通过 real_live2d_controller 全局实例访问
    try:
        from real_live2d_controller import real_live2d_controller
        if real_live2d_controller and real_live2d_controller.model:
            return real_live2d_controller.model
    except (ImportError, AttributeError):
        pass
    
    # 方式2: 从渲染器获取控制器
    if hasattr(renderer, 'controller') and hasattr(renderer.controller, 'model'):
        return renderer.controller.model
    
    # 方式3: 直接从渲染器获取模型（适配不同的结构）
    if hasattr(renderer, 'model'):
        return renderer.model
    
    # 方式4: 检查渲染器是否有 real_live2d_controller 的引用
    if hasattr(renderer, 'real_live2d_controller') and hasattr(renderer.real_live2d_controller, 'model'):
        return renderer.real_live2d_controller.model
    
    return None

@app.route('/model/resize', methods=['POST'])
def resize_model():
    """调整模型画布大小"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        width = data.get('width')
        height = data.get('height')
        
        if width is None or height is None:
            return jsonify({'success': False, 'error': '缺少width或height参数'}), 400
        
        model.Resize(width, height)
        
        return jsonify({
            'success': True,
            'width': width,
            'height': height
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/motion/random', methods=['POST'])
def start_random_motion():
    """开始随机动作"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json() or {}
        group = data.get('group')
        priority = data.get('priority', 3)
        
        model.StartRandomMotion(group, priority)
        
        return jsonify({
            'success': True,
            'group': group,
            'priority': priority
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/expression/random', methods=['POST'])
def set_random_expression():
    """设置随机表情"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        expression_id = model.SetRandomExpression()
        
        return jsonify({
            'success': True,
            'expression_id': expression_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/hit_test', methods=['POST'])
def hit_test():
    """点击测试"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        hit_area_name = data.get('hit_area_name')
        x = data.get('x')
        y = data.get('y')
        
        if not hit_area_name or x is None or y is None:
            return jsonify({'success': False, 'error': '缺少hit_area_name、x或y参数'}), 400
        
        is_hit = model.HitTest(hit_area_name, x, y)
        
        return jsonify({
            'success': True,
            'hit_area_name': hit_area_name,
            'x': x,
            'y': y,
            'is_hit': is_hit
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/drag', methods=['POST'])
def drag_model():
    """拖拽模型"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        
        if x is None or y is None:
            return jsonify({'success': False, 'error': '缺少x或y参数'}), 400
        
        model.Drag(x, y)
        
        return jsonify({
            'success': True,
            'x': x,
            'y': y
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/offset', methods=['POST'])
def set_offset():
    """设置模型偏移"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        dx = data.get('dx')
        dy = data.get('dy')
        
        if dx is None or dy is None:
            return jsonify({'success': False, 'error': '缺少dx或dy参数'}), 400
        
        model.SetOffset(dx, dy)
        
        return jsonify({
            'success': True,
            'dx': dx,
            'dy': dy
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/scale', methods=['POST'])
def set_scale():
    """设置模型缩放"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        scale = data.get('scale')
        
        if scale is None:
            return jsonify({'success': False, 'error': '缺少scale参数'}), 400
        
        model.SetScale(scale)
        
        return jsonify({
            'success': True,
            'scale': scale
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/rotate', methods=['POST'])
def rotate_model():
    """旋转模型"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        degrees = data.get('degrees')
        
        if degrees is None:
            return jsonify({'success': False, 'error': '缺少degrees参数'}), 400
        
        model.Rotate(degrees)
        
        return jsonify({
            'success': True,
            'degrees': degrees
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/parameter_detailed', methods=['POST'])
def set_parameter_detailed():
    """设置参数（包含权重）"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        param_id = data.get('param_id')
        value = data.get('value')
        weight = data.get('weight', 1.0)
        
        if param_id is None or value is None:
            return jsonify({'success': False, 'error': '缺少param_id或value参数'}), 400
        
        model.SetParameterValue(param_id, value, weight)
        
        return jsonify({
            'success': True,
            'param_id': param_id,
            'value': value,
            'weight': weight
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/parameter/add', methods=['POST'])
def add_parameter_value():
    """添加参数值"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        param_id = data.get('param_id')
        value = data.get('value')
        
        if param_id is None or value is None:
            return jsonify({'success': False, 'error': '缺少param_id或value参数'}), 400
        
        model.AddParameterValue(param_id, value)
        
        return jsonify({
            'success': True,
            'param_id': param_id,
            'added_value': value
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/auto_breath', methods=['POST'])
def set_auto_breath():
    """设置自动呼吸"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        enable = data.get('enable')
        
        if enable is None:
            return jsonify({'success': False, 'error': '缺少enable参数'}), 400
        
        model.SetAutoBreathEnable(enable)
        
        return jsonify({
            'success': True,
            'auto_breath_enabled': enable
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/auto_blink', methods=['POST'])
def set_auto_blink():
    """设置自动眨眼"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        enable = data.get('enable')
        
        if enable is None:
            return jsonify({'success': False, 'error': '缺少enable参数'}), 400
        
        model.SetAutoBlinkEnable(enable)
        
        return jsonify({
            'success': True,
            'auto_blink_enabled': enable
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/parameters/info', methods=['GET'])
def get_parameters_info():
    """获取所有参数信息"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        param_count = model.GetParameterCount()
        param_ids = model.GetParamIds()
        
        parameters_info = []
        for i in range(param_count):
            param = model.GetParameter(i)
            parameters_info.append({
                'index': i,
                'id': param_ids[i] if i < len(param_ids) else f"param_{i}",
                'current_value': model.GetParameterValue(i),
                'parameter_obj': str(param)  # Parameter对象的字符串表示
            })
        
        return jsonify({
            'success': True,
            'parameter_count': param_count,
            'parameters': parameters_info
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/parts/info', methods=['GET'])
def get_parts_info():
    """获取部件信息"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        part_count = model.GetPartCount()
        part_ids = model.GetPartIds()
        
        parts_info = []
        for i in range(part_count):
            parts_info.append({
                'index': i,
                'id': part_ids[i] if i < len(part_ids) else f"part_{i}"
            })
        
        return jsonify({
            'success': True,
            'part_count': part_count,
            'parts': parts_info
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/part/opacity', methods=['POST'])
def set_part_opacity():
    """设置部件透明度"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        index = data.get('index')
        opacity = data.get('opacity')
        
        if index is None or opacity is None:
            return jsonify({'success': False, 'error': '缺少index或opacity参数'}), 400
        
        model.SetPartOpacity(index, opacity)
        
        return jsonify({
            'success': True,
            'part_index': index,
            'opacity': opacity
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/part/hit', methods=['POST'])
def hit_part():
    """点击部件测试"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        top_only = data.get('top_only', False)
        
        if x is None or y is None:
            return jsonify({'success': False, 'error': '缺少x或y参数'}), 400
        
        hit_parts = model.HitPart(x, y, top_only)
        
        return jsonify({
            'success': True,
            'x': x,
            'y': y,
            'top_only': top_only,
            'hit_parts': hit_parts
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/part/screen_color', methods=['POST'])
def set_part_screen_color():
    """设置部件屏幕颜色"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        part_index = data.get('part_index')
        r = data.get('r', 0.0)
        g = data.get('g', 0.0)
        b = data.get('b', 0.0)
        a = data.get('a', 1.0)
        
        if part_index is None:
            return jsonify({'success': False, 'error': '缺少part_index参数'}), 400
        
        model.SetPartScreenColor(part_index, r, g, b, a)
        
        return jsonify({
            'success': True,
            'part_index': part_index,
            'color': {'r': r, 'g': g, 'b': b, 'a': a}
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/part/multiply_color', methods=['POST'])
def set_part_multiply_color():
    """设置部件乘法颜色"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        part_index = data.get('part_index')
        r = data.get('r', 1.0)
        g = data.get('g', 1.0)
        b = data.get('b', 1.0)
        a = data.get('a', 1.0)
        
        if part_index is None:
            return jsonify({'success': False, 'error': '缺少part_index参数'}), 400
        
        model.SetPartMultiplyColor(part_index, r, g, b, a)
        
        return jsonify({
            'success': True,
            'part_index': part_index,
            'color': {'r': r, 'g': g, 'b': b, 'a': a}
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/drawable/info', methods=['GET'])
def get_drawable_info():
    """获取可绘制对象信息"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        drawable_ids = model.GetDrawableIds()
        
        return jsonify({
            'success': True,
            'drawable_count': len(drawable_ids),
            'drawable_ids': drawable_ids
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/drawable/multiply_color', methods=['POST'])
def set_drawable_multiply_color():
    """设置可绘制对象乘法颜色"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        index = data.get('index')
        r = data.get('r', 1.0)
        g = data.get('g', 1.0)
        b = data.get('b', 1.0)
        a = data.get('a', 1.0)
        
        if index is None:
            return jsonify({'success': False, 'error': '缺少index参数'}), 400
        
        model.SetDrawableMultiplyColor(index, r, g, b, a)
        
        return jsonify({
            'success': True,
            'drawable_index': index,
            'color': {'r': r, 'g': g, 'b': b, 'a': a}
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/drawable/screen_color', methods=['POST'])
def set_drawable_screen_color():
    """设置可绘制对象屏幕颜色"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        index = data.get('index')
        r = data.get('r', 0.0)
        g = data.get('g', 0.0)
        b = data.get('b', 0.0)
        a = data.get('a', 1.0)
        
        if index is None:
            return jsonify({'success': False, 'error': '缺少index参数'}), 400
        
        model.SetDrawableScreenColor(index, r, g, b, a)
        
        return jsonify({
            'success': True,
            'drawable_index': index,
            'color': {'r': r, 'g': g, 'b': b, 'a': a}
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/expressions/info', methods=['GET'])
def get_expressions_info():
    """获取表情信息"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        expression_ids = model.GetExpressionIds()
        
        return jsonify({
            'success': True,
            'expression_count': len(expression_ids),
            'expression_ids': expression_ids
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/motions/info', methods=['GET'])
def get_motions_info():
    """获取动作信息"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        motion_groups = model.GetMotionGroups()
        
        return jsonify({
            'success': True,
            'motion_groups': motion_groups
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/motion/finished', methods=['GET'])
def is_motion_finished():
    """检查动作是否完成"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        finished = model.IsMotionFinished()
        
        return jsonify({
            'success': True,
            'motion_finished': finished
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/canvas/info', methods=['GET'])
def get_canvas_info():
    """获取画布信息"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        canvas_size = model.GetCanvasSize()
        canvas_size_pixel = model.GetCanvasSizePixel()
        pixels_per_unit = model.GetPixelsPerUnit()
        
        return jsonify({
            'success': True,
            'canvas_size': canvas_size,
            'canvas_size_pixel': canvas_size_pixel,
            'pixels_per_unit': pixels_per_unit
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/reset/expression', methods=['POST'])
def reset_expression():
    """重置表情"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        model.ResetExpression()
        
        return jsonify({
            'success': True,
            'message': '表情已重置'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/reset/parameters', methods=['POST'])
def reset_parameters():
    """重置参数"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        model.ResetParameters()
        
        return jsonify({
            'success': True,
            'message': '参数已重置'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/reset/pose', methods=['POST'])
def reset_pose():
    """重置姿态"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        model.ResetPose()
        
        return jsonify({
            'success': True,
            'message': '姿态已重置'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/motions/stop', methods=['POST'])
def stop_all_motions():
    """停止所有动作"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        model.StopAllMotions()
        
        return jsonify({
            'success': True,
            'message': '所有动作已停止'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== 增强功能路由 ==========

@app.route('/model/sound_path', methods=['POST'])
def get_sound_path():
    """获取音频文件路径"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        group = data.get('group')
        index = data.get('index')
        
        if group is None or index is None:
            return jsonify({'success': False, 'error': '缺少group或index参数'}), 400
        
        sound_path = model.GetSoundPath(group, index)
        
        return jsonify({
            'success': True,
            'group': group,
            'index': index,
            'sound_path': sound_path
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== 补充遗漏的接口 ==========

@app.route('/model/parameter/by_index', methods=['POST'])
def set_parameter_by_index():
    """通过索引设置参数"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        index = data.get('index')
        value = data.get('value')
        weight = data.get('weight', 1.0)
        
        if index is None or value is None:
            return jsonify({'success': False, 'error': '缺少index或value参数'}), 400
        
        model.SetIndexParamValue(index, value, weight)
        
        return jsonify({
            'success': True,
            'parameter_index': index,
            'value': value,
            'weight': weight
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/parameter/add_by_index', methods=['POST'])
def add_parameter_value_by_index():
    """通过索引添加参数值"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        index = data.get('index')
        value = data.get('value')
        
        if index is None or value is None:
            return jsonify({'success': False, 'error': '缺少index或value参数'}), 400
        
        model.AddIndexParamValue(index, value)
        
        return jsonify({
            'success': True,
            'parameter_index': index,
            'added_value': value
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/moc_consistency', methods=['POST'])
def check_moc_consistency():
    """检查MOC文件一致性"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        moc_file_name = data.get('moc_file_name')
        
        if not moc_file_name:
            return jsonify({'success': False, 'error': '缺少moc_file_name参数'}), 400
        
        is_consistent = model.HasMocConsistencyFromFile(moc_file_name)
        
        return jsonify({
            'success': True,
            'moc_file_name': moc_file_name,
            'is_consistent': is_consistent
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/offset_x', methods=['POST'])
def set_offset_x():
    """设置X轴偏移"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        sx = data.get('sx')
        
        if sx is None:
            return jsonify({'success': False, 'error': '缺少sx参数'}), 400
        
        model.SetOffsetX(sx)
        
        return jsonify({
            'success': True,
            'offset_x': sx
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/offset_y', methods=['POST'])
def set_offset_y():
    """设置Y轴偏移"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        sy = data.get('sy')
        
        if sy is None:
            return jsonify({'success': False, 'error': '缺少sy参数'}), 400
        
        model.SetOffsetY(sy)
        
        return jsonify({
            'success': True,
            'offset_y': sy
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/expression/add', methods=['POST'])
def add_expression():
    """添加表情"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        exp_id = data.get('expression_id')
        
        if not exp_id:
            return jsonify({'success': False, 'error': '缺少expression_id参数'}), 400
        
        model.AddExpression(exp_id)
        
        return jsonify({
            'success': True,
            'expression_id': exp_id,
            'message': '表情已添加'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/expression/remove', methods=['POST'])
def remove_expression():
    """移除表情"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        exp_id = data.get('expression_id')
        
        if not exp_id:
            return jsonify({'success': False, 'error': '缺少expression_id参数'}), 400
        
        model.RemoveExpression(exp_id)
        
        return jsonify({
            'success': True,
            'expression_id': exp_id,
            'message': '表情已移除'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/reset/expressions', methods=['POST'])
def reset_expressions():
    """重置所有表情"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        model.ResetExpressions()
        
        return jsonify({
            'success': True,
            'message': '所有表情已重置'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/part/screen_color/get', methods=['POST'])
def get_part_screen_color():
    """获取部件屏幕颜色"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        part_index = data.get('part_index')
        
        if part_index is None:
            return jsonify({'success': False, 'error': '缺少part_index参数'}), 400
        
        color = model.GetPartScreenColor(part_index)
        
        return jsonify({
            'success': True,
            'part_index': part_index,
            'color': {'r': color[0], 'g': color[1], 'b': color[2], 'a': color[3]} if color else None
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/model/part/multiply_color/get', methods=['POST'])
def get_part_multiply_color():
    """获取部件乘法颜色"""
    try:
        model = get_model()
        if not model:
            return jsonify({'success': False, 'error': '模型未加载或渲染器未连接'}), 503
        
        data = request.get_json()
        part_index = data.get('part_index')
        
        if part_index is None:
            return jsonify({'success': False, 'error': '缺少part_index参数'}), 400
        
        color = model.GetPartMultiplyColor(part_index)
        
        return jsonify({
            'success': True,
            'part_index': part_index,
            'color': {'r': color[0], 'g': color[1], 'b': color[2], 'a': color[3]} if color else None
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("此处已停止服务...")
    # """直接运行此文件时启动完整的API服务"""
    # print("=" * 50)
    # print("Live2D Desktop API 服务")
    # print("=" * 50)
    
    # # 导入真实的Live2D控制器
    # from real_live2d_controller import real_live2d_controller
    
    # # 初始化Live2D引擎
    # real_live2d_controller.initialize()
    
    # # 创建适配器将控制器接口适配到渲染器接口
    # class Live2DControllerAdapter:
    #     def __init__(self, controller):
    #         self.controller = controller
    #         print("✓ Live2D控制器适配器已初始化")
            
    #     @property
    #     def current_model(self):
    #         return self.controller.model_path
            
    #     @property
    #     def parameters(self):
    #         return self.controller.get_all_parameters()
            
    #     def load_model(self, model_path):
    #         return self.controller.load_model(model_path)
            
    #     def set_parameter(self, param_name, value):
    #         return self.controller.set_parameter(param_name, value)
            
    #     def play_expression(self, expression_name):
    #         return self.controller.play_expression(expression_name)
        
    #     def play_motion(self, motion_name, motion_no, motion_priority):
    #         return self.controller.play_motion(motion_name, motion_no, motion_priority)
        
    #     def get_model_info(self):
    #         return self.controller.get_model_info()
    
    # # 设置适配器
    # adapter = Live2DControllerAdapter(real_live2d_controller)
    # set_renderer(adapter)
    
    # print(f"✓ 模型目录: {config.MODELS_DIR}")
    # print(f"✓ API端口: {config.API_PORT}")
    # print(f"✓ 访问地址: http://{config.API_HOST}:{config.API_PORT}")
    # print()
    # print("API服务启动中...")
    # print("按 Ctrl+C 停止服务")
    # print()
    
    # # 启动Flask服务
    # try:
    #     app.run(
    #         host=config.API_HOST,
    #         port=config.API_PORT,
    #         debug=False,
    #         use_reloader=False,
    #         threaded=True
    #     )
    # except KeyboardInterrupt:
    #     print("\n服务已停止")
    # except Exception as e:
    #     print(f"启动失败: {e}")