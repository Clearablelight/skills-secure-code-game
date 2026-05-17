use crate::git::{AuthorStats, CommitInfo};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum View { Log, Stats }

impl View {
    pub fn toggle(self) -> Self {
        match self { View::Log => View::Stats, View::Stats => View::Log }
    }
}

pub struct App {
    pub view: View,
    pub commits: Vec<CommitInfo>,
    pub authors: Vec<AuthorStats>,
    pub selected: usize,
    pub scroll_offset: usize,
    pub repo_name: String,
    pub should_quit: bool,
}

impl App {
    pub fn new(repo_name: String, commits: Vec<CommitInfo>, authors: Vec<AuthorStats>) -> Self {
        App { view: View::Log, commits, authors, selected: 0, scroll_offset: 0, repo_name, should_quit: false }
    }

    fn list_len(&self) -> usize {
        match self.view { View::Log => self.commits.len(), View::Stats => self.authors.len() }
    }

    pub fn scroll_down(&mut self, visible_rows: usize) {
        let len = self.list_len();
        if len == 0 { return; }
        if self.selected + 1 < len {
            self.selected += 1;
            if self.selected >= self.scroll_offset + visible_rows {
                self.scroll_offset += 1;
            }
        }
    }

    pub fn scroll_up(&mut self) {
        if self.selected > 0 {
            self.selected -= 1;
            if self.selected < self.scroll_offset {
                self.scroll_offset = self.selected;
            }
        }
    }

    pub fn go_to_top(&mut self) { self.selected = 0; self.scroll_offset = 0; }

    pub fn go_to_bottom(&mut self, visible_rows: usize) {
        let len = self.list_len();
        if len == 0 { return; }
        self.selected = len - 1;
        self.scroll_offset = if len > visible_rows { len - visible_rows } else { 0 };
    }

    pub fn switch_view(&mut self) {
        self.view = self.view.toggle();
        self.selected = 0;
        self.scroll_offset = 0;
    }

    pub fn selected_commit(&self) -> Option<&CommitInfo> {
        self.commits.get(self.selected)
    }
}
