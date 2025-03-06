use tokio::{
    io::{AsyncBufReadExt, AsyncWriteExt, BufReader},
    net::{UnixListener, UnixStream},
    select,
};
use std::{error::Error, path::PathBuf};

const SOCKET_PATH: &str = "/tmp/chat.sock";

async fn handle_chat(mut stream: UnixStream) -> Result<(), Box<dyn Error>> {
    let (reader, mut writer) = stream.split();
    let mut reader = BufReader::new(reader);
    let mut line = String::new();

    let mut stdin = BufReader::new(tokio::io::stdin());
    let mut input = String::new();

    println!("Chat started! Type messages and press Enter to send.");

    loop {
        select! {
            result = reader.read_line(&mut line) => {
                match result {
                    Ok(0) => {
                        println!("Peer disconnected");
                        break;
                    },
                    Ok(_) => {
                        print!("Received: {}", line);
                        line.clear();
                    }
                    Err(e) => {
                        eprintln!("Read error: {}", e);
                        break;
                    }
                }
            }
            result = stdin.read_line(&mut input) => {
                match result {
                    Ok(0) => break,
                    Ok(_) => {
                        writer.write_all(input.as_bytes()).await?;
                        input.clear();
                    }
                    Err(e) => {
                        eprintln!("Input error: {}", e);
                        break;
                    }
                }
            }
        }
    }
    Ok(())
}

async fn run_listener() -> Result<(), Box<dyn Error>> {
    let socket = PathBuf::from(SOCKET_PATH);
    let listener = UnixListener::bind(&socket)?;
    println!("Listening for connections...");

    loop {
        match listener.accept().await {
            Ok((stream, _)) => {
                println!("Peer connected!");
                if let Err(e) = handle_chat(stream).await {
                    eprintln!("Chat error: {}", e);
                }
                println!("Ready for new connection...");
            }
            Err(e) => {
                eprintln!("Accept error: {}", e);
                break;
            }
        }
    }
    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let socket = PathBuf::from(SOCKET_PATH);
    
    match UnixStream::connect(&socket).await {
        Ok(stream) => {
            println!("Connected to existing chat!");
            handle_chat(stream).await?;
        }
        Err(_) => {
            // If connection fails, become a listener
            run_listener().await?;
        }
    }

    Ok(())
}
