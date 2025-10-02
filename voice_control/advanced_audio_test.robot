*** Settings ***
Documentation     高级音频播放测试套件
...               包含设备验证、sink切换验证等完整测试
Library           AudioKeywords.py
Library           OperatingSystem
Library           Collections
Suite Setup       验证测试环境
Suite Teardown    测试清理

*** Variables ***
${AUDIO_FILE}     /home/thortron/Tools/Audio_test/file_example_WAV_2MG.wav
${DURATION}       5

*** Test Cases ***
TC01 - 验证Scarlett虚拟设备存在
    [Documentation]    确认 setup_pipewire_routing_v3.sh 已正确执行
    [Tags]    setup    prerequisite
    ${exists}=    Check Scarlett Sinks Exist
    Should Be True    ${exists}    msg=Scarlett 虚拟设备不存在，请先运行 setup_pipewire_routing_v3.sh

TC02 - 验证声道1和2使用Scarlett_1-2
    [Documentation]    验证声道1和2路由到正确的sink
    [Tags]    routing
    ${sink}=    Get Sink For Channel    1
    Should Be Equal    ${sink}    Scarlett_1-2
    ${sink}=    Get Sink For Channel    2
    Should Be Equal    ${sink}    Scarlett_1-2

TC03 - 验证声道3和4使用Scarlett_3-4
    [Documentation]    验证声道3和4路由到正确的sink
    [Tags]    routing
    ${sink}=    Get Sink For Channel    3
    Should Be Equal    ${sink}    Scarlett_3-4
    ${sink}=    Get Sink For Channel    4
    Should Be Equal    ${sink}    Scarlett_3-4

TC04 - 测试声道1播放并验证sink切换
    [Documentation]    播放到声道1，确认sink已切换
    [Tags]    playback    channel-1
    ${result}=    Play Audio To Channel    ${AUDIO_FILE}    1    ${DURATION}
    Should Be True    ${result}
    ${current_sink}=    Get Current Default Sink
    Should Be Equal    ${current_sink}    Scarlett_1-2

TC05 - 测试声道2播放并验证sink切换
    [Documentation]    播放到声道2，确认sink已切换
    [Tags]    playback    channel-2
    ${result}=    Play Audio To Channel    ${AUDIO_FILE}    2    ${DURATION}
    Should Be True    ${result}
    ${current_sink}=    Get Current Default Sink
    Should Be Equal    ${current_sink}    Scarlett_1-2

TC06 - 测试声道3播放并验证sink切换
    [Documentation]    播放到声道3，确认sink已切换到3-4
    [Tags]    playback    channel-3
    ${result}=    Play Audio To Channel    ${AUDIO_FILE}    3    ${DURATION}
    Should Be True    ${result}
    ${current_sink}=    Get Current Default Sink
    Should Be Equal    ${current_sink}    Scarlett_3-4

TC07 - 测试声道4播放并验证sink切换
    [Documentation]    播放到声道4，确认sink已切换到3-4
    [Tags]    playback    channel-4
    ${result}=    Play Audio To Channel    ${AUDIO_FILE}    4    ${DURATION}
    Should Be True    ${result}
    ${current_sink}=    Get Current Default Sink
    Should Be Equal    ${current_sink}    Scarlett_3-4

TC08 - 测试所有声道循环播放
    [Documentation]    使用自定义关键字测试所有声道
    [Tags]    playback    all-channels
    ${results}=    Test All Channels Sequentially    ${AUDIO_FILE}    ${DURATION}
    ${all_passed}=    Verify All Channels Passed    ${results}
    Should Be True    ${all_passed}    msg=部分声道测试失败

TC09 - 测试快速切换声道
    [Documentation]    快速在声道间切换以测试稳定性
    [Tags]    stress
    FOR    ${i}    IN RANGE    3
        Log    第 ${i+1} 轮快速切换测试
        ${result}=    Play Audio To Channel    ${AUDIO_FILE}    1    2
        Should Be True    ${result}
        ${result}=    Play Audio To Channel    ${AUDIO_FILE}    4    2
        Should Be True    ${result}
    END

TC10 - 负面测试：无效声道号
    [Documentation]    测试无效的声道参数
    [Tags]    negative
    ${result}=    Play Audio To Channel    ${AUDIO_FILE}    0    ${DURATION}
    Should Not Be True    ${result}
    ${result}=    Play Audio To Channel    ${AUDIO_FILE}    5    ${DURATION}
    Should Not Be True    ${result}

TC11 - 负面测试：不存在的文件
    [Documentation]    测试不存在的音频文件
    [Tags]    negative
    ${result}=    Play Audio To Channel    /tmp/nonexistent_audio.wav    1    ${DURATION}
    Should Not Be True    ${result}

*** Keywords ***
验证测试环境
    [Documentation]    测试前的环境检查
    Log    开始音频测试套件
    File Should Exist    ${AUDIO_FILE}    msg=测试音频文件不存在
    ${sinks}=    List Available Sinks
    Log    可用的音频设备: ${sinks}

测试清理
    [Documentation]    测试后清理
    Log    音频测试套件完成
    ${current_sink}=    Get Current Default Sink
    Log    当前默认sink: ${current_sink}
