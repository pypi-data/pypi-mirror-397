import os
import re
from mcp.server.fastmcp import FastMCP
from mcp.types import Resource

# Create an MCP server
mcp = FastMCP("fmcmcpkd", json_response=True)

# --- Helpers ---

def _get_fmc_file(fmc_name: str) -> str:
    """Resolve FMC name (like 'US FMC', 'HQ', or 'US') to a file path in FMC_DIR, loosely matching filenames"""
    fmc_dir = os.environ.get("FMC_DIR")
    if not fmc_dir or not os.path.isdir(fmc_dir):
        raise FileNotFoundError("FMC_DIR not set or directory missing")

    base = fmc_name.strip().lower().replace(" ", "_")

    if base in ("hq", "hq_fmc"):
        base = "us_fmc"
    elif base == "us":
        base = "us_fmc"

    candidates = [
        os.path.join(fmc_dir, fname)
        for fname in os.listdir(fmc_dir)
        if fname.endswith(".txt") and base in fname.lower()
    ]

    if not candidates:
        raise FileNotFoundError(f"No FMC file found for {fmc_name}")

    candidates.sort(key=os.path.getmtime, reverse=True)
    return candidates[0]


def _read_fmc_file(fmc_name: str) -> str:
    path = _get_fmc_file(fmc_name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _read_fmc_sections(fmc_name: str) -> dict:
    content = _read_fmc_file(fmc_name)
    sections = re.split(r"===\s*(.*?)\s*===", content)
    parsed = {}
    for i in range(1, len(sections), 2):
        header = sections[i].strip().lower()
        body = sections[i+1].strip()
        parsed[header] = body
    return parsed


# --- Dispatcher Tool ---

@mcp.tool(name="get_fmc_info")
def get_fmc_info(fmc_name: str, section_name: str) -> str:
    try:
        sections = _read_fmc_sections(fmc_name)
    except FileNotFoundError as e:
        return str(e)

    # alias mapping
    aliases = {
        "fmc network objects": "fmc objects",
        "network objects": "fmc objects",
        "objects": "fmc objects",
    }

    normalized = section_name.lower()
    normalized = aliases.get(normalized, normalized)

    print(f"[DEBUG] Requested section '{section_name}' normalized to '{normalized}' for FMC '{fmc_name}'")

    # fuzzy fallback
    if normalized not in sections:
        for key in sections.keys():
            if normalized in key or key in normalized:
                print(f"[DEBUG] Fuzzy matched '{normalized}' to '{key}'")
                return sections[key]

    return sections.get(normalized, f"Section '{section_name}' not found in {fmc_name}")


# --- Auto-generated Section Tools ---

SECTION_NAMES = [
    "FMC Server Version",
    "Prefilter Policies",
    "Access Policies",
    "NAT Polices",
    "FMC Objects",
    "FMC Network Groups",
    "FMC Network Objects",  # alias tool
]

for section in SECTION_NAMES:
    func_name = f"get_{section.lower().replace(' ', '_')}"
    @mcp.tool(name=func_name)
    def generated_tool(fmc_name: str, section_name=section.lower()) -> str:
        return get_fmc_info(fmc_name, section_name)
    globals()[func_name] = generated_tool


# --- Resource: raw FMC file ---

@mcp.resource("file://fmc_raw")
def fmc_raw() -> Resource:
    try:
        fmc_dir = os.environ.get("FMC_DIR")
        if not fmc_dir or not os.path.isdir(fmc_dir):
            raise FileNotFoundError("FMC_DIR not set or directory missing")

        candidates = [
            os.path.join(fmc_dir, fname)
            for fname in os.listdir(fmc_dir)
            if fname.endswith(".txt")
        ]
        if not candidates:
            raise FileNotFoundError("No FMC files found in FMC_DIR")

        candidates.sort(key=os.path.getmtime, reverse=True)
        latest_file = candidates[0]

        with open(latest_file, "r", encoding="utf-8") as f:
            data = f.read()
        name = os.path.basename(latest_file)

    except FileNotFoundError as e:
        data = str(e)
        name = "Missing FMC"

    return Resource(
        uri="file://fmc_raw",
        name=f"{name} FMC Raw Output",
        description=f"Full FMC text output file ({name})",
        mimeType="text/plain",
        data=data,
    )


# --- Entrypoint ---

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()