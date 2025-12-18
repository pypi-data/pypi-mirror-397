"""Prompts for the RegisterUZ MCP server."""


def register_prompts(mcp):
    """Register all prompts with the MCP server."""

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

    @mcp.prompt(description="Get company financial reports by tax ID (DIČ)")
    def search_company_by_dic(dic: str) -> str:
        """Prompt to search for company by tax ID."""
        return f"""Search for the company with DIČ (tax ID) {dic} in the Slovak Registry of Financial Statements.

Steps:
1. Use get_uctovne_jednotky with dic={dic} and a recent zmenene_od date (e.g., 2020-01-01) to find the accounting unit ID
2. Use get_uctovna_jednotka to get the company details
3. Get the related accounting closures and financial reports

Please provide a summary of the company's information and financial data."""

    @mcp.prompt(description="Explore financial report template structure")
    def explore_template(template_id: int) -> str:
        """Prompt to explore a financial report template."""
        return f"""Explore the structure of financial report template ID {template_id}.

Steps:
1. Use get_sablona with id={template_id} to get the full template details
2. Analyze the table structures, headers, and row definitions
3. Explain what data each table contains and how it should be interpreted

Provide a clear explanation of the template structure and what financial data it represents."""
