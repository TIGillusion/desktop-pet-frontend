# Live2D Desktop API 使用示例

本文档展示了如何使用 Live2D Desktop API 的各种接口来控制 Live2D 模型。

## 基础信息

### 获取 API 信息
```bash
curl http://localhost:6000/
```

### 获取可用模型列表
```bash
curl http://localhost:6000/models
```

### 获取当前模型信息
```bash
curl http://localhost:6000/model/info
```

## 参数控制

### 设置单个参数
```bash
curl -X POST http://localhost:6000/model/parameter \
  -H "Content-Type: application/json" \
  -d '{"name": "ParamAngleX", "value": 15.0}'
```

### 设置参数（包含权重）
```bash
curl -X POST http://localhost:6000/model/parameter_detailed \
  -H "Content-Type: application/json" \
  -d '{"param_id": "ParamAngleX", "value": 15.0, "weight": 0.5}'
```

### 通过索引设置参数
```bash
curl -X POST http://localhost:6000/model/parameter/by_index \
  -H "Content-Type: application/json" \
  -d '{"index": 0, "value": 10.0, "weight": 1.0}'
```

### 添加参数值
```bash
curl -X POST http://localhost:6000/model/parameter/add \
  -H "Content-Type: application/json" \
  -d '{"param_id": "ParamAngleX", "value": 5.0}'
```

### 获取所有参数信息
```bash
curl http://localhost:6000/model/parameters/info
```

## 表情控制

### 播放表情
```bash
curl -X POST http://localhost:6000/model/expression \
  -H "Content-Type: application/json" \
  -d '{"expression": "happy"}'
```

### 设置随机表情
```bash
curl -X POST http://localhost:6000/model/expression/random
```

### 获取表情信息
```bash
curl http://localhost:6000/model/expressions/info
```

### 重置表情
```bash
curl -X POST http://localhost:6000/model/reset/expression
```

## 动作控制

### 播放动作
```bash
curl -X POST http://localhost:6000/model/motion \
  -H "Content-Type: application/json" \
  -d '{"motion": "idle", "no": 0, "priority": 3}'
```

### 开始随机动作
```bash
curl -X POST http://localhost:6000/model/motion/random \
  -H "Content-Type: application/json" \
  -d '{"group": "idle", "priority": 3}'
```

### 检查动作是否完成
```bash
curl http://localhost:6000/model/motion/finished
```

### 停止所有动作
```bash
curl -X POST http://localhost:6000/model/motions/stop
```

### 获取动作信息
```bash
curl http://localhost:6000/model/motions/info
```

## 模型变换

### 调整画布大小
```bash
curl -X POST http://localhost:6000/model/resize \
  -H "Content-Type: application/json" \
  -d '{"width": 800, "height": 600}'
```

### 设置模型偏移
```bash
curl -X POST http://localhost:6000/model/offset \
  -H "Content-Type: application/json" \
  -d '{"dx": 50.0, "dy": -20.0}'
```

### 设置 X 轴偏移
```bash
curl -X POST http://localhost:6000/model/offset_x \
  -H "Content-Type: application/json" \
  -d '{"sx": 100.0}'
```

### 设置缩放
```bash
curl -X POST http://localhost:6000/model/scale \
  -H "Content-Type: application/json" \
  -d '{"scale": 1.2}'
```

### 旋转模型
```bash
curl -X POST http://localhost:6000/model/rotate \
  -H "Content-Type: application/json" \
  -d '{"degrees": 15.0}'
```

## 交互功能

### 点击测试
```bash
curl -X POST http://localhost:6000/model/hit_test \
  -H "Content-Type: application/json" \
  -d '{"hit_area_name": "head", "x": 400, "y": 300}'
```

### 拖拽模型
```bash
curl -X POST http://localhost:6000/model/drag \
  -H "Content-Type: application/json" \
  -d '{"x": 400, "y": 300}'
```

### 点击部件测试
```bash
curl -X POST http://localhost:6000/model/part/hit \
  -H "Content-Type: application/json" \
  -d '{"x": 400, "y": 300, "top_only": false}'
```

## 部件控制

### 获取部件信息
```bash
curl http://localhost:6000/model/parts/info
```

### 设置部件透明度
```bash
curl -X POST http://localhost:6000/model/part/opacity \
  -H "Content-Type: application/json" \
  -d '{"index": 0, "opacity": 0.8}'
```

### 设置部件屏幕颜色
```bash
curl -X POST http://localhost:6000/model/part/screen_color \
  -H "Content-Type: application/json" \
  -d '{"part_index": 0, "r": 1.0, "g": 0.5, "b": 0.5, "a": 1.0}'
```

### 获取部件屏幕颜色
```bash
curl -X POST http://localhost:6000/model/part/screen_color/get \
  -H "Content-Type: application/json" \
  -d '{"part_index": 0}'
```

## 可绘制对象控制

### 获取可绘制对象信息
```bash
curl http://localhost:6000/model/drawable/info
```

### 设置可绘制对象颜色
```bash
curl -X POST http://localhost:6000/model/drawable/multiply_color \
  -H "Content-Type: application/json" \
  -d '{"index": 0, "r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0}'
```

## 自动功能

### 设置自动呼吸
```bash
curl -X POST http://localhost:6000/model/auto_breath \
  -H "Content-Type: application/json" \
  -d '{"enable": true}'
```

### 设置自动眨眼
```bash
curl -X POST http://localhost:6000/model/auto_blink \
  -H "Content-Type: application/json" \
  -d '{"enable": true}'
```

### 设置嘴部开合
```bash
curl -X POST http://localhost:6000/model/mouth \
  -H "Content-Type: application/json" \
  -d '{"open": 0.5}'
```

## 信息查询

### 获取画布信息
```bash
curl http://localhost:6000/model/canvas/info
```

### 获取音频文件路径
```bash
curl -X POST http://localhost:6000/model/sound_path \
  -H "Content-Type: application/json" \
  -d '{"group": "voice", "index": 0}'
```

### 检查 MOC 文件一致性
```bash
curl -X POST http://localhost:6000/model/moc_consistency \
  -H "Content-Type: application/json" \
  -d '{"moc_file_name": "model.moc3"}'
```

## Python 示例

```python
import requests
import json

# API 基础URL
BASE_URL = "http://localhost:6000"

def set_parameter(name, value):
    """设置参数"""
    url = f"{BASE_URL}/model/parameter"
    data = {"name": name, "value": value}
    response = requests.post(url, json=data)
    return response.json()

def play_expression(expression):
    """播放表情"""
    url = f"{BASE_URL}/model/expression"
    data = {"expression": expression}
    response = requests.post(url, json=data)
    return response.json()

def play_motion(motion, no=0, priority=3):
    """播放动作"""
    url = f"{BASE_URL}/model/motion"
    data = {"motion": motion, "no": no, "priority": priority}
    response = requests.post(url, json=data)
    return response.json()

def get_model_info():
    """获取模型信息"""
    url = f"{BASE_URL}/model/info"
    response = requests.get(url)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 设置头部角度
    result = set_parameter("ParamAngleX", 15.0)
    print("设置参数:", result)
    
    # 播放开心表情
    result = play_expression("happy")
    print("播放表情:", result)
    
    # 播放挥手动作
    result = play_motion("wave", 0, 3)
    print("播放动作:", result)
    
    # 获取模型信息
    info = get_model_info()
    print("模型信息:", info)
```

## JavaScript 示例

```javascript
const BASE_URL = 'http://localhost:6000';

// 设置参数
async function setParameter(name, value) {
    const response = await fetch(`${BASE_URL}/model/parameter`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, value }),
    });
    return await response.json();
}

// 播放表情
async function playExpression(expression) {
    const response = await fetch(`${BASE_URL}/model/expression`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ expression }),
    });
    return await response.json();
}

// 获取参数信息
async function getParametersInfo() {
    const response = await fetch(`${BASE_URL}/model/parameters/info`);
    return await response.json();
}

// 使用示例
(async () => {
    try {
        // 设置眼部参数
        const result1 = await setParameter('ParamEyeLOpen', 0.8);
        console.log('设置参数:', result1);
        
        // 播放随机表情
        const response = await fetch(`${BASE_URL}/model/expression/random`, {
            method: 'POST',
        });
        const result2 = await response.json();
        console.log('随机表情:', result2);
        
        // 获取所有参数信息
        const params = await getParametersInfo();
        console.log('参数信息:', params);
    } catch (error) {
        console.error('API 调用失败:', error);
    }
})();
```

## 响应格式

所有 API 接口都返回统一的 JSON 格式：

### 成功响应
```json
{
    "success": true,
    "data": "具体数据",
    "message": "操作成功信息（可选）"
}
```

### 错误响应
```json
{
    "success": false,
    "error": "错误信息"
}
```

## 注意事项

1. **模型加载**: 在调用其他接口前，确保已加载 Live2D 模型
2. **参数名称**: 使用正确的 Live2D 参数名称（如 `ParamAngleX`, `ParamEyeLOpen` 等）
3. **数值范围**: 参数值应在模型定义的范围内
4. **动作优先级**: 高优先级动作会中断低优先级动作
5. **异步操作**: 某些操作（如动作播放）是异步的，可通过状态查询接口检查完成情况

## 常用参数名称

- `ParamAngleX`: 头部左右角度
- `ParamAngleY`: 头部上下角度  
- `ParamAngleZ`: 头部倾斜角度
- `ParamEyeLOpen`: 左眼开合
- `ParamEyeROpen`: 右眼开合
- `ParamMouthOpenY`: 嘴部开合
- `ParamBodyAngleX`: 身体角度X
- `ParamBodyAngleY`: 身体角度Y
- `ParamBreath`: 呼吸参数

具体的参数名称请通过 `/model/parameters/info` 接口查询当前模型的所有可用参数。