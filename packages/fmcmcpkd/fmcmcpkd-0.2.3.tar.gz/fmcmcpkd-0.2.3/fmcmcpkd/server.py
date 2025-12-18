import os
import re
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("fmcmcpkd", json_response=True)

FMC_DIR = os.environ.get("FMC_DIR")

def _read_fmc_sections(fmc_name: str = None) -> dict:
    """Read FMC file and split into sections by headers"""
    if not FMC_DIR or not os.path.isdir(FMC_DIR):
        return {}

    # pick the latest FMC file if no name given
    if fmc_name:
        base = fmc_name.strip().lower().replace(" ", "_")
        candidates = [
            os.path.join(FMC_DIR, fname)
            for fname in os.listdir(FMC_DIR)
            if fname.endswith(".txt") and base in fname.lower()
        ]
    else:
        candidates = [
            os.path.join(FMC_DIR, fname)
            for fname in os.listdir(FMC_DIR)
            if fname.endswith(".txt")
        ]

    if not candidates:
        return {}

    candidates.sort(key=os.path.getmtime, reverse=True)
    path = candidates[0]

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    sections = re.split(r"===\s*(.*?)\s*===", content)
    parsed = {}
    for i in range(1, len(sections), 2):
        header = sections[i].strip()
        body = sections[i+1].strip()
        parsed[header] = body
    return parsed

def _list_fmc_files() -> list[str]:
    """Return all FMC file names in FMC_DIR"""
    if not FMC_DIR or not os.path.isdir(FMC_DIR):
        return []
    return [fname for fname in os.listdir(FMC_DIR) if fname.endswith(".txt")]

# --- New tool: list all FMCs ---
@mcp.tool()
def list_fmcs() -> str:
    """List all available FMCs (based on filenames in FMC_DIR)"""
    files = _list_fmc_files()
    if not files:
        return "No FMC files found in FMC_DIR"
    fmcs = [os.path.splitext(f)[0] for f in files]
    return "Available FMCs:\n" + "\n".join(fmcs)

# --- Separate tools for each section ---

@mcp.tool()
def get_server_version(fmc_name: str = None) -> str:
    """Return FMC Server Version section"""
    return _read_fmc_sections(fmc_name).get("FMC Server Version", "Section not found")

@mcp.tool()
def get_prefilter_policies(fmc_name: str = None) -> str:
    """Return Prefilter Policies section"""
    return _read_fmc_sections(fmc_name).get("Prefilter Policies", "Section not found")

@mcp.tool()
def get_access_policies(fmc_name: str = None) -> str:
    """Return Access Policies section"""
    return _read_fmc_sections(fmc_name).get("Access Policies", "Section not found")

@mcp.tool()
def get_nat_policies(fmc_name: str = None) -> str:
    """Return NAT Policies section"""
    # note: file header may be "NAT Polices"
    return _read_fmc_sections(fmc_name).get("NAT Polices", "Section not found")

@mcp.tool()
def get_network_objects(fmc_name: str = None) -> str:
    """Return FMC Objects section (network objects)"""
    # file header is "FMC Objects"
    return _read_fmc_sections(fmc_name).get("FMC Objects", "Section not found")

@mcp.tool()
def get_network_groups(fmc_name: str = None) -> str:
    """Return FMC Network Groups section"""
    return _read_fmc_sections(fmc_name).get("FMC Network Groups", "Section not found")

# --- Optional generic tool ---
@mcp.tool()
def get_section(name: str, fmc_name: str = None) -> str:
    """Return any FMC section by name"""
    return _read_fmc_sections(fmc_name).get(name, f"Section '{name}' not found")

# --- Entrypoint ---
def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()