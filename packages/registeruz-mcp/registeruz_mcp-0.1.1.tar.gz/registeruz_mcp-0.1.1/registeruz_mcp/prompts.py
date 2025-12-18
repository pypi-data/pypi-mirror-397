"""Prompts for the RegisterUZ MCP server."""


def register_prompts(mcp):
    """Register all prompts with the MCP server."""

    # =========================================================================
    # Company Search Prompts
    # =========================================================================

    @mcp.prompt(description="Search for a company by IČO and get its financial statements")
    def search_company_by_ico(ico: str) -> str:
        """Prompt to search for company by ICO."""
        return f"""Search for the company with IČO (registration number) {ico} in the Slovak Registry of Financial Statements.

Steps:
1. Use get_uctovne_jednotky with ico={ico} and a recent zmenene_od date (e.g., 2020-01-01) to find the accounting unit ID
2. Use get_uctovna_jednotka to get the company details including idUctovnychZavierok
3. For each accounting closure ID, use get_uctovna_zavierka to get closure details
4. Use get_uctovny_vykaz to get the actual financial report data
5. If needed, use get_sablona with the idSablony to understand the report structure

Please provide a summary of the company's financial information."""

    @mcp.prompt(description="Search for a company by tax ID (DIČ)")
    def search_company_by_dic(dic: str) -> str:
        """Prompt to search for company by tax ID."""
        return f"""Search for the company with DIČ (tax ID) {dic} in the Slovak Registry of Financial Statements.

Steps:
1. Use get_uctovne_jednotky with dic={dic} and a recent zmenene_od date (e.g., 2020-01-01) to find the accounting unit ID
2. Use get_uctovna_jednotka to get the company details
3. Get the related accounting closures and financial reports

Please provide a summary of the company's information and financial data."""

    @mcp.prompt(description="Search for companies by legal form (e.g., s.r.o., a.s.)")
    def search_companies_by_legal_form(legal_form_code: str, since_date: str = "2024-01-01") -> str:
        """Prompt to search for companies by legal form."""
        return f"""Find companies with legal form code {legal_form_code} that have been updated since {since_date}.

Steps:
1. First, use get_pravne_formy to verify the legal form code and get its full name
2. Use get_uctovne_jednotky with pravna_forma={legal_form_code} and zmenene_od={since_date}
3. Use get_zostavajuce_id_uctovne_jednotky to get the total count of matching companies
4. For the first few results, use get_uctovna_jednotka to get company details

Common legal form codes:
- 112: Spoločnosť s ručením obmedzeným (s.r.o.) - Limited liability company
- 121: Akciová spoločnosť (a.s.) - Joint stock company
- 101: Fyzická osoba - Natural person / Sole proprietor
- 331: Príspevková organizácia - Contributory organization

Provide a summary of the companies found."""

    # =========================================================================
    # Financial Analysis Prompts
    # =========================================================================

    @mcp.prompt(description="Get the latest financial statements for a company")
    def get_latest_financials(company_id: int) -> str:
        """Prompt to get latest financials for a company."""
        return f"""Retrieve the latest financial statements for accounting unit ID {company_id}.

Steps:
1. Use get_uctovna_jednotka with id={company_id} to get company details and list of idUctovnychZavierok
2. Get the most recent accounting closure using get_uctovna_zavierka
3. For each financial report in idUctovnychVykazov, use get_uctovny_vykaz
4. Use get_sablona to understand the structure of each report type

Summarize the key financial metrics from the reports."""

    @mcp.prompt(description="Compare company financials across multiple years")
    def compare_financials_year_over_year(company_id: int, num_years: int = 3) -> str:
        """Prompt to compare financials across years."""
        return f"""Compare financial statements for accounting unit ID {company_id} over the last {num_years} years.

Steps:
1. Use get_uctovna_jednotka with id={company_id} to get company details and all idUctovnychZavierok
2. For each accounting closure, use get_uctovna_zavierka to get period dates (obdobieOd, obdobieDo)
3. Select closures from the last {num_years} years
4. For each year's closure, get financial reports using get_uctovny_vykaz
5. Use get_uctovny_vykaz_with_labeled_tables for easier data interpretation

Compare and analyze:
- Revenue trends (Tržby)
- Profit/Loss trends (Výsledok hospodárenia)
- Total Assets (SPOLU MAJETOK)
- Total Equity & Liabilities (SPOLU VLASTNÉ IMANIE A ZÁVÄZKY)
- Key financial ratios

Present the comparison in a clear table format with year-over-year changes."""

    @mcp.prompt(description="Extract specific financial metrics (profit, assets, liabilities)")
    def extract_financial_metrics(report_id: int) -> str:
        """Prompt to extract key financial metrics from a report."""
        return f"""Extract key financial metrics from financial report ID {report_id}.

Steps:
1. Use get_uctovny_vykaz_with_labeled_tables with id={report_id} to get labeled data
2. Use get_uctovny_vykaz_table_value_by_labels to search for specific metrics:

Key metrics to extract:
- Total Assets: row_label="SPOLU MAJETOK" or row_code="r. 01" in balance sheet (Súvaha)
- Fixed Assets: row_label="Neobežný majetok" or row_code="A."
- Current Assets: row_label="Obežný majetok" or row_code="B."
- Equity: row_label="Vlastné imanie" or row_code="A."
- Liabilities: row_label="Záväzky" or row_code="B."
- Revenue: row_label="Tržby" in income statement (Výkaz ziskov a strát)
- Net Profit/Loss: row_label="Výsledok hospodárenia" (look for the final one)

Present the extracted metrics in a structured format with values and their context."""

    @mcp.prompt(description="Get balance sheet (Súvaha) data for a company")
    def get_balance_sheet(company_id: int) -> str:
        """Prompt to get balance sheet data."""
        return f"""Extract balance sheet (Súvaha) data for accounting unit ID {company_id}.

Steps:
1. Use get_uctovna_jednotka with id={company_id} to get the latest idUctovnychZavierok
2. Use get_uctovna_zavierka to get the closure with idUctovnychVykazov
3. Use get_uctovny_vykaz_with_labeled_tables to get labeled financial data
4. Filter for tables containing "Súvaha" (Balance Sheet)

Extract and present:
**ASSETS (AKTÍVA)**
- A. Non-current assets (Neobežný majetok)
  - A.I. Intangible assets (Dlhodobý nehmotný majetok)
  - A.II. Tangible assets (Dlhodobý hmotný majetok)
  - A.III. Financial assets (Dlhodobý finančný majetok)
- B. Current assets (Obežný majetok)
  - B.I. Inventory (Zásoby)
  - B.II. Receivables (Pohľadávky)
  - B.III. Financial accounts (Finančné účty)
- TOTAL ASSETS (SPOLU MAJETOK)

**EQUITY & LIABILITIES (PASÍVA)**
- A. Equity (Vlastné imanie)
- B. Liabilities (Záväzky)
- TOTAL EQUITY & LIABILITIES (SPOLU VLASTNÉ IMANIE A ZÁVÄZKY)

Present values for current and previous period side by side."""

    @mcp.prompt(description="Get income statement (Výkaz ziskov a strát) for a company")
    def get_income_statement(company_id: int) -> str:
        """Prompt to get income statement data."""
        return f"""Extract income statement (Výkaz ziskov a strát) data for accounting unit ID {company_id}.

Steps:
1. Use get_uctovna_jednotka with id={company_id} to get the latest idUctovnychZavierok
2. Use get_uctovna_zavierka to get the closure with idUctovnychVykazov
3. Use get_uctovny_vykaz_with_labeled_tables for each report
4. Filter for tables containing "Výkaz ziskov a strát" (Income Statement)

Extract and present key items:
- I. Tržby z predaja tovaru (Revenue from sale of goods)
- II. Tržby z predaja vlastných výrobkov a služieb (Revenue from own products and services)
- A. Náklady vynaložené na obstaranie predaného tovaru (Cost of goods sold)
- B. Spotreba materiálu, energie a ostatných neskladovateľných dodávok (Material and energy costs)
- * Pridaná hodnota (Added value)
- D. Osobné náklady (Personnel costs)
- *** Výsledok hospodárenia z hospodárskej činnosti (Operating profit/loss)
- **** Výsledok hospodárenia za účtovné obdobie (Net profit/loss for period)

Present values for current and previous period with comparison."""

    # =========================================================================
    # Change Tracking & Monitoring Prompts
    # =========================================================================

    @mcp.prompt(description="Analyze changes in accounting units over a period")
    def analyze_changes(start_date: str, end_date: str | None = None) -> str:
        """Prompt to analyze changes in accounting units."""
        end_info = f" up to {end_date}" if end_date else ""
        return f"""Analyze changes in accounting units since {start_date}{end_info}.

Steps:
1. Use get_uctovne_jednotky with zmenene_od={start_date} to get changed entity IDs
2. Use get_zostavajuce_id_uctovne_jednotky to understand the total count
3. For a sample of entities, use get_uctovna_jednotka to examine the changes
4. Optionally examine related accounting closures and financial reports

Provide a summary of:
- Total number of changed entities
- Types of changes observed
- Any notable patterns"""

    @mcp.prompt(description="Monitor new financial statements filed since a date")
    def monitor_new_filings(since_date: str) -> str:
        """Prompt to monitor new financial statement filings."""
        return f"""Find all new financial statements filed since {since_date}.

Steps:
1. Use get_uctovne_zavierky with zmenene_od={since_date} to get new/updated closures
2. Use get_zostavajuce_id_uctovne_zavierky to get the total count
3. For a sample, use get_uctovna_zavierka to get closure details
4. Use get_uctovna_jednotka to get the company information

Provide a summary:
- Total number of new filings
- Breakdown by closure type (riadna, mimoriadna, priebezna)
- List of companies with new filings (name, IČO, filing date)

This is useful for monitoring competitors or market activity."""

    @mcp.prompt(description="Track a specific company for recent changes")
    def track_company_changes(ico: str, since_date: str = "2024-01-01") -> str:
        """Prompt to track changes for a specific company."""
        return f"""Track all changes for company with IČO {ico} since {since_date}.

Steps:
1. Use get_uctovne_jednotky with ico={ico} and zmenene_od={since_date}
2. Get company details using get_uctovna_jednotka
3. Check all accounting closures in idUctovnychZavierok
4. For each closure, get details and check modification dates
5. Check annual reports using get_vyrocne_spravy

Report on:
- Company basic info changes (address, legal form, etc.)
- New financial statements filed
- New annual reports
- Timeline of all changes

This is useful for due diligence or ongoing company monitoring."""

    # =========================================================================
    # Document & Download Prompts
    # =========================================================================

    @mcp.prompt(description="Get all downloadable documents for a company")
    def get_company_documents(company_id: int) -> str:
        """Prompt to get all downloadable documents for a company."""
        return f"""Get all downloadable documents for accounting unit ID {company_id}.

Steps:
1. Use get_uctovna_jednotka with id={company_id} to get company details
2. For each idUctovnychZavierok, use get_uctovna_zavierka
3. For each financial report, use get_uctovny_vykaz and note prilohy (attachments)
4. Use get_financial_report_pdf_url to get PDF URLs for each report
5. Use get_attachment_url for any attachments
6. Check for annual reports using idVyrocnychSprav

Compile a list of all available documents:
- Financial report PDFs (with download URLs)
- Attachments to financial reports
- Annual reports (Výročné správy)

Present as a downloadable document catalog with URLs."""

    @mcp.prompt(description="Download annual reports (Výročné správy) for a company")
    def get_annual_reports(company_id: int) -> str:
        """Prompt to get annual reports for a company."""
        return f"""Get all annual reports (Výročné správy) for accounting unit ID {company_id}.

Steps:
1. Use get_uctovna_jednotka with id={company_id} to get idVyrocnychSprav list
2. For each annual report ID, use get_vyrocna_sprava to get details
3. Note the prilohy (attachments) which contain the actual report files
4. Use get_attachment_url for each attachment to get download URLs

Present:
- List of annual reports with years/periods
- Report types and status
- Download URLs for all attachments

Annual reports contain narrative information about company strategy,
management discussion, and other qualitative information."""

    # =========================================================================
    # Template & Structure Prompts
    # =========================================================================

    @mcp.prompt(description="Explore financial report template structure")
    def explore_template(template_id: int) -> str:
        """Prompt to explore a financial report template."""
        return f"""Explore the structure of financial report template ID {template_id}.

Steps:
1. Use get_sablona with id={template_id} to get the full template details
2. Analyze the table structures, headers, and row definitions
3. Explain what data each table contains and how it should be interpreted

Provide a clear explanation of the template structure and what financial data it represents."""

    @mcp.prompt(description="List all available report templates with their purposes")
    def list_all_templates() -> str:
        """Prompt to list all available templates."""
        return """List all available financial report templates and explain their purposes.

Steps:
1. Use get_sablony to get all available templates
2. For each unique template type, use get_sablona to get structure details
3. Categorize templates by type

Present:
- Template ID, name, and applicable regulation (predpis)
- Validity period (platnostOd, platnostDo)
- Template type/purpose:
  - Súvaha (Balance Sheet) - for various entity types
  - Výkaz ziskov a strát (Income Statement)
  - Poznámky (Notes to financial statements)
  - Prehľad peňažných tokov (Cash flow statement)
  - Prehľad zmien vlastného imania (Statement of changes in equity)

This helps understand which templates apply to different company types."""

    # =========================================================================
    # Classifier & Reference Data Prompts
    # =========================================================================

    @mcp.prompt(description="Get all Slovak regions and districts hierarchy")
    def get_location_hierarchy() -> str:
        """Prompt to get Slovak administrative divisions."""
        return """Get the complete hierarchy of Slovak administrative divisions.

Steps:
1. Use get_kraje to get all regions (kraje)
2. Use get_okresy to get all districts (okresy) with their parent regions
3. Optionally use get_sidla for settlements (this is a large dataset)

Present as a hierarchical structure:
- Bratislavský kraj
  - Okres Bratislava I
  - Okres Bratislava II
  - ...
- Trnavský kraj
  - Okres Trnava
  - ...
(etc.)

This is useful for geographic analysis of companies."""

    @mcp.prompt(description="Get all legal forms with explanations")
    def get_legal_forms_explained() -> str:
        """Prompt to get and explain legal forms."""
        return """Get all legal forms (právne formy) and explain what each means.

Steps:
1. Use get_pravne_formy to get all legal form codes
2. Categorize and explain each type

Common categories:
- Business entities (obchodné spoločnosti): s.r.o., a.s., k.s., v.o.s.
- State/public organizations: príspevkové organizácie, štátne podniky
- Non-profits: občianske združenia, nadácie
- Individual entrepreneurs: fyzické osoby - podnikatelia
- Foreign entities: organizačné zložky zahraničných osôb

Present with codes, Slovak names, and English translations/explanations."""

    @mcp.prompt(description="Explore SK NACE industry classification codes")
    def explore_sk_nace(section: str | None = None) -> str:
        """Prompt to explore SK NACE codes."""
        section_filter = f" focusing on section {section}" if section else ""
        return f"""Explore SK NACE (economic activity classification) codes{section_filter}.

Steps:
1. Use get_sk_nace to get all SK NACE codes
2. Organize by main sections (A-U)

SK NACE Main Sections:
- A: Agriculture, forestry and fishing
- B: Mining and quarrying
- C: Manufacturing
- D: Electricity, gas, steam supply
- E: Water supply, sewerage, waste
- F: Construction
- G: Wholesale and retail trade
- H: Transportation and storage
- I: Accommodation and food service
- J: Information and communication
- K: Financial and insurance activities
- L: Real estate activities
- M: Professional, scientific, technical
- N: Administrative and support services
- O: Public administration
- P: Education
- Q: Human health and social work
- R: Arts, entertainment, recreation
- S: Other service activities

Present hierarchical structure with codes and descriptions."""

    # =========================================================================
    # Bulk/Export Prompts
    # =========================================================================

    @mcp.prompt(description="Export basic data for multiple companies")
    def bulk_export_companies(since_date: str, max_companies: int = 100) -> str:
        """Prompt for bulk export of company data."""
        return f"""Export basic data for companies updated since {since_date} (limit: {max_companies}).

Steps:
1. Use get_uctovne_jednotky with zmenene_od={since_date} and max_zaznamov={max_companies}
2. For each company ID, use get_uctovna_jednotka to get details
3. Compile data into a structured format

Export fields for each company:
- id: Internal ID
- ico: Registration number (IČO)
- dic: Tax ID (DIČ)
- nazov: Company name
- pravnaForma: Legal form code
- ulica, cislo, psc, obec: Address
- datumZalozenia: Founding date
- konpi: End of accounting period indicator

Present as a structured table or JSON suitable for further processing.

Note: For large exports, use pagination with pokracovat_za_id."""

    @mcp.prompt(description="Generate company financial summary report")
    def generate_financial_summary(ico: str) -> str:
        """Prompt to generate a comprehensive financial summary."""
        return f"""Generate a comprehensive financial summary report for company with IČO {ico}.

Steps:
1. Use get_uctovne_jednotky with ico={ico} to find the company
2. Use get_uctovna_jednotka to get full company profile
3. Get the last 3 years of financial closures
4. For each closure, use get_uctovny_vykaz_with_labeled_tables
5. Extract key metrics using get_uctovny_vykaz_table_value_by_labels

Generate a report with:

**COMPANY PROFILE**
- Name, IČO, DIČ
- Legal form, SK NACE activity
- Address
- Founding date

**FINANCIAL HIGHLIGHTS (3-year trend)**
| Metric | Year N-2 | Year N-1 | Year N | Change % |
|--------|----------|----------|--------|----------|
| Total Assets | | | | |
| Total Equity | | | | |
| Total Revenue | | | | |
| Net Profit/Loss | | | | |

**KEY RATIOS**
- Debt ratio (Záväzky / Aktíva)
- Equity ratio (Vlastné imanie / Aktíva)
- Profit margin (if revenue available)

**AVAILABLE DOCUMENTS**
- List of downloadable PDFs and attachments

This is a comprehensive report suitable for due diligence or investor review."""
