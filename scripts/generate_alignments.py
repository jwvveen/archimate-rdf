"""Genereer archimate-alignments.ttl.

Koppelt de termen van de ArchiMate 4.0-ontologie (https://w3id.org/archimate#)
aan twee eerdere ArchiMate-ontologieën:

* de 3.2-ontologie van Alberto D. Mendoza (https://purl.org/archimate#,
  ontologie https://purl.org/archimate/owl, Apache-2.0);
* bp4mc2 archimate2rdf (http://bp4mc2.org/def/archimate#).

Alleen naar termen die in die bestanden echt bestaan. Regels:

* klasse met dezelfde naam (in kern of 3.2-profiel): skos:exactMatch;
* datatype-eigenschap met dezelfde naam: skos:exactMatch;
* een directe relatie uit de suikerlaag (am:serves) tegenover hun directe
  relatie (serving): skos:closeMatch; bij ons is de relatie zelf een
  resource (am:Serving) en het directe predicaat afgeleid;
* view en gezichtspunt: skos:closeMatch.

De bronnen staan vast op een commit en worden gecached in
sources/.cache/ (niet in git: bp4mc2 heeft geen licentie).

    py scripts/generate_alignments.py
"""
from __future__ import annotations

import urllib.request
from pathlib import Path

import rdflib
from rdflib import OWL, RDF, RDFS

WORTEL = Path(__file__).resolve().parent.parent
MAP = WORTEL
CACHE = MAP / "sources" / ".cache"
UIT = MAP / "archimate-alignments.ttl"
AM = "https://w3id.org/archimate#"

BRONNEN = {
    "mendoza": {
        "ns": "https://purl.org/archimate#",
        "prefix": "am32",
        "naam": "ArchiMate 3.2 ontology (Alberto D. Mendoza)",
        "ontologie": "https://purl.org/archimate/owl",
        "url": "https://raw.githubusercontent.com/AlbertoDMendoza/archimate_ontology/"
               "9c3e0dec9987e750e9879d0f345bac22082389da/ontology/archimate.ttl",
    },
    "bp4mc2": {
        "ns": "http://bp4mc2.org/def/archimate#",
        "prefix": "bp4mc2",
        "naam": "bp4mc2 archimate2rdf",
        "ontologie": "http://bp4mc2.org/def/archimate",
        "url": "https://raw.githubusercontent.com/bp4mc2/archimate2rdf/"
               "91224f8db6c23db88237ab2e003daa9218eb8cd9/src/main/resources/ontology/archimate.ttl",
    },
}

# Directe predicaten van de suikerlaag tegenover die van de bronnen.
SUIKER = {
    "serves": "serving", "composes": "composition", "aggregates": "aggregation",
    "assignedTo": "assignment", "realizes": "realization", "accesses": "access",
    "influences": "influence", "triggers": "triggering", "flowsTo": "flow",
    "specializes": "specialization", "associatedWith": "association",
}
# Andere naam, vergelijkbare betekenis.
DICHTBIJ = {"View": "ArchiMateView", "Viewpoint": "ArchiMateViewpoint"}

KLASSE = (OWL.Class, RDFS.Class)
EIGENSCHAP = (OWL.ObjectProperty, OWL.DatatypeProperty, RDF.Property, OWL.AnnotationProperty)


def _bron(sleutel: str) -> rdflib.Graph:
    b = BRONNEN[sleutel]
    pad = CACHE / f"{sleutel}.ttl"
    if not pad.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(b["url"], timeout=60) as r:  # noqa: S310 (vaste https-url)
            pad.write_bytes(r.read())
    g = rdflib.Graph()
    g.parse(pad.as_uri(), format="turtle")
    return g


def _termen(g: rdflib.Graph, ns: str) -> tuple[set[str], set[str]]:
    def namen(typen: tuple) -> set[str]:
        return {str(s)[len(ns):] for t in typen for s in g.subjects(RDF.type, t)
                if str(s).startswith(ns) and str(s) != ns}
    return namen(KLASSE), namen(EIGENSCHAP)


def _onze() -> tuple[set[str], set[str], set[str]]:
    g = rdflib.Graph()
    for f in ("archimate.ttl", "archimate-profile-3.2.ttl", "archimate-views.ttl"):
        g.parse((MAP / f).as_uri(), format="turtle")
    klassen, eigenschappen = _termen(g, AM)
    datatype = {str(s)[len(AM):] for s in g.subjects(RDF.type, OWL.DatatypeProperty)
                if str(s).startswith(AM)}
    return klassen, eigenschappen, datatype


def genereer() -> str:
    klassen, eigenschappen, datatype = _onze()
    regels = [
        f"@prefix am:     <{AM}> .",
        *[f"@prefix {b['prefix']}:{' ' * (6 - len(b['prefix']))} <{b['ns']}> ." for b in BRONNEN.values()],
        "@prefix owl:    <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix skos:   <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix dcterms: <http://purl.org/dc/terms/> .",
        "",
        "# GEGENEREERD BESTAND; niet met de hand bewerken.",
        f"# Generator: scripts/{Path(__file__).name}",
        "# Alleen naar termen die in de bron echt bestaan; bronnen vast op een commit.",
        "",
        "<https://w3id.org/archimate/alignments>",
        "    a owl:Ontology ;",
        '    rdfs:label "ArchiMate-alignments"@nl , "ArchiMate alignments"@en ;',
        '    dcterms:description "Koppelingen van de ArchiMate 4.0-ontologie naar eerdere'
        ' ArchiMate-ontologieën in RDF."@nl , "Mappings from the ArchiMate 4.0 ontology to'
        ' earlier ArchiMate ontologies in RDF."@en ;',
        *[f"    dcterms:references <{b['ontologie']}> ;" for b in BRONNEN.values()],
        "    owl:imports <https://w3id.org/archimate> ;",
        '    owl:versionInfo "0.3.0-concept" .',
        "",
    ]
    tellingen = []
    for sleutel, b in BRONNEN.items():
        hun_k, hun_p = _termen(_bron(sleutel), b["ns"])
        px = b["prefix"]
        paren: list[tuple[str, str, str]] = []
        paren += [(k, "skos:exactMatch", k) for k in sorted(klassen & hun_k)]
        paren += [(p, "skos:exactMatch", p) for p in sorted(datatype & hun_p)]
        paren += [(o, "skos:closeMatch", h) for o, h in sorted(SUIKER.items())
                  if o in eigenschappen and h in hun_p]
        paren += [(o, "skos:closeMatch", h) for o, h in sorted(DICHTBIJ.items())
                  if o in klassen and h in hun_k]
        regels.append(f"# {b['naam']}: {len(paren)} koppelingen")
        regels += [f"am:{o} {rel} {px}:{h} ." for o, rel, h in paren]
        regels.append("")
        tellingen.append(f"{sleutel} {len(paren)}")
    print("koppelingen:", ", ".join(tellingen))
    return "\n".join(regels)


def main() -> None:
    ttl = genereer()
    UIT.write_text(ttl, encoding="utf-8", newline="\n")
    print(f"geschreven: {UIT} ({len(ttl.splitlines())} regels)")


if __name__ == "__main__":
    main()
