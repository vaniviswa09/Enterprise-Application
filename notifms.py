# notifms.py (Notification Service)

import aio_pika
import asyncio

async def send_notification(message: str):
    # Here you would implement the actual logic for sending emails or SMS
    print(f"Sending notification: {message}")

async def listen_for_registration():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")  # Connect to RabbitMQ
    async with connection:
        channel = await connection.channel()  # Create a channel
        queue = await channel.declare_queue("user.registration")  # Declare the queue

        async for message in queue:  # Consume messages from the queue
            async with message.process():
                user_data = message.body.decode()  # Decode the message body
                await send_notification(f"New registration: {user_data}")  # Send a mock notification

# Start listening for messages
if __name__ == "__main__":
    asyncio.run(listen_for_registration())

