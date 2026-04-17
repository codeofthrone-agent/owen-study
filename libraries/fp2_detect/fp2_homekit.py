"""
fp2_homekit.py - Aqara FP2 HomeKit 整合工具 (All-in-One)

提供三個主要功能：
1. discover: 尋找區網內的 HomeKit 設備
2. pair: 自動發現 FP2 並配對（使用 .env 的 fp2_setup_code）
3. monitor: 監聽 FP2 的所有 OccupancySensor (區域佔用狀態)，並判定雨遮/空間是否被佔用

設備發現：
- macOS: 使用 dns-sd（系統內建）
- Linux: 使用 avahi-browse（需安裝 avahi-utils）

配對後再連線：
- 優先使用 pairing_data.json 中儲存的 IP 直接連線
- 只有連線失敗（FP2 重啟/換 IP）才重新發現

多台 FP2 支援：透過 --pairing-file 指定不同配對檔案
  例：uv run python fp2_homekit.py pair --pairing-file tpe_pairing_data.json
      uv run python fp2_homekit.py monitor --pairing-file us_pairing_data.json
"""

import argparse
import asyncio
import logging
import os
import platform
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from aiohomekit import Controller
from aiohomekit.controller.ip import IpDiscovery
from aiohomekit.exceptions import AlreadyPairedError
from aiohomekit.model import Categories
from aiohomekit.model.feature_flags import FeatureFlags
from aiohomekit.model.status_flags import StatusFlags
from aiohomekit.zeroconf import HAP_TYPE_TCP, HAP_TYPE_UDP, HomeKitService, ZeroconfServiceListener
from dotenv import load_dotenv
from zeroconf.asyncio import AsyncServiceBrowser, AsyncZeroconf

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
        total = len(self.zone_states)
        slide_threshold = int(self.current_options.get("slide_threshold", 1))
        awning_threshold = int(self.current_options.get("awning_threshold", 2))
        # 若實際 zone 數量少於設定的閾值，自動下調至 1（避免永遠無法觸發）
        if total < awning_threshold:
            awning_threshold = 1
        if total < slide_threshold:
            slide_threshold = 1

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


async def _lookup_fp2_macos(instance_name: str) -> Optional[Tuple[str, int, str, int]]:
    """dns-sd -L 查詢單一設備，回傳 (host, port, device_id, sf) 或 None"""
    lookup = await asyncio.create_subprocess_exec(
        "dns-sd", "-L", instance_name, "_hap._tcp", "local",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
    )
    host, port, device_id, sf = None, None, None, None
    try:
        async with asyncio.timeout(10):
            while True:
                line = (await lookup.stdout.readline()).decode()
                m = re.search(r'can be reached at (\S+?):(\d+)', line)
                if m:
                    host = m.group(1).rstrip('.')
                    port = int(m.group(2))
                m2 = re.search(r'\bid=([0-9A-Fa-f:]{17})', line)
                if m2:
                    device_id = m2.group(1)
                m3 = re.search(r'\bsf=(\d+)', line)
                if m3:
                    sf = int(m3.group(1))
                if host and port and device_id and sf is not None:
                    break
    except asyncio.TimeoutError:
        pass
    finally:
        lookup.terminate()
        await lookup.wait()

    if not (host and port and device_id):
        return None
    return host, port, device_id, sf if sf is not None else 1


async def _discover_fp2_macos(timeout: int = 90, unpaired_only: bool = False) -> Optional[Tuple[str, int, str]]:
    """macOS: 用 dns-sd 發現 FP2，回傳 (ip, port, device_id)。
    unpaired_only=True: 只找 sf=1（用於 pair）；False: 接受任何 sf（用於 monitor 重新發現）
    """
    print(f"  使用 dns-sd 掃描（最多 {timeout} 秒）...")

    browse = await asyncio.create_subprocess_exec(
        "dns-sd", "-B", "_hap._tcp", "local",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
    )
    host, port, device_id = None, None, None
    try:
        async with asyncio.timeout(timeout):
            while True:
                line = (await browse.stdout.readline()).decode()
                if not (("FP2" in line or "Presence" in line) and "Add" in line):
                    continue
                parts = line.strip().split()
                if len(parts) < 7:
                    continue
                instance_name = " ".join(parts[6:])
                print(f"  發現設備: {instance_name}，查詢狀態...")
                result = await _lookup_fp2_macos(instance_name)
                if not result:
                    continue
                h, p, did, sf = result
                if unpaired_only and sf != 1:
                    print(f"  跳過 {instance_name}（sf={sf}，已配對）")
                    continue
                host, port, device_id = h, p, did
                break
    except asyncio.TimeoutError:
        pass
    finally:
        browse.terminate()
        await browse.wait()

    if not (host and port and device_id):
        return None

    resolve = await asyncio.create_subprocess_exec(
        "dns-sd", "-G", "v4", host,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
    )
    ip = None
    try:
        async with asyncio.timeout(10):
            while True:
                line = (await resolve.stdout.readline()).decode()
                m = re.search(r'Add\s+\S+\s+\S+\s+\S+\s+(\d+\.\d+\.\d+\.\d+)', line)
                if m:
                    ip = m.group(1)
                    break
    except asyncio.TimeoutError:
        pass
    finally:
        resolve.terminate()
        await resolve.wait()

    if not ip:
        return None
    print(f"  解析完成: {ip}:{port}  Device ID: {device_id}")
    return ip, port, device_id


async def _discover_fp2_linux(timeout: int = 90, unpaired_only: bool = False) -> Optional[Tuple[str, int, str]]:
    """Linux: 用 avahi-browse -r 發現 FP2，回傳 (ip, port, device_id)"""
    print(f"  使用 avahi-browse 掃描（最多 {timeout} 秒）...")

    proc = await asyncio.create_subprocess_exec(
        "avahi-browse", "-r", "_hap._tcp",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
    )
    ip, port, device_id, sf = None, None, None, None
    in_block = False
    try:
        async with asyncio.timeout(timeout):
            while True:
                line = (await proc.stdout.readline()).decode()
                if not line:
                    break
                if ("FP2" in line or "Presence" in line) and line.startswith("="):
                    in_block = True
                    ip, port, device_id, sf = None, None, None, None  # 重置，準備讀新設備
                if in_block:
                    m = re.search(r'address = \[(\d+\.\d+\.\d+\.\d+)\]', line)
                    if m:
                        ip = m.group(1)
                    m = re.search(r'port = \[(\d+)\]', line)
                    if m:
                        port = int(m.group(1))
                    m = re.search(r'"id=([0-9A-Fa-f:]{17})"', line)
                    if m:
                        device_id = m.group(1)
                    m = re.search(r'"sf=(\d+)"', line)
                    if m:
                        sf = int(m.group(1))
                    if ip and port and device_id and sf is not None:
                        if unpaired_only and sf != 1:
                            print(f"  跳過已配對設備（sf={sf}），繼續尋找...")
                            in_block = False
                            ip, port, device_id, sf = None, None, None, None
                        else:
                            break
    except asyncio.TimeoutError:
        pass
    finally:
        proc.terminate()
        await proc.wait()

    if not (ip and port and device_id):
        return None
    print(f"  解析完成: {ip}:{port}  Device ID: {device_id}")
    return ip, port, device_id


async def _discover_fp2(timeout: int = 90, unpaired_only: bool = False) -> Optional[Tuple[str, int, str]]:
    """自動選擇平台工具發現 FP2：macOS 用 dns-sd，Linux 用 avahi-browse"""
    if platform.system() == "Darwin":
        return await _discover_fp2_macos(timeout, unpaired_only=unpaired_only)
    else:
        return await _discover_fp2_linux(timeout, unpaired_only=unpaired_only)


# ==========================================
# 1. 設備探索 (Discover)
# ==========================================
async def do_discover():
    print("=== 尋找區網內的 HomeKit 設備 (掃描 20 秒) ===")
    azc = AsyncZeroconf()
    AsyncServiceBrowser(azc.zeroconf, [HAP_TYPE_TCP, HAP_TYPE_UDP], listener=ZeroconfServiceListener())
    controller = Controller(async_zeroconf_instance=azc)
    await controller.async_start()
    
    found_any = False
    fp2_unpaired = []
    print(f"\nScanning...")
    print("-" * 50)
    
    await asyncio.sleep(20)
    
    for device_id in controller.discoveries:
        dev = controller.discoveries[device_id]
        found_any = True
        desc = dev.description
        name = desc.name
        model = desc.model
        ip = desc.address
        sf = int(desc.status_flags)
        status = "🟢 可配對 (sf=1)" if sf == 1 else "🔴 已配對 (sf=0)"
        
        print(f"名稱: {name}")
        print(f"型號: {model} | IP: {ip} | ID: {device_id}")
        print(f"狀態: {status}")
        print("-" * 50)
        
        # 記錄可配對的 FP2
        if sf == 1 and ("FP2" in name or "PS-S02D" in model or "Presence" in name):
            fp2_unpaired.append(dev)

    if not found_any:
        print("找不到任何 HomeKit 設備。")
    
    if fp2_unpaired:
        print("\n💡 發現尚未配對的 FP2，但由於 discover 指令不帶配對碼，請使用 pair 指令進行配對。")
        
    await controller.async_stop()
    await azc.async_close()

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
    print(f"目標設備: {target_device.description.name} | 使用 Setup Code: {setup_code} | Alias: {alias}")
    
    try:
        print("配對中...")
        finish_pairing = await target_device.async_start_pairing(alias)
        await finish_pairing(setup_code)
        
        controller.save_data(PAIRING_FILE)
        print(f"✅ 配對成功！設定已儲存至 {PAIRING_FILE}")
    except AlreadyPairedError:
        print("⚠️ 設備已配對過。如果需要重新配對，請先重置 FP2 並刪除 pairing_data.json")
    except Exception as e:
        print(f"❌ 配對失敗: {e}")

async def do_pair(alias: str, setup_code: str, pairing_file: str = PAIRING_FILE):
    """自動發現 FP2 並配對（macOS: dns-sd / Linux: avahi-browse）"""
    print("=== 尋找可配對的 FP2 ===")
    result = await _discover_fp2(timeout=90, unpaired_only=True)
    if not result:
        print("❌ 找不到 FP2，請確認設備已開機並處於配對模式（黃燈閃爍）")
        return
    ip, port, device_id = result
    await do_pair_ip(ip, port, device_id, alias, setup_code, pairing_file)


# ==========================================
# 3. 狀態監聽 (Monitor)
# ==========================================
# (check_state 和 on_event 已移至 FP2StateManager)


async def _ensure_connected(controller: Controller, alias: str, pairing_file: str):
    """確保 FP2 連線，回傳 (services, error_msg)。

    策略：
    1. 先用 pairing_data.json 中儲存的 IP 直接連線（最快，FP2 未重啟時不需 mDNS）
    2. 若連線失敗（FP2 重啟後 IP/Port 改變），再用 dns-sd/avahi 重新發現並重試
    """
    pairing = controller.aliases.get(alias)
    if not pairing:
        return None, f"配對資料中找不到 FP2 (Alias: {alias})"

    stored_ip = pairing.pairing_data.get("AccessoryIP", "")
    stored_port = pairing.pairing_data.get("AccessoryPort", 0)

    if stored_ip:
        print(f"連線中 {stored_ip}:{stored_port}...")
        try:
            services = await asyncio.wait_for(
                pairing.list_accessories_and_characteristics(), timeout=15
            )
            return services, None
        except Exception:
            print("直接連線失敗，重新發現 FP2...")

    result = await _discover_fp2(timeout=90)
    if not result:
        return None, "找不到 FP2，請確認設備已連上 Wi-Fi"

    ip, port, _ = result
    pairing.pairing_data["AccessoryIP"] = ip
    pairing.pairing_data["AccessoryPort"] = port
    # 同步更新 connection 物件，否則實際 TCP 連線仍用舊 IP/Port
    if hasattr(pairing, "connection") and pairing.connection is not None:
        pairing.connection.hosts = [ip]
        pairing.connection.port = port
        pairing.connection.reconnect_soon()  # 中斷 backoff sleep，立即用新 IP 重連
    controller.save_data(pairing_file)  # 儲存新 IP 供下次直連

    try:
        services = await asyncio.wait_for(
            pairing.list_accessories_and_characteristics(), timeout=15
        )
        return services, None
    except Exception as e:
        return None, f"連線失敗: {e}"


async def do_monitor(alias: str, mode: str, pairing_file: str = PAIRING_FILE):
    state_mgr = FP2StateManager(mode=mode)

    print(f"=== FP2 HomeKit 區域佔用監控 ({alias} - {'旅行車側推艙模式' if mode == 'slide' else '雨遮模式'}) ===")
    azc = AsyncZeroconf()
    AsyncServiceBrowser(azc.zeroconf, [HAP_TYPE_TCP, HAP_TYPE_UDP], listener=ZeroconfServiceListener())
    controller = Controller(async_zeroconf_instance=azc)
    await controller.async_start()

    try:
        controller.load_data(pairing_file)
    except FileNotFoundError:
        print(f"❌ 找不到 {pairing_file}，請先執行 'uv run python fp2_homekit.py pair --pairing-file {pairing_file}'")
        await controller.async_stop()
        await azc.async_close()
        return

    if alias not in controller.aliases:
        print(f"❌ 配對資料中找不到 FP2 (Alias: {alias})")
        await controller.async_stop()
        await azc.async_close()
        return

    services, err = await _ensure_connected(controller, alias, pairing_file)
    if err:
        print(f"❌ {err}")
        await controller.async_stop()
        await azc.async_close()
        return

    pairing = controller.aliases[alias]
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
        await controller.async_stop()
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
        tick = 0
        while True:
            await asyncio.sleep(1)
            tick += 1
            # 每 5 秒主動輪詢一次，作為 push 事件失效時的備援
            # 使用 list_accessories_and_characteristics（與初始連線同一路徑，已驗證可用）
            if tick % 5 == 0:
                try:
                    fresh = await asyncio.wait_for(
                        pairing.list_accessories_and_characteristics(), timeout=12
                    )
                    fresh_accs = fresh if isinstance(fresh, list) else fresh.get("accessories", [])
                    for acc in fresh_accs:
                        aid = acc.get("aid", 1)
                        for svc in acc.get("services", []):
                            for char in svc.get("characteristics", []):
                                ctype = char.get("type", "")
                                iid = char["iid"]
                                key = (aid, iid)
                                if OCCUPANCY_UUID.upper() in ctype.upper() or ctype.upper() == "71":
                                    if key in state_mgr.zone_states:
                                        old = state_mgr.zone_states[key]
                                        new_val = int(char.get("value", 0))
                                        if old != new_val:
                                            state_mgr.zone_states[key] = new_val
                                            label = state_mgr.zone_labels.get(key, f"[{aid},{iid}]")
                                            status = "🛑 空間被佔用" if new_val == 1 else "⚪ 空間淨空"
                                            print(f"[{format_time()}] 🔄 輪詢更新 {label}: {status}  (舊={old}→新={new_val})")
                                            new_state = state_mgr.check_state()
                                            if new_state != state_mgr.current_state:
                                                state_mgr.current_state = new_state
                                                occ = sum(1 for v in state_mgr.zone_states.values() if v == 1)
                                                print(f"\n[{format_time()}] ══ 系統狀態改變: {state_mgr.current_state} "
                                                      f"（{occ}/{len(state_mgr.zone_states)} 個區域有訊號）══\n")
                                elif LIGHT_LEVEL_UUID.upper() in ctype.upper() or ctype.upper() == "6B":
                                    if key in state_mgr.light_levels:
                                        new_lx = float(char.get("value", 0))
                                        old_lx = state_mgr.light_levels[key]
                                        if abs(new_lx - old_lx) >= 1.0:
                                            state_mgr.light_levels[key] = new_lx
                                            print(f"[{format_time()}] 🔄 輪詢更新 💡 光照度: {new_lx} lux (舊={old_lx})")
                except Exception as poll_err:
                    err_name = type(poll_err).__name__
                    print(f"[{format_time()}] ⚠️ 輪詢失敗: {err_name}: {poll_err}")
                    # 連線斷開時自動重新發現並重連
                    if any(k in err_name for k in ("Disconnected", "Connection", "Timeout")):
                        print(f"[{format_time()}] 🔄 偵測到斷線，重新連線中...")
                        await asyncio.sleep(5)  # 等設備穩定
                        services, err = await _ensure_connected(controller, alias, pairing_file)
                        if err:
                            print(f"[{format_time()}] ❌ 重新連線失敗: {err}")
                        else:
                            pairing = controller.aliases[alias]
                            await pairing.subscribe(subscribe_targets)
                            pairing.dispatcher_connect(state_mgr.on_event)
                            print(f"[{format_time()}] ✅ 重新連線成功，繼續監聽")
            if tick % 30 == 0:
                occupied_count = sum(1 for v in state_mgr.zone_states.values() if v == 1)
                print(f"[{format_time()}] ♥ 心跳確認 — 目前狀態: {state_mgr.current_state}（{occupied_count}/{len(state_mgr.zone_states)} 個區域有訊號）")
    except KeyboardInterrupt:
        pass
    finally:
        print("\n關閉連線...")
        await controller.async_stop()
        await azc.async_close()


# ==========================================
# 4. 單次查詢 (Single-shot query for Robot Framework)
# ==========================================
async def get_status_once(alias: str, mode: str, options: dict = None,
                         pairing_file: str = PAIRING_FILE) -> dict:
    """提供給 Robot Framework 單次讀取狀態的 API"""
    safe_options = options or {}

    azc = AsyncZeroconf()
    AsyncServiceBrowser(azc.zeroconf, [HAP_TYPE_TCP, HAP_TYPE_UDP], listener=ZeroconfServiceListener())
    controller = Controller(async_zeroconf_instance=azc)
    await controller.async_start()

    # 支援相對路徑與絕對路徑（Robot Framework 從專案根執行時需要絕對路徑）
    resolved_file = pairing_file
    if not os.path.isabs(pairing_file):
        abs_path = os.path.join(os.path.dirname(__file__), pairing_file)
        if os.path.exists(abs_path):
            resolved_file = abs_path

    try:
        controller.load_data(resolved_file)
    except FileNotFoundError:
        await controller.async_stop()
        await azc.async_close()
        return {"error": f"找不到配對設定檔 {resolved_file}，請先執行 pair。"}

    if alias not in controller.aliases:
        await controller.async_stop()
        await azc.async_close()
        return {"error": f"配對資料中找不到 FP2 (Alias: {alias})"}

    services, err = await _ensure_connected(controller, alias, resolved_file)
    if err:
        await controller.async_stop()
        await azc.async_close()
        return {"error": err}

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

    await controller.async_stop()
    await azc.async_close()

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
# 4. 直接 IP 配對 (Pair with IP)
# ==========================================
async def do_pair_ip(ip: str, port: int, device_id: str, alias: str, setup_code: str,
                    pairing_file: str = PAIRING_FILE):
    """繞過 mDNS，直接透過 IP/Port 配對（手動指定或由 do_pair 自動呼叫）"""
    if not setup_code:
        setup_code = os.getenv("FP2_SETUP_CODE") or os.getenv("fp2_setup_code")
    if not setup_code:
        print("❌ 錯誤：未提供 setup_code 且 .env 找不到 'fp2_setup_code'")
        return

    if len(setup_code) == 8 and "-" not in setup_code:
        setup_code = f"{setup_code[:3]}-{setup_code[3:5]}-{setup_code[5:]}"

    print(f"=== 直接 IP 配對 FP2 ===")
    print(f"IP: {ip}  Port: {port}  Device ID: {device_id}  Setup Code: {setup_code}")
    print(f"配對檔案: {pairing_file}")

    azc = AsyncZeroconf()
    AsyncServiceBrowser(azc.zeroconf, [HAP_TYPE_TCP, HAP_TYPE_UDP], listener=ZeroconfServiceListener())
    controller = Controller(async_zeroconf_instance=azc)
    await controller.async_start()

    desc = HomeKitService(
        name=alias,
        id=device_id.lower(),
        model="PS-S02D",
        feature_flags=FeatureFlags(2),
        status_flags=StatusFlags(1),
        config_num=1,
        state_num=1,
        category=Categories(10),
        protocol_version="1.1",
        type=HAP_TYPE_TCP,
        address=ip,
        addresses=[ip],
        port=port,
    )
    device = IpDiscovery(controller, desc)

    try:
        print("配對中...")
        finish_pairing = await device.async_start_pairing(alias)
        pairing_obj = await finish_pairing(setup_code)
        controller.aliases[alias] = pairing_obj  # save_data 依賴 aliases，必須手動註冊
        controller.save_data(pairing_file)
        print(f"✅ 配對成功！設定已儲存至 {pairing_file}")
    except AlreadyPairedError:
        print(f"⚠️ 設備已配對過，若需重新配對請先重置 FP2 並刪除 {pairing_file}")
    except Exception as e:
        print(f"❌ 配對失敗: {e}")
    finally:
        await controller.async_stop()
        await azc.async_close()


# ==========================================
# CLI 進入點
# ==========================================
def main():
    parser = argparse.ArgumentParser(
        description="Aqara FP2 HomeKit 整合工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
多台 FP2 範例：
  uv run python fp2_homekit.py pair    --alias tpe_fp2 --pairing-file tpe_pairing_data.json
  uv run python fp2_homekit.py monitor --alias tpe_fp2 --pairing-file tpe_pairing_data.json
  uv run python fp2_homekit.py pair    --alias us_fp2  --pairing-file us_pairing_data.json
  uv run python fp2_homekit.py monitor --alias us_fp2  --pairing-file us_pairing_data.json
        """,
    )
    parser.add_argument("action", choices=["discover", "pair", "pair-ip", "monitor"],
                        help="執行的動作：discover / pair / pair-ip / monitor")
    parser.add_argument("--mode", choices=["awning", "slide"], default="awning",
                        help="監聽模式：awning(雨遮, 預設), slide(旅行車側推艙)")
    parser.add_argument("--alias", default="my_fp2_sensor",
                        help="設備配對名稱，多台 FP2 時用來區分 (預設: my_fp2_sensor)")
    parser.add_argument("--pairing-file", default=PAIRING_FILE,
                        help=f"配對資料檔案路徑 (預設: {PAIRING_FILE})，多台 FP2 時指定不同檔案")
    parser.add_argument("--setup-code", default="", help="設備配對碼 (pair 時使用，也可設 FP2_SETUP_CODE 環境變數)")
    parser.add_argument("--ip", default="", help="FP2 IP 位址 (pair-ip 時使用)")
    parser.add_argument("--port", type=int, default=0, help="FP2 Port (pair-ip 時使用)")
    parser.add_argument("--device-id", default="", help="FP2 Device ID (pair-ip 時使用，格式 XX:XX:XX:XX:XX:XX)")
    args = parser.parse_args()

    try:
        if args.action == "discover":
            asyncio.run(do_discover())
        elif args.action == "pair":
            asyncio.run(do_pair(args.alias, args.setup_code, args.pairing_file))
        elif args.action == "pair-ip":
            if not args.ip or not args.port or not args.device_id:
                parser.error("pair-ip 需要 --ip, --port, --device-id")
            asyncio.run(do_pair_ip(args.ip, args.port, args.device_id,
                                   args.alias, args.setup_code, args.pairing_file))
        elif args.action == "monitor":
            asyncio.run(do_monitor(args.alias, args.mode, args.pairing_file))
    except KeyboardInterrupt:
        print("\n已終止。")


if __name__ == "__main__":
    main()
