# Robot Framework 音频测试文档

## 📋 概述

本项目提供了完整的 Python + Robot Framework 音频测试解决方案，用于测试 Scarlett 2i4 音频接口的 4 个声道输出。

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `ultimate_play.py` | Python 版音频播放器（支持命令行和库调用） |
| `AudioKeywords.py` | Robot Framework 自定义关键字库 |
| `audio_test.robot` | 基础测试套件 |
| `advanced_audio_test.robot` | 高级测试套件（含设备验证） |
| `run_tests.sh` | 测试运行脚本 |

## 🚀 快速开始

### 1. 安装 Robot Framework

```bash
pip3 install robotframework
```

### 2. 确保 PipeWire 路由已配置

```bash
./setup_pipewire_routing_v3.sh
```

### 3. 运行测试

```bash
# 运行基础测试
./run_tests.sh

# 运行高级测试
./run_tests.sh advanced

# 运行所有测试
./run_tests.sh all

# 运行特定标签的测试
./run_tests.sh tag channel-1
```

## 📊 测试套件说明

### 基础测试套件 (audio_test.robot)

- ✅ 测试各个声道的基本播放功能
- ✅ 测试所有声道循环播放
- ✅ 负面测试（无效参数、不存在的文件）

**测试用例：**
- 测试声道1播放
- 测试声道2播放
- 测试声道3播放
- 测试声道4播放
- 测试所有声道循环播放
- 测试无效声道参数
- 测试不存在的音频文件

### 高级测试套件 (advanced_audio_test.robot)

- ✅ 验证 Scarlett 虚拟设备是否存在
- ✅ 验证声道路由配置
- ✅ 验证播放后 sink 切换是否正确
- ✅ 压力测试（快速切换声道）

**测试用例：**
- TC01 - 验证Scarlett虚拟设备存在
- TC02 - 验证声道1和2使用Scarlett_1-2
- TC03 - 验证声道3和4使用Scarlett_3-4
- TC04-TC07 - 测试各声道播放并验证sink切换
- TC08 - 测试所有声道循环播放
- TC09 - 测试快速切换声道（压力测试）
- TC10 - 负面测试：无效声道号
- TC11 - 负面测试：不存在的文件

## 🏷️ 可用测试标签

| 标签 | 说明 |
|------|------|
| `channel-1` | 声道1相关测试 |
| `channel-2` | 声道2相关测试 |
| `channel-3` | 声道3相关测试 |
| `channel-4` | 声道4相关测试 |
| `all-channels` | 所有声道循环测试 |
| `setup` | 环境设置验证 |
| `routing` | 路由配置验证 |
| `playback` | 播放功能测试 |
| `negative` | 负面测试 |
| `stress` | 压力测试 |

## 🔧 直接使用 Python 模块

### 命令行方式

```bash
# 播放5秒到声道1
python3 ultimate_play.py /path/to/audio.wav 1

# 或直接执行
./ultimate_play.py /path/to/audio.wav 1
```

### Python 代码中使用

```python
from ultimate_play import AudioPlayer, play_audio_to_channel

# 方式1: 使用便捷函数
success = play_audio_to_channel("audio.wav", 1, duration=5)

# 方式2: 使用类
player = AudioPlayer("audio.wav", 1)
success = player.run(duration=5)
```

### 在 Robot Framework 中使用

```robot
*** Settings ***
Library    /home/thortron/Tools/Audio_test/ultimate_play.py

*** Test Cases ***
我的测试
    ${result}=    Play Audio To Channel    /path/to/audio.wav    1    5
    Should Be True    ${result}
```

## 📝 自定义关键字库 (AudioKeywords)

### 可用关键字

| 关键字 | 说明 | 参数 |
|--------|------|------|
| `Play Audio To Channel` | 播放音频到指定声道 | audio_file, channel, duration |
| `Get Current Default Sink` | 获取当前默认sink | - |
| `Verify Sink Is` | 验证当前sink是否匹配 | expected_sink |
| `List Available Sinks` | 列出所有可用sink | - |
| `Check Scarlett Sinks Exist` | 检查Scarlett设备是否存在 | - |
| `Get Sink For Channel` | 获取声道对应的sink名称 | channel |
| `Test All Channels Sequentially` | 测试所有声道 | audio_file, duration |
| `Verify All Channels Passed` | 验证所有声道测试是否通过 | results |

### 使用示例

```robot
*** Settings ***
Library    AudioKeywords.py

*** Test Cases ***
自定义测试
    # 检查设备
    ${exists}=    Check Scarlett Sinks Exist
    Should Be True    ${exists}

    # 播放音频
    ${result}=    Play Audio To Channel    audio.wav    1    5

    # 验证sink
    ${sink}=    Get Current Default Sink
    Should Be Equal    ${sink}    Scarlett_1-2
```

## 📈 查看测试报告

测试完成后，报告生成在 `reports/` 目录：

- `report.html` - 测试报告（包含统计和结果）
- `log.html` - 详细日志
- `output.xml` - 机器可读的输出

在浏览器中打开 `reports/report.html` 查看可视化测试结果。

## 🎯 测试流程说明

每个测试的执行流程：

1. **验证输入** - 检查音频文件和声道参数
2. **配置路由** - 确定使用的 sink 和声道映射
3. **切换设备** - 使用 `pactl` 切换默认 sink
4. **播放音频** - 通过 ffmpeg + aplay 播放
5. **验证结果** - 检查播放是否成功

## ⚙️ 技术架构

```
┌─────────────────────────────────────┐
│   Robot Framework 测试套件          │
│   (audio_test.robot /              │
│    advanced_audio_test.robot)      │
└──────────────┬──────────────────────┘
               │
               ├─────────────────────────┐
               │                         │
┌──────────────▼──────────┐   ┌─────────▼────────────┐
│  AudioKeywords.py       │   │  ultimate_play.py    │
│  (自定义关键字库)        │   │  (核心播放模块)       │
└──────────────┬──────────┘   └─────────┬────────────┘
               │                         │
               └─────────┬───────────────┘
                         │
              ┌──────────▼──────────┐
              │  AudioPlayer 类     │
              │  - 输入验证          │
              │  - 路由配置          │
              │  - 设备切换          │
              │  - 音频播放          │
              └──────────┬──────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
┌────────▼─────┐  ┌──────▼──────┐  ┌────▼─────┐
│    pactl     │  │   ffmpeg    │  │  aplay   │
│ (PipeWire控制)│  │ (音频处理)   │  │ (播放器)  │
└──────────────┘  └─────────────┘  └──────────┘
```

## 🐛 故障排查

### 问题：测试提示 "Scarlett 虚拟设备不存在"

**解决：**
```bash
./setup_pipewire_routing_v3.sh
```

### 问题：import 错误

**解决：** 确保在正确目录运行，或使用绝对路径
```bash
cd /home/thortron/Tools/Audio_test
./run_tests.sh
```

### 问题：音频没有声音

**检查：**
1. Scarlett 2i4 是否正确连接
2. 音量是否设置正确
3. 使用 `pactl list sinks` 检查设备状态

## 📞 获取帮助

```bash
# 查看测试脚本帮助
./run_tests.sh help

# 查看 Robot Framework 帮助
robot --help
```
