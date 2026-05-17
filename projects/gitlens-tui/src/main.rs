mod app;
mod git;
mod ui;

use app::App;
use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode, KeyEventKind},
    execute,
    terminal::{EnterAlternateScreen, LeaveAlternateScreen, disable_raw_mode, enable_raw_mode},
};
use git::{compute_author_stats, load_commits, open_repo, repo_name};
use ratatui::{Terminal, backend::CrosstermBackend};
use std::{
    env,
    io::{self, Stdout},
    path::PathBuf,
    time::Duration,
};

struct TerminalGuard {
    terminal: Terminal<CrosstermBackend<Stdout>>,
}

impl TerminalGuard {
    fn new() -> io::Result<Self> {
        enable_raw_mode()?;
        let mut stdout = io::stdout();
        execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
        let backend = CrosstermBackend::new(io::stdout());
        let terminal = Terminal::new(backend)?;
        Ok(TerminalGuard { terminal })
    }
}

impl Drop for TerminalGuard {
    fn drop(&mut self) {
        let _ = disable_raw_mode();
        let _ = execute!(
            self.terminal.backend_mut(),
            LeaveAlternateScreen,
            DisableMouseCapture
        );
        let _ = self.terminal.show_cursor();
    }
}

fn parse_args() -> PathBuf {
    let args: Vec<String> = env::args().collect();
    let mut i = 1;
    while i < args.len() {
        if args[i] == "--path" || args[i] == "-p" {
            if i + 1 < args.len() {
                return PathBuf::from(&args[i + 1]);
            } else {
                eprintln!("Error: --path requires an argument");
                std::process::exit(1);
            }
        } else if args[i] == "--help" || args[i] == "-h" {
            print_help();
            std::process::exit(0);
        }
        i += 1;
    }
    PathBuf::from(".")
}

fn print_help() {
    println!(
        "gitlens-tui {}\n\
         Explore your git history without leaving the terminal.\n\n\
         USAGE:\n\
         \x20   gitlens-tui [OPTIONS]\n\n\
         OPTIONS:\n\
         \x20   -p, --path <DIR>   Path to a git repository (default: current directory)\n\
         \x20   -h, --help         Print this help message\n\n\
         KEY BINDINGS:\n\
         \x20   j / ↓    Scroll down\n\
         \x20   k / ↑    Scroll up\n\
         \x20   g        Go to top\n\
         \x20   G        Go to bottom\n\
         \x20   Tab      Switch between Log and Stats views\n\
         \x20   q / Esc  Quit",
        env!("CARGO_PKG_VERSION")
    );
}

fn main() {
    let repo_path = parse_args();

    let repo = match open_repo(&repo_path) {
        Ok(r) => r,
        Err(e) => {
            eprintln!("Error: could not open git repository at '{}': {}", repo_path.display(), e);
            std::process::exit(1);
        }
    };

    let name = repo_name(&repo);
    let commits = match load_commits(&repo, 500) {
        Ok(c) => c,
        Err(e) => { eprintln!("Error reading commits: {}", e); std::process::exit(1); }
    };

    let authors = compute_author_stats(&commits);
    let mut app = App::new(name, commits, authors);

    let mut guard = match TerminalGuard::new() {
        Ok(g) => g,
        Err(e) => { eprintln!("Failed to initialise terminal: {}", e); std::process::exit(1); }
    };

    let mut visible_rows: usize = 20;

    loop {
        guard.terminal.draw(|frame| ui::draw(frame, &app, &mut visible_rows)).expect("failed to draw frame");

        if event::poll(Duration::from_millis(100)).unwrap_or(false) {
            match event::read() {
                Ok(Event::Key(key)) if key.kind == KeyEventKind::Press => {
                    handle_key(&mut app, key.code, visible_rows);
                }
                Ok(Event::Resize(_, _)) => {}
                _ => {}
            }
        }

        if app.should_quit { break; }
    }
}

fn handle_key(app: &mut App, code: KeyCode, visible_rows: usize) {
    match code {
        KeyCode::Char('q') | KeyCode::Esc         => { app.should_quit = true; }
        KeyCode::Char('j') | KeyCode::Down        => { app.scroll_down(visible_rows); }
        KeyCode::Char('k') | KeyCode::Up          => { app.scroll_up(); }
        KeyCode::Char('g')                        => { app.go_to_top(); }
        KeyCode::Char('G')                        => { app.go_to_bottom(visible_rows); }
        KeyCode::Tab                              => { app.switch_view(); }
        _ => {}
    }
}
