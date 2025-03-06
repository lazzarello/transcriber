use std::error;
use crate::socket::SocketConnection;

/// Application result type.
pub type AppResult<T> = std::result::Result<T, Box<dyn error::Error>>;

/// Application.
#[derive(Debug)]
pub struct App {
    /// Is the application running?
    pub running: bool,
    /// counter
    pub counter: u8,
    pub responses: Vec<String>,
    pub size: ratatui::layout::Rect,
    pub socket: Option<SocketConnection>,  // Changed to Option<SocketConnection>
}

impl Default for App {
    fn default() -> Self {
        Self {
            running: true,
            counter: 0,
            // responses: Vec::new(),
            responses: vec![
                String::from("Hello"),
                String::from("World")
            ],
            size: ratatui::layout::Rect::default(),
            socket: None,  // Initialize as None
        }
    }
}

impl App {
    /// Constructs a new instance of [`App`].
    pub fn new() -> Self {
        let mut app = Self::default();
        app.receive_response(String::from("Welcome to the application!"));
        app
    }

    /// Handles the tick event of the terminal.
    pub fn tick(&self) {}

    /// Set running to false to quit the application.
    pub fn quit(&mut self) {
        self.running = false;
    }

    pub fn increment_counter(&mut self) {
        if let Some(res) = self.counter.checked_add(1) {
            self.counter = res;
        }
    }

    pub fn decrement_counter(&mut self) {
        if let Some(res) = self.counter.checked_sub(1) {
            self.counter = res;
        }
    }

    pub fn receive_response(&mut self, response: String) {
        self.responses.push(response);
    }

    pub fn send_transcribe_command(&mut self, socket: &mut SocketConnection) -> Result<(), Box<dyn error::Error>> {
        let message = r#"{"event": "on", "type": "transcribe", "language": "en"}"#;
        socket.send_message(message);
        Ok(())
    }
}
