import asyncio
import os

async def receive_messages(reader):
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(f"\nReceived: {message}")
            print("> ", end='', flush=True)
    except ConnectionError:
        print("\nPeer disconnected")

async def send_messages(writer):
    try:
        while True:
            message = await asyncio.get_event_loop().run_in_executor(
                None, lambda: input("> ")
            )
            writer.write(message.encode('utf-8'))
            await writer.drain()
    except ConnectionError:
        print("\nConnection lost")

async def main():
    socket_path = f'{os.getcwd()}/../engine/my_socket.sock'
    reader, writer = await asyncio.open_unix_connection(socket_path)
    
    print("Connected. Type messages and press Enter to send. Ctrl+C to quit.")
    
    try:
        await asyncio.gather(
            receive_messages(reader),
            send_messages(writer)
        )
    finally:
        writer.close()
        await writer.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDisconnecting...")
