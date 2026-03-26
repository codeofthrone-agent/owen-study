*** Settings ***
Documentation       Disk Management Keywords Test Suite
...                 驗證磁碟空間管理與檔案清理功能
Library             ../../../libraries/system_maintenance/DiskManagementKeywords.py
Library             OperatingSystem
Library             DateTime

Test Setup          Create Temporary Test Environment
Test Teardown       Cleanup Temporary Test Environment

*** Variable ***
${TEST_DIR}         output/test_disk_cleanup
${OLD_FILE}         old_image.jpg
${NEW_FILE}         new_image.jpg
${TODAY_FILE}       today_image.jpg

*** Test Cases ***
Scenario: Check Disk Space
    [Documentation]    驗證磁碟空間檢查功能
    Given 磁碟剩餘空間應大於 "30000" MB

Scenario: Cleanup Old Debug Images By Days
    [Documentation]    驗證依天數清理舊檔案功能
    # create files first
    Create File With Timestamp    ${TEST_DIR}/${OLD_FILE}    8
    Create File With Timestamp    ${TEST_DIR}/${NEW_FILE}    1
    
    # 驗證檔案存在
    File Should Exist    ${TEST_DIR}/${OLD_FILE}
    File Should Exist    ${TEST_DIR}/${NEW_FILE}
    
    # 清理超過 7 天的檔案
    When 清理超過 "7" 天前的 Debug 圖片    target_dir=output/test_disk_cleanup
    
    # 驗證結果: 舊檔應刪除，新檔應保留
    File Should Not Exist    ${TEST_DIR}/${OLD_FILE}
    File Should Exist        ${TEST_DIR}/${NEW_FILE}

Scenario: Keep Latest Debug Images By Count
    [Documentation]    驗證保留最新 N 張圖片功能
    # 建立 5 個檔案，時間依序遞增 (file1 最舊, file5 最新)
    Create File With Timestamp    ${TEST_DIR}/file1.jpg    5
    Create File With Timestamp    ${TEST_DIR}/file2.jpg    4
    Create File With Timestamp    ${TEST_DIR}/file3.jpg    3
    Create File With Timestamp    ${TEST_DIR}/file4.jpg    2
    Create File With Timestamp    ${TEST_DIR}/file5.jpg    1
    
    # 保留最新的 3 張
    When 保留最新的 "3" 張 Debug 圖片    target_dir=output/test_disk_cleanup
    
    # 驗證: file1, file2 (最舊的兩張) 應被刪除
    File Should Not Exist    ${TEST_DIR}/file1.jpg
    File Should Not Exist    ${TEST_DIR}/file2.jpg
    
    # 驗證: file3, file4, file5 (最新的三張) 應保留
    File Should Exist    ${TEST_DIR}/file3.jpg
    File Should Exist    ${TEST_DIR}/file4.jpg
    File Should Exist    ${TEST_DIR}/file5.jpg

*** Keywords ***
Create Temporary Test Environment
    Create Directory    ${TEST_DIR}

Cleanup Temporary Test Environment
    Remove Directory    ${TEST_DIR}    recursive=True

Create File With Timestamp
    [Arguments]    ${path}    ${days_ago}
    Create File    ${path}    content=dummy
    ${past_time}=    Get Current Date    increment=-${days_ago} day    result_format=epoch
    Set Modified Time    ${path}    ${past_time}
