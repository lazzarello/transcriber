use tokio::net::UnixStream;
use tokio::net::unix::{OwnedReadHalf, OwnedWriteHalf};
use tokio::io::{BufReader, AsyncBufReadExt, AsyncWriteExt};
use std::path::PathBuf;
use std::error::Error;

pub struct SocketConnection {
    reader: BufReader<OwnedReadHalf>,
    writer: OwnedWriteHalf,
}

impl SocketConnection {
    pub async fn connect(socket_path: PathBuf) -> Result<Self, Box<dyn Error>> {
        let stream = UnixStream::connect(socket_path).await?;
        let (read_half, write_half) = stream.into_split();
        let reader = BufReader::new(read_half);
        Ok(Self { 
            reader, 
            writer: write_half 
        })
    }

    pub async fn send_message(&mut self, message: &str) -> Result<(), Box<dyn Error>> {
        self.writer.write_all(message.as_bytes()).await?;
        self.writer.flush().await?;
        Ok(())
    }

    pub async fn receive_message(&mut self) -> Result<String, Box<dyn Error>> {
        let mut buffer = String::new();
        self.reader.read_line(&mut buffer).await?;
        Ok(buffer)
    }
}
