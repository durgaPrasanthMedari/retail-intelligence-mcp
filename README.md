# Retail Intelligence MCP Server

An MCP (Model Context Protocol) server that connects to Claude Desktop 
to a retail database, enabling natural language querying of business data.

## What it does

Ask Claude questions like:
- "Which SKUs are below 40% sell-through and need markdown?"
- "Get the weather forecast for Milan and tell me which categories to push"
- "Generate an Excel report and email it to the buying team"

## Tools (16 total)

| Tool | Description |
|------|-------------|
| get_sell_through_report | Sell-through % by product/category |
| get_markdown_candidates | Urgency-scored markdown prioritisation |
| get_rate_of_sale | Weekly ROS and weeks cover |
| generate_excel_report | Formatted 3-sheet Excel report |
| get_weather_and_demand_forecast | Open-Meteo API + demand signals |
| scan_fashion_trends | DuckDuckGo web search for trends |
| send_alert_email | Gmail email alerts |
| ... | and 9 more |

## Tech Stack

- Python 3.11 · FastMCP 3.2.4 · SQLite
- Open-Meteo API (weather) · DuckDuckGo Search
- openpyxl (Excel) · smtplib (email)
- Connects to Claude Desktop via stdio transport

## Setup

```bash
python -m venv venv
venv\Scripts\activate.bat    # Windows
pip install fastmcp openpyxl duckduckgo-search python-dotenv
python create_db.py
python server.py
```

## Author

Durga Prasanth Medari — linkedin.com/in/durgaprasanth
