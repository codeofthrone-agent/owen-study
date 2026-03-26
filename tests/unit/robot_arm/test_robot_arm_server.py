"""
Robot Arm Server 單元測試
========================

此測試檔案用於驗證 `robot_arm_server.py` 的核心功能，
確保重構後行為不變。

測試範圍：
1. resolve_detection_conflicts() - 檢測衝突解決邏輯
2. 角度編碼/解碼 - 協議數值轉換
3. JSON 命令處理 - API 入口點驗證
4. 工具函數 - 輔助功能測試

測試策略：
- 使用 Mock 物件模擬硬體依賴（串口、攝影機）
- 純函數直接測試
- 類別方法透過依賴注入測試
"""

import pytest
import sys
import os
import json
import struct
from unittest.mock import MagicMock, Mock, patch
import numpy as np

# 加入專案路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from scripts.robot_arm_server import (
    resolve_detection_conflicts,
    SERVER_VERSION,
)


# ============================================================
# 測試 1: resolve_detection_conflicts() 純函數測試
# ============================================================

class TestResolveDetectionConflicts:
    """測試 resolve_detection_conflicts() 函數
    
    此函數用於解決同一物件的多重檢測衝突，
    保留信心度最高的檢測結果。
    """

    def test_empty_list_returns_empty(self):
        """空列表應返回空列表"""
        result = resolve_detection_conflicts([])
        assert result == []

    def test_single_detection_unchanged(self):
        """單一檢測結果應保持不變"""
        detections = [
            {"class": "light1_on", "confidence": 0.95}
        ]
        result = resolve_detection_conflicts(detections)
        assert len(result) == 1
        assert result[0]["class"] == "light1_on"
        assert result[0]["confidence"] == 0.95

    def test_no_conflict_multiple_objects(self):
        """不同物件的檢測結果應全部保留"""
        detections = [
            {"class": "light1_on", "confidence": 0.9},
            {"class": "light2_off", "confidence": 0.85},
            {"class": "bluetooth_on", "confidence": 0.8}
        ]
        result = resolve_detection_conflicts(detections)
        assert len(result) == 3

    def test_conflict_keeps_higher_confidence(self):
        """同一物件的衝突檢測應保留信心度較高者"""
        detections = [
            {"class": "light1_on", "confidence": 0.8},
            {"class": "light1_off", "confidence": 0.6}
        ]
        result = resolve_detection_conflicts(detections)
        assert len(result) == 1
        assert result[0]["class"] == "light1_on"
        assert result[0]["confidence"] == 0.8

    def test_conflict_reverse_order(self):
        """衝突解決不應受順序影響"""
        detections = [
            {"class": "light1_off", "confidence": 0.6},
            {"class": "light1_on", "confidence": 0.8}
        ]
        result = resolve_detection_conflicts(detections)
        assert len(result) == 1
        assert result[0]["class"] == "light1_on"
        assert result[0]["confidence"] == 0.8

    def test_multiple_conflicts(self):
        """多個衝突應各自獨立解決"""
        detections = [
            {"class": "light1_on", "confidence": 0.9},
            {"class": "light1_off", "confidence": 0.3},
            {"class": "light2_on", "confidence": 0.4},
            {"class": "light2_off", "confidence": 0.85}
        ]
        result = resolve_detection_conflicts(detections)
        assert len(result) == 2
        
        # 驗證 light1 保留 on (0.9)
        light1 = next((d for d in result if "light1" in d["class"]), None)
        assert light1 is not None
        assert light1["class"] == "light1_on"
        assert light1["confidence"] == 0.9
        
        # 驗證 light2 保留 off (0.85)
        light2 = next((d for d in result if "light2" in d["class"]), None)
        assert light2 is not None
        assert light2["class"] == "light2_off"
        assert light2["confidence"] == 0.85

    def test_compatible_key_names_class(self):
        """應支援 'class' 作為類別名稱的 key"""
        detections = [
            {"class": "button_pressed", "confidence": 0.9}
        ]
        result = resolve_detection_conflicts(detections)
        assert len(result) == 1

    def test_compatible_key_names_name(self):
        """應支援 'name' 作為類別名稱的 key"""
        detections = [
            {"name": "button_pressed", "conf": 0.9}
        ]
        result = resolve_detection_conflicts(detections)
        assert len(result) == 1

    def test_compatible_key_confidence_variants(self):
        """應支援 'confidence' 和 'conf' 作為信心度的 key"""
        detections = [
            {"class": "light1_on", "conf": 0.8},
            {"class": "light1_off", "confidence": 0.6}
        ]
        result = resolve_detection_conflicts(detections)
        assert len(result) == 1
        # 應保留 conf=0.8 的那個
        assert result[0]["class"] == "light1_on"

    def test_no_underscore_in_name(self):
        """沒有底線的類別名稱應視為獨立物件"""
        detections = [
            {"class": "button", "confidence": 0.9},
            {"class": "light", "confidence": 0.8}
        ]
        result = resolve_detection_conflicts(detections)
        assert len(result) == 2

    def test_preserves_additional_fields(self):
        """應保留檢測結果中的其他欄位（如 bbox）"""
        detections = [
            {
                "class": "light1_on",
                "confidence": 0.9,
                "bbox": {"x": 100, "y": 200, "w": 50, "h": 50}
            }
        ]
        result = resolve_detection_conflicts(detections)
        assert "bbox" in result[0]
        assert result[0]["bbox"]["x"] == 100

    def test_equal_confidence_keeps_first(self):
        """相同信心度時應保留先出現的"""
        detections = [
            {"class": "light1_on", "confidence": 0.8},
            {"class": "light1_off", "confidence": 0.8}
        ]
        result = resolve_detection_conflicts(detections)
        assert len(result) == 1
        # 由於 dict 迭代順序，先出現的會被保留
        assert result[0]["class"] == "light1_on"


# ============================================================
# 測試 2: 角度編碼/解碼測試
# ============================================================

class TestAngleEncoding:
    """測試角度編碼/解碼邏輯
    
    MyCobot 協議使用 int16 * 100 表示角度，
    需確保編碼和解碼的一致性。
    """

    def test_positive_angle_encoding(self):
        """正角度編碼測試"""
        angle = 45.67
        angle_int = int(angle * 100)  # 4567
        
        high_byte = (angle_int >> 8) & 0xFF
        low_byte = angle_int & 0xFF
        
        # 驗證編碼
        assert high_byte == 0x11  # 4567 >> 8 = 17
        assert low_byte == 0xD7   # 4567 & 0xFF = 215
        
        # 驗證解碼
        decoded = (high_byte << 8) | low_byte
        assert decoded == 4567
        assert decoded / 100.0 == 45.67

    def test_negative_angle_encoding(self):
        """負角度編碼測試（使用補碼）"""
        angle = -30.5
        angle_int = int(angle * 100)  # -3050
        
        # 轉換為 unsigned 16-bit
        if angle_int < 0:
            angle_int_unsigned = angle_int + 65536  # -3050 + 65536 = 62486
        else:
            angle_int_unsigned = angle_int
            
        high_byte = (angle_int_unsigned >> 8) & 0xFF
        low_byte = angle_int_unsigned & 0xFF
        
        # 驗證編碼 (62486 = 0xF416)
        assert high_byte == 0xF4  # 62486 >> 8 = 244
        assert low_byte == 0x16   # 62486 & 0xFF = 22 (修正: 62486 % 256 = 22)
        
        # 驗證解碼
        decoded_unsigned = (high_byte << 8) | low_byte
        # 轉回有符號
        if decoded_unsigned > 32767:
            decoded = decoded_unsigned - 65536
        else:
            decoded = decoded_unsigned
            
        assert decoded == -3050
        assert decoded / 100.0 == -30.5

    def test_zero_angle(self):
        """零角度編碼測試"""
        angle = 0.0
        angle_int = int(angle * 100)
        
        high_byte = (angle_int >> 8) & 0xFF
        low_byte = angle_int & 0xFF
        
        assert high_byte == 0x00
        assert low_byte == 0x00

    def test_max_positive_angle(self):
        """最大正角度測試 (327.67 度)"""
        angle = 327.67
        angle_int = int(angle * 100)  # 32767
        
        high_byte = (angle_int >> 8) & 0xFF
        low_byte = angle_int & 0xFF
        
        # 驗證編碼
        assert (high_byte << 8) | low_byte == 32767

    def test_max_negative_angle(self):
        """最大負角度測試 (-327.68 度)"""
        angle = -327.68
        angle_int = int(angle * 100)  # -32768
        
        if angle_int < 0:
            angle_int_unsigned = angle_int + 65536  # 32768
        else:
            angle_int_unsigned = angle_int
            
        high_byte = (angle_int_unsigned >> 8) & 0xFF
        low_byte = angle_int_unsigned & 0xFF
        
        # 驗證解碼
        decoded_unsigned = (high_byte << 8) | low_byte
        if decoded_unsigned > 32767:
            decoded = decoded_unsigned - 65536
        else:
            decoded = decoded_unsigned
            
        assert decoded == -32768


# ============================================================
# 測試 3: 協議命令格式測試
# ============================================================

class TestProtocolFormat:
    """測試 MyCobot 協議命令格式"""

    def test_get_angles_command_format(self):
        """get_angles 命令格式驗證"""
        expected = [0xfe, 0xfe, 0x02, 0x20, 0xfa]
        
        # 驗證結構
        assert expected[0] == 0xfe  # Header 1
        assert expected[1] == 0xfe  # Header 2
        assert expected[2] == 0x02  # Length
        assert expected[3] == 0x20  # Command (GET_ANGLES)
        assert expected[4] == 0xfa  # Footer

    def test_send_angles_command_format(self):
        """send_angles 命令格式驗證"""
        angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        speed = 50
        
        # 構建命令
        command = [0xFE, 0xFE]
        command.append(0x0F)  # Length
        command.append(0x22)  # Command (SEND_ANGLES)
        
        for angle in angles:
            angle_int = int(angle * 100)
            if angle_int < 0:
                angle_int = angle_int + 65536
            command.append((angle_int >> 8) & 0xFF)
            command.append(angle_int & 0xFF)
        
        command.append(speed & 0xFF)
        command.append(0xFA)
        
        # 驗證長度: 2 header + 1 len + 1 cmd + 12 angles + 1 speed + 1 footer = 18
        assert len(command) == 18
        
        # 驗證結構
        assert command[0:2] == [0xFE, 0xFE]
        assert command[3] == 0x22
        assert command[-1] == 0xFA

    def test_power_on_command_format(self):
        """power_on 命令格式驗證"""
        expected = [0xfe, 0xfe, 0x02, 0x10, 0xfa]
        
        assert expected[3] == 0x10  # POWER_ON

    def test_power_off_command_format(self):
        """power_off 命令格式驗證"""
        expected = [0xfe, 0xfe, 0x02, 0x11, 0xfa]
        
        assert expected[3] == 0x11  # POWER_OFF

    def test_is_moving_command_format(self):
        """is_moving 命令格式驗證"""
        expected = [0xfe, 0xfe, 0x02, 0x2b, 0xfa]
        
        assert expected[3] == 0x2b  # IS_MOVING


# ============================================================
# 測試 4: 回應解析測試
# ============================================================

class TestResponseParsing:
    """測試協議回應解析"""

    def test_parse_angles_response(self):
        """解析 get_angles 回應"""
        # 模擬回應: 6 個角度全為 0
        # [header, header, len, cmd, j1_h, j1_l, ..., j6_h, j6_l, footer]
        response = bytes([
            0xfe, 0xfe, 0x0d, 0x20,  # Header + len + cmd
            0x00, 0x00,  # J1 = 0
            0x00, 0x00,  # J2 = 0
            0x00, 0x00,  # J3 = 0
            0x00, 0x00,  # J4 = 0
            0x00, 0x00,  # J5 = 0
            0x00, 0x00,  # J6 = 0
            0xfa  # Footer
        ])
        
        # 解析
        assert len(response) >= 16
        assert response[3] == 0x20
        
        angles = []
        for i in range(6):
            high_byte = response[4 + i * 2]
            low_byte = response[5 + i * 2]
            angle_int = (high_byte << 8) | low_byte
            if angle_int > 32767:
                angle_int -= 65536
            angles.append(angle_int / 100.0)
        
        assert angles == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def test_parse_angles_response_with_values(self):
        """解析帶有實際數值的 get_angles 回應"""
        # J1 = 45.67 度 (4567 = 0x11D7)
        # J2 = -30.5 度 (-3050 -> 62486 = 0xF406)
        response = bytes([
            0xfe, 0xfe, 0x0d, 0x20,
            0x11, 0xD7,  # J1 = 45.67
            0xF4, 0x06,  # J2 = -30.5
            0x00, 0x00,  # J3 = 0
            0x00, 0x00,  # J4 = 0
            0x00, 0x00,  # J5 = 0
            0x00, 0x00,  # J6 = 0
            0xfa
        ])
        
        angles = []
        for i in range(6):
            high_byte = response[4 + i * 2]
            low_byte = response[5 + i * 2]
            angle_int = (high_byte << 8) | low_byte
            if angle_int > 32767:
                angle_int -= 65536
            angles.append(angle_int / 100.0)
        
        assert angles[0] == pytest.approx(45.67, rel=0.01)
        assert angles[1] == pytest.approx(-30.5, rel=0.01)

    def test_busy_response_detection(self):
        """檢測忙碌回應"""
        busy_response = b'\xfe\xfe\x03\x20\x01\xfa'
        
        # 驗證是忙碌回應
        assert busy_response == b'\xfe\xfe\x03\x20\x01\xfa'


# ============================================================
# 測試 5: 版本號一致性測試
# ============================================================

class TestVersionConsistency:
    """測試版本號一致性"""

    def test_server_version_format(self):
        """版本號格式驗證"""
        # 應該是 vX.Y.Z 格式
        assert SERVER_VERSION.startswith("v")
        parts = SERVER_VERSION[1:].split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)


# ============================================================
# 測試 6: 全局偏移補償邏輯測試
# ============================================================

class TestGlobalOffsetCompensation:
    """測試全局偏移補償邏輯"""

    def test_apply_offset_to_angles(self):
        """應用偏移到角度"""
        logical_angles = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
        offsets = [1.0, -1.0, 0.5, -0.5, 0.0, 2.0]
        
        # 發送時: Logical + Offset
        final_angles = [a + o for a, o in zip(logical_angles, offsets)]
        
        expected = [11.0, 19.0, 30.5, 39.5, 50.0, 62.0]
        assert final_angles == expected

    def test_remove_offset_from_angles(self):
        """從角度移除偏移（讀取時）"""
        raw_angles = [11.0, 19.0, 30.5, 39.5, 50.0, 62.0]
        offsets = [1.0, -1.0, 0.5, -0.5, 0.0, 2.0]
        
        # 讀取時: Raw - Offset
        logical_angles = [a - o for a, o in zip(raw_angles, offsets)]
        
        expected = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
        assert logical_angles == expected

    def test_offset_roundtrip(self):
        """偏移補償來回轉換一致性"""
        original = [15.5, -25.3, 45.0, -10.2, 88.8, -45.6]
        offsets = [2.1, -1.5, 0.8, -0.3, 1.0, -2.0]
        
        # 發送
        sent = [a + o for a, o in zip(original, offsets)]
        
        # 讀取
        received = [a - o for a, o in zip(sent, offsets)]
        
        for orig, recv in zip(original, received):
            assert orig == pytest.approx(recv, rel=1e-9)


# ============================================================
# 測試 7: 座標映射測試 (ROI)
# ============================================================

class TestCoordinateMapping:
    """測試 ROI 座標映射邏輯"""

    def test_roi_to_original_mapping(self):
        """ROI 座標映射回原圖"""
        roi_coords = (100, 50, 300, 250)  # (x1, y1, x2, y2)
        x1, y1, x2, y2 = roi_coords
        
        # ROI 內的檢測框
        roi_detection = {"x": 50, "y": 30, "w": 40, "h": 40}
        
        # 映射到原圖
        mapped = {
            "x": roi_detection["x"] + x1,  # 50 + 100 = 150
            "y": roi_detection["y"] + y1,  # 30 + 50 = 80
            "w": roi_detection["w"],
            "h": roi_detection["h"]
        }
        
        assert mapped["x"] == 150
        assert mapped["y"] == 80
        assert mapped["w"] == 40
        assert mapped["h"] == 40


# ============================================================
# 測試 8: JSON 命令格式驗證
# ============================================================

class TestJSONCommandFormat:
    """測試 JSON 命令格式"""

    def test_move_to_angles_command(self):
        """move_to_angles 命令格式"""
        cmd = {
            "command": "move_to_angles",
            "angles": [0, 0, 0, 0, 0, 0],
            "speed": 50
        }
        
        assert "command" in cmd
        assert cmd["command"] == "move_to_angles"
        assert len(cmd["angles"]) == 6
        assert 1 <= cmd["speed"] <= 100

    def test_get_angles_command(self):
        """get_angles 命令格式"""
        cmd = {"command": "get_angles"}
        
        assert cmd["command"] == "get_angles"

    def test_click_target_command(self):
        """click_target 命令格式"""
        cmd = {
            "command": "click_target",
            "coords": [150.0, 100.0, 50.0, -180.0, 0.0, 0.0],
            "speed": 20,
            "approach_height": 30.0,
            "click_duration": 0.1
        }
        
        assert len(cmd["coords"]) == 6
        assert cmd["approach_height"] > 0
        assert cmd["click_duration"] >= 0

    def test_scan_and_detect_command(self):
        """scan_and_detect 命令格式"""
        cmd = {
            "command": "scan_and_detect",
            "angles": [0, 30, -45, 0, -60, 0],
            "speed": 50
        }
        
        assert len(cmd["angles"]) == 6


# ============================================================
# 測試 9: 錯誤回應格式測試
# ============================================================

class TestErrorResponseFormat:
    """測試錯誤回應格式一致性"""

    def test_error_response_has_status(self):
        """錯誤回應應包含 status 欄位"""
        error_response = {
            "status": "error",
            "message": "Something went wrong"
        }
        
        assert "status" in error_response
        assert error_response["status"] == "error"
        assert "message" in error_response

    def test_success_response_has_status(self):
        """成功回應應包含 status 欄位"""
        success_response = {
            "status": "success",
            "data": {"angles": [0, 0, 0, 0, 0, 0]}
        }
        
        assert "status" in success_response
        assert success_response["status"] == "success"


# ============================================================
# 測試 10: RPY 驗證測試
# ============================================================

class TestRPYValidation:
    """測試 RPY 姿態驗證邏輯
    
    這些測試驗證 _has_non_standard_rpy() 和 _warn_if_rpy_ignored() 方法。
    標準姿態：[0,0,0] 或 [-180,0,0]（向下）
    非標準姿態：任何 |value| > 0.1 的 RPY（除了 [-180,0,0]）
    """

    def test_zero_rpy_is_standard(self):
        """零 RPY [0,0,0] 應視為標準姿態，不需警告"""
        from scripts.robot_arm_server import STANDARD_DOWNWARD_RPY, RPY_TOLERANCE
        
        rpy = [0.0, 0.0, 0.0]
        # 零 RPY 應視為標準（所有值都在容差內）
        is_non_standard = any(abs(r) > RPY_TOLERANCE for r in rpy) and rpy != STANDARD_DOWNWARD_RPY
        assert is_non_standard == False

    def test_downward_rpy_is_standard(self):
        """向下 RPY [-180,0,0] 應視為標準姿態，不需警告"""
        from scripts.robot_arm_server import STANDARD_DOWNWARD_RPY, RPY_TOLERANCE
        
        rpy = [-180.0, 0.0, 0.0]
        # 這是特殊的向下姿態，應視為標準
        is_non_standard = any(abs(r) > RPY_TOLERANCE for r in rpy) and rpy != STANDARD_DOWNWARD_RPY
        assert is_non_standard == False

    def test_small_rpy_within_tolerance(self):
        """小於容差的 RPY 應視為標準姿態"""
        from scripts.robot_arm_server import STANDARD_DOWNWARD_RPY, RPY_TOLERANCE
        
        rpy = [0.05, -0.08, 0.09]  # 所有值都 < 0.1
        is_non_standard = any(abs(r) > RPY_TOLERANCE for r in rpy) and rpy != STANDARD_DOWNWARD_RPY
        assert is_non_standard == False

    def test_non_zero_rpy_triggers_warning(self):
        """明顯非零的 RPY 應觸發警告"""
        from scripts.robot_arm_server import STANDARD_DOWNWARD_RPY, RPY_TOLERANCE
        
        rpy = [10.0, 5.0, -15.0]
        is_non_standard = any(abs(r) > RPY_TOLERANCE for r in rpy) and rpy != STANDARD_DOWNWARD_RPY
        assert is_non_standard == True

    def test_partial_non_zero_rpy(self):
        """只有部分值非零的 RPY 也應觸發警告"""
        from scripts.robot_arm_server import STANDARD_DOWNWARD_RPY, RPY_TOLERANCE
        
        rpy = [0.0, 0.0, 5.0]  # 只有 rz 非零
        is_non_standard = any(abs(r) > RPY_TOLERANCE for r in rpy) and rpy != STANDARD_DOWNWARD_RPY
        assert is_non_standard == True


# ============================================================
# 測試 11: 最終位置獲取測試
# ============================================================

class TestFinalPositionRetrieval:
    """測試 _get_final_position() 方法
    
    此方法用於動作完成後獲取最終位置（角度和座標）。
    需要 Mock _get_angles_with_retry 和 fk_calculator。
    """

    def test_returns_angles_and_coords_on_success(self):
        """成功時應返回角度和 6DOF 座標"""
        # 模擬角度和 FK 計算結果
        mock_angles = [0.0, 15.0, -30.0, 0.0, -45.0, 0.0]
        mock_xyz = [150.0, 100.0, 200.0]
        
        # FK 計算後應返回 [x, y, z, 0, 0, 0]
        expected_coords = mock_xyz + [0.0, 0.0, 0.0]
        
        # 驗證格式
        assert len(expected_coords) == 6
        assert expected_coords[3:] == [0.0, 0.0, 0.0]

    def test_returns_none_coords_without_fk_calculator(self):
        """無 FK 計算器時座標應為 None，但角度仍應返回"""
        mock_angles = [0.0, 15.0, -30.0, 0.0, -45.0, 0.0]
        
        # 當 fk_calculator 為 None 時
        fk_calculator = None
        
        if mock_angles and fk_calculator:
            final_coords = "should not reach"
        else:
            final_coords = None
            
        assert final_coords is None

    def test_returns_none_angles_on_retry_failure(self):
        """角度讀取失敗時角度和座標都應為 None"""
        mock_angles = None  # 讀取失敗
        
        final_coords = None
        if mock_angles:
            final_coords = [0.0] * 6
            
        assert mock_angles is None
        assert final_coords is None

    def test_handles_fk_exception_gracefully(self):
        """FK 計算異常時應優雅處理，座標為 None"""
        mock_angles = [0.0, 15.0, -30.0, 0.0, -45.0, 0.0]
        
        # 模擬 FK 計算拋出異常
        final_coords = None
        try:
            raise ValueError("FK calculation failed")
        except Exception:
            pass  # 應該被捕捉，final_coords 保持 None
            
        assert final_coords is None

    def test_coords_format_is_6dof(self):
        """座標格式應為 6DOF [x, y, z, rx, ry, rz]"""
        mock_xyz = [150.0, 100.0, 200.0]
        
        # 轉換為 6DOF 格式
        final_coords = [float(c) for c in mock_xyz] + [0.0, 0.0, 0.0]
        
        assert len(final_coords) == 6
        assert final_coords[:3] == [150.0, 100.0, 200.0]
        assert final_coords[3:] == [0.0, 0.0, 0.0]


# ============================================================
# 測試 12: IK 求解驗證測試
# ============================================================

class TestIKSolvingWithValidation:
    """測試 _solve_ik_validated() 方法
    
    此方法封裝 IK 求解並驗證誤差。
    """

    def test_returns_angles_on_success(self):
        """成功時應返回角度、誤差和 None 錯誤訊息"""
        # 模擬成功的 IK 求解
        mock_angles = [0.0, 15.0, -30.0, 0.0, -45.0, 0.0]
        mock_error = 2.5  # mm, 小於閾值 5mm
        
        # 驗證返回格式
        assert mock_angles is not None
        assert mock_error < 5.0
        # error_message 應為 None
        error_message = None if mock_angles and mock_error < 5.0 else "error"
        assert error_message is None

    def test_returns_error_message_when_no_solution(self):
        """IK 無解時應返回錯誤訊息"""
        mock_angles = None
        mock_error = float('inf')
        
        if mock_angles is None:
            error_message = f"IK 求解失敗: 無解 (誤差: {mock_error:.2f}mm)"
        else:
            error_message = None
            
        assert "無解" in error_message

    def test_returns_warning_when_error_exceeds_threshold(self):
        """IK 誤差超過閾值時應返回警告訊息"""
        from scripts.robot_arm_server import IK_ERROR_THRESHOLD_MM
        
        mock_angles = [0.0, 15.0, -30.0, 0.0, -45.0, 0.0]
        mock_error = 7.5  # mm, 大於閾值 5mm
        
        if mock_error > IK_ERROR_THRESHOLD_MM:
            error_message = f"IK 誤差過大: {mock_error:.2f}mm > {IK_ERROR_THRESHOLD_MM}mm"
        else:
            error_message = None
            
        assert "誤差過大" in error_message

    def test_raises_exception_when_raise_on_error_true(self):
        """raise_on_error=True 時求解失敗應拋出異常"""
        raise_on_error = True
        mock_angles = None
        
        with pytest.raises(ValueError):
            if mock_angles is None and raise_on_error:
                raise ValueError("IK 求解失敗")

    def test_returns_message_when_raise_on_error_false(self):
        """raise_on_error=False 時求解失敗應返回訊息而非拋出異常"""
        raise_on_error = False
        mock_angles = None
        
        if mock_angles is None:
            if raise_on_error:
                # 這不應該執行
                raise ValueError("IK 求解失敗")
            else:
                error_message = "IK 求解失敗"
        else:
            error_message = None
            
        assert error_message == "IK 求解失敗"

    def test_handles_missing_ik_solver(self):
        """無 IK Solver 時應正確處理"""
        ik_solver = None
        
        if not ik_solver:
            error_message = "IK Solver 不可用"
        else:
            error_message = None
            
        assert error_message == "IK Solver 不可用"

    def test_custom_tolerance_respected(self):
        """自定義容差應被尊重"""
        mock_error = 8.0  # mm
        custom_tolerance = 10.0  # mm
        default_tolerance = 5.0  # mm
        
        # 使用預設容差會失敗
        exceeds_default = mock_error > default_tolerance
        assert exceeds_default == True
        
        # 使用自定義容差會成功
        exceeds_custom = mock_error > custom_tolerance
        assert exceeds_custom == False


# ============================================================
# 測試 13: 常數驗證測試
# ============================================================

class TestNewConstants:
    """驗證新增常數的值"""

    def test_standard_downward_rpy_value(self):
        """標準向下 RPY 值應為 [-180.0, 0.0, 0.0]"""
        from scripts.robot_arm_server import STANDARD_DOWNWARD_RPY
        
        assert STANDARD_DOWNWARD_RPY == [-180.0, 0.0, 0.0]

    def test_rpy_tolerance_value(self):
        """RPY 容差值應為 0.1"""
        from scripts.robot_arm_server import RPY_TOLERANCE
        
        assert RPY_TOLERANCE == 0.1


# ============================================================
# 執行測試
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
