import torch
import json
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import asyncio
import os
import subprocess

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
model_id = "openai/whisper-large-v3"
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True)
model.to(device)

async def start_recording():
    cmd = ["arecord", "--device=pipewire", "test.wav"]
    handle = subprocess.Popen(cmd)  # Use Popen instead of run
    return handle

async def stop_recording(handle):
    if handle:
        handle.terminate()
        handle.wait()  # Wait for the process to actually terminate
    return handle

async def receive_messages(reader, writer):  # Add writer parameter
    recording_handle = None
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(message)
            
            # Convert string representation of dict to actual dict
            if message.startswith('{') and message.endswith('}'):
                try:
                    msg_dict = json.loads(message)  # More reliable than eval()
                    # debug why this logic always uses the default language
                    lang = "en"
                    if msg_dict.get('type') == 'transcribe':
                        if msg_dict.get('event') == 'on' and not recording_handle:
                            lang = msg_dict.get('language')
                            recording_handle = await start_recording()
                            print("Recording started")
                        elif msg_dict.get('event') == 'off' and recording_handle:
                            await stop_recording(recording_handle)
                            recording_handle = None
                            print("Recording stopped")
                            # run automatic_speech_recognition on test.wav and send result
                            result = await automatic_speech_recognition(audio_file="test.wav",
                                                                        language=lang)
                            response = {"type": "transcription", "text": result}
                            writer.write(str(response).encode('utf-8'))
                            await writer.drain()
                except Exception as e:
                    print(f"Error processing message: {e}")
                    error_msg = {"type": "error", "message": str(e)}
                    writer.write(str(error_msg).encode('utf-8'))
                    await writer.drain()
                    
    except ConnectionError:
        print("Peer disconnected")
    finally:
        # Ensure recording is stopped if connection is lost
        if recording_handle:
            await stop_recording(recording_handle)

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

# refactor to use real parameters or kwargs not globals
async def automatic_speech_recognition(audio_file, language):
    processor = AutoProcessor.from_pretrained(model_id)
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        chunk_length_s=30,
        device=device,
        return_timestamps=True,
    )
    print("Output language: ", language)
    result = pipe(audio_file, generate_kwargs={"language": language })
    return result["text"]

async def handle_connection(reader, writer):
    receive_task = asyncio.create_task(receive_messages(reader, writer))
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
