use tokio::{
    io::{AsyncBufReadExt, AsyncWriteExt, BufReader},
    net::{UnixListener, UnixStream},
    select,
};
use std::{error::Error, path::PathBuf};

const SOCKET_PATH: &str = "/tmp/chat.sock";

async fn handle_connection(mut stream: UnixStream) -> Result<(), Box<dyn Error>> {
    let (reader, mut writer) = stream.split();
    let mut reader = BufReader::new(reader);
    let mut line = String::new();

    let mut stdin = BufReader::new(tokio::io::stdin());
    let mut input = String::new();
    loop {
        select! {
            result = reader.read_line(&mut line) => {
                match result {
                    Ok(0) => break,
                    Ok(_) => {
                        println!("Received: {}", line);
                        line.clear();
                    }
                    Err(e) => return Err(e.into()),
                }
            }
            result = stdin.read_line(&mut input) => {
                match result {
                    Ok(0) => break,
                    Ok(_) => {
                        writer.write_all(input.as_bytes()).await?;
                        input.clear();
                    }
                    Err(e) => return Err(e.into()),
                }
            }
        }
    }
    Ok(())
}

async fn start_server() -> Result<(), Box<dyn Error>> {
    let socket = PathBuf::from(SOCKET_PATH);
    if socket.exists() {
        std::fs::remove_file(&socket)?;
    }
    let listener = UnixListener::bind(socket)?;
    loop {
        let (stream, _) = listener.accept().await?;
        println!("New connection established!");
        tokio::spawn(async move {
            if let Err(e) = handle_connection(stream).await {
                eprintln!("Connection error: {}", e);
            }
        });
    }
}

async fn connect_as_client() -> Result<(), Box<dyn Error>> {
    let stream = UnixStream::connect(SOCKET_PATH).await?;
    println!("Connected to chat server!");
    handle_connection(stream).await
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let socket = PathBuf::from(SOCKET_PATH);
    if socket.exists() {
        connect_as_client().await
    } else {
        start_server().await
    }
}