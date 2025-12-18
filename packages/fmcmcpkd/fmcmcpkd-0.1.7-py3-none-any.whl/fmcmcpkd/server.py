import os
import re
from mcp.server.fastmcp import FastMCP
from mcp.types import Resource

# Create an MCP server
mcp = FastMCP("fmcmcpkd", json_response=True)

# --- Helpers ---

def _get_fmc_file(fmc_name: str) -> str:
    """Resolve FMC name (like 'US FMC') to a file path in FMC_DIR, loosely matching filenames"""
    fmc_dir = os.environ.get("FMC_DIR")
    if not fmc_dir or not os.path.isdir(fmc_dir):
        raise FileNotFoundError("FMC_DIR not set or directory missing")

    # normalize: lower, replace spaces with underscores
    base = fmc_name.lower().replace(" ", "_")

    # scan all txt files in the directory and look for partial matches
    candidates = [
        os.path.join(fmc_dir, fname)
        for fname in os.listdir(fmc_dir)
        if fname.endswith(".txt") and base in fname.lower()
    ]

    if not candidates:
        raise FileNotFoundError(f"No FMC file found for {fmc_name}")

    # pick the most recently modified match
    candidates.sort(key=os.path.getmtime, reverse=True)
    return candidates[0]


def _read_fmc_file(fmc_name: str) -> str:
    """Read the entire FMC file for a given FMC name"""
    path = _get_fmc_file(fmc_name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _read_fmc_sections(fmc_name: str) -> dict:
    """Read FMC file and split into sections by headers"""
    content = _read_fmc_file(fmc_name)
    # Split by section headers === Section Name ===
    sections = re.split(r"=== (.*?) ===", content)
    parsed = {}
    for i in range(1, len(sections), 2):
        header = sections[i].strip()
        body = sections[i+1].strip()
        parsed[header] = body
    return parsed


# --- Dispatcher Tool ---

@mcp.tool()
def get_fmc_info(fmc_name: str, section_name: str) -> str:
    """
    Return a specific section from a given FMC file.
    Example: get_fmc_info("US FMC", "Access Policies")
             get_fmc_info("US", "Access Policies")
    """
    try:
        sections = _read_fmc_sections(fmc_name)
    except FileNotFoundError as e:
        return str(e)
    return sections.get(section_name, f"Section '{section_name}' not found in {fmc_name}")


# --- Auto-generated Section Tools ---

SECTION_NAMES = [
    "FMC Server Version",
    "Prefilter Policies",
    "Access Policies",
    "NAT Policies",
    "FMC Network Objects",
]

for section in SECTION_NAMES:
    def make_tool(section_name: str):
        @mcp.tool()
        def tool(fmc_name: str) -> str:
            """Return a specific FMC section"""
            return get_fmc_info(fmc_name, section_name)
        tool.__name__ = f"get_{section_name.lower().replace(' ', '_')}"
        return tool

    globals()[f"get_{section.lower().replace(' ', '_')}"] = make_tool(section)


# --- Resource: raw FMC file ---

@mcp.resource("file://fmc_raw")
def fmc_raw(fmc_name: str) -> Resource:
    """Return the full FMC file as plain text for a given FMC name"""
    try:
        data = _read_fmc_file(fmc_name)
    except FileNotFoundError as e:
        data = str(e)
    return Resource(
        uri=f"file://{fmc_name}_raw",
        name=f"{fmc_name} FMC Raw Output",
        description=f"Full FMC text output file for {fmc_name}",
        mimeType="text/plain",
        data=data,
    )


# --- Entrypoint ---

def main():
    """Entrypoint for fmcmcpkd"""
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()