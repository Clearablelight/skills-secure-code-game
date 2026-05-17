use chrono::{Local, TimeZone, Utc};
use git2::{DiffOptions, Repository};
use std::cell::RefCell;
use std::collections::HashMap;
use std::path::Path;

#[derive(Debug, Clone)]
pub struct FileDiff {
    pub path: String,
    pub additions: usize,
    pub deletions: usize,
}

#[derive(Debug, Clone)]
pub struct CommitInfo {
    pub short_hash: String,
    pub full_hash: String,
    pub author_name: String,
    pub author_email: String,
    pub timestamp: i64,
    pub message: String,
    pub files: Vec<FileDiff>,
}

impl CommitInfo {
    pub fn relative_time(&self) -> String {
        let now = Utc::now().timestamp();
        let delta = now - self.timestamp;
        if delta < 60 { "just now".to_string() }
        else if delta < 3600 { let m = delta/60; format!("{} min{} ago", m, if m==1 {""} else {"s"}) }
        else if delta < 86400 { let h = delta/3600; format!("{} hour{} ago", h, if h==1 {""} else {"s"}) }
        else if delta < 86400*30 { let d = delta/86400; format!("{} day{} ago", d, if d==1 {""} else {"s"}) }
        else if delta < 86400*365 { let mo = delta/(86400*30); format!("{} month{} ago", mo, if mo==1 {""} else {"s"}) }
        else { let y = delta/(86400*365); format!("{} year{} ago", y, if y==1 {""} else {"s"}) }
    }

    pub fn formatted_date(&self) -> String {
        match Local.timestamp_opt(self.timestamp, 0) {
            chrono::LocalResult::Single(dt) => dt.format("%Y-%m-%d %H:%M:%S").to_string(),
            _ => "unknown".to_string(),
        }
    }

    pub fn summary(&self) -> &str {
        self.message.lines().next().unwrap_or("")
    }
}

#[derive(Debug, Clone)]
pub struct AuthorStats {
    pub name: String,
    #[allow(dead_code)]
    pub email: String,
    pub commit_count: usize,
    pub additions: usize,
    pub deletions: usize,
    pub last_commit: i64,
}

impl AuthorStats {
    pub fn last_commit_date(&self) -> String {
        match Local.timestamp_opt(self.last_commit, 0) {
            chrono::LocalResult::Single(dt) => dt.format("%Y-%m-%d").to_string(),
            _ => "unknown".to_string(),
        }
    }
}

pub fn open_repo(path: &Path) -> Result<Repository, git2::Error> {
    Repository::discover(path)
}

pub fn repo_name(repo: &Repository) -> String {
    let base = repo.workdir().unwrap_or_else(|| repo.path())
        .canonicalize()
        .unwrap_or_else(|_| repo.workdir().unwrap_or_else(|| repo.path()).to_path_buf());
    base.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_else(|| "unknown".to_string())
}

pub fn load_commits(repo: &Repository, limit: usize) -> Result<Vec<CommitInfo>, git2::Error> {
    let mut revwalk = repo.revwalk()?;
    match revwalk.push_head() {
        Ok(_) => {}
        Err(e) if e.code() == git2::ErrorCode::UnbornBranch => return Ok(Vec::new()),
        Err(e) => return Err(e),
    }
    revwalk.set_sorting(git2::Sort::TIME)?;

    let mut commits = Vec::new();
    for oid_result in revwalk.take(limit) {
        let oid = oid_result?;
        let commit = repo.find_commit(oid)?;
        let author = commit.author();
        commits.push(CommitInfo {
            short_hash: format!("{:.7}", oid),
            full_hash: oid.to_string(),
            author_name: author.name().unwrap_or("Unknown").to_string(),
            author_email: author.email().unwrap_or("").to_string(),
            timestamp: commit.time().seconds(),
            message: commit.message().unwrap_or("").trim_end().to_string(),
            files: collect_file_diffs(repo, &commit)?,
        });
    }
    Ok(commits)
}

fn collect_file_diffs(repo: &Repository, commit: &git2::Commit) -> Result<Vec<FileDiff>, git2::Error> {
    let commit_tree = commit.tree()?;
    let parent_tree = if commit.parent_count() > 0 { Some(commit.parent(0)?.tree()?) } else { None };
    let mut diff_opts = DiffOptions::new();
    let diff = repo.diff_tree_to_tree(parent_tree.as_ref(), Some(&commit_tree), Some(&mut diff_opts))?;

    let files: RefCell<Vec<FileDiff>> = RefCell::new(Vec::new());
    diff.foreach(
        &mut |delta, _| {
            let path = delta.new_file().path().or_else(|| delta.old_file().path())
                .map(|p| p.to_string_lossy().into_owned()).unwrap_or_else(|| "<unknown>".to_string());
            files.borrow_mut().push(FileDiff { path, additions: 0, deletions: 0 });
            true
        },
        None, None,
        Some(&mut |_delta, _hunk, line| {
            let mut f = files.borrow_mut();
            if let Some(last) = f.last_mut() {
                match line.origin() { '+' => last.additions += 1, '-' => last.deletions += 1, _ => {} }
            }
            true
        }),
    )?;
    Ok(files.into_inner())
}

pub fn compute_author_stats(commits: &[CommitInfo]) -> Vec<AuthorStats> {
    let mut map: HashMap<String, AuthorStats> = HashMap::new();
    for c in commits {
        let entry = map.entry(c.author_email.clone()).or_insert_with(|| AuthorStats {
            name: c.author_name.clone(), email: c.author_email.clone(),
            commit_count: 0, additions: 0, deletions: 0, last_commit: 0,
        });
        entry.commit_count += 1;
        if c.timestamp > entry.last_commit {
            entry.last_commit = c.timestamp;
            entry.name = c.author_name.clone();
        }
        for f in &c.files { entry.additions += f.additions; entry.deletions += f.deletions; }
    }
    let mut stats: Vec<AuthorStats> = map.into_values().collect();
    stats.sort_by(|a, b| b.commit_count.cmp(&a.commit_count).then_with(|| a.name.cmp(&b.name)));
    stats
}
