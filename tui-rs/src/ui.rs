use ratatui::{
    layout::{Alignment, Layout, Direction, Constraint},
    style::{Color, Style},
    widgets::{Block, BorderType, Paragraph},
    Frame,
};

use crate::app::App;

/// Renders the user interface widgets.
pub fn render(app: &mut App, frame: &mut Frame) {
    // Create a vertical layout
    let chunks = ratatui::layout::Layout::default()
        .direction(ratatui::layout::Direction::Vertical)
        .constraints([
            ratatui::layout::Constraint::Percentage(50),
            ratatui::layout::Constraint::Percentage(50),
        ])
        .split(frame.size());

    // Render the first widget in the top half
    frame.render_widget(
        Paragraph::new(format!(
            "This is a transcriber box build with the simple-async ratatui template.\n\
                Press `Esc`, `Ctrl-C` or `q` to stop running.\n\
                Press left and right to increment and decrement the counter respectively.\n\
                Counter: {}",
            app.counter
        ))
        .block(
            Block::bordered()
                .title("Transcriber")
                .title_alignment(Alignment::Center)
                .border_type(BorderType::Rounded),
        )
        .style(Style::default().fg(Color::Cyan).bg(Color::Black))
        .centered(),
        chunks[0],
    );

    // Render the second widget in the bottom half
    frame.render_widget(
        Paragraph::new("Transcription Results")
            .block(
                Block::bordered()
                    .title("Output")
                    .title_alignment(Alignment::Center)
                    .border_type(BorderType::Rounded),
            )
            .style(Style::default().fg(Color::White).bg(Color::Black))
            .centered(),
        chunks[1],
    );
}
