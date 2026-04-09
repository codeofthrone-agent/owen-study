"""
fp2_homekit.py - Aqara FP2 HomeKit 整合工具 (All-in-One)

提供三個主要功能：
1. discover: 尋找區網內的 HomeKit 設備
2. pair: 透過 .env 中的 fp2_setup_code 將 FP2 加入本地控制
3. monitor: 監聽 FP2 的所有 OccupancySensor (區域佔用狀態)，並判定雨遮/空間是否被佔用
"""

import argparse
import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Tuple

from aiohomekit import Controller
from aiohomekit.exceptions import AlreadyPairedError
from aiohomekit.zeroconf import async_discover_homekit_devices
from dotenv import load_dotenv

logging.basicConfig(level=logging.WARNING)
load_dotenv()

# ── 設定 ────────────────────────────────────────────────────────
PAIRING_FILE = "pairing_data.json"
OCCUPANCY_UUID = "00000071-0000-1000-8000-0026BB765291"
LIGHT_LEVEL_UUID = "0000006B-0000-1000-8000-0026BB765291"

class FP2StateManager:
    """封裝狀態與事件處理邏輯，避免多執行緒或多次呼叫時的全域變數競態問題"""
    def __init__(self, mode: str = "awning", options: dict = None):
        self.zone_states: Dict[Tuple, int] = {}
        self.zone_labels: Dict[Tuple, str] = {}
        self.light_levels: Dict[Tuple, float] = {}
        self.current_state: str = "未知"
        self.current_mode: str = mode
        self.current_options: dict = options or {}

    def check_state(self) -> str:
        occupied = sum(1 for v in self.zone_states.values() if v == 1)
        slide_threshold = int(self.current_options.get("slide_threshold", 1))
        awning_threshold = int(self.current_options.get("awning_threshold", 2))
        
        if self.current_mode == "slide":
            return "🚐 車廂已收起 (變小/被牆壁佔用)" if occupied >= slide_threshold else "🚙 車廂已展開 (變大/淨空)"
        else:
            return "🌧️  雨遮已展開 (被佔用)" if occupied >= awning_threshold else "☀️  雨遮已縮回 (淨空)"

    def on_event(self, events: dict):
        ts = format_time()

        for (aid, iid), data in events.items():
            key = (aid, iid)
            value = data.get("value", data) if isinstance(data, dict) else data
            
            # 處理光照度更新
            if key in self.light_levels:
                old_lx = self.light_levels[key]
                new_lx = float(value)
                self.light_levels[key] = new_lx
                print(f"[{ts}] 💡 環境亮度更新: {new_lx} lux (舊={old_lx})")
                continue

            # 處理區域佔用更新
            if key not in self.zone_states:
                continue

            old_val = self.zone_states[key]
            new_val = int(value)
            self.zone_states[key] = new_val

            label = self.zone_labels.get(key, f"[{aid},{iid}]")
            status = "🛑 空間被佔用（偵測到物體/牆壁）" if new_val == 1 else "⚪ 空間淨空"
            print(f"[{ts}] {label}: {status}  (舊={old_val}→新={new_val})")

            new_state = self.check_state()
            if new_state != self.current_state:
                self.current_state = new_state
                occupied_count = sum(1 for v in self.zone_states.values() if v == 1)
                total = len(self.zone_states)
                print(f"\n[{ts}] ══ 系統狀態改變: {self.current_state} "
                      f"（{occupied_count}/{total} 個區域有訊號）══\n")


def format_time() -> str:
    return datetime.now().strftime("%H:%M:%S")


# ==========================================
# 1. 設備探索 (Discover)
# ==========================================
async def do_discover():
    print("=== 尋找區網內的 HomeKit 設備 (掃描 20 秒) ===")
    controller = Controller()
    devices = await controller.discover_ip(max_seconds=20)
    
    if not devices:
        print("找不到任何 HomeKit 設備。")
        return

    fp2_unpaired = []
    print(f"\n找到 {len(devices)} 個設備：")
    print("-" * 50)
    for dev in devices:
        info = dev.info
        name = info.get("name", "Unknown")
        model = info.get("md", "Unknown")
        ip = info.get("address", "Unknown IP")
        sf = info.get("sf", "Unknown")
        status = "🟢 可配對 (sf=1)" if sf == 1 else "🔴 已配對 (sf=0)"
        
        print(f"名稱: {name}")
        print(f"型號: {model} | IP: {ip}")
        print(f"狀態: {status}")
        print("-" * 50)
        
        # 記錄可配對的 FP2
        if sf == 1 and ("FP2" in name or "PS-S02D" in model or "Presence" in name):
            fp2_unpaired.append(dev)

    # 若有找到未配對的 FP2，直接觸發配對
    if fp2_unpaired:
        print("\n💡 發現尚未配對的 FP2，但由於 discover 指令不帶配對碼，請使用 pair 指令進行配對。")


# ==========================================
# 2. 設備配對 (Pair)
# ==========================================
async def _perform_pairing(target_device, controller: Controller, alias: str, setup_code: str):
    """執行實際的配對流程"""
    if not setup_code:
        setup_code = os.getenv("FP2_SETUP_CODE") or os.getenv("fp2_setup_code")
    if not setup_code:
        print("❌ 錯誤：未提供 setup_code 且 .env 檔案中找不到 'fp2_setup_code'")
        return

    # 確保格式為 XXX-XX-XXX
    if len(setup_code) == 8 and "-" not in setup_code:
        setup_code = f"{setup_code[:3]}-{setup_code[3:5]}-{setup_code[5:]}"
    
    print(f"=== 開始配對 FP2 ===")
    print(f"目標設備: {target_device.info.get('name')} | 使用 Setup Code: {setup_code} | Alias: {alias}")
    
    try:
        print("配對中...")
        finish_pairing = await target_device.start_pairing(alias)
        await finish_pairing(setup_code)
        
        controller.save_data(PAIRING_FILE)
        print(f"✅ 配對成功！設定已儲存至 {PAIRING_FILE}")
    except AlreadyPairedError:
        print("⚠️ 設備已配對過。如果需要重新配對，請先重置 FP2 並刪除 pairing_data.json")
    except Exception as e:
        print(f"❌ 配對失敗: {e}")

async def do_pair(alias: str, setup_code: str):
    print("=== 尋找可配對的 FP2 (掃描 20 秒) ===")
    controller = Controller()
    devices = await controller.discover_ip(max_seconds=20)
    
    fp2_device = None
    for dev in devices:
        name = dev.info.get("name", "")
        model = dev.info.get("md", "")
        if "FP2" in name or "PS-S02D" in model or "Presence" in name:
            fp2_device = dev
            break
            
    if not fp2_device:
        print("❌ 找不到可用的 FP2，請確認設備已開機並處於配對模式（黃燈閃爍）")
        return

    await _perform_pairing(fp2_device, controller, alias, setup_code)


# ==========================================
# 3. 狀態監聽 (Monitor)
# ==========================================
# (check_state 和 on_event 已移至 FP2StateManager)


async def refresh_ip(controller: Controller, alias: str) -> bool:
    pairing = controller.pairings.get(alias)
    if not pairing:
        return False
    target_id = pairing.pairing_data.get("AccessoryPairingID", "").upper()
    devices = await async_discover_homekit_devices(max_seconds=10)
    for dev in devices:
        if dev.get("id", "").upper() == target_id:
            ip, port = dev["address"], dev["port"]
            pairing.pairing_data["AccessoryIP"] = ip
            pairing.pairing_data["AccessoryPort"] = port
            pairing.connection.host = ip
            pairing.connection.port = port
            print(f"更新 IP 成功: {ip}:{port}")
            return True
    return True


async def do_monitor(alias: str, mode: str):
    state_mgr = FP2StateManager(mode=mode)

    print(f"=== FP2 HomeKit 區域佔用監控 ({alias} - {'旅行車側推艙模式' if mode == 'slide' else '雨遮模式'}) ===")
    controller = Controller()
    try:
        controller.load_data(PAIRING_FILE)
    except FileNotFoundError:
        print(f"❌ 找不到 {PAIRING_FILE}，請先執行 'uv run python fp2_homekit.py pair'")
        return

    if alias not in controller.pairings:
        print(f"❌ 配對資料中找不到 FP2 (Alias: {alias})")
        return

    print("尋找設備並連線中...")
    await refresh_ip(controller, alias)
    pairing = controller.pairings[alias]

    try:
        services = await pairing.list_accessories_and_characteristics()
    except Exception as e:
        print(f"❌ 連線失敗: {e}\n請確認 FP2 已連上 Wi-Fi")
        return

    accs = services if isinstance(services, list) else services.get("accessories", [])
    subscribe_targets: List[Tuple] = []
    zone_index = 1

    print("\n=== 偵測到的區域 (Zone) ===")
    for acc in accs:
        aid = acc.get("aid", 1)
        for svc in acc.get("services", []):
            # 移除服務類型過濾，改為掃描所有特徵值

            for char in svc.get("characteristics", []):
                ctype = char.get("type", "")
                iid = char["iid"]
                key = (aid, iid)
                label = f"Zone {zone_index:02d} [{aid},{iid}]"
                
                if OCCUPANCY_UUID.upper() in ctype.upper() or ctype.upper() == "71":
                    state_mgr.zone_labels[key] = label
                    state_mgr.zone_states[key] = int(char.get("value", 0))
                    subscribe_targets.append(key)

                    status = "🛑 被佔用" if state_mgr.zone_states[key] == 1 else "⚪ 淨空"
                    print(f"  {label}: {status}")
                    zone_index += 1
                
                elif LIGHT_LEVEL_UUID.upper() in ctype.upper() or ctype.upper() == "6B":
                    val = float(char.get("value", 0))
                    state_mgr.light_levels[key] = val
                    subscribe_targets.append(key)
                    print(f"  💡 光照度感測器 [{aid},{iid}]: {val} lux")

    if not subscribe_targets:
        print("❌ 找不到任何區域。請確保在 Aqara App 開啟了『名稱同步』")
        await pairing.close()
        return

    state_mgr.current_state = state_mgr.check_state()
    occupied_count = sum(1 for v in state_mgr.zone_states.values() if v == 1)
    
    print(f"\n✅ 成功訂閱 {len(subscribe_targets)} 個區域")
    print(f"初始狀態：{state_mgr.current_state}（{occupied_count}/{len(state_mgr.zone_states)} 個區域有訊號）")
    print("開始即時監聽狀態（按 Ctrl+C 停止）")
    print("─" * 50)

    try:
        await pairing.subscribe(subscribe_targets)
        pairing.dispatcher_connect(state_mgr.on_event)
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n關閉連線...")
        await pairing.close()


# ==========================================
# 4. 單次查詢 (Single-shot query for Robot Framework)
# ==========================================
async def get_status_once(alias: str, mode: str, options: dict = None) -> dict:
    """提供給 Robot Framework 單次讀取狀態的 API"""
    safe_options = options or {}

    controller = Controller()
    try:
        # 當從 Robot 呼叫時，需使用絕對路徑尋找 pairing_data.json
        # 假設執行目錄在專案根目錄，但 pairing_data.json 存在 libraries/fp2_detect/
        file_path = os.path.join(os.path.dirname(__file__), PAIRING_FILE)
        if not os.path.exists(file_path):
             file_path = PAIRING_FILE # 退回相對路徑
        controller.load_data(file_path)
    except FileNotFoundError:
        return {"error": f"找不到配對設定檔，請確保 FP2 已配對。"}

    if alias not in controller.pairings:
        return {"error": f"配對資料中找不到 FP2 (Alias: {alias})"}

    await refresh_ip(controller, alias)
    pairing = controller.pairings[alias]

    try:
        services = await pairing.list_accessories_and_characteristics()
    except Exception as e:
        return {"error": f"連線失敗: {e}"}

    accs = services if isinstance(services, list) else services.get("accessories", [])
    
    local_zone_states = {}
    local_light_levels = {}
    
    for acc in accs:
        aid = acc.get("aid", 1)
        for svc in acc.get("services", []):
            for char in svc.get("characteristics", []):
                ctype = char.get("type", "")
                iid = char["iid"]
                key = (aid, iid)
                if OCCUPANCY_UUID.upper() in ctype.upper() or ctype.upper() == "71":
                    local_zone_states[key] = int(char.get("value", 0))
                elif LIGHT_LEVEL_UUID.upper() in ctype.upper() or ctype.upper() == "6B":
                    local_light_levels[key] = float(char.get("value", 0))

    await pairing.close()

    occupied = sum(1 for v in local_zone_states.values() if v == 1)
    slide_threshold = int(safe_options.get("slide_threshold", 1))
    awning_threshold = int(safe_options.get("awning_threshold", 2))
    
    if mode == "slide":
        state_str = "close" if occupied >= slide_threshold else "open"
        is_occupied = occupied >= slide_threshold
    else:
        state_str = "close" if occupied >= awning_threshold else "open"
        is_occupied = occupied >= awning_threshold

    # 回傳結構化資料，便於測試程式斷言
    return {
        "status": "success",
        "state_id": state_str,
        "is_occupied": is_occupied,
        "occupied_zones_count": occupied,
        "total_zones": len(local_zone_states),
        "zones": {f"{k[0]}_{k[1]}": v for k, v in local_zone_states.items()},
        "lights": {f"{k[0]}_{k[1]}": v for k, v in local_light_levels.items()}
    }

# ==========================================
# CLI 進入點
# ==========================================
def main():
    parser = argparse.ArgumentParser(description="Aqara FP2 HomeKit 整合工具")
    parser.add_argument("action", choices=["discover", "pair", "monitor"], 
                        help="執行的動作：discover(尋找設備), pair(配對), monitor(監聽狀態)")
    parser.add_argument("--mode", choices=["awning", "slide"], default="awning",
                        help="監聽模式：awning(雨遮, 預設), slide(旅行車側推艙)")
    parser.add_argument("--alias", default="my_fp2_sensor", help="設備配對名稱 (預設: my_fp2_sensor)")
    parser.add_argument("--setup-code", default="", help="設備配對碼 (pair 時使用)")
    args = parser.parse_args()

    try:
        if args.action == "discover":
            asyncio.run(do_discover())
        elif args.action == "pair":
            asyncio.run(do_pair(args.alias, args.setup_code))
        elif args.action == "monitor":
            asyncio.run(do_monitor(args.alias, args.mode))
    except KeyboardInterrupt:
        print("\n已終止。")


if __name__ == "__main__":
    main()
