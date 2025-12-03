#!/usr/bin/env python3
# coding: utf-8
"""
多 RTSP 串流監控網頁工具

功能：
- 同時顯示多個 RTSP 影像串流
- 支援四格顯示模式
- 可動態配置 RTSP URL
- 支援影像品質調整
- 響應式網頁設計

版本：v1.0 (2025-11-19)
作者：Claude AI

使用方式：
    python3 multi_rtsp_viewer.py
    然後在瀏覽器開啟: http://localhost:5001
"""

import cv2
import numpy as np
import base64
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from flask import Flask, render_template, request, jsonify, Response
from concurrent.futures import ThreadPoolExecutor
import yaml
import argparse
import socket
import os
from urllib.parse import urlparse, urlunparse

# 嘗試載入 python-dotenv
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("⚠️  python-dotenv 未安裝，無法讀取 .env 文件")
    print("   可使用: pip install python-dotenv 來安裝")

app = Flask(__name__)

def load_env_variables():
    """載入環境變數"""
    if DOTENV_AVAILABLE:
        # 嘗試從多個位置載入 .env 文件
        project_root = Path(__file__).parent.parent
        env_paths = [
            project_root / ".env",
            Path.cwd() / ".env",
            Path(".env")
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                print(f"✅ 載入環境變數: {env_path}")
                return True
        
        print("⚠️  未找到 .env 文件")
    return False

def build_rtsp_url(base_url: str, username: str = None, password: str = None) -> str:
    """
    建構包含認證資訊的 RTSP URL
    
    Args:
        base_url: 基本 RTSP URL (例如: rtsp://192.168.1.100:554/stream1)
        username: 使用者名稱
        password: 密碼
        
    Returns:
        str: 完整的 RTSP URL
    """
    if not username or not password:
        return base_url
    
    try:
        parsed = urlparse(base_url)
        
        # 如果 URL 已經包含認證資訊，則不修改
        if '@' in parsed.netloc:
            return base_url
        
        # 建構新的 netloc 包含認證資訊
        new_netloc = f"{username}:{password}@{parsed.netloc}"
        
        # 重建 URL
        new_parsed = parsed._replace(netloc=new_netloc)
        return urlunparse(new_parsed)
        
    except Exception as e:
        print(f"⚠️  建構 RTSP URL 時發生錯誤: {e}")
        return base_url

def get_rtsp_credentials():
    """
    從環境變數取得 RTSP 認證資訊
    
    Returns:
        tuple: (username, password)
    """
    username = os.getenv('IPCAM_USERNAME', '')
    password = os.getenv('IPCAM_PASSWORD', '')
    
    if username and password:
        print(f"✅ 載入 RTSP 認證: {username[:3]}***")
        return username, password
    else:
        print("⚠️  未找到 RTSP 認證資訊 (IPCAM_USERNAME/IPCAM_PASSWORD)")
        return None, None

class RTSPStreamManager:
    """RTSP 串流管理器"""
    
    def __init__(self, max_workers: int = 4):
        self.streams = {}  # stream_id -> stream_config
        self.latest_frames = {}  # stream_id -> latest_frame
        self.frame_timestamps = {}  # stream_id -> timestamp
        self.capture_threads = {}  # stream_id -> thread
        self.running = {}  # stream_id -> bool
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.lock = threading.Lock()
        
    def add_stream(self, stream_id: str, rtsp_url: str, name: str = "", refresh_rate: float = 1.0, auto_auth: bool = True) -> bool:
        """
        添加新的 RTSP 串流
        
        Args:
            stream_id: 串流唯一識別碼
            rtsp_url: RTSP 串流 URL
            name: 顯示名稱
            refresh_rate: 更新頻率（秒）
            auto_auth: 是否自動添加認證資訊
            
        Returns:
            bool: 是否成功添加
        """
        try:
            # 如果啟用自動認證且 URL 沒有包含認證資訊，則自動添加
            final_rtsp_url = rtsp_url
            if auto_auth and '@' not in rtsp_url:
                username, password = get_rtsp_credentials()
                if username and password:
                    final_rtsp_url = build_rtsp_url(rtsp_url, username, password)
                    print(f"🔐 為串流 {stream_id} 添加認證資訊")
            
            with self.lock:
                if stream_id in self.streams:
                    print(f"⚠️  串流 {stream_id} 已存在，將更新配置")
                    self.remove_stream(stream_id)
                
                self.streams[stream_id] = {
                    'rtsp_url': final_rtsp_url,
                    'original_url': rtsp_url,  # 保存原始 URL 用於顯示
                    'name': name or f"串流 {stream_id}",
                    'refresh_rate': refresh_rate,
                    'status': 'stopped'
                }
                
                self.latest_frames[stream_id] = None
                self.frame_timestamps[stream_id] = 0
                self.running[stream_id] = False
                
            # 顯示時使用原始 URL（不包含密碼）
            display_url = rtsp_url if len(rtsp_url) < 60 else rtsp_url[:60] + "..."
            print(f"✅ 成功添加串流: {stream_id} -> {display_url}")
            return True
            
        except Exception as e:
            print(f"❌ 添加串流失敗: {e}")
            return False
    
    def remove_stream(self, stream_id: str) -> bool:
        """移除 RTSP 串流"""
        try:
            with self.lock:
                if stream_id not in self.streams:
                    return False
                
                # 停止串流
                self.stop_stream(stream_id)
                
                # 清理資源
                del self.streams[stream_id]
                if stream_id in self.latest_frames:
                    del self.latest_frames[stream_id]
                if stream_id in self.frame_timestamps:
                    del self.frame_timestamps[stream_id]
                if stream_id in self.capture_threads:
                    del self.capture_threads[stream_id]
                if stream_id in self.running:
                    del self.running[stream_id]
            
            print(f"✅ 成功移除串流: {stream_id}")
            return True
            
        except Exception as e:
            print(f"❌ 移除串流失敗: {e}")
            return False
    
    def start_stream(self, stream_id: str) -> bool:
        """啟動 RTSP 串流擷取"""
        if stream_id not in self.streams:
            return False
        
        if self.running.get(stream_id, False):
            print(f"⚠️  串流 {stream_id} 已在運行中")
            return True
        
        try:
            self.running[stream_id] = True
            self.streams[stream_id]['status'] = 'starting'
            
            # 啟動擷取線程
            thread = threading.Thread(
                target=self._capture_stream_worker,
                args=(stream_id,),
                daemon=True
            )
            thread.start()
            self.capture_threads[stream_id] = thread
            
            print(f"🚀 啟動串流擷取: {stream_id}")
            return True
            
        except Exception as e:
            print(f"❌ 啟動串流失敗: {e}")
            self.running[stream_id] = False
            self.streams[stream_id]['status'] = 'error'
            return False
    
    def stop_stream(self, stream_id: str) -> bool:
        """停止 RTSP 串流擷取"""
        if stream_id not in self.streams:
            return False
        
        try:
            self.running[stream_id] = False
            self.streams[stream_id]['status'] = 'stopped'
            
            # 等待線程結束
            if stream_id in self.capture_threads:
                thread = self.capture_threads[stream_id]
                if thread.is_alive():
                    thread.join(timeout=2.0)
            
            print(f"⏹️  停止串流擷取: {stream_id}")
            return True
            
        except Exception as e:
            print(f"❌ 停止串流失敗: {e}")
            return False
    
    def _capture_stream_worker(self, stream_id: str):
        """串流擷取工作線程"""
        stream_config = self.streams[stream_id]
        rtsp_url = stream_config['rtsp_url']
        refresh_rate = stream_config['refresh_rate']
        
        print(f"📡 開始擷取串流: {stream_id} -> {rtsp_url}")
        
        cap = None
        consecutive_failures = 0
        max_failures = 5
        
        try:
            while self.running.get(stream_id, False):
                try:
                    # 初始化攝影機連接
                    if cap is None or not cap.isOpened():
                        if cap is not None:
                            cap.release()
                        
                        print(f"🔌 連接 RTSP: {stream_id}")
                        cap = cv2.VideoCapture(rtsp_url)
                        
                        if not cap.isOpened():
                            raise Exception(f"無法連接 RTSP: {rtsp_url}")
                        
                        # 設定緩衝區大小
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        self.streams[stream_id]['status'] = 'running'
                        consecutive_failures = 0
                    
                    # 讀取幀
                    ret, frame = cap.read()
                    
                    if ret and frame is not None:
                        # 調整影像大小以節省頻寬
                        height, width = frame.shape[:2]
                        if width > 640:
                            scale = 640 / width
                            new_width = 640
                            new_height = int(height * scale)
                            frame = cv2.resize(frame, (new_width, new_height))
                        
                        # 更新最新幀
                        with self.lock:
                            self.latest_frames[stream_id] = frame.copy()
                            self.frame_timestamps[stream_id] = time.time()
                        
                        consecutive_failures = 0
                    else:
                        consecutive_failures += 1
                        if consecutive_failures >= max_failures:
                            raise Exception(f"連續讀取失敗 {max_failures} 次")
                    
                    # 控制更新頻率
                    time.sleep(refresh_rate)
                    
                except Exception as e:
                    print(f"❌ 串流 {stream_id} 擷取錯誤: {e}")
                    self.streams[stream_id]['status'] = 'error'
                    
                    if cap is not None:
                        cap.release()
                        cap = None
                    
                    # 等待重試
                    time.sleep(5.0)
                    consecutive_failures = 0
                    
                    if self.running.get(stream_id, False):
                        print(f"🔄 嘗試重新連接串流: {stream_id}")
        
        finally:
            if cap is not None:
                cap.release()
            
            self.streams[stream_id]['status'] = 'stopped'
            print(f"🛑 串流擷取線程結束: {stream_id}")
    
    def get_latest_frame_base64(self, stream_id: str) -> Optional[str]:
        """取得最新幀的 Base64 編碼"""
        with self.lock:
            frame = self.latest_frames.get(stream_id)
            if frame is None:
                return None
            
            try:
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                return base64.b64encode(buffer).decode('utf-8')
            except Exception as e:
                print(f"❌ 編碼幀失敗 {stream_id}: {e}")
                return None
    
    def get_stream_info(self, stream_id: str) -> Optional[Dict]:
        """取得串流資訊"""
        if stream_id not in self.streams:
            return None
        
        stream_config = self.streams[stream_id].copy()
        
        with self.lock:
            stream_config['last_update'] = self.frame_timestamps.get(stream_id, 0)
            stream_config['has_frame'] = stream_id in self.latest_frames and self.latest_frames[stream_id] is not None
        
        return stream_config
    
    def get_all_streams_info(self) -> Dict:
        """取得所有串流資訊"""
        result = {}
        for stream_id in self.streams:
            result[stream_id] = self.get_stream_info(stream_id)
        return result
    
    def stop_all_streams(self):
        """停止所有串流"""
        for stream_id in list(self.streams.keys()):
            self.stop_stream(stream_id)

# 全域串流管理器
stream_manager = RTSPStreamManager()

# 載入 EnvironmentConfig
import sys
import os
# 將專案根目錄加入 sys.path 以便匯入 config 模組
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from config.robot_arm.environment_config import EnvironmentConfig
except ImportError as e:
    print(f"❌ 無法載入 EnvironmentConfig: {e}")
    sys.exit(1)

def load_streams_from_env(environment: str, default_interval: float = 1.0, stream_suffix: str = None):
    """從指定環境載入串流配置"""
    try:
        if not EnvironmentConfig.validate_environment(environment):
            print(f"⚠️  找不到環境配置: {environment}")
            return False
            
        env_config = EnvironmentConfig.get_environment(environment)
        cameras = EnvironmentConfig.get_cameras(environment)
        
        print(f"🔄 切換至環境: {environment} ({env_config.get('description', '')})")
        
        # 停止並移除現有串流
        stream_manager.stop_all_streams()
        current_streams = list(stream_manager.streams.keys())
        for stream_id in current_streams:
            stream_manager.remove_stream(stream_id)
            
        # 載入新串流
        count = 0
        for cam in cameras:
            cam_id = cam.get('id')
            rtsp_url = cam.get('rtsp_url')
            
            # 如果用戶有指定 suffix (例如 live1)，則覆蓋預設 URL
            if stream_suffix:
                # 解析原始 URL
                parsed = urlparse(rtsp_url)
                # 替換路徑
                new_path = f"/{stream_suffix}" if not stream_suffix.startswith('/') else stream_suffix
                new_parsed = parsed._replace(path=new_path)
                rtsp_url = urlunparse(new_parsed)
                
            stream_manager.add_stream(
                stream_id=cam_id,
                rtsp_url=rtsp_url,
                name=cam.get('description', cam_id),
                refresh_rate=default_interval,
                auto_auth=False # EnvironmentConfig 已經處理了認證
            )
            count += 1
            
        print(f"✅ 已載入 {count} 個串流 (環境: {environment})")
        return True
        
    except Exception as e:
        print(f"❌ 載入環境串流失敗: {e}")
        return False

def load_default_config(default_interval: float = 1.0, stream_suffix: str = None):
    """載入預設配置 (預設使用 taipei_lab 環境)"""
    # 載入環境變數
    load_env_variables()
    
    # 預設載入 taipei_lab 環境
    load_streams_from_env('taipei_lab', default_interval, stream_suffix)

# Flask 路由
@app.route('/')
def index():
    """主頁面"""
    return render_template('multi_rtsp_viewer.html')

@app.route('/api/streams', methods=['GET'])
def get_streams():
    """取得所有串流資訊"""
    streams_info = stream_manager.get_all_streams_info()
    return jsonify({
        'success': True,
        'streams': streams_info,
        'total_count': len(streams_info)
    })

@app.route('/api/streams/<stream_id>/frame', methods=['GET'])
def get_stream_frame(stream_id):
    """取得指定串流的最新幀"""
    frame_base64 = stream_manager.get_latest_frame_base64(stream_id)
    
    if frame_base64 is None:
        return jsonify({
            'success': False,
            'error': f'串流 {stream_id} 無可用幀'
        })
    
    return jsonify({
        'success': True,
        'stream_id': stream_id,
        'image_base64': frame_base64,
        'timestamp': time.time()
    })

@app.route('/api/streams/<stream_id>/start', methods=['POST'])
def start_stream(stream_id):
    """啟動指定串流"""
    success = stream_manager.start_stream(stream_id)
    
    return jsonify({
        'success': success,
        'stream_id': stream_id,
        'message': f'串流 {stream_id} {"啟動成功" if success else "啟動失敗"}'
    })

@app.route('/api/streams/<stream_id>/stop', methods=['POST'])
def stop_stream(stream_id):
    """停止指定串流"""
    success = stream_manager.stop_stream(stream_id)
    
    return jsonify({
        'success': success,
        'stream_id': stream_id,
        'message': f'串流 {stream_id} {"停止成功" if success else "停止失敗"}'
    })

@app.route('/api/streams', methods=['POST'])
def add_stream():
    """添加新串流"""
    data = request.json
    
    stream_id = data.get('stream_id')
    rtsp_url = data.get('rtsp_url')
    name = data.get('name', '')
    refresh_rate = data.get('refresh_rate', 1.0)
    
    if not stream_id or not rtsp_url:
        return jsonify({
            'success': False,
            'error': '缺少必要參數: stream_id 或 rtsp_url'
        })
    
    success = stream_manager.add_stream(stream_id, rtsp_url, name, refresh_rate)
    
    return jsonify({
        'success': success,
        'stream_id': stream_id,
        'message': f'串流 {stream_id} {"添加成功" if success else "添加失敗"}'
    })

@app.route('/api/streams/<stream_id>', methods=['DELETE'])
def remove_stream(stream_id):
    """移除指定串流"""
    success = stream_manager.remove_stream(stream_id)
    
    return jsonify({
        'success': success,
        'stream_id': stream_id,
        'message': f'串流 {stream_id} {"移除成功" if success else "移除失敗"}'
    })

@app.route('/api/streams/start_all', methods=['POST'])
def start_all_streams():
    """啟動所有串流"""
    streams_info = stream_manager.get_all_streams_info()
    results = {}
    
    for stream_id in streams_info:
        results[stream_id] = stream_manager.start_stream(stream_id)
    
    return jsonify({
        'success': True,
        'results': results,
        'message': '批次啟動完成'
    })

@app.route('/api/streams/stop_all', methods=['POST'])
def stop_all_streams():
    """停止所有串流"""
    stream_manager.stop_all_streams()
    
    return jsonify({
        'success': True,
        'message': '所有串流已停止'
    })

@app.route('/api/environments', methods=['GET'])
def get_environments():
    """取得可用環境列表"""
    try:
        env_list = EnvironmentConfig.list_environments()
        result = []
        
        for env_id in env_list:
            env_config = EnvironmentConfig.get_environment(env_id)
            cameras = EnvironmentConfig.get_cameras(env_id)
            
            result.append({
                'id': env_id,
                'description': env_config.get('name', env_id),
                'camera_count': len(cameras)
            })
            
        return jsonify({
            'success': True,
            'environments': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/environments/<env_name>/load', methods=['POST'])
def load_environment(env_name):
    """載入指定環境"""
    data = request.json or {}
    interval = data.get('interval', 1.0)
    suffix = data.get('suffix')  # 可選，若無則使用預設配置
    
    success = load_streams_from_env(env_name, interval, suffix)
    
    return jsonify({
        'success': success,
        'message': f'環境 {env_name} {"載入成功" if success else "載入失敗"}'
    })

def get_local_ip():
    """取得本機 IP 位址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def main():
    parser = argparse.ArgumentParser(description='多 RTSP 串流監控網頁工具')
    parser.add_argument('--port', type=int, default=5001, help='Web 伺服器端口 (預設: 5001)')
    parser.add_argument('--no-default-config', action='store_true', help='不載入預設配置')
    parser.add_argument('--max-workers', type=int, default=4, help='最大工作線程數 (預設: 4)')
    parser.add_argument('--interval', type=float, default=1.0, help='預設更新頻率 (秒) (預設: 1.0)')
    parser.add_argument('--stream-suffix', type=str, default='live1', help='RTSP 串流路徑後綴 (例如: stream1, live1) (預設: 使用設定檔中的路徑)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📺 多 RTSP 串流監控網頁工具")
    print("=" * 60)
    
    # 載入預設配置
    if not args.no_default_config:
        load_default_config(default_interval=args.interval, stream_suffix=args.stream_suffix)
    
    try:
        local_ip = get_local_ip()
        print(f"🌐 Web 伺服器啟動於:")
        print(f"   - 本機: http://localhost:{args.port}")
        print(f"   - 區網: http://{local_ip}:{args.port}")
        print(f"📱 在手機或平板上可透過區網 IP 存取")
        print("=" * 60)
        
        app.run(host='0.0.0.0', port=args.port, debug=False, threaded=True)
        
    except KeyboardInterrupt:
        print("\n🛑 正在停止所有串流...")
        stream_manager.stop_all_streams()
        print("✅ 程式已安全結束")
    
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())