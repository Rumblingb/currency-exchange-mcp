#!/usr/bin/env python3
"""
Currency Exchange MCP Server — Real-time exchange rates via open.er-api.com
Free, no API key required. 166 currencies. Updates daily.
"""
import json
from mcp.server.lowlevel import Server, stdio_server
import httpx

CHARACTER_LIMIT = 25000
API_BASE = "https://open.er-api.com/v6"

server = Server("currency-exchange")

# ── Tool: currency_convert ────────────────────────────────────────────
@server.tool(
    name="currency_convert",
    description="Convert an amount from one currency to another using live exchange rates. Returns the converted amount, rate, and timestamp.",
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
    input_schema={
        "type": "object",
        "properties": {
            "amount": {
                "type": "number",
                "description": "The amount to convert"
            },
            "from_currency": {
                "type": "string",
                "description": "Source currency code (e.g., 'USD', 'EUR', 'GBP')"
            },
            "to_currency": {
                "type": "string",
                "description": "Target currency code (e.g., 'JPY', 'CAD', 'AUD')"
            },
            "response_format": {
                "type": "string",
                "enum": ["json", "markdown"],
                "description": "Output format: 'json' for programmatic use, 'markdown' for readability",
                "default": "json"
            }
        },
        "required": ["amount", "from_currency", "to_currency"]
    }
)
async def currency_convert(
    amount: float,
    from_currency: str,
    to_currency: str,
    response_format: str = "json"
) -> str:
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{API_BASE}/latest/{from_currency}")
            resp.raise_for_status()
            data = resp.json()

        if data.get("result") != "success":
            return json.dumps({
                "status": "error",
                "error": "API returned unsuccessful result",
                "isError": True,
                "next_steps": ["Verify currency code is valid", "Try again later"]
            })

        rates = data.get("rates", {})
        if to_currency not in rates:
            return json.dumps({
                "status": "error",
                "error": f"Currency '{to_currency}' not found. Use currency_list to see available currencies.",
                "isError": True,
                "next_steps": ["Check currency code spelling", "Use currency_list tool to see valid codes"]
            })

        rate = rates[to_currency]
        converted = round(amount * rate, 4)

        result = {
            "status": "ok",
            "from": from_currency,
            "to": to_currency,
            "amount": amount,
            "rate": rate,
            "converted": converted,
            "timestamp": data.get("time_last_update_utc", "unknown")
        }

        if response_format == "markdown":
            return (
                f"# Currency Conversion\n\n"
                f"**{amount:,.4f} {from_currency}** = **{converted:,.4f} {to_currency}**\n\n"
                f"| Field | Value |\n|-------|-------|\n"
                f"| Rate | 1 {from_currency} = {rate} {to_currency} |\n"
                f"| Updated | {result['timestamp']} |\n"
            )
        return json.dumps(result, indent=2)

    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "error": f"Exchange rate API returned {e.response.status_code}",
            "isError": True,
            "next_steps": ["Verify base currency code is valid", "Try again later"]
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e),
            "isError": True,
            "next_steps": ["Check network connectivity", "Retry the request"]
        })


# ── Tool: currency_rates ──────────────────────────────────────────────
@server.tool(
    name="currency_rates",
    description="Get all exchange rates for a base currency. Returns rates for all 166 supported currencies.",
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
    input_schema={
        "type": "object",
        "properties": {
            "base": {
                "type": "string",
                "description": "Base currency code (e.g., 'USD', 'EUR', 'GBP'). Default: 'USD'",
                "default": "USD"
            },
            "limit": {
                "type": "integer",
                "description": "Max currencies to return (default: 50, max: 166)",
                "default": 50
            },
            "offset": {
                "type": "integer",
                "description": "Pagination offset for listing currencies alphabetically",
                "default": 0
            },
            "response_format": {
                "type": "string",
                "enum": ["json", "markdown"],
                "description": "Output format",
                "default": "json"
            }
        },
        "required": []
    }
)
async def currency_rates(
    base: str = "USD",
    limit: int = 50,
    offset: int = 0,
    response_format: str = "json"
) -> str:
    base = base.upper()
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{API_BASE}/latest/{base}")
            resp.raise_for_status()
            data = resp.json()

        if data.get("result") != "success":
            return json.dumps({
                "status": "error",
                "error": "API returned unsuccessful result",
                "isError": True,
                "next_steps": ["Verify currency code is valid", "Try again later"]
            })

        all_rates = data.get("rates", {})
        sorted_items = sorted(all_rates.items())
        total = len(sorted_items)
        page = sorted_items[offset:offset + limit]
        page_dict = dict(page)

        has_more = offset + limit < total
        next_offset = offset + limit if has_more else 0
        truncated = len(all_rates) > limit

        result = {
            "status": "ok",
            "base": base,
            "total": total,
            "count": len(page_dict),
            "offset": offset,
            "has_more": has_more,
            "next_offset": next_offset,
            "rates": page_dict,
            "timestamp": data.get("time_last_update_utc", "unknown"),
            "truncated": truncated
        }

        result_json = json.dumps(result, indent=2)
        if len(result_json) > CHARACTER_LIMIT:
            half = limit // 2
            page2 = dict(sorted_items[offset:offset + half])
            result["rates"] = page2
            result["count"] = len(page2)
            result["truncated"] = True
            result["_message"] = "Response truncated. Use pagination (offset/limit) or filter to a smaller set."
            return json.dumps(result, indent=2)

        if response_format == "markdown":
            rate_table = "\n".join(
                f"| {code} | {rate} |" for code, rate in page
            )
            m = (
                f"# Exchange Rates (base: {base})\n\n"
                f"Updated: {result['timestamp']}\n"
                f"Total currencies: {total} | Showing: {result['count']} (offset: {offset})\n\n"
                f"| Currency | Rate |\n|----------|------|\n{rate_table}\n\n"
            )
            if has_more:
                m += f"_Use offset={next_offset} for next page._\n"
            return m
        return result_json

    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "error": f"Exchange rate API returned {e.response.status_code}",
            "isError": True,
            "next_steps": ["Verify currency code is valid", "Try again later"]
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e),
            "isError": True,
            "next_steps": ["Check network connectivity", "Retry the request"]
        })


# ── Tool: currency_list ───────────────────────────────────────────────
@server.tool(
    name="currency_list",
    description="List all available currency codes with their current USD exchange rates. Use this to discover valid currency codes.",
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
    input_schema={
        "type": "object",
        "properties": {
            "search": {
                "type": "string",
                "description": "Optional filter: return only currencies whose code contains this string (e.g., 'EU' returns EUR). Case-insensitive."
            },
            "response_format": {
                "type": "string",
                "enum": ["json", "markdown"],
                "description": "Output format",
                "default": "json"
            }
        },
        "required": []
    }
)
async def currency_list(search: str = "", response_format: str = "json") -> str:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{API_BASE}/latest/USD")
            resp.raise_for_status()
            data = resp.json()

        if data.get("result") != "success":
            return json.dumps({
                "status": "error",
                "error": "API returned unsuccessful result",
                "isError": True,
                "next_steps": ["Try again later"]
            })

        all_rates = data.get("rates", {})
        if search:
            search_upper = search.upper()
            filtered = {k: v for k, v in all_rates.items() if search_upper in k}
        else:
            filtered = all_rates

        sorted_items = sorted(filtered.items())
        result = {
            "status": "ok",
            "total_available": len(all_rates),
            "count": len(sorted_items),
            "currencies": {k: v for k, v in sorted_items},
            "timestamp": data.get("time_last_update_utc", "unknown"),
            "search": search if search else None
        }

        result_json = json.dumps(result, indent=2)
        if len(result_json) > CHARACTER_LIMIT and not search:
            # Too large (166 currencies); show first 50 + pagination hint
            result["currencies"] = dict(sorted_items[:50])
            result["count"] = 50
            result["truncated"] = True
            result["_message"] = "Showing first 50 currencies. Use 'search' param to narrow, or use currency_rates with pagination."
            return json.dumps(result, indent=2)

        if response_format == "markdown":
            rate_table = "\n".join(f"| {k} | {v} |" for k, v in sorted_items[:100])
            m = (
                f"# Available Currencies ({len(sorted_items)} shown)\n\n"
                f"Updated: {result['timestamp']}\n\n"
                f"| Code | 1 USD = |\n|------|--------|\n{rate_table}\n"
            )
            if len(sorted_items) > 100:
                m += f"\n_... and {len(sorted_items) - 100} more. Use 'search' to filter._\n"
            return m
        return result_json

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e),
            "isError": True,
            "next_steps": ["Check network connectivity", "Retry the request"]
        })


# ── Entry point ───────────────────────────────────────────────────────
def main():
    import anyio
    async def run():
        async with stdio_server() as streams:
            await server.run(
                streams[0], streams[1],
                server.create_initialization_options()
            )
    anyio.run(run)

if __name__ == "__main__":
    main()
