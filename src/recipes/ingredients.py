"""Best-effort extraction of a shopping-list-friendly name from an ingredient line.

Ingredient lines in the catalog are free text such as ``"600ml Double Cream"`` or
``"1 Head of Broccoli"`` with no structured quantity/unit/name fields. :func:`export_name`
strips a recognised leading quantity (and unit, and connector word such as "of") so the
recipe export feature can list ingredient names without quantities. When no confidently
recognised quantity prefix is present, the original text is returned unchanged rather than
risking an incorrect edit.
"""

import re

_NUMBER = r"\d+(?:[.,/]\d+)?"
_QUANTITY = rf"(?:~\s*)?(?:half|{_NUMBER}(?:\s*-\s*{_NUMBER})?)"
_ATTACHED_UNIT = r"(?:g|kg|ml|l|cl|cm)\b"
_QUANTITY_WITH_ATTACHED_UNIT = (
    rf"(?:~\s*)?{_NUMBER}(?:{_ATTACHED_UNIT})?(?:\s*-\s*{_NUMBER})?{_ATTACHED_UNIT}"
)
_UNIT_WORD = (
    r"(?:tablespoons?|tbsps?|teaspoons?|tsps?|cups?|tins?|cans?|cloves?|slices?|"
    r"rashers?|heads?|balls?|bunc(?:h|hes)|sprigs?|packets?|jars?|sheets?|"
    r"pinch(?:es)?|handfuls?|dash(?:es)?|knobs?|splash(?:es)?|dollops?|drizzles?|"
    r"sprinkles?|glugs?|squeezes?|scoops?|wedges?|litres?|liters?|sticks?)"
)
# Words that themselves imply an (unmeasured) quantity, without a preceding number,
# e.g. "Pinch of Salt" or "Handful Fresh Basil".
_STANDALONE_UNIT_WORD = (
    r"(?:pinch(?:es)?|handfuls?|dash(?:es)?|knobs?|splash(?:es)?|dollops?|drizzles?|"
    r"sprinkles?|glugs?|squeezes?|scoops?|wedges?|couples?|several|a\s+few)"
)
_PARENTHETICAL = r"(?:\([^)]*\)\s*)?"
_CONNECTOR = r"(?:of|the|an?)\s+"

_QUANTITY_PREFIX = re.compile(
    rf"""^\s*
    (?:
        {_QUANTITY_WITH_ATTACHED_UNIT}\s*{_PARENTHETICAL}
        |
        {_QUANTITY}\s+{_UNIT_WORD}\s*{_PARENTHETICAL}
        |
        (?:a|an)?\s*{_STANDALONE_UNIT_WORD}\s*{_PARENTHETICAL}
        |
        {_QUANTITY}\s+
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)
_CONNECTOR_PREFIX = re.compile(rf"^{_CONNECTOR}", re.IGNORECASE)


def export_name(ingredient: str) -> str:
    """Return `ingredient` with any recognised leading quantity/unit removed.

    Falls back to the original (stripped) text whenever no leading quantity is
    recognised, so ingredients with no quantity (e.g. "Salt and Pepper (To Taste)")
    are returned unchanged.
    """
    text = ingredient.strip()
    match = _QUANTITY_PREFIX.match(text)
    if not match:
        return text
    remainder = text[match.end() :].strip()
    connector_match = _CONNECTOR_PREFIX.match(remainder)
    if connector_match:
        remainder = remainder[connector_match.end() :].strip()
    return remainder if remainder else text
