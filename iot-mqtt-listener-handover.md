# IoT MQTT Listener — 開發交接文件

> 開發利用 `awsiotsdk` (AWS IoT Device SDK for Python) 訂閱 AWS IoT Core MQTT 主題，替代 AWS Console MQTT test client 的聆聽程式

---

## 1. 背景與目的

**問題**：AWS Console 的 MQTT test client 每次使用都要開瀏覽器、登入 AWS、進 IoT Core 頁面、輸入 topic filter，無法自動化，session 還會過期。

**解決方案**：用 `awsiotsdk` 寫一個 Python 腳本，透過 X.509 憑證直接連到 IoT Core MQTT broker 做 subscribe，訊息即時印出或轉存。

**與 Console test client 的關係**：兩者本質相同——都是 MQTT subscriber，訂同一個 topic filter 就會收到完全一樣的訊息。Console 用 IAM 認證（你的 AWS 帳號），腳本用 X.509 憑證（設備憑證）。

---

## 2. 架構

```
┌─────────────────────────────┐
│       AWS IoT Core          │
│       (MQTT Broker)         │
└──────────┬──────────────────┘
           │  publish "device/+/status"
           │
   ┌───────┴────────┐
   │  MQTT Listener  │  ← 本專案
   │  (awsiotsdk)    │
   └───────┬────────┘
           │ stdout / file / DB / webhook
           ▼
    你的 downstream 應用
```

### 元件

| 元件 | 說明 |
|------|------|
| `awsiotsdk` | AWS IoT Device SDK v2 for Python，處理 MQTT 連線、TLS 握手、pub/sub |
| X.509 憑證 | 設備身份認證（`cert.pem` + `private.pem.key` + `AmazonRootCA1.pem`） |
| IoT Core Endpoint | `xxxxxxxxx-ats.iot.<region>.amazonaws.com` |
| IoT Policy | 控制哪些 topic 可 subscribe / receive |

---

## 3. 前置準備

### 3.1 安裝相依套件

```bash
pip install awsiotsdk
```

### 3.2 取得 AWS IoT Core Endpoint

```bash
# 需要先裝好 AWS CLI 並設定 credentials
aws iot describe-endpoint --endpoint-type iot:Data-ATS
```

回傳範例：
```json
{
    "endpointAddress": "abcd1234xyz-ats.iot.ap-northeast-1.amazonaws.com"
}
```

### 3.3 準備憑證 (X.509)

有三種方式：

**方式 A：用 AWS CLI 建立新憑證**（最簡單，測試用）

```bash
aws iot create-keys-and-certificate \
  --set-as-active \
  --certificate-pem-outfile cert.pem \
  --public-key-outfile public.pem \
  --private-key-outfile private.pem.key
```

**方式 B：使用現有設備憑證**（正式環境）

```bash
# 通常 IoT 設備註冊時已有憑證
# 確認 cert.pem + private.pem.key + AmazonRootCA1.pem 都存在
```

**方式 C：下載 Amazon Root CA**

```bash
curl -o AmazonRootCA1.pem https://www.amazontrust.com/repositories/AmazonRootCA1.pem
```

### 3.4 建立 IoT Policy（允許 Subscribe）

如果還沒有適用的 policy：

```bash
aws iot create-policy --policy-name mqtt-listener-policy --policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "iot:Connect",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Subscribe",
      "Resource": "arn:aws:iot:ap-northeast-1:ACCOUNT_ID:topicfilter/*"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Receive",
      "Resource": "arn:aws:iot:ap-northeast-1:ACCOUNT_ID:topic/*"
    }
  ]
}'
```

然後 attach 到憑證：

```bash
aws iot attach-policy --policy-name mqtt-listener-policy --principal "$(cat cert.pem | openssl x509 -noout -fingerprint | cut -d= -f2 | tr -d ':')"
```

---

## 4. 程式碼

### 4.1 基礎版 listen.py（接收即印）

```python
#!/usr/bin/env python3
"""
MQTT Listener — 簡單版

用法:
    python listen.py <endpoint> <topic_filter>

範例:
    python listen.py abcd1234xyz-ats.iot.ap-northeast-1.amazonaws.com "device/#"
"""
import sys, time
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

IOT_ENDPOINT = sys.argv[1]
TOPIC_FILTER = sys.argv[2]
CLIENT_ID = "mqtt-listener-cli"
CERT_PATH = "cert.pem"
KEY_PATH = "private.pem.key"
CA_PATH = "AmazonRootCA1.pem"


def on_message(topic, payload, dup, qos, retain, **kwargs):
    """收到 MQTT 訊息時的回呼"""
    print(f"\n{'='*60}")
    print(f"主題: {topic}")
    print(f"QoS : {qos}")
    print(f"保留: {retain}")
    print(f"{'─'*60}")
    print(payload.decode())
    print(f"{'='*60}")


def on_connection_interrupted(connection, error, **kwargs):
    print(f"⚠️  連線中斷: {error}")


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(f"✅  連線恢復 (session_present={session_present})")


def main():
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=IOT_ENDPOINT,
        cert_filepath=CERT_PATH,
        pri_key_filepath=KEY_PATH,
        ca_filepath=CA_PATH,
        client_bootstrap=client_bootstrap,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=30,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
    )

    print(f"🔗  正在連線到 {IOT_ENDPOINT} ...")
    connect_future = mqtt_connection.connect()
    connect_future.result()
    print(f"✅  已連線 (client_id: {CLIENT_ID})")

    print(f"📡  正在訂閱 {TOPIC_FILTER} ...")
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=TOPIC_FILTER,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message,
    )
    sub_result = subscribe_future.result()
    print(f"✅  訂閱成功 (packet_id={packet_id}, result={sub_result['mqtt:suback']})")

    print(f"⏳  等待訊息中（按 Ctrl+C 離開）...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋  正在斷開連線...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("✅  已斷開連線")


if __name__ == "__main__":
    main()
```

### 4.2 進階版 listen-daemon.py（可 daemon 化 + 存檔）

```python
#!/usr/bin/env python3
"""
MQTT Listener — Daemon 版

功能:
    - 可指定輸出檔案
    - timestamp + topic 每行
    - 支援 SIGTERM 優雅關閉
    - 連線中斷自動重連

用法:
    python listen-daemon.py <endpoint> <topic_filter> [output_file]

範例:
    python listen-daemon.py abcd1234xyz-ats.iot.ap-northeast-1.amazonaws.com "device/#"
    python listen-daemon.py abcd1234xyz-ats.iot.ap-northeast-1.amazonaws.com "device/#" /tmp/mqtt.log
"""
import sys, os, time, signal, json, datetime
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

IOT_ENDPOINT = sys.argv[1]
TOPIC_FILTER = sys.argv[2]
OUTPUT_FILE = sys.argv[3] if len(sys.argv) > 3 else None
CLIENT_ID = f"mqtt-listener-{os.uname().nodename}-{os.getpid()}"
CERT_PATH = "cert.pem"
KEY_PATH = "private.pem.key"
CA_PATH = "AmazonRootCA1.pem"

running = True


def signal_handler(sig, frame):
    global running
    print(f"\n📥  收到 signal {sig}，優雅關閉中...")
    running = False


def log_message(topic, payload):
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "topic": topic,
        "payload": payload.decode(errors="replace"),
    }
    line = json.dumps(entry, ensure_ascii=False)

    # stdout
    print(line)

    # file
    if OUTPUT_FILE:
        with open(OUTPUT_FILE, "a") as f:
            f.write(line + "\n")
            f.flush()


def on_message(topic, payload, **kwargs):
    log_message(topic, payload)


def on_connection_interrupted(connection, error, **kwargs):
    print(json.dumps({
        "event": "connection_interrupted",
        "error": str(error),
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }))


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(json.dumps({
        "event": "connection_resumed",
        "session_present": session_present,
        "return_code": str(return_code),
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }))


def main():
    global running
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=IOT_ENDPOINT,
        cert_filepath=CERT_PATH,
        pri_key_filepath=KEY_PATH,
        ca_filepath=CA_PATH,
        client_bootstrap=client_bootstrap,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=30,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
    )

    # 送出啟動事件
    print(json.dumps({
        "event": "started",
        "endpoint": IOT_ENDPOINT,
        "topic_filter": TOPIC_FILTER,
        "client_id": CLIENT_ID,
        "output_file": OUTPUT_FILE,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }))

    connect_future = mqtt_connection.connect()
    connect_future.result()

    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=TOPIC_FILTER,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message,
    )
    subscribe_future.result()

    while running:
        time.sleep(0.5)

    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print(json.dumps({
        "event": "stopped",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }))


if __name__ == "__main__":
    main()
```

---

## 5. 執行方式

### 5.1 直接執行（測試）

```bash
# 準備憑證檔案（放在執行目錄）
ls cert.pem private.pem.key AmazonRootCA1.pem

# 執行
python listen.py abcd1234xyz-ats.iot.ap-northeast-1.amazonaws.com "device/#"
```

### 5.2 用 tmux 掛背景（臨時用）

```bash
tmux new -s mqtt-listener
python listen-daemon.py abcd1234xyz-ats.iot.ap-northeast-1.amazonaws.com "device/#" /tmp/mqtt.log
# Ctrl+B D 脫離
# tmux attach -t mqtt-listener 回來看
```

### 5.3 用 systemd 設為服務（長期 daemon）

**建立 service 檔** `/etc/systemd/system/mqtt-listener.service`：

```ini
[Unit]
Description=AWS IoT MQTT Listener
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=owen
WorkingDirectory=/home/owen/mqtt-listener
ExecStart=/usr/bin/python3 /home/owen/mqtt-listener/listen-daemon.py \
    abcd1234xyz-ats.iot.ap-northeast-1.amazonaws.com \
    "device/#" \
    /var/log/mqtt-listener.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable mqtt-listener
sudo systemctl start mqtt-listener
sudo systemctl status mqtt-listener
# 看 log: journalctl -u mqtt-listener -f
```

### 5.4 macOS 用 launchd

`~/Library/LaunchAgents/com.mqtt.listener.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mqtt.listener</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/owen/mqtt-listener/listen-daemon.py</string>
        <string>abcd1234xyz-ats.iot.ap-northeast-1.amazonaws.com</string>
        <string>device/#</string>
        <string>/tmp/mqtt-listener.log</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/owen/mqtt-listener</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/mqtt-listener.stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/mqtt-listener.stderr.log</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.mqtt.listener.plist
launchctl start com.mqtt.listener
# 確認: launchctl list | grep mqtt
# 停止: launchctl unload ~/Library/LaunchAgents/com.mqtt.listener.plist
```

---

## 6. 常見問題與除錯

### 6.1 連線失敗

```
❌ 無法連線到 endpoint
```

**排查清單**：

| 檢查項 | 指令/做法 |
|--------|----------|
| endpoint 是否正確 | `aws iot describe-endpoint --endpoint-type iot:Data-ATS` |
| 憑證是否 active | `aws iot describe-certificate --certificate-id $(...)` |
| Policy 是否 attach | `aws iot list-principal-policies --principal "$(cat cert.pem)"` |
| Policy 內容是否正確 | `aws iot get-policy --policy-name mqtt-listener-policy` |
| 網路能連到 endpoint？ | `nc -zv abcd1234xyz-ats.iot.ap-northeast-1.amazonaws.com 8883` |
| Root CA 檔案是否正確 | 檢查 MD5 vs Amazon 官方 |

### 6.2 憑證檔案錯誤

```
[SSL: CERTIFICATE_VERIFY_FAILED]
```

→ 確認三個檔案的內容正確：

```bash
openssl x509 -in cert.pem -text -noout | head -5
openssl rsa -in private.pem.key -check -noout
openssl x509 -in AmazonRootCA1.pem -text -noout | head -5
```

### 6.3 IoT Policy 權限不足

```
Error: AWS IoT error message="Subscribing to topics is not allowed"
```

→ 確認 policy 中有 `iot:Subscribe` + `iot:Receive`，且 resource 包含你要訂閱的 topic filter。

---

## 7. 憑證管理

### 7.1 憑證與現有設備共用

如果你是為了監聽**已在運作的設備**的訊息：

1. 不要用該設備的憑證（萬一斷線影響設備運作）
2. **另外建立一組憑證**，attach 同樣允許 subscribe 的 policy
3. 同一個 topic filter 可以有多個 subscriber，設備不會知道你的存在

### 7.2 憑證過期

AWS IoT Core 憑證有到期日（預設 20 年，或自訂）：

```bash
# 檢查憑證到期日
openssl x509 -in cert.pem -noout -enddate
```

過期前要 renew：
```bash
aws iot update-certificate --certificate-id <id> --new-status ACTIVE
```

或用新憑證取代。

---

## 8. 安全注意事項

| 注意事項 | 說明 |
|---------|------|
| **憑證不可進 Git** | 永遠不要把 `private.pem.key` commit 進 repo。加 `.gitignore` |
| **最小權限原則** | Policy 的 topic resource 寫越窄越好，不要用 wildcard `#` 除非必要 |
| **client ID 唯一性** | 同一個 client ID 同時連線會互踢。正式環境加 pid/hostname 確保唯一 |
| **連線加密** | `mtls_from_path` 預設走 TLS 1.2 + port 8883，安全無虞 |
| **不要存明碼** | 正式部署建議用 Secrets Manager 或環境變數傳遞憑證路徑 |

---

## 9. 專案結構建議

```
mqtt-listener/
├── cert.pem              # TODO: replace with real cert (DO NOT COMMIT)
├── private.pem.key       # TODO: replace with real key (DO NOT COMMIT)
├── AmazonRootCA1.pem     # Amazon Root CA
├── listen.py             # 簡單版（直接印訊息）
├── listen-daemon.py      # Daemon 版（JSON line + 可存檔）
├── requirements.txt      # 相依套件清單
├── .gitignore            # 忽略 *.pem *.key
└── README.md             # 本文件
```

`.gitignore` 內容：
```
*.pem
*.key
*.log
```

---

## 10. 下一步可開發方向

- [ ] **訊息過濾** — 只在 payload 符合條件時才印出/存檔
- [ ] **Webhook 轉發** — 收到訊息就 POST 到某個 HTTP endpoint
- [ ] **多 topic filter** — 同時訂閱多個 patterns
- [ ] **MQTT over WebSocket** — 當環境限制不能開 port 8883 時
- [ ] **QoS 設定** — 目前用 AT_LEAST_ONCE，可依需求調整
- [ ] **Metrics 輸出** — Prometheus / statsd 統計訊息量、延遲
- [ ] **收到後觸發本機指令** — 例如收到特定 topic 就跑某個 script

---

> **Key Principle**  
> MQTT 的 pub-sub 模型是 topic-based broadcast——你寫的 listener 跟 Console test client 是同等地位的 subscriber，差別只在於你的 listener 可以 24 小時運行、自動化處理、不依賴瀏覽器。
