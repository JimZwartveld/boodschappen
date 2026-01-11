# requirements.md — Groceries Master List (Docker + MCP + Siri/Shortcuts)

## 0. Summary
Build a self-hosted “master” groceries list service that can be updated from:
- **iOS Siri** (via iOS Shortcuts, including HomePod Personal Requests)
- **ChatGPT** (via MCP tools, or via iOS Shortcut share sheet)
and can be exported per store (e.g., **Albert Heijn** / **Jumbo**) via dedicated iOS Shortcuts.

Primary access for the family should be **Tailscale** (private, simple). Optional public domain support (e.g. `boodschappen.jimzwartveld.com`) may be added later via Cloudflare Tunnel for web UI.

---

## 1. Goals
- Single source of truth: **one master list** with item states (open/checked/removed/snoozed).
- Fast & frictionless adding items by voice: “Hey Siri, add bread…”.
- View/edit list before export (mobile-friendly web UI + “Show list” Shortcut).
- Per-store exports (AH/Jumbo) using Shortcuts at shopping time.
- Robust handling of **not-checked items**: default remain open; optional session close rules.
- Secure and private by default (Tailscale); safe-by-design if exposed publicly.

## 2. Non-goals (for v1)
- Direct integration with Albert Heijn / Jumbo official apps or private APIs.
- Barcode scanning, receipt ingestion, or price comparisons.
- Multi-language NLP perfection (simple parsing first; improve iteratively).

---

## 3. Personas & User Stories
### P-USR-001: Household users (Jim + partner)
- As a user, I can say “Hey Siri, add bread” and it appears on the master list.
- As a user, I can add multiple items at once (“bread, milk, 2x limes”).
- As a user, I can open a web page on my phone and see/modify the list.
- As a user, I can export the current open items for AH or Jumbo right before shopping.
- As a user, I can check items off while shopping and keep leftovers for next time.

### P-ADM-001: Admin (Jim)
- As admin, I can deploy via Docker and secure with Tailscale.
- As admin, I can inspect logs and rotate any tokens if public exposure is enabled.

---

## 4. High-level Architecture
- **groceries-api**: FastAPI (or similar) service providing REST endpoints + optional MCP endpoint.
- **groceries-ui**: small web UI (PWA-friendly) for list viewing and checking items.
- **storage**: SQLite (v1) with upgrade path to Postgres.
- **access**:
  - Default: Tailscale (MagicDNS + optional Tailscale Serve for HTTPS).
  - Optional: Cloudflare Tunnel for public domain + access controls.

---

## 5. Functional Requirements (R-*)
### 5.1 List Management
- **R-LIST-001**: Create/add items via text input (multi-line and comma-separated).
- **R-LIST-002**: Support quantities and units (e.g., `2x limes`, `milk 2L`, `chicken 800g`).
- **R-LIST-003**: Normalize item naming (trim, lowercase, collapse spaces) while preserving a display name.
- **R-LIST-004**: Deduplicate items by normalized name; adding increases quantity when appropriate.
- **R-LIST-005**: Allow manual editing: rename item, adjust quantity, add notes.
- **R-LIST-006**: Allow deleting/removing item from master list.
- **R-LIST-007**: Allow “snooze” item until a date/time; snoozed items are excluded from exports by default.
- **R-LIST-008**: Allow “unsnooze” returning item to open list.
- **R-LIST-009**: Allow marking item as purchased/checked, and unchecking.

### 5.2 Shopping Sessions
- **R-SESS-001**: Starting an export creates a **shopping session** (store + timestamp).
- **R-SESS-002**: Session captures a snapshot of exported items (IDs + quantities at export time).
- **R-SESS-003**: Items checked during session are recorded against the session.
- **R-SESS-004**: Session close action supports policies:
  - **keep_open** (default): leftover items remain open
  - **snooze_leftovers** (e.g., 7 days)
  - **remove_leftovers**
- **R-SESS-005**: Ability to view session history (basic list with timestamps, store, counts).

### 5.3 Store Exports
- **R-EXP-001**: Provide export views per store: `AH`, `Jumbo`, plus a generic export.
- **R-EXP-002**: Export content types:
  - plaintext checklist (best for clipboard)
  - JSON (for UI/automation)
- **R-EXP-003**: Export includes only `open` items excluding snoozed items by default.
- **R-EXP-004**: Optional per-item store preference (`preferred_store`) with logic:
  - Store export includes items with matching preference or no preference.

### 5.4 Siri / iOS Shortcuts
- **R-IOS-001**: “Add to Groceries” Shortcut:
  - Accepts shared text input (Share Sheet) or prompted dictation if empty.
  - POST to API endpoint to add items.
  - Speaks/returns confirmation list.
- **R-IOS-002**: “Show Groceries” Shortcut:
  - GET list and show in Quick Look (readable format).
- **R-IOS-003**: “Export AH” Shortcut:
  - GET export, show preview, copy to clipboard, open Appie.
- **R-IOS-004**: “Export Jumbo” Shortcut:
  - GET export, show preview, copy to clipboard, open Jumbo app.
- **R-IOS-005**: HomePod support: Shortcuts must be callable via Siri as Personal Requests.
- **R-IOS-006**: Shortcut responses are designed to work without needing browser cookies.

### 5.5 MCP Integration (Optional but supported)
- **R-MCP-001**: Provide MCP tools:
  - `list_items`
  - `add_items`
  - `check_item`
  - `uncheck_item`
  - `remove_item`
  - `export_store`
  - `start_session` / `close_session`
- **R-MCP-002**: MCP tools must be idempotent where possible (e.g., repeated add merges).
- **R-MCP-003**: If MCP is used from ChatGPT cloud, expose a secure public endpoint (Cloudflare Tunnel + auth).

### 5.6 Web UI (PWA)
- **R-UI-001**: Mobile-first list view with:
  - open items
  - checked items (optional collapsed)
  - snoozed items (separate tab/section)
- **R-UI-002**: Checkbox interaction updates item status immediately.
- **R-UI-003**: Inline edit quantity/notes.
- **R-UI-004**: Button(s): Export AH, Export Jumbo (generate and show export text + copy).
- **R-UI-005**: Session view (simple history).
- **R-UI-006**: Add item input with quick parsing.

---

## 6. API Requirements (v1 REST)
Base URL: `/api/v1`

### 6.1 Items
- **GET** `/items`  
  Returns items (optionally filter by status).
- **POST** `/items:add`  
  Body: `{ "text": "bread\n2x limes", "source": "siri|chatgpt|ui", "preferred_store": null|"AH"|"Jumbo" }`
- **POST** `/items/{id}:check`
- **POST** `/items/{id}:uncheck`
- **PATCH** `/items/{id}`  
  Update: name, qty, unit, notes, preferred_store, snooze_until.
- **DELETE** `/items/{id}`

### 6.2 Sessions
- **POST** `/sessions:start`  
  Body: `{ "store": "AH|Jumbo|generic" }`  
  Returns session id.
- **POST** `/sessions/{id}:close`  
  Body: `{ "policy": "keep_open|snooze_leftovers|remove_leftovers", "snooze_days": 7 }`
- **GET** `/sessions`  
  List recent sessions.

### 6.3 Exports
- **GET** `/export/{store}`  
  Query: `format=plaintext|json`, `include_checked=false`, `include_snoozed=false`
  - Should also create a session implicitly if requested (or require explicit `sessions:start`—choose one approach and document).

---

## 7. Data Model Requirements (SQLite v1)
### 7.1 Tables (suggested)
- `items`
  - `id` (uuid)
  - `name_raw`
  - `name_norm` (unique-ish)
  - `qty` (float)
  - `unit` (text, nullable)
  - `notes` (text, nullable)
  - `status` (`open|checked|removed`)
  - `preferred_store` (`AH|Jumbo|null`)
  - `snooze_until` (datetime nullable)
  - `created_at`, `updated_at`, `last_added_at`
- `sessions`
  - `id` (uuid)
  - `store` (`AH|Jumbo|generic`)
  - `started_at`, `closed_at`
  - `close_policy`
- `session_items`
  - `session_id`
  - `item_id`
  - `qty_at_export`, `unit_at_export`
  - `checked_at` (nullable)
  - `state` (`exported|checked|leftover`)

### 7.2 Parsing Rules (v1)
- Accept patterns:
  - `2x bread`
  - `bread 2x`
  - `milk 2L`, `chicken 800g`
- Default quantity = 1, unit = null.
- If item already exists (same `name_norm`), increment qty when numeric; else keep as separate note if ambiguous.


## 7.3 Persistent Data & Non-destructive Deployments
- **R-DATA-010**: Application containers must be **stateless**; no database file is baked into the Docker image.
- **R-DATA-011**: The database must persist across deployments using either:
  - a Docker **named volume**, or
  - a **bind mount** to a fixed host directory (recommended for simple backups).
- **R-DATA-012**: Rolling out a new application version must not overwrite or reset the database.
- **R-DATA-013**: Schema changes must be handled via migrations (e.g., Alembic) executed on startup or as a deploy step.
- **R-DATA-014**: Provide a simple backup/restore procedure for SQLite (copy/`sqlite .backup`) and document it.

---

## 8. Security & Privacy
- **R-SEC-001**: Default deployment is private via Tailscale.
- **R-SEC-002**: If exposed publicly (Cloudflare Tunnel), require authentication:
  - Option A: Cloudflare Access (SSO) for UI
  - Option B: API token (header) for write endpoints
- **R-SEC-003**: Rate limit write endpoints if public.
- **R-SEC-004**: Do not log secrets or full auth headers.
- **R-SEC-005**: CORS locked down to expected origins.

---

## 9. Deployment Requirements

### 9.1 CI/CD (GitHub Actions)
- **R-CICD-001**: Provide a GitHub Actions workflow that builds the Docker image on every push to `main`.
- **R-CICD-002**: Workflow pushes the built image to a container registry (preferred: GHCR) with:
  - `:latest` tag for mainline
  - immutable tag (e.g., commit SHA)
- **R-CICD-003**: Workflow deploys to the home server by pulling the new image and restarting the service (e.g., `docker compose pull` + `docker compose up -d`).
- **R-CICD-004**: Deployment must be non-destructive to persistent data (see R-DATA-010..012).
- **R-CICD-005**: The repository may include a reference GitHub Actions YAML (provided separately) which the implementation should follow/adapt.

- **R-DEP-001**: Provide `docker-compose.yml` with services:
  - groceries-api
  - groceries-ui (optional; can be served by api too)
  - volume for SQLite
- **R-DEP-002**: Provide `.env.example` for config (port, base_url, auth mode).
- **R-DEP-003**: Health checks for services.
- **R-DEP-004**: Documentation for:
  - enabling Tailscale MagicDNS + (optional) Tailscale Serve
  - setting up iOS Shortcuts (Add/Show/Export AH/Export Jumbo)
  - HomePod requirements: Personal Requests + Voice Recognition

---

## 10. UX Requirements (Shortcuts & UI)
- **R-UX-001**: “Add” Shortcut must succeed with minimal taps/voice.
- **R-UX-002**: “Export” Shortcut must show preview before copying + opening store app.
- **R-UX-003**: UI must be readable on iPhone (large tap targets, quick check-off).
- **R-UX-004**: Offline tolerance: if server unreachable, Shortcut should show friendly error.

---

## 11. Testing Requirements
- **R-TST-001**: Unit tests for parser and dedup logic.
- **R-TST-002**: API contract tests for key endpoints.
- **R-TST-003**: Minimal E2E test: add → list → export → check → close session.

---

## 12. Acceptance Criteria (v1)
- AC-001: Saying “Boodschappen toevoegen brood” via Siri adds “brood” to master list.
- AC-002: From iPhone web UI, list is visible and items can be checked/unchecked.
- AC-003: Export AH/Jumbo Shortcuts preview and copy text successfully.
- AC-004: Leftover (not-checked) items remain open after a shopping session by default.
- AC-005: Tailscale-only deployment works for both users on iPhone.

---

## 13. Future Enhancements (Backlog)
- Better categorization (zuivel/groente/etc.) with editable categories.
- Multi-list support (e.g., “Costco”, “DIY”, “Pharmacy”).
- “Pantry inventory” mode.
- Multi-device push notifications.
- Optional cloud sync.
