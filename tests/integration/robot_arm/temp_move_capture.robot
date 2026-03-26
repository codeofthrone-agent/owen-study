*** Settings ***
Documentation    Temporary test to move robot arm to specific angles and capture image.
Library          ../../../libraries/robot_arm_control/RobotArmKeywords.py
Library          Collections

*** Test Cases ***
Move Arm And Capture Multi Angle Images
    [Documentation]    Move robot arm to multiple specified angles and capture images to check for reflections/ghosting.
    
    # 1. Initialize Environment
    Given 測試環境設定為 "taipei_lab"
    Given 機器手臂已正確連接到控制面板

    # 2. Define Angle Sets
    # Format: [j1, j2, j3, j4, j5, j6]
    @{angles_original}=    Create List    43.4    6.8    -64.2    -27.2    -4.3    0
    @{angles_var1}=        Create List    45.0    10.0   -60.0    -25.0    -5.0    0
    @{angles_home}=        Create List    0.0     0.0    0.0      0.0      0.0     0
    @{angles_mirror}=      Create List    -43.4   6.8    -64.2    -27.2    -4.3    0
    
    # Create dictionary for iteration
    &{test_sets}=    Create Dictionary    
    ...    original=@{angles_original}
    # ...    var1=@{angles_var1}
    # ...    home=@{angles_home}
    # ...    mirror=@{angles_mirror}

    # 3. Iterate and Capture
    FOR    ${key}    IN    @{test_sets.keys()}
        ${current_angles}=    Get From Dictionary    ${test_sets}    ${key}
        Log    Testing position: ${key} with angles: ${current_angles}    console=True
        
        # Move Arm
        Log    Moving to position: ${key}    console=True
        移動機器手臂到指定角度    ${current_angles}    speed=30
        
        # Wait for stability (important for ghosting check)
        Sleep    10
        
        # Capture Image
        ${filepath}=    拍攝並儲存影像    filename_tag=debug_ghosting_${key}
        Log    Image saved to: ${filepath}    console=True
    END
