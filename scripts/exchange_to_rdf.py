"""Convert an ArchiMate Model Exchange Format file to RDF (canonical form).

Every element becomes a resource of its am: class, every relationship a
resource of its relationship class with am:source and am:target (the
canonical form; materialize the direct-predicate sugar layer separately if
you want it). Multilingual names and documentation become language-tagged
rdfs:label and dcterms:description. Views become am:View with am:shows.

Types keep their exchange-format names: 3.2 layer-specific types are
subclasses of the 4.0 layer-generic types in archimate-profile-3.2.ttl,
so the output validates against the 4.0 matrix without any translation.

Usage:  python scripts/exchange_to_rdf.py <model.xml> <output.ttl> [base-uri]
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

NS = "{http://www.opengroup.org/xsd/archimate/3.0/}"
XSI = "{http://www.w3.org/2001/XMLSchema-instance}"
XML = "{http://www.w3.org/XML/1998/namespace}"

ACCESS_TYPE = {
    "Read": "am:ReadAccess",
    "Write": "am:WriteAccess",
    "ReadWrite": "am:ReadWriteAccess",
    "Access": "am:UnspecifiedAccess",
}


def _lit(value: str, lang: str = "") -> str:
    out = value.replace("\\", "\\\\").replace('"', '\\"')
    out = out.replace("\r", "").replace("\n", "\\n")
    return f'"{out}"' + (f"@{lang}" if lang else "")


def _texts(node: ET.Element, tag: str) -> list[tuple[str, str]]:
    """(lang, text) pairs for all <tag> children, default language en."""
    out = []
    for child in node.findall(NS + tag):
        text = (child.text or "").strip()
        if text:
            out.append((child.attrib.get(XML + "lang", "en"), text))
    return out


def convert(source: Path, base: str) -> str:
    tree = ET.parse(source)
    root = tree.getroot()

    lines = [
        "@prefix am:   <https://purl.org/archimate#> .",
        f"@prefix m:    <{base}> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix dcterms: <http://purl.org/dc/terms/> .",
        "",
        "# GENERATED FILE; do not edit by hand.",
        f"# Source: {source.name} (ArchiMate Model Exchange Format)",
        f"# Generator: scripts/{Path(__file__).name}, {date.today().isoformat()}",
        "",
    ]

    elements = root.find(NS + "elements")
    n_el = 0
    for el in elements.findall(NS + "element") if elements is not None else []:
        ident = el.attrib.get("identifier")
        typ = el.attrib.get(XSI + "type")
        if not ident or not typ:
            continue
        n_el += 1
        pairs = [f"a am:{typ}"]
        for lang, text in _texts(el, "name"):
            pairs.append(f"rdfs:label {_lit(text, lang)}")
        for lang, text in _texts(el, "documentation"):
            pairs.append(f"dcterms:description {_lit(text, lang)}")
        pairs.append(f"am:identifier {_lit(ident)}")
        lines.append(f"m:{ident}\n    " + " ;\n    ".join(pairs) + " .\n")

    rels = root.find(NS + "relationships")
    n_rel = 0
    for rel in rels.findall(NS + "relationship") if rels is not None else []:
        ident = rel.attrib.get("identifier")
        typ = rel.attrib.get(XSI + "type")
        src = rel.attrib.get("source")
        tgt = rel.attrib.get("target")
        if not (ident and typ and src and tgt):
            continue
        n_rel += 1
        pairs = [f"a am:{typ}", f"am:source m:{src}", f"am:target m:{tgt}",
                 f"am:identifier {_lit(ident)}"]
        for lang, text in _texts(rel, "name"):
            pairs.append(f"rdfs:label {_lit(text, lang)}")
        access = rel.attrib.get("accessType")
        if typ == "Access":
            pairs.append("am:accessType "
                         + ACCESS_TYPE.get(access or "Access", "am:UnspecifiedAccess"))
        modifier = rel.attrib.get("modifier")
        if typ == "Influence" and modifier:
            pairs.append(f"am:influenceStrength {_lit(modifier)}")
        if typ == "Association" and rel.attrib.get("isDirected"):
            pairs.append(f"am:isDirected {rel.attrib['isDirected'].lower()}")
        lines.append(f"m:{ident}\n    " + " ;\n    ".join(pairs) + " .\n")

    n_views = 0
    views = root.find(NS + "views")
    diagrams = views.find(NS + "diagrams") if views is not None else None
    for view in diagrams.findall(NS + "view") if diagrams is not None else []:
        ident = view.attrib.get("identifier")
        if not ident:
            continue
        n_views += 1
        pairs = ["a am:View", f"am:identifier {_lit(ident)}"]
        for lang, text in _texts(view, "name"):
            pairs.append(f"rdfs:label {_lit(text, lang)}")
        shown = {node.attrib.get("elementRef")
                 for node in view.iter(NS + "node") if node.attrib.get("elementRef")}
        for ref in sorted(shown):
            pairs.append(f"am:shows m:{ref}")
        lines.append(f"m:{ident}\n    " + " ;\n    ".join(pairs) + " .\n")

    lines.insert(8, f"# {n_el} elements, {n_rel} relationships, {n_views} views.")
    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    source, out = Path(sys.argv[1]), Path(sys.argv[2])
    base = sys.argv[3] if len(sys.argv) > 3 else "https://example.org/archisurance/"
    ttl = convert(source, base)
    out.write_text(ttl, encoding="utf-8", newline="\n")
    print(f"written: {out} ({len(ttl.splitlines())} lines)")


if __name__ == "__main__":
    main()
