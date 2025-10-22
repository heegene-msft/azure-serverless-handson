"""Event Hub에서 메시지 읽기"""
from azure.eventhub import EventHubConsumerClient
from azure.identity import DefaultAzureCredential
import os
from dotenv import load_dotenv

load_dotenv()

eventhub_namespace = os.getenv("EVENTHUB_NAMESPACE")
eventhub_name = os.getenv("EVENTHUB_NAME")

print(f"Reading messages from Event Hub: {eventhub_name}")
print(f"Namespace: {eventhub_namespace}")
print("-" * 60)

credential = DefaultAzureCredential()

# Consumer 생성
consumer = EventHubConsumerClient(
    fully_qualified_namespace=eventhub_namespace,
    eventhub_name=eventhub_name,
    consumer_group='$Default',
    credential=credential
)

message_count = 0
max_messages = 10

def on_event(partition_context, event):
    global message_count
    if event:
        message_count += 1
        print(f"\n📨 Message {message_count}:")
        print(f"   Partition: {partition_context.partition_id}")
        print(f"   Sequence Number: {event.sequence_number}")
        print(f"   Offset: {event.offset}")
        print(f"   Enqueued Time: {event.enqueued_time}")
        print(f"   Body: {event.body_as_str()}")
        
        if message_count >= max_messages:
            print(f"\n✅ Read {message_count} messages. Stopping...")
            raise KeyboardInterrupt

def on_error(partition_context, error):
    print(f"❌ Error: {error}")

try:
    print("Starting to receive messages (press Ctrl+C to stop)...\n")
    with consumer:
        consumer.receive(
            on_event=on_event,
            on_error=on_error,
            starting_position="-1"  # 가장 오래된 메시지부터 읽기
        )
except KeyboardInterrupt:
    print(f"\n\n✅ Total messages read: {message_count}")
except Exception as e:
    print(f"\n❌ Error: {e}")
