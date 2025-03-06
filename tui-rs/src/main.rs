use std::io;
use std::path::PathBuf;
use crate::socket::SocketConnection;
use ratatui::{backend::CrosstermBackend, Terminal};

use crate::{
    app::{App, AppResult},
    event::{Event, EventHandler},
    handler::{handle_key_events, handle_mouse_events},
    tui::Tui,
};

// These module names are directly related to file names in the source directory
pub mod app;
pub mod event;
pub mod handler;
pub mod tui;
pub mod ui;
pub mod socket;

#[tokio::main]
async fn main() -> AppResult<()> {
    let socket_path = PathBuf::from("../engine/my_socket.sock");
    let socket = SocketConnection::connect(socket_path).await?;

    // Create an application.
    let mut app = App::new();
    app.socket = Some(socket);

    // Initialize the terminal user interface.
    let backend = CrosstermBackend::new(io::stdout());
    let terminal = Terminal::new(backend)?;
    let events = EventHandler::new(250);
    let mut tui = Tui::new(terminal, events);
    tui.init()?;

    // Start the main loop.
    while app.running {
        // Render the user interface.
        // Generated through Augment and wrong
        // app.size = tui.terminal.size()?;
        tui.draw(&mut app)?;
        // Handle events.
        tokio::select! {
            Ok(event) = tui.events.next() => {
                match event {
                    Event::Tick => app.tick(),
                    Event::Key(key_event) => handle_key_events(key_event, &mut app)?,
                    Event::Mouse(mouse_event) => handle_mouse_events(mouse_event, &mut app).await?,
                    Event::Resize(_, _) => {}
                }
            }
        }
    }

    // Exit the user interface.
    tui.exit()?;
    Ok(())
}
