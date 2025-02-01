import asyncio
import os

async def receive_messages(reader):
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(message)
    except ConnectionError:
        print("Peer disconnected")

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

async def handle_connection(reader, writer):
    receive_task = asyncio.create_task(receive_messages(reader))
    send_task = asyncio.create_task(send_messages(writer))
    await asyncio.gather(receive_task, send_task)

async def main():
    socket_path = f'{os.getcwd()}/my_socket.sock'
    if os.path.exists(socket_path):
        os.remove(socket_path)

    server = await asyncio.start_unix_server(
        handle_connection, socket_path
    )
    print("Server started, waiting for connection...")
    
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
