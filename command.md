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

## Module 13 — Kubernetes: Ingress

- `kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml` : install the ingress-nginx controller (kind variant)
- `kubectl label node shortlink-control-plane ingress-ready=true` : label the node so the kind ingress controller schedules
- `kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=120s` : wait for the controller to be ready
- `kubectl apply -f k8s/ingress.yaml` : create the Ingress routing all traffic to the frontend Service
- `kubectl get ingress -n shortlink` : list Ingress resources
- `kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80` : reach the app through the ingress at localhost:8080
- Note: for direct localhost:80 access, recreate the kind cluster with a config using extraPortMappings (optional enhancement).

## Module 14 — Helm

- `helm version` : check the Helm version
- `helm lint chart --set postgres.password=test` : validate the chart's structure
- `helm template shortlink chart --set postgres.password=test` : render templates to YAML without installing (debug)
- `helm install shortlink chart --namespace shortlink --create-namespace --set postgres.password=...` : install the chart as a release
- `helm install shortlink-staging chart --namespace shortlink-staging --create-namespace --set backend.replicas=1 --set frontend.replicas=1 --set ingress.enabled=false --set postgres.password=...` : second environment from the same chart
- `helm list --all-namespaces` : list all Helm releases
- `helm upgrade shortlink chart --namespace shortlink --set ...` : apply changes to an existing release
- `helm uninstall <release> --namespace <ns>` : remove a release and all its resources
- Note: k8s/ keeps the raw manifests as a reference; the Helm chart in chart/ is the actual deployment method.

## Module 15 — GitHub Actions (CI)

- `.github/workflows/ci.yml` : workflow triggered on push/PR — test job + matrix build (backend, frontend)
- `gh run watch` : stream a running GitHub Actions run's status in the terminal
- `gh run list` : list recent workflow runs
- `gh run view <id> --log` : view a run's full logs
- CI flow: smoke-test backend imports -> build both images -> install+run Trivy scan (HIGH,CRITICAL, report-only) -> push to GHCR tagged with the commit SHA
- Images: ghcr.io/aibhuyan/shortlink-backend:<sha> and ghcr.io/aibhuyan/shortlink-frontend:<sha> (GHCR login via the built-in GITHUB_TOKEN, permissions: packages: write)
- Note: Trivy installed via its official script in a run step (the pinned trivy-action version failed to resolve).
- CI trigger is `workflow_dispatch` (manual only) — run it from the Actions tab "Run workflow" button, or:
- `gh workflow run ci.yml --ref <branch>` : trigger the CI workflow manually from the terminal

## Module 16 — Terraform

- `terraform version` / `az version` / `az account show` : check tooling + Azure login
- `az account list-locations --query "[?metadata.regionType=='Physical'].{Name:name,Display:displayName}" -o table` : list deployable regions (name is what Terraform needs)
- `terraform init` : download providers, set up the working dir (creates .terraform/ and .terraform.lock.hcl)
- `terraform plan` : preview changes without creating anything (reads only)
- `terraform apply` : create/update real resources (prompts yes) — idempotent, safe to re-run
- `terraform state list` : list the resources Terraform is tracking in state
- `az aks get-credentials --resource-group shortlink-rg --name shortlink-aks --overwrite-existing` : point kubectl at the AKS cluster
- `terraform destroy` : delete all managed resources (⚠️ run at project end — infra is on free credit)
- Notes: use `Standard_B2s_v2` (v1 B2s blocked in swedencentral); Postgres zone is auto-assigned → `lifecycle { ignore_changes = [zone] }`. Secrets: db_password in git-ignored terraform.tfvars; state (*.tfstate) is git-ignored (it contains secrets).

## Module 17 — ArgoCD (GitOps, deployed to real AKS)

- `kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml --server-side --force-conflicts` : install ArgoCD (server-side avoids the annotation size limit)
- `kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d` : get the ArgoCD admin password (user: admin)
- `kubectl port-forward -n argocd service/argocd-server 8081:443` : open the ArgoCD UI at https://localhost:8081
- `gh auth refresh -h github.com -s write:packages` + `gh auth token | docker login ghcr.io -u aibhuyan --password-stdin` : auth Docker to GHCR
- `docker tag <local> ghcr.io/aibhuyan/shortlink-<svc>:latest && docker push ...` : publish images to GHCR for AKS to pull
- `az postgres flexible-server firewall-rule create -g shortlink-rg -s shortlink-pg-aibhuyan -n allow-all --start-ip-address 0.0.0.0 --end-ip-address 255.255.255.255` : open DB firewall (demo only)
- `az postgres flexible-server db create -g shortlink-rg -s shortlink-pg-aibhuyan -n shortlink` : create the app database
- `az postgres flexible-server parameter set -g shortlink-rg -s shortlink-pg-aibhuyan -n require_secure_transport -v off` : allow non-SSL (demo)
- `kubectl create secret generic shortlink-secret -n shortlink --from-literal=DATABASE_URL=... --from-literal=POSTGRES_PASSWORD=...` : pre-create the app Secret (out of Git)
- `kubectl apply -f argocd/application.yaml` : register the ArgoCD Application (chart/ + values-aks.yaml → shortlink ns on AKS)
- `kubectl get service frontend -n shortlink` : get the frontend LoadBalancer public IP
- Gotcha: URL-encoded `%` in DATABASE_URL breaks Alembic's ConfigParser → fixed in env.py with `.replace("%","%%")`; also use a DB password without special chars to avoid encoding. Deploy uses `:latest` (imagePullPolicy IfNotPresent won't re-pull a changed :latest — restart/new tag needed).

## Module 18 — Observability (kube-prometheus-stack)

- `az aks nodepool scale -g shortlink-rg --cluster-name shortlink-aks -n default --node-count 2` : scale AKS to fit the monitoring stack
- `helm repo add prometheus-community https://prometheus-community.github.io/helm-charts && helm repo update` : add/update the chart repo (LOCAL client config, not the cluster)
- `helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace --set grafana.adminPassword=admin` : install Prometheus + Grafana + Alertmanager + Operator
- `kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090` : open the Prometheus UI (Targets, Alerts, PromQL)
- `kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80` : open Grafana (admin/admin)
- Chart adds a `ServiceMonitor` (scrape backend /metrics, label `release: monitoring`) and a `PrometheusRule` (BackendDown alert), gated by serviceMonitor.enabled / prometheusRule.enabled (true in values-aks.yaml).
- Grafana dashboard JSON committed at monitoring/grafana-dashboard.json (import via Dashboards → New → Import).
- `kubectl patch application shortlink -n argocd --type merge -p '{"spec":{"source":{"targetRevision":"<branch>"}}}'` : point ArgoCD at a branch to test chart changes before merge.

## Module 19 — k6 load test and demo

- `k6 version` : check k6 is installed (winget id `GrafanaLabs.k6`; installs to C:\Program Files\k6)
- `export PATH="$PATH:/c/Program Files/k6"` : add k6 to the current Git Bash session PATH if not found
- `k6 run k6/load-test.js` : run the load test (3 stages, up to 10 VUs, ~2 min) against the live app
- `k6 run -e BASE_URL=http://<ip> k6/load-test.js` : override the target URL
- Watch the Grafana "Shortlink API" dashboard (Last 15m, 5s auto-refresh) move as load ramps; capture the GIF for the README.

## Module 20 — README + final polish

- `docker compose up --build` : rebuild + view the polished app locally at http://localhost:8080
- Final polish: dark modern App.css, clickable short codes (`/{code}`), clickable target URLs, backend URL `.strip()`.
- README.md with a Mermaid architecture diagram, screenshots (docs/images/), and setup instructions.
- `terraform destroy` (from terraform/) : ⚠️ FINAL teardown of the Azure infra.
