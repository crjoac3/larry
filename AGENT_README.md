# WestWorld Inventory Portal - AI Context & Handoff

*This document is intended for AI agents continuing work on this project to quickly understand the architecture, design patterns, and recent history.*

## 🏗️ Architecture & Stack
- **Framework**: Python 3.9+ with Streamlit (UI) and Pandas (Data Manipulation).
- **Deployment**: Dockerized (`Dockerfile` / `docker-compose.yml`), intended to be run behind a Traefik reverse proxy (see `docker-compose remote.yml` for production tags).
- **Data Storage**: State is entirely maintained in local CSV files and a JSON settings file. 
  - `master_inventory.csv`: Core source of truth for all assets.
  - `recall_requests_log.csv`: Tracks return/recall workflows.
  - `audit_requests_log.csv`: Tracks audit workflows.
  - `users.csv`: Simple RBAC definition and user credentials.
  - `companies.csv`: Lists valid tenant companies.
  - `settings.json`: Stores configuration like email notification rules.
  - *Note*: These files must be persisted in a Docker volume (`/data`).

## 🔑 Core Design Paradigms
- **Tenant Isolation (RBAC)**: Users belong to a `company`. The UI filters the `master_inventory.csv` strictly by the logged-in user's company (unless they are a "Master User" belonging to the org `WestWorld`).
- **Data Editing (`st.data_editor`)**: 
  - The application relies heavily on `st.data_editor`.
  - When a user modifies a dataframe (e.g., checking "Select for Recall" or updating a tracking number), the app explicitly detects the change, updates the backing *file* (CSV), and immediately triggers an `st.rerun()` to maintain UI synchronicity.
- **Global Standards**:
  - **Themes**: Supports Light and Dark modes. Dark mode has extensive custom CSS injection in `app.py` (`get_theme_css`). Text color and popups required hardcoded CSS to fix internal Streamlit bugs.
  - **Dates**: Standardized to `MM-DD-YYYY` via `st.column_config.DatetimeColumn`.
  - **Currency**: Standardized to `$%.2f` via `st.column_config.NumberColumn`.

## 🔄 The "Force Update" Mechanism
- The `admin` user belonging to `WestWorld` has a "Super Admin" console.
- **Auto-Update (`entrypoint.sh`)**: On container boot, if `GIT_UPDATE=true` is set in the compose file, the script will automatically `git pull` the latest code from GitHub.
- **UI Update Button (`app.py`)**: The UI features a "Force Update from GitHub" button. 
  - *Crucial Context*: Because the app runs inside Docker but uses a mounted volume for the code (or relies on fetching over the baked-in code), it was prone to `exit status 128` ("dubious ownership") and `fatal: not a git repository` errors.
  - *The Fix*: The subprocess calls explicitely inject `git config --global --add safe.directory /app`, forcefully set `cwd="/app"`, and implement self-healing initialization (`git init` and `git remote add`) if `.git` is missing (e.g., when deployed via a zip file).

## 🚀 Recent Implementations (v5)
1. **Excel Upload Pipeline**: The code specifically looks for the `Total Units Received` tab in the mock client excel sheets as the primary import trigger, handling "Sold" and "Returned" states on adjacent tabs.
2. **Super Administrator Wipe Tool**: Added tools to surgically remove a specific company's records across all CSV files, or truncate files entirely, avoiding manual DB edits.
3. **Traefik Compatibility**: Remote deploy compose files are configured for the `proxy-net` network with standard Traefik TLS labels.

## 🛠️ Typical Agent Workflows
- **Modifying UI**: Will almost always occur in `app.py`. Be extremely careful with state management (`st.session_state`) and ensure `.to_csv(index=False)` is called after dataframe mutations before `st.rerun()`.
- **Modifying Data Structure**: Any new columns added to CSVs must be handled during the `pd.read_csv` loading phase and specifically formatted in the `st.data_editor` column configurations.
