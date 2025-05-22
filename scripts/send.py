#!/usr/bin/env python3.12
"""
RabbitMQ sender: round-robin, latency, or persistence test.
"""

import argparse
import time

import pika

parser = argparse.ArgumentParser(
    description="RabbitMQ sender: round-robin, latency, or persistence test"
)
parser.add_argument(
    "--count", type=int, default=1,
    help="Number of messages to send"
)
parser.add_argument(
    "--no-sleep", action="store_true",
    help="Don't pause between messages"
)
parser.add_argument(
    "--latency", action="store_true",
    help="Measure single-message round-trip latency and exit"
)
parser.add_argument(
    "--mode", choices=["transient", "persistent"], default="persistent",
    help="Publish messages as transient (delivery_mode=1) "
         "or persistent (delivery_mode=2)"
)
args = parser.parse_args()

RECEIVER_NODES = [
    {"host": "192.168.0.113", "user": "node2", "pass": "node2pass"},
    {"host": "192.168.0.114", "user": "node3", "pass": "node3pass"},
]
current_node = 0


def send_message() -> None:
    """Send one message to the next node in a round-robin fashion."""
    global current_node

    node = RECEIVER_NODES[current_node]
    current_node = (current_node + 1) % len(RECEIVER_NODES)

    creds = pika.PlainCredentials(node["user"], node["pass"])
    params = pika.ConnectionParameters(
        host=node["host"],
        port=5672,
        credentials=creds,
        heartbeat=600,
    )

    try:
        conn = pika.BlockingConnection(params)
        ch = conn.channel()
        ch.queue_declare(queue="test-queue", durable=True)

        dm = 1 if args.mode == "transient" else 2
        msg = f"Test message at {time.strftime('%H:%M:%S')}"

        ch.basic_publish(
            exchange="",
            routing_key="test-queue",
            body=msg,
            properties=pika.BasicProperties(delivery_mode=dm),
        )
        print(f"[x] Sent to {node['host']} ({args.mode}): {msg}", flush=True)
        conn.close()

    except Exception as exc:  # noqa: BLE001
        print(f"[!!] Failed on {node['host']}: {exc}", flush=True)
        time.sleep(1)


if __name__ == "__main__":
    # ----- LATENCY MODE -----
    if args.latency:
        print("Measuring round-trip latency for one message...", flush=True)
        t0 = time.time()
        send_message()
        t1 = time.time()
        print(f"→ Round-trip latency: {(t1 - t0) * 1000:.2f} ms", flush=True)
        exit(0)

    # ----- THROUGHPUT / PERSISTENCE MODE -----
    start = time.time()
    for _ in range(args.count):
        send_message()
        if not args.no_sleep:
            time.sleep(3)
    elapsed = time.time() - start

    print(
        f"\n→ Sent {args.count} messages in {elapsed:.2f} s "
        f"({args.count / elapsed:.1f} msg/s)",
        flush=True,
    )
