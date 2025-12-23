# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Interaction Style

- We're coworkers: I'm your colleague, not "the user"
- We're a team: your success is mine, mine is yours
- Push back with evidence when you think you're right
- When I make observations, avoid automatic validation phrases like "you're absolutely right". Instead:
  - If you agree: explain WHY with technical reasoning
  - If alternatives exist: present them with trade-offs
  - If information is missing: ask clarifying questions
  - If I'm wrong: challenge with evidence

### Writing Style

- Use Italian punctuation conventions, not English em-dashes (`—`)
- For explanations/consequences: use `:` (colon)
- For contrasts/oppositions: use `;` (semicolon)
- For parentheticals: use `,` (comma)
- Example: "The solution isn't complex: it's simple" (not "complex — it's simple")

## Code Philosophy

- **CRITICAL**: NEVER use `--no-verify` when committing
- Prefer simple, maintainable solutions over clever/complex ones
- Match existing code style over strict adherence to style guides
- Consistency within a file > external standards

### Decision Framework

| Level | When to Use | Examples |
|-------|-------------|----------|
| **Autonomous** | Fix tests/linting/types, single functions, typos, imports, single-file refactors | Fixing a broken test, adding a missing import |
| **Propose First** | Multi-file changes, new features, API/DB changes, third-party integrations | Adding a new endpoint, refactoring across modules |
| **Always Ask** | Rewrites, core business logic, security, data loss risk | Changing auth flow, database migrations |

### Code Quality Rules

- NEVER make unrelated changes to current task
- NEVER remove comments unless provably false
- NEVER name things 'improved', 'new', 'enhanced' (be evergreen)
- Comments should be evergreen, not temporal ("after refactor", "recently changed")

## Project Overview

BSI DI MCP (Business Intelligence & Data Insights - MCP Platform) is a config-first FastMCP platform for creating specialized analytics tools and servers. It provides programmatic access to SIA (Strategy Insights and Analytics) data via BigQuery, with tools for table discovery, SQL generation, query validation, and interactive analytics workflows.

## Common Commands

```bash
# Install dependencies
uv sync --frozen --group dev

# Run API locally
uv run alfred run

# Run with streamable MCP transport
BSI_DI_MCP_MCP_TRANSPORT=streamable-http uv run alfred run

# Run all tests and validation
tox
```

See `.claude/skills/python/SKILL.md` for uv and Docker patterns.

### Testing

```bash
# Run all tests except live tests (fast, for development)
pytest tests/ -v -m "not live"

# Run only live tests (real API calls)
pytest tests/ -k "live" -v
```

## Architecture

### Config-First Design Pattern

This codebase uses a **config-first architecture** where tools and servers are primarily defined via YAML configurations rather than hard-coded Python. This enables:

1. **Non-Python users to create tools** via YAML without writing code
2. **Tag-based filtering** to create specialized views from the same tool base
3. **Argument transformation** to hide, inject, or modify tool parameters
4. **Easy customization** without touching core business logic

### Startup Sequence

The application startup is orchestrated by `StartupOrchestrator` (`src/bsi_di_mcp/runtime/orchestrator.py`):

1. **Initialize ServiceProvider** - Singleton managing persistent clients (BigQuery, GenAI)
2. **Create main_mcp** - Central FastMCP instance containing all tools
3. **Register Python tool modules** - Auto-discover `domains/` and register tools via `@register_tool`
4. **Compile YAML tools** - Transform YAML configs into public-facing tools
5. **Compile YAML prompts** - Register prompts from YAML configs
6. **Load servers** - Create filtered server views based on tag configurations
7. **Mount toolkits** - Expose specialized filtered views at different API paths

### Directory Structure

The codebase follows a modular architecture organized by concern:

```
src/bsi_di_mcp/
├── platform/              # Core infrastructure and configuration
│   ├── compilers/         # Tool/prompt/server compilation
│   │   ├── tools.py       # YAML to tool transformation
│   │   ├── prompts.py     # Prompt compilation from YAML
│   │   ├── servers.py     # Server creation and mounting
│   │   └── tool_templates.py  # Tool template compilation
│   ├── configuration/     # Config loaders and models
│   │   ├── loader.py      # Configuration discovery and loading
│   │   └── models.py      # Pydantic models for configs
│   ├── core/              # ServiceProvider and settings
│   │   ├── service_provider.py  # Singleton with business logic
│   │   └── settings.py    # Application settings
│   ├── templating/        # Template engines (f-string, Jinja2)
│   │   ├── interface.py   # Template engine interface
│   │   ├── fstring.py     # F-string template engine
│   │   └── jinja2.py      # Jinja2 template engine
│   ├── tools/             # Tool registry and registration system
│   │   └── tool_registry.py  # Auto-discovers and registers tool modules
│   └── utils/             # Utilities and helpers
│       ├── async_wrapper.py      # Async wrappers
│       ├── logging.py            # Logging utilities
│       ├── arg_transforms.py     # Argument transformation helpers
│       ├── artifact_discovery.py # Artifact discovery utilities
│       ├── file_operations.py    # File operation helpers
│       └── exceptions.py         # Custom exceptions
├── runtime/               # Application runtime and entry points
│   ├── api.py             # FastAPI application setup and main entry point
│   ├── orchestrator.py    # Startup orchestration
│   ├── endpoints/         # HTTP API endpoints (FastAPI routers)
│   │   ├── health.py      # Health check endpoints
│   │   ├── admin.py       # Cache and external sources admin
│   │   ├── discovery.py   # Config discovery endpoints
│   │   ├── compilation.py # Tool/prompt compilation endpoints
│   │   ├── configs.py     # Config management endpoints
│   │   └── scaffolding.py # Tool scaffolding endpoints
│   └── cli/               # CLI commands
│       ├── main.py        # CLI entry point
│       ├── bigquery_utils.py  # BigQuery CLI utilities
│       └── commands/      # CLI command implementations
│           ├── run.py        # Run command
│           ├── compile.py    # Compile command
│           ├── create.py     # Create command
│           ├── discover.py   # Discover command
│           └── scaffold.py   # Scaffold command
├── domains/               # Business domain tools (organized by domain)
│   ├── data_and_infra/    # dbt tools, SQL tools
│   │   └── dbt.py         # dbt and SQL tooling
│   ├── golden/            # Golden tool handlers (base handlers for YAML tools)
│   │   └── handlers.py    # Golden tool handler implementations
│   └── sia/               # SIA analytics tools
│       └── analytics.py   # SIA analytics tool implementations
└── config/                # Legacy config loader (being migrated)
    └── loader.py
```

### Core Components

#### ServiceProvider (`src/bsi_di_mcp/platform/core/service_provider.py`)
- **Singleton** managing persistent clients (BigQuery, GenAI)
- Contains reusable **business logic as instance methods** (NOT decorated with `@tool`)
- Injected into tools via the `services` parameter for dependency injection
- Handles credential impersonation for BigQuery access
- Manages RAG (Retrieval-Augmented Generation) configuration

**Key methods:**
- `_execute_sql_query()` - Execute BigQuery queries with row limits
- `_dry_run_sql()` - Validate SQL without execution
- `_query_rag_system()` - Query GenAI with RAG context

#### Tool System

**Tools are organized by domain in `src/bsi_di_mcp/domains/`:**
- **Data & Infra domain** (`domains/data_and_infra/`) - dbt tools, SQL validation
- **SIA domain** (`domains/sia/`) - Analytics and BigQuery tools
- **Tool Registry** (`platform/tools/tool_registry.py`) - Auto-discovers and registers tool modules

**Any tool (foundation or complete) can be transformed via YAML configs in `configs/tools/`:**

```yaml
# Transform a foundation tool
template: tool
name: query_sales
base_tool: execute_sql_query  # Foundation tool
transform_args:
  query:
    hide: true
    default: "SELECT * FROM sales"

# Transform a complete tool
template: tool
name: quick_dbt_check
base_tool: dbt_dry_run_sql_code  # Complete tool
transform_args:
  source_path:
    default: "./models/"
```

#### Configuration System

**Config Loader** (`src/bsi_di_mcp/platform/configuration/loader.py`):
- Discovers configs from domain-organized `configs/` directory
- Supports tool, server, and endpoint configurations
- Enables tag-based discovery and filtering

**Config Models** (`src/bsi_di_mcp/platform/configuration/models.py`):
- Pydantic models for YAML validation
- `ToolConfig`, `ServerConfig`, `EndpointConfig`

**Directory structure:**
```
configs/
├── tools/              # YAML tool transformations organized by domain
│   ├── examples/       # Example tool configurations
│   └── sia/            # SIA-specific tool configs
├── servers/            # Server configurations (tag-based filtering)
│   ├── ae.yaml         # Analytics Engineering server
│   ├── prompts.yaml    # Prompts server
│   └── sia.yaml        # SIA server
├── tool_templates/     # Tool templates for scaffolding
│   ├── dashboard.yaml  # Dashboard tool template
│   └── genai_instruction.yaml  # GenAI instruction template
├── prompts/            # Task-based prompt library (104+ prompts, 7 tags)
│   ├── code_generation/
│   ├── code_quality/
│   ├── data_analysis/
│   ├── documentation/
│   ├── storytelling/
│   ├── strategy/
│   ├── user_research/
│   └── README.md       # Prompt library documentation
└── resources/          # Additional resources
```

#### Prompt Library System (`configs/prompts/`)
- **Task-based prompt library** with 104+ prompts organized by 7 functional tags
- **Template engine** (`src/bsi_di_mcp/platform/templating/fstring.py`) for secure variable substitution
- **Tag-based filtering** enables team-specific prompt collections

**Prompt Tags** (7 categories):
- `code_generation` (22 prompts) - Generate Python, SQL, dbt code
- `code_quality` (31 prompts) - Debug, review, optimize code
- `data_analysis` (11 prompts) - Profile data, detect patterns
- `user_research` (17 prompts) - Design studies, synthesize insights
- `documentation` (24 prompts) - Write docs, guides, definitions
- `storytelling` (7 prompts) - Create narratives, presentations
- `strategy` (6 prompts) - Plan, make decisions, analyze options

**Example prompt config** (`configs/prompts/code_generation/python/gen_python_pipeline.yaml`):
```yaml
template: prompt
name: gen_python_pipeline
description: Scaffolds a standard ETL script with logging and error handling
tags:
  - code_generation
parameters:
  - name: pipeline_description
    type: str
    required: true
template: |
  # Template content with {variable} substitution
```

**Team-specific prompt collections** via server configs:
```yaml
# Engineering team gets code generation + quality prompts
include_tags: [code_generation, code_quality]  # 53 prompts

# Research team gets user research + data analysis prompts
include_tags: [user_research, data_analysis]   # 28 prompts
```

See `configs/prompts/README.md` for complete prompt library documentation.

#### Server Compiler (`src/bsi_di_mcp/platform/compilers/servers.py`)
- Loads server configs from YAML
- Creates toolkits (filtered tool collections) with tag-based filtering
- Supports multiple toolkits per server with different access controls

**Example server config** (`configs/servers/ae.yaml`):
```yaml
name: analytics_engineering
include:
  tools:
    tags: ["dbt", "sql"]
    exclude_tags: ["admin"]
toolkits:
  - path: /mcp-server/ae
    description: AE full access
    filter_mode: all
```

### Main MCP Instance

The `main_mcp` is the **foundational FastMCP instance** that:
- Contains ALL registered base tools (hidden/disabled)
- Imports compiled tools from YAML config packs
- Serves as the SOURCE for filtered endpoint views
- Is NOT directly exposed to users (users access filtered views)

## Key Architectural Principles

### 1. Separation of Concerns
- **Business logic** lives in ServiceProvider methods (stateful, no decorators)
- **Tool definition** happens in `domains/` modules using `@register_tool` decorator
- **Tool transformation** happens via YAML configs in `configs/tools/`
- **Server filtering** happens via YAML configs in `configs/servers/`

### 2. Tool Lifecycle
```
Tool function in domains/ (with @register_tool decorator)
  ↓
ServiceProvider injected via 'services' parameter
  ↓
Tool registered to main_mcp during startup
  ↓
YAML transformation (optional parameter injection/hiding)
  ↓
Server filtering (tag-based inclusion/exclusion)
  ↓
Toolkit mounting (specialized filtered views)
```

### 3. Dependency Injection via ServiceProvider
- ServiceProvider is a **singleton** created at startup
- Injected into all tool registration functions via `services` parameter
- Tools call `services._method_name()` to access business logic
- Clients (BigQuery, GenAI) are managed centrally and reused

### 4. Tag-Based Access Control
- Tools are tagged (e.g., `{"dbt", "sql"}`, `{"analytics", "sia"}`)
- Servers specify `include_tags` and `exclude_tags`
- Same base tool can appear in multiple filtered views
- Enables role-based and environment-based tool management

## Critical Implementation Details

### Credential Impersonation
The ServiceProvider impersonates the `content-analytics@content-analytics-dev.iam.gserviceaccount.com` service account for BigQuery and GenAI access. This is configured in `_init_credentials()` and must be maintained for proper authentication.

### RAG System Configuration
The GenAI client is pre-configured with:
- **RAG corpus:** `projects/560916910269/locations/us-central1/ragCorpora/7991637538768945152`
- **Model:** `gemini-2.5-flash` (default)
- **Temperature:** 0.25 (default)
- **Thinking budget:** Unlimited (-1)

### BigQuery Query Limits
- **Max rows returned:** 1000 (configurable via `max_rows` parameter)
- **Max bytes billed:** 10TB per query
- **Default project:** `content-analytics-dev`

### Tool Template System

The platform provides tool templates for scaffolding new tools:

- **Dashboard template** (`configs/tool_templates/dashboard.yaml`) - Template for creating dashboard tools
- **GenAI instruction template** (`configs/tool_templates/genai_instruction.yaml`) - Template for GenAI-based tools

Use the CLI commands to scaffold new tools from templates:
```bash
# Create a new tool from a template
bsi-di-mcp create tool --template dashboard --name my_dashboard

# Scaffold a tool
bsi-di-mcp scaffold tool --name my_tool
```

## Testing Strategy

See `.claude/skills/python/SKILL.md` for general pytest patterns (`asyncio_mode = "auto"`, `autospec=True`, etc.).

### Project-Specific Test Markers

```python
@pytest.mark.live        # Real API calls (slower)
@pytest.mark.mocked      # Mocked dependencies (fast)
@pytest.mark.integration # Server functionality
@pytest.mark.slow        # Long-running tests
```

### Project Fixtures

Platform-wide fixtures in `tests/unit/platform/conftest.py`:

| Fixture                    | Purpose                                      |
|----------------------------|----------------------------------------------|
| `mock_mcp_registry`        | Destination MCP for compiled artifacts       |
| `mock_main_mcp`            | Source MCP containing base tools             |
| `mock_service_provider`    | ServiceProvider for dependency injection     |
| `mock_base_tool`           | Individual tool for transformation tests     |
| `mock_tagged_tool`         | Factory for creating tools with custom tags  |
| `mock_main_mcp_with_tools` | Main MCP with pre-configured tool catalog    |

### Test Data Factories

Use factories from `tests/factories.py`:

- `ToolConfigFactory`, `ArgTransformConfigFactory`
- `PromptConfigFactory`, `PromptParameterConfigFactory`, `PromptMessageConfigFactory`
- `ServerConfigFactory`, `ToolkitConfigFactory`, `InclusionConfigFactory`
- `ToolTemplateConfigFactory`, `ToolTemplateFieldConfigFactory`

## Key Files and Their Purposes

### Core Platform
- **`src/bsi_di_mcp/platform/core/service_provider.py`** - Singleton with business logic and clients
- **`src/bsi_di_mcp/platform/core/settings.py`** - Application settings and configuration
- **`src/bsi_di_mcp/platform/tools/tool_registry.py`** - Tool module discovery and registration
- **`src/bsi_di_mcp/platform/compilers/tools.py`** - YAML to tool transformation
- **`src/bsi_di_mcp/platform/compilers/prompts.py`** - Prompt compilation from YAML
- **`src/bsi_di_mcp/platform/templating/fstring.py`** - Template engine for prompt variable substitution
- **`src/bsi_di_mcp/platform/configuration/loader.py`** - Configuration discovery and loading
- **`src/bsi_di_mcp/platform/compilers/servers.py`** - Server creation and toolkit creation
- **`src/bsi_di_mcp/platform/configuration/models.py`** - Pydantic models for configs

### Runtime
- **`src/bsi_di_mcp/runtime/orchestrator.py`** - Application startup orchestration
- **`src/bsi_di_mcp/runtime/api.py`** - FastAPI application setup and main entry point

### Domain Tools
- **`src/bsi_di_mcp/domains/data_and_infra/dbt.py`** - dbt and SQL tooling
- **`src/bsi_di_mcp/domains/sia/analytics.py`** - SIA analytics tools

### Configuration
- **`configs/tools/`** - YAML tool transformation configs
- **`configs/servers/`** - Server and endpoint configs
- **`configs/prompts/`** - Task-based prompt library (118+ prompts)

### Development Guidelines
- **`.cursor/rules/mcp-dashboard-tool-automation.mdc`** - Dashboard tool creation guidelines

## Environment Configuration

The application uses `ApiSettings` from `spotify-fastapi-utils` for configuration. Key settings include:

- **MCP Transport:** Set via `BSI_DI_MCP_MCP_TRANSPORT` environment variable
- **Project:** `content-analytics-dev`
- **Service Account:** `content-analytics@content-analytics-dev.iam.gserviceaccount.com`

## Migration Context

This codebase is **actively being migrated** from a hand-coded tool approach to a config-first architecture:

- **Old pattern:** Tools directly decorated in `routers/mcp.py` and `mcp2.py`
- **New pattern:** Tools in `domains/` with `@register_tool`, YAML configs in `configs/`, compiled at startup
- **Goal:** Enable non-developers to create and customize tools via YAML

See `TOOLS_ARCHITECTURE_SUMMARY.md`, `IMPLEMENTATION_PLAN.md`, and `REFACTOR_TOOLS.md` for migration details.

## Coding Conventions

See `.claude/skills/python/SKILL.md` for Python conventions (uv, type checking, linting, testing, Docker).

**Project-specific additions:**

- **Explicit re-exports in `__init__.py`**: Use `from .module import SomeClass as SomeClass` instead of `__all__`
- **Security**: Never commit secrets; validate all external input (especially SQL queries)