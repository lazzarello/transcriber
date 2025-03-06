use ratatui::{
    // layout::{Alignment, Layout, Direction, Constraint},
    layout::Alignment,
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
        .split(frame.area());

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
        Paragraph::new(format!(
            "Transcription Results: {}",
            app.responses.join("\n")))
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

    // Render the "Transcribe" button
    frame.render_widget(
        Paragraph::new("Transcribe")
            .block(
                Block::bordered()
                    .title("Control")
                    .title_alignment(Alignment::Center)
                    .border_type(BorderType::Rounded),
            )
            .style(Style::default().fg(Color::Black).bg(Color::White))  // Inverted colors to look like a button
            .alignment(Alignment::Center),
        ratatui::layout::Rect::new(
            (frame.area().width.saturating_sub(30)) / 2,  // Center horizontally
            chunks[0].y + (chunks[0].height / 2),         // Center vertically in top chunk
            30,                                           // Width of 30 characters
            3,                                            // Height of 3 rows (border + text)
        ),
    );
}
