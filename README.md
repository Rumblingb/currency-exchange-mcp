# 💱 Currency Exchange MCP

[![MCP](https://img.shields.io/badge/MCP-server-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Smithery](https://img.shields.io/badge/Smithery-listed-purple)](https://smithery.ai)

**Real-time exchange rates for AI agents.** Convert currencies, fetch rates, and discover 166 world currencies — all with zero API keys.

## ✨ Features

- **166 currencies** — Every ISO 4217 currency covered
- **Live rates** — Updated daily via [ExchangeRate-API](https://www.exchangerate-api.com)
- **Zero config** — No API key, no signup, works instantly
- **Dual output** — JSON for programmatic use, Markdown for readability
- **Pagination** — Smart offset/limit for large currency lists
- **Production quality** — CHARACTER_LIMIT protection, error-as-result, tool annotations

## 🔧 Tools

| Tool | Description |
|------|-------------|
| `currency_convert` | Convert an amount from one currency to another |
| `currency_rates` | Get all exchange rates for a base currency (paginated) |
| `currency_list` | List available currency codes with USD rates |

### `currency_convert`

```json
{
  "amount": 100,
  "from_currency": "USD",
  "to_currency": "EUR"
}
```

Returns:
```json
{
  "status": "ok",
  "from": "USD",
  "to": "EUR",
  "amount": 100,
  "rate": 0.8499,
  "converted": 84.99,
  "timestamp": "Mon, 11 May 2026 00:02:32 +0000"
}
```

### `currency_rates`

```json
{
  "base": "GBP",
  "limit": 20,
  "offset": 0
}
```

### `currency_list`

```json
{
  "search": "EU"
}
```

Returns currencies containing "EU" (EUR, etc.)

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

### With Claude Desktop

```json
{
  "mcpServers": {
    "currency-exchange": {
      "command": "python3",
      "args": ["/path/to/currency-exchange-mcp/server.py"]
    }
  }
}
```

### With Cursor / VS Code

```json
{
  "mcpServers": {
    "currency-exchange": {
      "command": "python3",
      "args": ["server.py"],
      "cwd": "/path/to/currency-exchange-mcp"
    }
  }
}
```

### With Smithery

Click "Install on Smithery" or add via Smithery CLI.

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│          AI Agent (Claude/GPT)      │
└──────────────┬──────────────────────┘
               │ MCP Protocol (stdio JSON-RPC)
┌──────────────▼──────────────────────┐
│     Currency Exchange MCP Server     │
│  ┌─────────┐ ┌────────┐ ┌────────┐ │
│  │convert  │ │ rates  │ │  list  │ │
│  └────┬────┘ └───┬────┘ └───┬────┘ │
│       └──────────┴──────────┘       │
│                  │                   │
└──────────────────┼───────────────────┘
                   │ HTTPS
┌──────────────────▼───────────────────┐
│    open.er-api.com (ExchangeRate)    │
│    166 currencies · Free · Daily     │
└──────────────────────────────────────┘
```

## 💰 Pricing

| Tier | Price | Limits |
|------|-------|--------|
| **Free** | $0 | 50 queries/month |
| **Pro** | $19/mo | Unlimited queries, priority support |
| **Enterprise** | $99/mo | Custom SLA, dedicated instance |

[Subscribe to Pro →](https://buy.stripe.com/5kQ3cxflRabW9PW1AD1oI0r)

## 🛠️ Development

```bash
# Install deps
pip install -r requirements.txt

# Run locally
python3 server.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python3 server.py
```

## 📚 Quality Standards

This MCP server follows production-quality patterns:

- ✅ **Tool annotations** — `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`
- ✅ **Service-prefixed naming** — `currency_convert`, `currency_rates`, `currency_list`
- ✅ **Dual response format** — JSON (default) + Markdown
- ✅ **Pagination contract** — `{total, count, offset, items, has_more, next_offset}`
- ✅ **Error as result** — Errors inside response with `isError: true`, never thrown exceptions
- ✅ **CHARACTER_LIMIT truncation** — Response truncated with guidance on pagination/filters
- ✅ **Lifespan management** — `httpx.AsyncClient` with proper cleanup

## 📄 License

MIT — build on it, sell it, improve it.

## 🔗 Related

- [MCP Server Directory](https://rumblingb.github.io/mcp-directory/) — Browse 36+ MCP servers
- [Jack's Toolbox](https://rumblingb.github.io/jacks-toolbox/) — Full product suite
- [AgentPay](https://rumblingb.github.io/Agentpay-landing/) — Agent infrastructure
