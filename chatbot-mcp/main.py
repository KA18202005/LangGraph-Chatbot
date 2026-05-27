from fastmcp import FastMCP

mcp = FastMCP("AsyncMathServer")
NumberInput = int | float | str


# ------------------ HELPER ------------------

def _as_number(x: NumberInput) -> float:
    """Convert a supported input value to float."""
    try:
        return float(x)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid number: {x}") from exc


# ------------------ TOOLS ------------------

@mcp.tool()
async def add(a: NumberInput, b: NumberInput) -> dict[str, float]:
    a, b = _as_number(a), _as_number(b)
    return {"result": a + b}


@mcp.tool()
async def subtract(a: NumberInput, b: NumberInput) -> dict[str, float]:
    a, b = _as_number(a), _as_number(b)
    return {"result": a - b}


@mcp.tool()
async def multiply(a: NumberInput, b: NumberInput) -> dict[str, float]:
    a, b = _as_number(a), _as_number(b)
    return {"result": a * b}


@mcp.tool()
async def divide(a: NumberInput, b: NumberInput) -> dict[str, float]:
    a, b = _as_number(a), _as_number(b)

    if b == 0:
        raise ValueError("Division by zero")

    return {"result": a / b}


@mcp.tool()
async def power(a: NumberInput, b: NumberInput) -> dict[str, float]:
    a, b = _as_number(a), _as_number(b)
    return {"result": a ** b}


@mcp.tool()
async def modulus(a: NumberInput, b: NumberInput) -> dict[str, float]:
    a, b = _as_number(a), _as_number(b)

    if b == 0:
        raise ValueError("Modulus by zero")

    return {"result": a % b}


# ------------------ RUN ------------------

if __name__ == "__main__":
    mcp.run()   # local MCP server