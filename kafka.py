# kafka.py mock
import json
import os

MSG_FILE = os.path.join(os.path.dirname(__file__), "kafka_messages.json")

def _read_messages():
    if os.path.exists(MSG_FILE):
        try:
            with open(MSG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def _write_messages(msgs):
    try:
        with open(MSG_FILE, "w") as f:
            json.dump(msgs, f)
    except Exception:
        pass

class KafkaProducer:
    def __init__(self, bootstrap_servers=None, value_serializer=None, **kwargs):
        self.value_serializer = value_serializer

    def send(self, topic, value):
        if self.value_serializer:
            if callable(self.value_serializer):
                try:
                    serialized = self.value_serializer(value)
                    if isinstance(serialized, bytes):
                        value = json.loads(serialized.decode())
                except Exception:
                    pass
        msgs = _read_messages()
        msgs.append({"topic": topic, "value": value})
        _write_messages(msgs)
        print(f"[Mock Kafka] Sent message to {topic}: {value}")

    def flush(self):
        pass

class KafkaMessage:
    def __init__(self, topic, value):
        self.topic = topic
        self.value = value

class KafkaConsumer:
    def __init__(self, topic, bootstrap_servers=None, value_deserializer=None, **kwargs):
        self.topic = topic
        self.value_deserializer = value_deserializer
        
        all_msgs = _read_messages()
        self.messages = [m["value"] for m in all_msgs if m["topic"] == topic]
        _write_messages([m for m in all_msgs if m["topic"] != topic])
        self.idx = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.idx < len(self.messages):
            val = self.messages[self.idx]
            self.idx += 1
            
            class MsgObj:
                def __init__(self, val, deserializer):
                    if deserializer:
                        try:
                            serialized = json.dumps(val).encode()
                            self.value = deserializer(serialized)
                        except Exception:
                            self.value = val
                    else:
                        self.value = val
            return MsgObj(val, self.value_deserializer)
        else:
            raise StopIteration
