# Command Notes

A running log of every command used in this project, with a one-line description.
Maintained continuously as the build progresses.

## Module 0 — Repo and Git

- `git init` : initialize a new Git repository in the current folder
- `git init -b main` : initialize a repo with `main` as the starting branch (ignored if repo already exists)
- `git branch -M main` : rename the current branch to `main` (force)
- `notepad .gitignore` : create/edit the `.gitignore` file listing paths Git should never track (secrets, build junk)
- `git status` : show the working tree state — current branch, staged/unstaged/untracked files
- `git add <files>` : stage the named files into the staging area, ready to commit
- `git commit -m "message"` : record the staged files as a permanent snapshot with a message
- `git log --oneline` : show commit history, one compact line per commit
- `gh --version` : show the installed GitHub CLI version
- `gh auth status` : check whether the GitHub CLI is logged in
- `gh auth login` : log in to GitHub interactively (opens a browser)
- `gh repo create <name> --public --source=. --remote=origin --push` : create a GitHub repo, link it as `origin`, and push
- `git remote -v` : list configured remotes and their URLs
- `git checkout -b <branch>` : create a new branch and switch to it
- `git push -u origin <branch>` : push a new branch and link it to its remote counterpart (only needed the first push)
- `gh pr create --base main --head <branch> --title "..." --body "..."` : open a pull request from a branch into main
- `gh pr merge <number> --merge --delete-branch` : merge a PR normally, then delete the branch locally and on GitHub
- `git pull` : download and merge remote commits into the current branch (sync local main after a merge)
