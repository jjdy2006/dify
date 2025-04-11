from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import threading
import json
import time
import uuid
import logging

app = Flask(__name__)

# MQTT 配置
MQTT_BROKER = "121.41.57.181"
MQTT_PORT = 1883
MQTT_USERNAME = "cx_serve"
MQTT_PASSWORD = "Ibex123!@#"
CLIENT_ID = f"cx_serve_{uuid.uuid4()}"
MQTT_TOPIC_SUBSCRIBE = "cx_serve"

MSG_TYPE_TEST = "test"
MSG_TYPE_RUN_ACTION = "run_action"

RA_CREATE_TXT = {"user_id":"liuqn","msg_type":"run_action","command":"touch /Users/liuqn/local_pip_env/python_project/dify_local_serve/static/aa.txt"}

# 全局变量存储接收到的消息
received_messages = []

# 定义消息处理器基类
class BaseMessageHandler:
    def handle(self, payload):
        raise NotImplementedError("子类必须实现 handle 方法.")

class MsgTypeTestJSQHandler(BaseMessageHandler):
    def handle(self, payload):
        print(f"收到测试消息: {payload}")

class UnknownTypeHandler(BaseMessageHandler):
    def handle(self, payload):
        print(f"未知消息类型: {payload}")

# 消息处理器注册表
message_handlers = {}

# 注册消息处理器
def register_handler(msg_type, handler_class):
    message_handlers[msg_type] = handler_class()

# 初始化注册表
register_handler(MSG_TYPE_TEST, MsgTypeTestJSQHandler)
register_handler("UNKNOWN", UnknownTypeHandler)

# 获取消息处理器
def get_handler(msg_type):
    return message_handlers.get(msg_type, message_handlers["UNKNOWN"])

# 连接回调
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Successfully connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC_SUBSCRIBE)
        print(f"Subscribed to topic: {MQTT_TOPIC_SUBSCRIBE}")
    else:
        print(f"Connection failed with return code {rc}")

# 消息接收回调
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Received valid JSON message: {payload}")
        msg_type = payload.get("msg_type")
        if not msg_type:
            raise ValueError("Missing 'msg_type' field in JSON message")

        handler = get_handler(msg_type)
        handler.handle(payload)
    except json.JSONDecodeError:
        print(f"Invalid JSON message received: {msg.payload.decode()}")
    except ValueError as e:
        print(f"Message processing error: {e}")

# 断开连接回调
def on_disconnect(client, userdata, rc):
    print(f"Disconnected from MQTT Broker with return code {rc}.")
    if rc != 0:
        print("Unexpected disconnection!")

# 初始化 MQTT 客户端
mqtt_client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# 发送 MQTT 消息的接口
@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    topic = data.get("user_id")
    msg_type = data.get("msg_type")

    # 检查 topic 和 msg_type 是否存在
    if not topic or not msg_type:
        return jsonify({"error": "Topic and message type are required"}), 400

    try:
        # 将数据序列化为 JSON 字符串
        payload = json.dumps(data)
        mqtt_client.publish(topic, payload)  # 发布消息
        return jsonify({"status": "Message sent", "message": data}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to send message: {e}"}), 500

# 启动 MQTT 客户端
def start_mqtt_client():
    try:
        print("Connecting to MQTT Broker...")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        mqtt_client.loop_start()
        print("MQTT client is running.")
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Failed to connect to MQTT Broker: {e}")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("MQTT client disconnected.")

if __name__ == '__main__':
    mqtt_thread = threading.Thread(target=start_mqtt_client, daemon=True)
    mqtt_thread.start()

    app.run(host='0.0.0.0', port=5803, debug=True)