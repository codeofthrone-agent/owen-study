*** Settings ***
Documentation     音频播放测试套件
...               测试通过 Scarlett 2i4 各个声道播放音频
Library           /home/thortron/Tools/Audio_test/ultimate_play.py
Library           OperatingSystem

*** Variables ***
${AUDIO_FILE}     /home/thortron/Tools/Audio_test/file_example_WAV_2MG.wav
${DURATION}       5

*** Test Cases ***
测试声道1播放
    [Documentation]    测试音频从物理输出1播放
    [Tags]    channel-1
    ${result}=    Play Audio To Channel    ${AUDIO_FILE}    ${1}    ${DURATION}
    Should Be True    ${result}    msg=声道1播放失败

测试声道2播放
    [Documentation]    测试音频从物理输出2播放
    [Tags]    channel-2
    ${result}=    Play Audio To Channel    ${AUDIO_FILE}    ${2}    ${DURATION}
    Should Be True    ${result}    msg=声道2播放失败

测试声道3播放
    [Documentation]    测试音频从物理输出3播放
    [Tags]    channel-3
    ${result}=    Play Audio To Channel    ${AUDIO_FILE}    ${3}    ${DURATION}
    Should Be True    ${result}    msg=声道3播放失败

测试声道4播放
    [Documentation]    测试音频从物理输出4播放
    [Tags]    channel-4
    ${result}=    Play Audio To Channel    ${AUDIO_FILE}    ${4}    ${DURATION}
    Should Be True    ${result}    msg=声道4播放失败

测试所有声道循环播放
    [Documentation]    依次测试所有4个声道
    [Tags]    all-channels
    FOR    ${channel}    IN RANGE    1    5
        Log    正在测试声道 ${channel}
        ${result}=    Play Audio To Channel    ${AUDIO_FILE}    ${channel}    ${DURATION}
        Should Be True    ${result}    msg=声道 ${channel} 播放失败
    END

测试无效声道参数
    [Documentation]    测试错误的声道参数应该失败
    [Tags]    negative
    ${result}=    Play Audio To Channel    ${AUDIO_FILE}    ${5}    ${DURATION}
    Should Not Be True    ${result}    msg=无效声道应该返回失败

测试不存在的音频文件
    [Documentation]    测试不存在的文件应该失败
    [Tags]    negative
    ${result}=    Play Audio To Channel    /nonexistent/file.wav    ${1}    ${DURATION}
    Should Not Be True    ${result}    msg=不存在的文件应该返回失败

*** Keywords ***
播放并验证
    [Arguments]    ${channel}
    [Documentation]    播放音频并验证结果
    ${result}=    Play Audio To Channel    ${AUDIO_FILE}    ${channel}    ${DURATION}
    Should Be True    ${result}
    RETURN    ${result}
