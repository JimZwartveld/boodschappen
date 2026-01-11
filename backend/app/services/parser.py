"""Parser service for Dutch grocery input."""
import re
from dataclasses import dataclass


@dataclass
class ParsedItem:
    """Parsed grocery item."""

    name: str
    qty: float = 1.0
    unit: str | None = None


# Unit normalization map
UNIT_MAP = {
    # Liters
    "l": "L",
    "liter": "L",
    "liters": "L",
    # Milliliters
    "ml": "ml",
    # Grams
    "g": "g",
    "gr": "g",
    "gram": "g",
    # Kilograms
    "kg": "kg",
    "kilo": "kg",
    "kilos": "kg",
}

# Units that should be removed (just quantity indicators)
QUANTITY_ONLY_UNITS = {"stuks", "stuk", "st", "x"}

# Regex patterns
# Match: "2x brood", "3 stuks", "500g", "2L", "800gr"
QUANTITY_PREFIX_PATTERN = re.compile(
    r"^(\d+(?:[.,]\d+)?)\s*(?:(x|stuks?|st)\s+)?(.+)$", re.IGNORECASE
)

# Match: "brood 2x", "melk 2L", "gehakt 500g"
QUANTITY_SUFFIX_PATTERN = re.compile(
    r"^(.+?)\s+(\d+(?:[.,]\d+)?)\s*(x|stuks?|st|l|liter|ml|g|gr|gram|kg|kilo)?$", re.IGNORECASE
)

# Match unit at the end: "500g", "2L"
UNIT_PATTERN = re.compile(r"^(\d+(?:[.,]\d+)?)\s*(l|liter|ml|g|gr|gram|kg|kilo)$", re.IGNORECASE)


def normalize_name(name: str) -> str:
    """Normalize item name for deduplication."""
    # Lowercase, strip, collapse whitespace
    normalized = name.lower().strip()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def parse_single_item(text: str) -> ParsedItem:
    """Parse a single item text into structured data."""
    text = text.strip()
    if not text:
        return ParsedItem(name="", qty=0)

    qty = 1.0
    unit = None
    name = text

    # Try quantity prefix: "2x brood", "3 stuks paprika", "500g gehakt"
    match = QUANTITY_PREFIX_PATTERN.match(text)
    if match:
        num_str = match.group(1).replace(",", ".")
        qty = float(num_str)
        unit_or_x = match.group(2)
        name = match.group(3).strip()

        # Check if the number has a unit attached (like "500g gehakt")
        unit_check = UNIT_PATTERN.match(match.group(1) + (unit_or_x or ""))
        if unit_check:
            qty = float(unit_check.group(1).replace(",", "."))
            unit_raw = unit_check.group(2).lower()
            if unit_raw in UNIT_MAP:
                unit = UNIT_MAP[unit_raw]
        elif unit_or_x and unit_or_x.lower() in QUANTITY_ONLY_UNITS:
            # "x" or "stuks" - just quantity, no unit
            unit = None
    else:
        # Try quantity suffix: "brood 2x", "melk 2L"
        match = QUANTITY_SUFFIX_PATTERN.match(text)
        if match:
            name = match.group(1).strip()
            qty = float(match.group(2).replace(",", "."))
            unit_raw = match.group(3)

            if unit_raw:
                unit_lower = unit_raw.lower()
                if unit_lower in UNIT_MAP:
                    unit = UNIT_MAP[unit_lower]
                elif unit_lower in QUANTITY_ONLY_UNITS:
                    unit = None

    return ParsedItem(name=name, qty=qty, unit=unit)


def parse_items(text: str) -> list[ParsedItem]:
    """
    Parse multiple items from text input.

    Supports:
    - Comma-separated: "brood, melk, eieren"
    - Newline-separated: "brood\\nmelk\\neieren"
    - Mixed: "brood, melk\\neieren"
    - With quantities: "2x brood, melk 2L, 500g gehakt"
    """
    items = []

    # Split by newlines first, then by commas
    lines = text.strip().split("\n")
    for line in lines:
        # Split by comma, but be careful with numbers like "1,5"
        # Use a smarter split that doesn't break "1,5 liter"
        parts = re.split(r",\s*(?![0-9])", line)
        for part in parts:
            part = part.strip()
            if part:
                parsed = parse_single_item(part)
                if parsed.name:
                    items.append(parsed)

    return items
