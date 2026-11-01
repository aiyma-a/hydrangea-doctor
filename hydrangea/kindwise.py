"""Plant.id (Kindwise): a second opinion on WHICH plant it is, used before the Gemini guess.

Plant.id is a service trained to recognise plants. It names the species with a score, which Gemini does not.
On the 42 garden photos (autumn, no leaves or flowers) it put Hydrangea paniculata first for 8 of 9 bushes and
Hydrangea arborescens for the 9th. It returned no variety (cultivar) names for any of them, so varieties are
asked from the user instead.
We only trust it when its top answer is one of our supported plants; anything else falls back to Gemini.
"""
import base64
import json
import os
import urllib.error
import urllib.request

URL = "https://plant.id/api/v3/identification?classification_level=all"
MIN_PLANT = 0.5  # "this is a plant" probability below this means no answer
HIGH, MEDIUM = 0.6, 0.35  # species score -> "high" / "medium" / "low"

# The botanical species Plant.id names -> which hydrangea kind (our pruning rules) it is.
HYDRANGEA_KINDS = {"paniculata": "panicle", "arborescens": "smooth", "macrophylla": "bigleaf", "quercifolia": "oakleaf"}
# genus -> our plant key. Prunus is split by species below.
GENUS = {"hydrangea": "hydrangea", "rosa": "rose", "paeonia": "peony", "syringa": "lilac", "tulipa": "tulip", "iris": "iris",
         "malus": "apple", "pyrus": "pear", "vitis": "grape", "ribes": "currant"}
PRUNUS = {"armeniaca": "apricot", "cerasus": "cherry", "avium": "cherry", "domestica": "plum", "cerasifera": "plum"}
RUBUS = {"idaeus": "raspberry"}


class Unavailable(Exception):
    """No key, or the service failed."""


def map_name(latin: str) -> tuple[str | None, str | None]:
    """'Hydrangea paniculata' -> ('hydrangea', 'panicle'). Unknown or unsupported -> (None, None)."""
    words = latin.lower().replace("×", " ").split()
    if not words:
        return None, None
    genus, epithet = words[0], words[1] if len(words) > 1 else ""
    if genus == "prunus":
        return PRUNUS.get(epithet), None
    if genus == "rubus":
        return RUBUS.get(epithet), None
    key = GENUS.get(genus)
    if key == "hydrangea":
        return key, HYDRANGEA_KINDS.get(epithet)
    return key, None


def build_request(jpegs: list[bytes]) -> dict:
    return {"images": ["data:image/jpeg;base64," + base64.b64encode(j).decode() for j in jpegs]}


def parse(data: dict) -> dict | None:
    """The top suggestion, mapped to our plants. None when it is not a plant or not one we support."""
    result = data["result"]
    if result["is_plant"]["probability"] < MIN_PLANT:
        return None
    top = result["classification"]["suggestions"][0]
    key, kind = map_name(top["name"])
    if key is None:
        return None
    p = top["probability"]
    return {"name": top["name"], "key": key, "kind": kind,
            "confidence": "high" if p >= HIGH else "medium" if p >= MEDIUM else "low"}


def identify(jpegs: list[bytes]) -> dict | None:
    key = os.environ.get("KINDWISE_API_KEY", "").strip()  # a stray newline in the secret breaks the HTTP header
    if not key:
        raise Unavailable("no key")
    req = urllib.request.Request(URL, json.dumps(build_request(jpegs)).encode(),
                                 {"Api-Key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return parse(json.load(r))
    except (urllib.error.URLError, KeyError, IndexError, ValueError, TimeoutError, TypeError) as e:
        raise Unavailable(type(e).__name__) from e
