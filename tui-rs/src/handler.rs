use crate::app::{App, AppResult};
use crossterm::event::{KeyCode, KeyEvent, KeyModifiers};
use crossterm::event::{MouseEvent, MouseEventKind};

// Add this at the top level of the file
static mut TOGGLE_COUNTER: i8 = 0;

/// Handles the key events and updates the state of [`App`].
pub fn handle_key_events(key_event: KeyEvent, app: &mut App) -> AppResult<()> {
    match key_event.code {
        // Exit application on `ESC` or `q`
        KeyCode::Esc | KeyCode::Char('q') => {
            app.quit();
        }
        // Exit application on `Ctrl-C`
        KeyCode::Char('c') | KeyCode::Char('C') => {
            if key_event.modifiers == KeyModifiers::CONTROL {
                app.quit();
            }
        }
        // Counter handlers
        KeyCode::Right => {
            app.increment_counter();
        }
        KeyCode::Left => {
            app.decrement_counter();
        }
        KeyCode::Char(' ') => {
            unsafe { 
                TOGGLE_COUNTER += 1;
                if let Some(ref mut socket) = &mut app.socket {
                    if TOGGLE_COUNTER % 2 == 1 {
                        // eprintln!("Recording Started");
                        socket.send_message(r#"{"event": "on", "type": "transcribe", "language": "en"}"#);
                    } else {
                        // eprintln!("Recording Stopped");
                        socket.send_message(r#"{"event": "off", "type": "transcribe"}"#);
                    }
                } else {
                    eprintln!("Socket connection not available");
                }
            }
        }
        // Other handlers you could add here.
        // Keep this at the bottom as the default match arm
        _ => {}
    }
    Ok(())
}

pub async fn handle_mouse_events(mouse_event: MouseEvent, app: &mut App) -> AppResult<()> {
    if let MouseEventKind::Down(_) = mouse_event.kind {
        let button_x = (app.size.width.saturating_sub(30)) / 2;
        let button_width = 30;
        let button_y = app.size.height / 4;

        eprintln!("Mouse click at ({}, {})", mouse_event.column, mouse_event.row);
        eprintln!("Button area: x={}-{}, y={}-{}", 
            button_x, button_x + button_width, 
            button_y, button_y + 3);

        // this logic is never matched                                        
        // if mouse_event.column >= button_x && mouse_event.column < button_x + button_width
        //    && mouse_event.row >= button_y && mouse_event.row < button_y + 3 
        if mouse_event.column >= button_x && mouse_event.row >= button_y 
        {
            eprintln!("Click detected in button area!");
        }
    }
    Ok(())
}

