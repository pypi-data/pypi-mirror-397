import os
import re
from typing import Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("fmcmcpkd", json_response=True)

FMC_DIR = os.environ.get("FMC_DIR")
print("FMC_DIR is:", os.environ.get("FMC_DIR"))

def _map_fmc_alias(fmc_name: str) -> str:
    """Map common FMC aliases to their canonical names."""
    alias_mappings = {
        # Test Aliases
        "ny": "NewYork-FMC",
        "nyc": "NewYork-FMC",
        "newyork": "NewYork-FMC",
        "new york": "NewYork-FMC",
        # ATH Aliases
        "ath": "Athens-FMC",
        "athens": "Athens-FMC",
        # US FMC Aliases
        "hq": "US-FMC",
        "b1": "US-FMC",
        "b4": "US-FMC",
        "b5": "US-FMC",
        "b6": "US-FMC",
        # IRE FMC Aliases
        "ire": "IRE-FMC",
        "ireland": "IRE-FMC",
        # GER FMC Aliases
        "ger": "GER-FMC",
        "germany": "GER-FMC",
        "gmbh": "GER-FMC"
    }
    
    # Normalize input for lookup
    normalized = fmc_name.strip().lower().replace(" ", "").replace("-", "").replace("_", "")
    
    # Check if there's a direct alias match
    for alias, canonical in alias_mappings.items():
        alias_normalized = alias.replace(" ", "").replace("-", "").replace("_", "")
        if normalized == alias_normalized:
            return canonical
    
    # Return original if no alias found
    return fmc_name

def _read_fmc_sections(fmc_name: Optional[str] = None) -> dict:
    """Read FMC file and split into sections by headers."""
    if not FMC_DIR or not os.path.isdir(FMC_DIR):
        return {}

    if fmc_name:
        fmc_name = _map_fmc_alias(fmc_name)
        base = fmc_name.strip().lower().replace(" ", "").replace("-", "").replace("_", "")
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

def _map_prefix_to_fmc(object_name: str) -> Optional[str]:
    """Map object name prefixes to FMC names for convenience."""
    prefix_mappings = {
        "ATH-": "Athens-FMC",
        "HQ-": "US-FMC",
        "IRE-": "IRE-FMC",
        "GER-": "GER-FMC",
        # Add more prefixes as needed
    }
    
    object_upper = object_name.upper()
    for prefix, fmc_name in prefix_mappings.items():
        if object_upper.startswith(prefix):
            return fmc_name
    
    return None

# --- Raw FMC file tool ---
@mcp.tool()
def get_fmc_raw(fmc_name: str) -> str:
    """Return the entire raw FMC text file for the given FMC.
    Use this tool as a fallback when a specific section or object lookup fails.
    LLM routing hint:
    * If you see raw FMC text returned, do NOT echo the whole file.
    * Instead, search the text for the requested section or object and extract the relevant details.
    * NEVER invent or guess values."""
    fmc_name = _map_fmc_alias(fmc_name)
    path = os.path.join(FMC_DIR, f"{fmc_name}.txt")
    if not os.path.exists(path):
        return f"FMC file '{fmc_name}' not found"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# --- Object IP lookup with fallback ---
@mcp.tool()
def get_object_ip(object_name: str, fmc_name: Optional[str] = None) -> str:
    """Use this tool when asked 'what IP does <object_name> correspond to?'.
    - Primary behavior: Looks up a single FMC object by name in the 'FMC Objects' section and returns its Value (IP/subnet).
    - If not found, automatically fall back to returning the full FMC file via get_fmc_raw.
    LLM routing hint:
    * If you see raw FMC text returned, search it for the object name and extract the 'Value'.
    * If no match exists even in the raw file, respond clearly: "Object <name> not found in FMC <fmc_name>."
    * NEVER invent or guess IP addresses."""
    if fmc_name:
        target_fmc = _map_fmc_alias(fmc_name)
    else:
        prefix_mapped = _map_prefix_to_fmc(object_name)
        target_fmc = _map_fmc_alias(prefix_mapped) if prefix_mapped else None
    sections = _read_fmc_sections(target_fmc)
    objects = sections.get("FMC Objects", "")
    pattern = rf"Name:\s*{re.escape(object_name)}\s*,\s*Type:\s*\w+\s*,\s*Value:\s*([^\n]+)"
    matches = re.findall(pattern, objects)
    if matches:
        return ", ".join(m.strip() for m in matches)
    if target_fmc:
        return get_fmc_raw(target_fmc)
    return f"Object '{object_name}' not found and no FMC specified"

# --- Access Policies ---
@mcp.tool()
def get_access_policies(fmc_name: Optional[str] = None) -> str:
    """Use this tool when asked 'show access policies' or 'get access rules'.
    - Primary behavior: Returns the 'Access Policies' section.
    - Fallback: If not found, return full FMC file for parsing."""
    if fmc_name:
        fmc_name = _map_fmc_alias(fmc_name)
    sections = _read_fmc_sections(fmc_name)
    policies = sections.get("Access Policies", "")
    if policies:
        return policies
    if fmc_name:
        return get_fmc_raw(fmc_name)
    return "Access Policies not found and no FMC specified"

# --- Prefilter Policies ---
@mcp.tool()
def get_prefilter_policies(fmc_name: Optional[str] = None) -> str:
    """Use this tool when asked 'show prefilter policies' or 'get prefilter rules'.
    - Primary behavior: Returns the 'Prefilter Policies' section.
    - Fallback: If not found, return full FMC file for parsing."""
    if fmc_name:
        fmc_name = _map_fmc_alias(fmc_name)
    sections = _read_fmc_sections(fmc_name)
    policies = sections.get("Prefilter Policies", "")
    if policies:
        return policies
    if fmc_name:
        return get_fmc_raw(fmc_name)
    return "Prefilter Policies not found and no FMC specified"

# --- NAT Policies ---
@mcp.tool()
def get_nat_policies(fmc_name: Optional[str] = None) -> str:
    """Use this tool when asked 'show NAT policies' or 'get NAT rules'.
    - Primary behavior: Returns the 'NAT Policies' section.
    - Fallback: If not found, return full FMC file for parsing."""
    if fmc_name:
        fmc_name = _map_fmc_alias(fmc_name)
    sections = _read_fmc_sections(fmc_name)
    policies = sections.get("NAT Policies", "")
    if policies:
        return policies
    if fmc_name:
        return get_fmc_raw(fmc_name)
    return "NAT Policies not found and no FMC specified"

# --- Network Objects ---
@mcp.tool()
def get_network_objects(fmc_name: Optional[str] = None) -> str:
    """Use this tool when asked 'show all FMC objects' or 'list network objects'.
    - Primary behavior: Returns the 'FMC Objects' section.
    - Fallback: If not found, return full FMC file for parsing."""
    if fmc_name:
        fmc_name = _map_fmc_alias(fmc_name)
    sections = _read_fmc_sections(fmc_name)
    objects = sections.get("FMC Objects", "")
    if objects:
        return objects
    if fmc_name:
        return get_fmc_raw(fmc_name)
    return "FMC Objects not found and no FMC specified"

# --- Network Groups ---
@mcp.tool()
def get_network_groups(fmc_name: Optional[str] = None) -> str:
    """Use this tool when asked 'show network groups' or 'list FMC groups'.
    - Primary behavior: Returns the 'FMC Network Groups' section.
    - Fallback: If not found, return full FMC file for parsing."""
    if fmc_name:
        fmc_name = _map_fmc_alias(fmc_name)
    sections = _read_fmc_sections(fmc_name)
    groups = sections.get("FMC Network Groups", "")
    if groups:
        return groups
    if fmc_name:
        return get_fmc_raw(fmc_name)
    return "FMC Network Groups not found and no FMC specified"

# --- Entrypoint ---
def main():
    print("Starting MCP server on stdio...")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()