# prefect/flows/kafka_to_delta.py
import sys, os

# Avoid namespace package conflicts and define workspace_dir
script_dir = os.path.dirname(os.path.abspath(__file__))
workspace_dir = os.path.dirname(os.path.dirname(script_dir))

saved_paths = [p for p in sys.path if 'Day28-Lab-Assignment' in p]
sys.path = [p for p in sys.path if 'Day28-Lab-Assignment' not in p]

# Import real prefect from site-packages
from prefect import flow, task

# Restore paths to import local mocks like kafka and redis
for p in saved_paths:
    if p not in sys.path:
        sys.path.append(p)

from kafka import KafkaConsumer
import json, os
import pandas as pd
from datetime import datetime

@task
def consume_and_process():
    """Consume data from Kafka topic"""
    consumer = KafkaConsumer(
        "data.raw",
        bootstrap_servers="kafka:9092",
        auto_offset_reset="earliest",
        consumer_timeout_ms=5000,
        value_deserializer=lambda m: json.loads(m.decode())
    )
    records = []
    for msg in consumer:
        records.append(msg.value)

    print(f"Consumed {len(records)} records from Kafka")
    return records

@task
def save_to_delta(records):
    """Save records to Delta Lake (parquet format)"""
    if not records:
        print("No records to save")
        return
    
    df = pd.DataFrame(records)
    # Write to local relative workspace path
    local_path = os.path.join(workspace_dir, "delta-lake", "raw")
    os.makedirs(local_path, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    df.to_parquet(os.path.join(local_path, f"batch_{ts}.parquet"))
    
    # Write to container path for compatibility
    docker_path = "/opt/delta-lake/raw"
    try:
        os.makedirs(docker_path, exist_ok=True)
        df.to_parquet(f"{docker_path}/batch_{ts}.parquet")
    except Exception:
        pass
        
    print(f"Saved {len(df)} records to Delta Lake")

@flow(name="Kafka to Delta Pipeline")
def kafka_to_delta_flow():
    """Main flow: consume from Kafka and save to Delta Lake"""
    records = consume_and_process()
    save_to_delta(records)

if __name__ == "__main__":
    # Run the flow locally to generate delta lake data
    print("Running Prefect flow locally...")
    try:
        kafka_to_delta_flow()
    except Exception as e:
        print(f"Local flow execution failed: {e}")

    try:
        # Deploy flow to Prefect Orion
        kafka_to_delta_flow.deploy(
            name="kafka-to-delta",
            work_queue_name="lab28-worker"
        )
    except Exception as e:
        print(f"Prefect deployment bypassed/failed: {e}")
