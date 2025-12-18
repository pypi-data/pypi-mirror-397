# Register UZ MCP Server

Model Context Protocol (MCP) server for Slovak Registry of Financial Statements (Register účtovných závierok) from Slovak Ministry of Finance based on the [API documentation](https://www.registeruz.sk/cruz-public/home/api).

**Author:** [@alhafoudh](https://github.com/alhafoudh)

## Features

- **Complete API Coverage**: All endpoints from the RegisterUZ Open API
- **Pydantic Models**: Fully typed response models for all API entities
- **25 MCP Tools**: Search, list, retrieve, and analyze financial data with labeled tables
- **8 MCP Resources**: Static classifier data and dynamic entity lookups
- **20 MCP Prompts**: Pre-built workflows for common integration scenarios
- **CLI Client**: Command-line tool for testing and exploration

## Data Available

- **Accounting Units** (Účtovné jednotky): Company/organization details including IČO, DIČ, address, legal form
- **Accounting Closures** (Účtovné závierky): Financial statement metadata and periods
- **Financial Reports** (Účtovné výkazy): Balance sheets, income statements with full data tables
- **Annual Reports** (Výročné správy): Annual report metadata and attachments
- **Templates** (Šablóny): Report structure definitions
- **Classifiers**: Legal forms, SK NACE codes, regions, districts, settlements

## Quick Start (Hosted Version)

Add the hosted MCP server to your Claude integration:

### Claude Code Integration (Hosted)

```bash
claude mcp add registeruz --transport http https://registeruz.fastmcp.app/mcp
```

### Claude Desktop Integration (Hosted)

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "registeruz": {
      "type": "streamable-http",
      "url": "https://registeruz.fastmcp.app/mcp"
    }
  }
}
```

### Make.com Integration (Hosted)

You can use the Autoform MCP server in [Make.com](https://www.make.com/) (formerly Integromat) using the **MCP Client - Call a tool** app:

1. Add the **MCP Client - Call a tool** module to your scenario
2. Create a new MCP server connection with these settings:
   - **URL**: `https://registeruz.fastmcp.app/mcp`
   - **API key / Access token**: Leave empty (no authentication required)
3. Select the tool you want to call and configure your query parameters

---

## Self-Hosted Installation

### From PyPI (recommended)

```bash
pip install registeruz-mcp
```

Or using uvx to run directly without installation:

```bash
uvx registeruz-mcp
```

### From source

```bash
# Clone the repository
git clone https://github.com/alhafoudh/registeruz-mcp.git
cd registeruz-mcp

# Install dependencies
uv sync
```

## Usage

### Run the MCP server (STDIO transport)

```bash
# If installed from PyPI
registeruz-mcp

# Or using uvx
uvx registeruz-mcp

# Or from source
uv run python registeruz_mcp.py
```

### Run with FastMCP CLI

```bash
uv run fastmcp run registeruz_mcp.py
```

### Inspect available tools

```bash
uv run fastmcp inspect registeruz_mcp.py
```

### Development mode with MCP Inspector

```bash
uv run fastmcp dev registeruz_mcp.py
```

## Available Tools

### List Tools (Get IDs)
| Tool | Description |
|------|-------------|
| `get_uctovne_jednotky` | Get accounting unit IDs changed since a date (supports filtering by IČO, DIČ, legal form) |
| `get_uctovne_zavierky` | Get accounting closure IDs changed since a date |
| `get_uctovne_vykazy` | Get financial report IDs changed since a date |
| `get_vyrocne_spravy` | Get annual report IDs changed since a date |

### Count Tools (Pagination)
| Tool | Description |
|------|-------------|
| `get_zostavajuce_id_uctovne_jednotky` | Count remaining accounting unit IDs |
| `get_zostavajuce_id_uctovne_zavierky` | Count remaining accounting closure IDs |
| `get_zostavajuce_id_uctovne_vykazy` | Count remaining financial report IDs |
| `get_zostavajuce_id_vyrocne_spravy` | Count remaining annual report IDs |

### Detail Tools
| Tool | Description |
|------|-------------|
| `get_uctovna_jednotka` | Get accounting unit details by ID |
| `get_uctovna_zavierka` | Get accounting closure details by ID |
| `get_uctovny_vykaz` | Get financial report with tables and data |
| `get_vyrocna_sprava` | Get annual report details by ID |

### Template Tools
| Tool | Description |
|------|-------------|
| `get_sablona` | Get template structure by ID |
| `get_sablony` | Get all available templates |

### Classifier Tools
| Tool | Description |
|------|-------------|
| `get_pravne_formy` | Get all legal forms |
| `get_sk_nace` | Get SK NACE classification codes |
| `get_druhy_vlastnictva` | Get ownership types |
| `get_velkosti_organizacie` | Get organization sizes |
| `get_kraje` | Get Slovak regions |
| `get_okresy` | Get Slovak districts |
| `get_sidla` | Get Slovak settlements |

### Download Tools
| Tool | Description |
|------|-------------|
| `get_attachment_url` | Get download URL for attachment |
| `get_financial_report_pdf_url` | Get PDF download URL for financial report |

### Labeled Data Tools
| Tool | Description |
|------|-------------|
| `get_uctovny_vykaz_with_labeled_tables` | Get financial report with labeled tables (combines report with template labels in one call) |
| `get_uctovny_vykaz_table_value_by_labels` | Search for specific values by row label, row code, column label, or table name |

## Available Resources

### Static Resources (Classifiers)
| URI | Description |
|-----|-------------|
| `ruz://classifiers/pravne-formy` | Legal forms |
| `ruz://classifiers/sk-nace` | SK NACE codes |
| `ruz://classifiers/druhy-vlastnictva` | Ownership types |
| `ruz://classifiers/velkosti-organizacie` | Organization sizes |
| `ruz://classifiers/kraje` | Regions |
| `ruz://classifiers/okresy` | Districts |
| `ruz://classifiers/sidla` | Settlements |
| `ruz://templates` | All templates |

### Dynamic Resource Templates
| URI Pattern | Description |
|-------------|-------------|
| `ruz://uctovna-jednotka/{id}` | Accounting unit by ID |
| `ruz://uctovna-zavierka/{id}` | Accounting closure by ID |
| `ruz://uctovny-vykaz/{id}` | Financial report by ID |
| `ruz://vyrocna-sprava/{id}` | Annual report by ID |
| `ruz://sablona/{id}` | Template by ID |

## Available Prompts

### Company Search Prompts
| Prompt | Description |
|--------|-------------|
| `search_company_by_ico` | Search for company by IČO and get financial statements |
| `search_company_by_dic` | Search for company by tax ID (DIČ) |
| `search_companies_by_legal_form` | Search for companies by legal form (e.g., s.r.o., a.s.) |

### Financial Analysis Prompts
| Prompt | Description |
|--------|-------------|
| `get_latest_financials` | Get latest financial statements for a company |
| `compare_financials_year_over_year` | Compare company financials across multiple years |
| `extract_financial_metrics` | Extract specific financial metrics (profit, assets, liabilities) |
| `get_balance_sheet` | Get balance sheet (Súvaha) data for a company |
| `get_income_statement` | Get income statement (Výkaz ziskov a strát) for a company |

### Change Tracking & Monitoring Prompts
| Prompt | Description |
|--------|-------------|
| `analyze_changes` | Analyze changes in accounting units over a period |
| `monitor_new_filings` | Monitor new financial statements filed since a date |
| `track_company_changes` | Track a specific company for recent changes |

### Document & Download Prompts
| Prompt | Description |
|--------|-------------|
| `get_company_documents` | Get all downloadable documents for a company |
| `get_annual_reports` | Download annual reports (Výročné správy) for a company |

### Template & Structure Prompts
| Prompt | Description |
|--------|-------------|
| `explore_template` | Explore financial report template structure |
| `list_all_templates` | List all available report templates with their purposes |

### Classifier & Reference Data Prompts
| Prompt | Description |
|--------|-------------|
| `get_location_hierarchy` | Get all Slovak regions and districts hierarchy |
| `get_legal_forms_explained` | Get all legal forms with explanations |
| `explore_sk_nace` | Explore SK NACE industry classification codes |

### Bulk/Export Prompts
| Prompt | Description |
|--------|-------------|
| `bulk_export_companies` | Export basic data for multiple companies |
| `generate_financial_summary` | Generate comprehensive company financial summary report |

## Claude Code Integration (Self-Hosted)

### Using uvx (recommended)

Run the server directly from PyPI without installation:

```bash
claude mcp add registeruz -- uvx registeruz-mcp
```

### Using local installation

If you've cloned the repository:

```bash
claude mcp add registeruz -- uv run --directory /path/to/registeruz-mcp python registeruz_mcp.py
```

## Claude Desktop Integration (Self-Hosted)

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

### Using uvx (recommended)

```json
{
  "mcpServers": {
    "registeruz": {
      "command": "uvx",
      "args": ["registeruz-mcp"]
    }
  }
}
```

### Using local installation

```json
{
  "mcpServers": {
    "registeruz": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/registeruz-mcp", "python", "registeruz_mcp.py"]
    }
  }
}
```

## Development

### Install dev dependencies

```bash
uv sync --all-extras
```

### Run tests

```bash
uv run pytest -v
```

## License

MIT
