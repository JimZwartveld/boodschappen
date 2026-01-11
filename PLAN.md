# Boodschappen (Groceries) App - Implementation Plan

## Overview

A self-hosted master groceries list service with iOS Siri/Shortcuts integration, MCP support for ChatGPT, and per-store exports. Primary access via Tailscale with optional public exposure via Cloudflare Tunnel.

---

## 1. Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite with async support (aiosqlite)
- **ORM/Migrations**: SQLAlchemy 2.0 + Alembic
- **Validation**: Pydantic v2
- **Server**: Uvicorn

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State**: React Query (TanStack Query)
- **PWA**: Vite PWA plugin

### Infrastructure
- **Container**: Docker with multi-stage builds
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions (self-hosted runner)
- **Network**: Tailscale (primary), Cloudflare Tunnel (optional)

---

## 2. Project Structure

```
boodschappen/
├── .github/
│   └── workflows/
│       └── deploy.yml              # CI/CD workflow
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry
│   │   ├── config.py               # Settings/env config
│   │   ├── database.py             # DB connection & session
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── item.py             # Item model
│   │   │   └── session.py          # Shopping session models
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── item.py             # Pydantic schemas
│   │   │   └── session.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── items.py            # /api/v1/items endpoints
│   │   │   ├── sessions.py         # /api/v1/sessions endpoints
│   │   │   ├── export.py           # /api/v1/export endpoints
│   │   │   └── health.py           # Health check endpoint
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── parser.py           # Item text parsing logic
│   │   │   ├── items.py            # Item business logic
│   │   │   └── sessions.py         # Session business logic
│   │   └── mcp/
│   │       ├── __init__.py
│   │       └── server.py           # MCP tools implementation
│   ├── migrations/
│   │   └── versions/               # Alembic migrations
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_parser.py
│   │   ├── test_items.py
│   │   └── test_api.py
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/
│   │   │   └── client.ts           # API client
│   │   ├── components/
│   │   │   ├── ItemList.tsx
│   │   │   ├── ItemRow.tsx
│   │   │   ├── AddItemForm.tsx
│   │   │   ├── ExportButtons.tsx
│   │   │   └── SessionHistory.tsx
│   │   ├── hooks/
│   │   │   └── useItems.ts
│   │   └── types/
│   │       └── index.ts
│   ├── public/
│   │   └── manifest.json           # PWA manifest
│   ├── index.html
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── shortcuts/
│   └── README.md                   # iOS Shortcuts setup guide
├── docs/
│   ├── DEPLOYMENT.md               # Deployment instructions
│   ├── TAILSCALE.md                # Tailscale setup guide
│   └── SHORTCUTS.md                # iOS Shortcuts instructions
├── docker-compose.yml              # Production compose
├── docker-compose.dev.yml          # Development compose
├── .env.example
├── requirements.md                 # Requirements (existing)
└── PLAN.md                         # This file
```

---

## 3. Implementation Phases

### Phase 1: Core Backend (Foundation)
**Goal**: Working API with basic item management

1. **Project Setup**
   - Initialize FastAPI project structure
   - Configure SQLAlchemy + SQLite
   - Set up Alembic for migrations
   - Create Dockerfile with multi-stage build

2. **Database Models**
   - `items` table with all fields from requirements
   - `sessions` table
   - `session_items` junction table
   - Initial migration

3. **Item Parser Service**
   - Parse quantities: `2x bread`, `bread 2x`
   - Parse units: `milk 2L`, `chicken 800g`
   - Normalize names (trim, lowercase, collapse spaces)
   - Handle multi-item input (newlines, commas)

4. **Items API**
   - `GET /api/v1/items` - List items with filters
   - `POST /api/v1/items:add` - Add items from text
   - `POST /api/v1/items/{id}:check` - Mark checked
   - `POST /api/v1/items/{id}:uncheck` - Uncheck
   - `PATCH /api/v1/items/{id}` - Update item
   - `DELETE /api/v1/items/{id}` - Remove item

5. **Unit Tests**
   - Parser tests (all patterns)
   - Deduplication logic tests
   - API endpoint tests

### Phase 2: Sessions & Export
**Goal**: Shopping sessions and store-specific exports

1. **Sessions API**
   - `POST /api/v1/sessions:start` - Start session
   - `POST /api/v1/sessions/{id}:close` - Close with policy
   - `GET /api/v1/sessions` - Session history

2. **Export API**
   - `GET /api/v1/export/{store}` - Export for AH/Jumbo/generic
   - Plaintext and JSON formats
   - Store preference filtering

3. **Session Logic**
   - Snapshot items on session start
   - Track checks during session
   - Apply close policies (keep_open, snooze, remove)

### Phase 3: Web UI
**Goal**: Mobile-friendly PWA for list management

1. **Project Setup**
   - React + Vite + TypeScript
   - Tailwind CSS configuration
   - PWA manifest and service worker

2. **Components**
   - Item list with sections (open/checked/snoozed)
   - Checkbox interaction (immediate update)
   - Inline edit (quantity, notes)
   - Add item form with quick parsing
   - Export buttons (AH/Jumbo)
   - Session history view

3. **API Integration**
   - React Query for data fetching
   - Optimistic updates for checkboxes
   - Error handling and offline states

4. **Mobile Optimization**
   - Large tap targets
   - Swipe gestures (optional)
   - Pull-to-refresh

### Phase 4: iOS Shortcuts Integration
**Goal**: Voice-activated list management via Siri

1. **API Endpoints for Shortcuts**
   - Simple auth token support (header-based)
   - Response formats optimized for Shortcuts
   - Clear error messages for voice feedback

2. **Shortcuts Documentation**
   - "Add to Groceries" shortcut
   - "Show Groceries" shortcut
   - "Export AH" shortcut
   - "Export Jumbo" shortcut
   - HomePod Personal Requests setup

### Phase 5: MCP Integration (Optional)
**Goal**: ChatGPT integration via MCP tools

1. **MCP Server**
   - `list_items` tool
   - `add_items` tool
   - `check_item` / `uncheck_item` tools
   - `remove_item` tool
   - `export_store` tool
   - Session management tools

2. **Authentication**
   - Token-based auth for MCP
   - Cloudflare Tunnel setup (if needed)

### Phase 6: Deployment & Documentation
**Goal**: Production-ready deployment

1. **Docker Configuration**
   - Optimized production Dockerfiles
   - docker-compose.yml with volumes
   - Health checks

2. **CI/CD Pipeline**
   - GitHub Actions workflow
   - Self-hosted runner deployment
   - Versioning strategy

3. **Documentation**
   - Deployment guide
   - Tailscale setup
   - iOS Shortcuts tutorial
   - Backup/restore procedures

---

## 4. Database Schema

### items
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| name_raw | VARCHAR(255) | NOT NULL | Original input name |
| name_norm | VARCHAR(255) | NOT NULL, INDEX | Normalized name for dedup |
| qty | FLOAT | DEFAULT 1 | Quantity |
| unit | VARCHAR(50) | NULLABLE | Unit (L, g, kg, etc.) |
| notes | TEXT | NULLABLE | Additional notes |
| status | ENUM | DEFAULT 'open' | open/checked/removed |
| preferred_store | ENUM | NULLABLE | AH/Jumbo/null |
| snooze_until | DATETIME | NULLABLE | Snooze expiry |
| created_at | DATETIME | NOT NULL | Creation timestamp |
| updated_at | DATETIME | NOT NULL | Last update |
| last_added_at | DATETIME | NOT NULL | Last time item was added |

### sessions
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| store | ENUM | NOT NULL | AH/Jumbo/generic |
| started_at | DATETIME | NOT NULL | Session start time |
| closed_at | DATETIME | NULLABLE | Session close time |
| close_policy | ENUM | NULLABLE | Applied close policy |

### session_items
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| session_id | UUID | FK | Reference to session |
| item_id | UUID | FK | Reference to item |
| qty_at_export | FLOAT | NOT NULL | Quantity at export time |
| unit_at_export | VARCHAR(50) | NULLABLE | Unit at export time |
| checked_at | DATETIME | NULLABLE | When checked during session |
| state | ENUM | NOT NULL | exported/checked/leftover |

---

## 5. API Design Summary

### Base URL: `/api/v1`

### Items
```
GET    /items                    # List items (filter: status, store)
POST   /items:add                # Add items from text
POST   /items/{id}:check         # Mark as checked
POST   /items/{id}:uncheck       # Mark as open
PATCH  /items/{id}               # Update item details
DELETE /items/{id}               # Remove item
```

### Sessions
```
POST   /sessions:start           # Start shopping session
POST   /sessions/{id}:close      # Close session with policy
GET    /sessions                 # List sessions
GET    /sessions/{id}            # Session details
```

### Export
```
GET    /export/{store}           # Export items for store
       ?format=plaintext|json
       &include_checked=false
       &include_snoozed=false
```

### Health
```
GET    /health                   # Health check
```

---

## 6. Parser Patterns

The parser will handle these input patterns:

| Input | Parsed |
|-------|--------|
| `bread` | qty=1, unit=null, name="bread" |
| `2x bread` | qty=2, unit=null, name="bread" |
| `bread 2x` | qty=2, unit=null, name="bread" |
| `milk 2L` | qty=2, unit="L", name="milk" |
| `chicken 800g` | qty=800, unit="g", name="chicken" |
| `2 limes` | qty=2, unit=null, name="limes" |
| `bread, milk, eggs` | 3 items, each qty=1 |
| `bread\nmilk\neggs` | 3 items, each qty=1 |

---

## 7. iOS Shortcuts Design

### 1. Add to Groceries (Boodschappen toevoegen)
```
Trigger: "Hey Siri, boodschappen toevoegen [items]"

Flow:
1. If input provided → use input
2. Else → Dictate text prompt
3. POST to /api/v1/items:add
4. Parse response
5. Speak: "Added [count] items: [names]"
```

### 2. Show Groceries (Boodschappen tonen)
```
Trigger: "Hey Siri, toon boodschappen"

Flow:
1. GET /api/v1/items?status=open
2. Format as readable list
3. Show in Quick Look
```

### 3. Export AH
```
Trigger: "Hey Siri, export Albert Heijn"

Flow:
1. GET /api/v1/export/AH?format=plaintext
2. Show preview
3. Copy to clipboard
4. Open Appie app (optional)
```

### 4. Export Jumbo
```
Trigger: "Hey Siri, export Jumbo"

Flow:
1. GET /api/v1/export/Jumbo?format=plaintext
2. Show preview
3. Copy to clipboard
4. Open Jumbo app (optional)
```

---

## 8. Deployment Architecture

### Network Topology
```
┌─────────────────────────────────────────────────────────────┐
│                     Home Server                              │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ groceries-api   │  │ groceries-ui    │                   │
│  │ (FastAPI)       │←─│ (nginx/static)  │                   │
│  │ :8000           │  │ :80             │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
│           │                    │                             │
│           └──────────┬─────────┘                             │
│                      │                                       │
│              ┌───────┴───────┐                               │
│              │   Tailscale   │                               │
│              │   (MagicDNS)  │                               │
│              └───────┬───────┘                               │
└──────────────────────┼──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
   ┌────┴────┐                  ┌─────┴─────┐
   │ iPhone  │                  │  HomePod  │
   │ (Jim)   │                  │ (Siri)    │
   └─────────┘                  └───────────┘
```

### Docker Compose Services
```yaml
services:
  groceries-api:
    build: ./backend
    ports:
      - "8002:8000"
    volumes:
      - groceries-data:/app/data
    environment:
      - DATABASE_URL=sqlite:///data/groceries.db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  groceries-ui:
    build: ./frontend
    ports:
      - "3082:80"
    depends_on:
      - groceries-api

volumes:
  groceries-data:
```

---

## 9. CI/CD Pipeline

### Workflow Triggers
- Push to `main` → Build and deploy
- Version tags (`v*`) → Build, tag, and deploy
- Pull requests → Build only (validation)

### Pipeline Stages
1. **Checkout** - Get latest code
2. **Version** - Extract version from git
3. **Build Backend** - Docker build for API
4. **Build Frontend** - Docker build for UI
5. **Test** - Run unit tests (optional in CI)
6. **Deploy** - docker-compose up -d
7. **Verify** - Health check
8. **Notify** - Show logs

### Available Secrets (from existing workflow)
- `CF_ACCESS_CLIENT_ID` - Cloudflare Access (for future public exposure)
- `CF_ACCESS_CLIENT_SECRET` - Cloudflare Access
- Repository-level Docker/compose access on self-hosted runner

---

## 10. Security Considerations

### Authentication Layers
1. **Tailscale** (primary) - Device-level trust
2. **API Token** (optional) - For public MCP access
3. **Cloudflare Access** (optional) - SSO for web UI

### Implementation
- API token via `X-API-Token` header
- Rate limiting on write endpoints (if public)
- CORS restricted to known origins
- No secrets in logs

---

## 11. Testing Strategy

### Unit Tests
- Parser: all quantity/unit patterns
- Deduplication logic
- Session close policies

### Integration Tests
- API endpoints
- Database operations
- Session workflows

### E2E Test
```
1. Add items via API
2. List items
3. Start session
4. Check some items
5. Export
6. Close session
7. Verify leftover handling
```

---

## 12. File Checklist for Initial Implementation

### Must Have (Phase 1)
- [ ] `backend/app/main.py`
- [ ] `backend/app/config.py`
- [ ] `backend/app/database.py`
- [ ] `backend/app/models/item.py`
- [ ] `backend/app/schemas/item.py`
- [ ] `backend/app/routers/items.py`
- [ ] `backend/app/services/parser.py`
- [ ] `backend/Dockerfile`
- [ ] `backend/requirements.txt`
- [ ] `docker-compose.yml`
- [ ] `.env.example`
- [ ] `.github/workflows/deploy.yml`

### Phase 2
- [ ] `backend/app/models/session.py`
- [ ] `backend/app/schemas/session.py`
- [ ] `backend/app/routers/sessions.py`
- [ ] `backend/app/routers/export.py`
- [ ] `backend/app/services/sessions.py`

### Phase 3
- [ ] `frontend/` (full React app)

### Phase 4+
- [ ] `docs/SHORTCUTS.md`
- [ ] `backend/app/mcp/server.py`

---

## 13. Estimated Effort

| Phase | Complexity | Description |
|-------|------------|-------------|
| 1 | Medium | Core backend with items API |
| 2 | Low-Medium | Sessions and export |
| 3 | Medium | Web UI (React PWA) |
| 4 | Low | iOS Shortcuts (config only) |
| 5 | Medium | MCP integration |
| 6 | Low | Documentation & polish |

---

## Next Steps

1. **Approve this plan** - Review and confirm approach
2. **Start Phase 1** - Set up backend project structure
3. **Iterate** - Implement phases incrementally
4. **Test on device** - Verify Siri integration works
