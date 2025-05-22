#!/usr/bin/env python3.12

import pika
import time
import sys

def start_consumer():
    credentials = pika.PlainCredentials('node2', 'node2pass')
    parameters = pika.ConnectionParameters(
        host='192.168.0.113',
        port=5672,
        credentials=credentials,
        heartbeat=600,
        connection_attempts=5,
        retry_delay=3
    )

    print(" [*] Attempting to connect to RabbitMQ...")

    try:
        connection = pika.BlockingConnection(parameters)
        print(" [*] Connected to RabbitMQ!")

        channel = connection.channel()
        channel.queue_declare(queue='test-queue', durable=True)
        print(" [*] Queue declared")

        def callback(ch, method, properties, body):
            print(f" [x] Received: {body.decode()}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(
            queue='test-queue',
            on_message_callback=callback,
            auto_ack=False
        )

        print(' [*] Waiting for messages. Press CTRL+C to exit')
        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError as e:
        print(f" [!!] Connection failed: {str(e)}")
        time.sleep(5)
        start_consumer()
    except KeyboardInterrupt:
        print(" [x] Stopping consumer...")
        try:
            connection.close()
        except:
            pass
        sys.exit(0)
    except Exception as e:
        print(f" [!!] Error: {str(e)}")
        time.sleep(5)
        start_consumer()

if __name__ == '__main__':
    start_consumer()
