use ratatui::{
    Frame,
    layout::{Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Cell, Paragraph, Row, Table, TableState},
};
use crate::app::{App, View};

const COLOR_HASH:   Color = Color::Yellow;
const COLOR_AUTHOR: Color = Color::Cyan;
const COLOR_TIME:   Color = Color::Green;
const COLOR_MSG:    Color = Color::White;
const COLOR_HEADER: Color = Color::LightBlue;
const COLOR_SELECTED_BG: Color = Color::DarkGray;
const COLOR_BORDER: Color = Color::Gray;
const COLOR_HELP:   Color = Color::DarkGray;
const COLOR_ADD:    Color = Color::Green;
const COLOR_DEL:    Color = Color::Red;

pub fn draw(frame: &mut Frame, app: &App, visible_rows: &mut usize) {
    let area = frame.area();
    let title = build_title(app);
    let outer = Block::default().borders(Borders::ALL)
        .border_style(Style::default().fg(COLOR_BORDER)).title(title);
    let inner = outer.inner(area);
    frame.render_widget(outer, area);
    match app.view {
        View::Log   => draw_log_view(frame, app, inner, visible_rows),
        View::Stats => draw_stats_view(frame, app, inner, visible_rows),
    }
}

fn build_title(app: &App) -> Line<'static> {
    let active = Style::default().fg(Color::White).add_modifier(Modifier::BOLD | Modifier::UNDERLINED);
    let inactive = Style::default().fg(COLOR_HELP);
    Line::from(vec![
        Span::styled(" gitlens-tui ", Style::default().fg(Color::LightYellow).add_modifier(Modifier::BOLD)),
        Span::styled("\u{2014} ", Style::default().fg(COLOR_BORDER)),
        Span::styled(app.repo_name.clone(), Style::default().fg(Color::LightCyan).add_modifier(Modifier::BOLD)),
        Span::styled("  [", Style::default().fg(COLOR_BORDER)),
        Span::styled("Log",   if app.view == View::Log   { active } else { inactive }),
        Span::styled(" | ", Style::default().fg(COLOR_BORDER)),
        Span::styled("Stats", if app.view == View::Stats { active } else { inactive }),
        Span::styled("] ", Style::default().fg(COLOR_BORDER)),
    ])
}

fn help_bar() -> Paragraph<'static> {
    Paragraph::new(Line::from(vec![
        Span::styled(" [j/k\u{2191}\u{2193}] scroll  ", Style::default().fg(COLOR_HELP)),
        Span::styled("[g/G] top/bottom  ",              Style::default().fg(COLOR_HELP)),
        Span::styled("[Tab] switch view  ",             Style::default().fg(COLOR_HELP)),
        Span::styled("[q/Esc] quit ",                   Style::default().fg(COLOR_HELP)),
    ])).block(Block::default().borders(Borders::TOP).border_style(Style::default().fg(COLOR_BORDER)))
}

fn draw_log_view(frame: &mut Frame, app: &App, area: Rect, visible_rows: &mut usize) {
    let chunks = Layout::default().direction(Direction::Vertical)
        .constraints([Constraint::Min(5), Constraint::Length(10), Constraint::Length(2)])
        .split(area);
    *visible_rows = chunks[0].height.saturating_sub(3) as usize;
    draw_commit_table(frame, app, chunks[0]);
    draw_commit_detail(frame, app, chunks[1]);
    frame.render_widget(help_bar(), chunks[2]);
}

fn draw_commit_table(frame: &mut Frame, app: &App, area: Rect) {
    let header = Row::new(
        ["Hash", "Author", "Time", "Message"].iter()
            .map(|h| Cell::from(*h).style(Style::default().fg(COLOR_HEADER).add_modifier(Modifier::BOLD)))
    ).height(1);

    let inner_height = area.height.saturating_sub(3) as usize;
    let rows: Vec<Row> = app.commits.iter().enumerate()
        .skip(app.scroll_offset).take(inner_height)
        .map(|(i, c)| {
            let bg = if i == app.selected { COLOR_SELECTED_BG } else { Color::Reset };
            let base = Style::default().bg(bg);
            Row::new(vec![
                Cell::from(c.short_hash.clone()).style(base.fg(COLOR_HASH)),
                Cell::from(truncate(&c.author_name, 20)).style(base.fg(COLOR_AUTHOR)),
                Cell::from(c.relative_time()).style(base.fg(COLOR_TIME)),
                Cell::from(truncate(c.summary(), 60)).style(base.fg(COLOR_MSG)),
            ]).height(1)
        }).collect();

    let title = if app.commits.is_empty() { " Commits (none) ".to_string() }
                else { format!(" Commits [{}/{}] ", app.selected + 1, app.commits.len()) };

    let table = Table::new(rows, [
        Constraint::Length(8), Constraint::Length(22),
        Constraint::Length(14), Constraint::Min(20),
    ]).header(header).block(
        Block::default().borders(Borders::ALL).border_style(Style::default().fg(COLOR_BORDER))
            .title(Span::styled(title, Style::default().fg(Color::White).add_modifier(Modifier::BOLD)))
    ).row_highlight_style(Style::default());

    frame.render_stateful_widget(table, area, &mut TableState::default());
}

fn draw_commit_detail(frame: &mut Frame, app: &App, area: Rect) {
    let block = Block::default().borders(Borders::ALL).border_style(Style::default().fg(COLOR_BORDER))
        .title(Span::styled(" Commit Detail ", Style::default().fg(Color::White).add_modifier(Modifier::BOLD)));
    let inner = block.inner(area);
    frame.render_widget(block, area);

    if app.commits.is_empty() {
        frame.render_widget(Paragraph::new("No commits found."), inner);
        return;
    }
    let c = match app.selected_commit() { Some(c) => c, None => return };

    let mut lines: Vec<Line> = vec![
        Line::from(vec![Span::styled("Commit:  ", Style::default().fg(COLOR_HEADER).add_modifier(Modifier::BOLD)), Span::styled(c.full_hash.clone(), Style::default().fg(COLOR_HASH))]),
        Line::from(vec![Span::styled("Author:  ", Style::default().fg(COLOR_HEADER).add_modifier(Modifier::BOLD)), Span::styled(format!("{} <{}>", c.author_name, c.author_email), Style::default().fg(COLOR_AUTHOR))]),
        Line::from(vec![Span::styled("Date:    ", Style::default().fg(COLOR_HEADER).add_modifier(Modifier::BOLD)), Span::styled(c.formatted_date(), Style::default().fg(COLOR_TIME))]),
        Line::from(vec![Span::styled("Message: ", Style::default().fg(COLOR_HEADER).add_modifier(Modifier::BOLD)), Span::styled(c.summary().to_string(), Style::default().fg(COLOR_MSG))]),
        Line::from(Span::styled("Files changed:", Style::default().fg(COLOR_HEADER).add_modifier(Modifier::BOLD))),
    ];

    if c.files.is_empty() {
        lines.push(Line::from(Span::styled("  (no file changes recorded)", Style::default().fg(COLOR_HELP))));
    } else {
        let avail = inner.height.saturating_sub(lines.len() as u16) as usize;
        for f in c.files.iter().take(avail.max(1)) {
            lines.push(Line::from(vec![
                Span::raw("  "),
                Span::styled(truncate(&f.path, 50).to_string(), Style::default().fg(COLOR_MSG)),
                Span::raw(" ("),
                Span::styled(format!("+{}", f.additions), Style::default().fg(COLOR_ADD)),
                Span::raw(" "),
                Span::styled(format!("-{}", f.deletions), Style::default().fg(COLOR_DEL)),
                Span::raw(")"),
            ]));
        }
    }
    frame.render_widget(Paragraph::new(lines), inner);
}

fn draw_stats_view(frame: &mut Frame, app: &App, area: Rect, visible_rows: &mut usize) {
    let chunks = Layout::default().direction(Direction::Vertical)
        .constraints([Constraint::Min(3), Constraint::Length(2)]).split(area);
    *visible_rows = chunks[0].height.saturating_sub(3) as usize;
    draw_stats_table(frame, app, chunks[0]);
    frame.render_widget(help_bar(), chunks[1]);
}

fn draw_stats_table(frame: &mut Frame, app: &App, area: Rect) {
    let header = Row::new(
        ["Author", "Commits", "+Lines", "-Lines", "Last Commit"].iter()
            .map(|h| Cell::from(*h).style(Style::default().fg(COLOR_HEADER).add_modifier(Modifier::BOLD)))
    ).height(1);

    let inner_height = area.height.saturating_sub(3) as usize;
    let rows: Vec<Row> = app.authors.iter().enumerate()
        .skip(app.scroll_offset).take(inner_height)
        .map(|(i, a)| {
            let bg = if i == app.selected { COLOR_SELECTED_BG } else { Color::Reset };
            let base = Style::default().bg(bg);
            Row::new(vec![
                Cell::from(truncate(&a.name, 30).to_string()).style(base.fg(COLOR_AUTHOR)),
                Cell::from(a.commit_count.to_string()).style(base.fg(Color::White)),
                Cell::from(format!("+{}", a.additions)).style(base.fg(COLOR_ADD)),
                Cell::from(format!("-{}", a.deletions)).style(base.fg(COLOR_DEL)),
                Cell::from(a.last_commit_date()).style(base.fg(COLOR_TIME)),
            ]).height(1)
        }).collect();

    let table = Table::new(rows, [
        Constraint::Min(24), Constraint::Length(9),
        Constraint::Length(9), Constraint::Length(9), Constraint::Length(12),
    ]).header(header).block(
        Block::default().borders(Borders::ALL).border_style(Style::default().fg(COLOR_BORDER))
            .title(Span::styled(
                format!(" Author Statistics [{} author(s)] ", app.authors.len()),
                Style::default().fg(Color::White).add_modifier(Modifier::BOLD)
            ))
    );
    frame.render_stateful_widget(table, area, &mut TableState::default());
}

fn truncate(s: &str, max: usize) -> String {
    if s.chars().count() <= max { s.to_string() }
    else { let mut out: String = s.chars().take(max.saturating_sub(1)).collect(); out.push('\u{2026}'); out }
}
