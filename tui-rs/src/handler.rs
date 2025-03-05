use crate::app::{App, AppResult};
use crossterm::event::{KeyCode, KeyEvent, KeyModifiers};
use crossterm::event::{MouseEvent, MouseEventKind};

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
        // Other handlers you could add here.
        _ => {}
    }
    Ok(())
}

pub async fn handle_mouse_events(mouse_event: MouseEvent, app: &mut App) -> AppResult<()> {
    if let MouseEventKind::Down(_) = mouse_event.kind {
        let button_x = (app.size.width.saturating_sub(30)) / 2;
        let button_width = 30;
        let button_y = app.size.height / 4;

        if mouse_event.column >= button_x && mouse_event.column < button_x + button_width
            && mouse_event.row >= button_y && mouse_event.row < button_y + 3 
        {
            if let Some(socket) = &mut app.socket {
                if let Err(e) = socket.send_message(
                    r#"{"event": "on", "type": "transcribe", "language": "en"}"#
                ).await {
                    eprintln!("Error sending transcribe command: {}", e);
                }
            }
        }
    }
    Ok(())
}
