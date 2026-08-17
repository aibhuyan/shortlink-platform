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

## Module 1 — Postgres, locally

- `psql --version` : print the installed Postgres client version (checks whether it's installed)
- `winget search PostgreSQL` : list PostgreSQL-related packages available via winget
- `winget install -e --id PostgreSQL.PostgreSQL.17` : install PostgreSQL 17 (server + psql + tools) via the official installer
- `Get-Service -Name postgresql*` : check whether the Postgres Windows service (server) is running
- `Get-ItemProperty "HKLM:\...\Uninstall\*" | Where DisplayName -like "*PostgreSQL*"` : identify the installer/publisher used
- `Get-Content "C:\Program Files\PostgreSQL\17\data\pg_hba.conf"` : view the host-based authentication rules (how connections are authed)
- `chcp 65001` : set the terminal code page to UTF-8 to fix garbled psql output on Windows
- `psql -U postgres` : connect to the Postgres server as the `postgres` superuser (prompts for password)
- `psql -U postgres -c "SELECT version();"` : run a single SQL statement non-interactively and exit
- `\l` : (psql meta-command) list all databases on the server
- `\c <db>` : (psql) switch the connection to another database
- `\dt` : (psql) list tables in the current database
- `\d <table>` : (psql) describe a table's columns and types
- `\x on` / `\x off` : (psql) toggle expanded display — vertical records, readable on narrow terminals
- `\q` : (psql) quit psql
- `CREATE DATABASE shortlink;` : create the project's dedicated database
- `CREATE TABLE scratch (id integer, name text);` : create a throwaway table to demo columns/types
- `INSERT INTO scratch (id, name) VALUES (1, 'Alice');` : add a row (string literals use single quotes)
- `SELECT * FROM scratch;` : read back all rows from a table
- `DROP TABLE scratch;` : delete a table and its data

## Module 2 — Backend: FastAPI skeleton

- `uv --version` : print the installed uv version (Python env/dependency manager)
- `uv init backend` : scaffold a new Python project in `backend/` (pyproject.toml, main.py, .python-version)
- `uv add fastapi "uvicorn[standard]"` : add FastAPI + uvicorn as deps, creating the `.venv` and recording them in pyproject.toml
- `git check-ignore -v .venv` : ask Git whether a path is ignored and by which rule (verify `.venv` won't be committed)
- `uv run python -c "import main; print('ok')"` : run a command inside the venv (used to syntax-check main.py)
- `uv run uvicorn main:app --reload` : start the ASGI server, loading `app` from main.py, auto-reloading on file changes
- `curl http://127.0.0.1:8000/` : send an HTTP GET to the running API and print the JSON response
- `curl -i http://127.0.0.1:8000/` : same, but include response status line and headers

## Module 3 — Backend: SQLAlchemy models

- `uv add sqlalchemy psycopg` : add the SQLAlchemy ORM + the sync Postgres driver (psycopg) as deps
- `uv run python -c "import models; print('ok')"` : import-check the models module inside the venv
- `uv run python -c "from sqlalchemy.schema import CreateTable; from models import Link; print(CreateTable(Link.__table__))"` : render the CREATE TABLE SQL SQLAlchemy generates from the model
- `uv run python -c "import database; print(database.DATABASE_URL)"` : verify the .env DATABASE_URL loads via python-dotenv
- `uv run python -c "from database import engine; from sqlalchemy import text; print(engine.connect().execute(text('SELECT 1')).scalar())"` : ping Postgres through the SQLAlchemy engine

## Module 4 — Backend: Alembic migrations

- `uv add alembic` : add Alembic (SQLAlchemy's migration tool) as a dependency
- `uv run alembic init alembic` : scaffold the migrations env (alembic.ini + alembic/ with env.py, versions/)
- `uv run alembic current` : show which migration revision the database is currently stamped at
- `uv run alembic revision --autogenerate -m "create links table"` : diff models vs DB and write a migration script
- `uv run alembic upgrade head` : apply all unapplied migrations up to the latest revision
- `uv run alembic downgrade -1` : roll back the most recent migration (reverse via its downgrade())

## Module 5 — Backend: full API

- `uv add asyncpg` : add the async Postgres driver used by the live API (Alembic keeps sync psycopg)
- `uv run python -c "from main import generate_code; print(generate_code())"` : sanity-check the short-code generator
- `curl -X POST http://127.0.0.1:8000/api/links -H "Content-Type: application/json" -d '{"target_url": "https://example.com"}'` : create a link (POST JSON body)
- `curl http://127.0.0.1:8000/api/links` : list all links (newest first) as a JSON array
- `curl -i http://127.0.0.1:8000/<code>` : follow a short code — expect 307 redirect + Location header, click counter increments
- `uv add prometheus-fastapi-instrumentator` : add auto-instrumentation that exposes app metrics at /metrics
- `curl http://127.0.0.1:8000/metrics` : fetch Prometheus-format metrics text

## Module 6 — Frontend: Vite + React + TypeScript

- `node --version && npm --version` : check Node.js runtime and npm package-manager versions
- `winget install OpenJS.NodeJS.LTS` : install/upgrade Node.js to current LTS (needed >=22.12 for Vite 8/rolldown)
- `npm create vite@latest frontend -- --template react-ts` : scaffold a React + TypeScript app in frontend/
- `npm install` : install the frontend's dependencies into node_modules (from package.json)
- `rm -rf node_modules package-lock.json && npm install` : clean reinstall (fixes skipped native bindings)
- `npm run dev` : start the Vite dev server with hot-reload (http://localhost:5173)
- `git check-ignore -v frontend/node_modules` : verify node_modules is git-ignored

## Module 7 — Frontend: wired to the API

- `npm run build` : type-check (tsc) and bundle the production build into frontend/dist/
- (edit `vite.config.ts` `server.proxy`) : forward `/api` from the Vite dev server (5173) to the backend (8000)

## Module 8 — Docker: backend image

- `docker --version && docker info` : check Docker CLI version and that the daemon is running
- `docker buildx ls` : list build drivers/builders (diagnosing the stuck buildkit boot)
- `docker build -t shortlink-backend:dev .` : build an image from ./Dockerfile, tag it name:tag
- `DOCKER_BUILDKIT=0 docker build -t shortlink-backend:dev .` : build with the legacy builder (bypass buildx)
- `docker pull python:3.12-slim` : pull a base image (used to test registry connectivity)
- `docker images shortlink-backend` : show an image and its size
- `docker run --rm shortlink-backend:dev ls -la /app` : run a throwaway container overriding the default command
- Git Bash note: absolute container paths like `/app` get mangled to Windows paths. Prefix with `MSYS_NO_PATHCONV=1` (e.g. `MSYS_NO_PATHCONV=1 docker run ... ls /app`) or use a leading double-slash `//app` to stop the translation.
- WSL/Docker note: disabled a standalone WSL docker daemon (`sudo systemctl disable --now docker docker.socket`) so only Docker Desktop's WSL integration is active; after changing it, `wsl --shutdown` + restart Docker Desktop to reset networking.

## Module 9 — Docker: frontend image (multi-stage + nginx)

- `docker build -t shortlink-frontend:dev .` : build the multi-stage frontend image (node build stage -> nginx runtime)
- `docker run --rm shortlink-frontend:dev ls -la /usr/share/nginx/html` : list the static files baked into the nginx image
- `docker run --rm shortlink-frontend:dev cat /etc/nginx/conf.d/default.conf` : print the nginx config inside the image
- Note: running the frontend image standalone fails because nginx can't resolve the `backend` hostname (that hostname is provided by Docker Compose in Module 10).

## Module 10 — Docker Compose

- `uv add "psycopg[binary]"` : switch to psycopg with a bundled libpq so it works in the slim container (no system libpq)
- `docker compose up --build` : build images and start all services (postgres, migrate, backend, frontend) on one network
- `docker compose down` : stop and remove the stack's containers/network (named volumes are kept)
- `docker compose down -v` : same, but also delete named volumes (wipes the database)
- `docker compose ps` : list the stack's running services
- `docker compose logs -f <service>` : follow logs for one service
- App served at http://localhost:8080 through nginx; short codes redirect at the same origin (e.g. /{code}).

## Module 11 — Kubernetes: concepts and kind

- `kind --version` / `kubectl version --client` : check the kind and kubectl tool versions
- `kind create cluster --name shortlink` : create a local single-node Kubernetes cluster (a Docker container node)
- `kubectl config current-context` : show which cluster kubectl is pointed at (kind-shortlink)
- `kubectl get nodes` : list cluster nodes and their status
- `kubectl cluster-info` : show the control-plane / CoreDNS endpoints
- `kubectl apply -f <file>.yaml` : declaratively create/update objects from a manifest
- `kubectl get pods` / `kubectl get service <name>` : list pods / inspect a service
- `kubectl delete pod <name>` : delete a pod (Deployment recreates it — self-healing demo)
- `kubectl port-forward service/<name> 8081:80` : tunnel localhost:8081 to a ClusterIP service for testing
- `kubectl delete -f <file>.yaml` : delete the objects defined in a manifest
- `kind delete cluster --name shortlink` : delete the whole local cluster (when finished with the project)

## Module 12 — Kubernetes: full app

- `kubectl apply -f k8s/namespace.yaml` : create the `shortlink` namespace
- `kubectl apply -f k8s/configmap.yaml` : create the non-secret config (POSTGRES_USER/DB)
- `kubectl create secret generic shortlink-secret -n shortlink --from-literal=POSTGRES_PASSWORD=... --from-literal=DATABASE_URL=...` : create the Secret imperatively (never committed)
- `kubectl apply -f k8s/postgres.yaml` : StatefulSet + headless Service + PVC for Postgres
- `kind load docker-image <name>:latest --name shortlink` : load a locally-built image into the kind cluster
- `kubectl apply -f k8s/migrate-job.yaml` : run `alembic upgrade head` as a one-shot Job
- `kubectl apply -f k8s/backend.yaml` : backend Deployment (2 replicas, /health probes) + Service
- `kubectl apply -f k8s/frontend.yaml` : frontend Deployment (2 replicas) + Service
- `kubectl get pods -n shortlink -w` : watch pods in the namespace (Ctrl+C to stop)
- `kubectl logs -n shortlink job/migrate` : view the migration Job logs
- `kubectl describe pod <pod> -n shortlink` : inspect a pod's events (debugging)
- `kubectl port-forward -n shortlink service/frontend 8090:80` : reach the app in the cluster at localhost:8090
- Note: images use `imagePullPolicy: IfNotPresent` so kind-loaded local images aren't pulled from a registry.
