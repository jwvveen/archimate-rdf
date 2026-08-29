"""Genereer archimate-matrix.ttl uit de machineleesbare 4.0-matrix.

De relatiematrix is data, geen documentatie (principe P3 uit het
ontologievoorstel). Dit script is de enige weg van de bron
(relationships-4.0.xml, overgenomen uit Appendix B.5 van C260) naar de
RDF-vorm; met de hand bijwerken van archimate-matrix.ttl is dus altijd fout.

Per cel ontstaat een am:MatrixCell met:
  * am:sourceType / am:targetType  (de twee concepttypen)
  * am:permitsRelation             (alles uit `relations`, incl. afgeleid)
  * am:permitsDirectRelation       (alleen `direct`: tekenbaar)

Draai vanuit de repo-wortel:  python scripts/generate_matrix_ttl.py
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
XML = REPO / "sources" / "relationships-4.0.xml"
UIT = REPO / "archimate-matrix.ttl"

# Zelfde codering als semanticxl.views.matrix; hier herhaald zodat het
# script ook zonder geinstalleerd pakket draait, met een importcheck die
# drift tussen de twee tabellen direct laat opvallen.
LETTER = {
    "a": "Access", "c": "Composition", "f": "Flow", "g": "Aggregation",
    "i": "Assignment", "n": "Influence", "o": "Association",
    "r": "Realization", "s": "Specialization", "t": "Triggering",
    "v": "Serving",
}


def _check_tegen_pakket() -> None:
    try:
        from semanticxl.views.matrix import _LETTER_TO_REL
    except ImportError:
        return
    if _LETTER_TO_REL != LETTER:
        sys.exit("lettercodering wijkt af van semanticxl.views.matrix; "
                 "maak de tabellen eerst weer gelijk")


def genereer() -> str:
    boom = ET.parse(XML)
    wortel = boom.getroot()
    versie = wortel.attrib.get("version", "4.0")
    bron = wortel.attrib.get("bron", "")

    regels = [
        "@prefix am:   <https://purl.org/archimate#> .",
        "@prefix amm:  <https://purl.org/archimate/matrix#> .",
        "@prefix owl:  <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix dcterms: <http://purl.org/dc/terms/> .",
        "",
        "# GEGENEREERD BESTAND; niet met de hand bewerken.",
        f"# Bron: {XML.name} ({bron})",
        f"# Generator: scripts/{Path(__file__).name}, {date.today().isoformat()}",
        "",
        "<https://purl.org/archimate/matrix>",
        "    a owl:Ontology ;",
        f'    rdfs:label "ArchiMate {versie} relatiematrix"@nl , "ArchiMate {versie} relationship matrix"@en ;',
        f'    dcterms:source "{bron}" ;',
        '    owl:versionInfo "0.1.0-concept" .',
        "",
    ]

    cellen = 0
    permits = 0
    direct = 0
    for src in wortel.findall("source"):
        s = src.attrib.get("concept")
        if not s:
            continue
        for tgt in src.findall("target"):
            t = tgt.attrib.get("concept")
            if not t:
                continue
            alles = sorted({LETTER[ch] for ch in tgt.attrib.get("relations", "")
                            if ch in LETTER})
            tekenbaar = sorted({LETTER[ch] for ch in tgt.attrib.get("direct", "")
                                if ch in LETTER})
            if not alles:
                continue
            cellen += 1
            permits += len(alles)
            direct += len(tekenbaar)
            blok = [f"amm:cell-{s}-{t} a am:MatrixCell ;",
                    f"    am:sourceType am:{s} ;",
                    f"    am:targetType am:{t} ;",
                    "    am:permitsRelation " + " , ".join(f"am:{r}" for r in alles)]
            if tekenbaar:
                blok.append("    am:permitsDirectRelation "
                            + " , ".join(f"am:{r}" for r in tekenbaar))
            regels.append(" ;\n".join(blok) + " .\n")

    regels.insert(10, f"# {cellen} cellen, {permits} permits-, {direct} direct-vermeldingen.")
    return "\n".join(regels)


def main() -> None:
    _check_tegen_pakket()
    ttl = genereer()
    UIT.parent.mkdir(parents=True, exist_ok=True)
    UIT.write_text(ttl, encoding="utf-8", newline="\n")
    print(f"geschreven: {UIT} ({len(ttl.splitlines())} regels)")


if __name__ == "__main__":
    main()
