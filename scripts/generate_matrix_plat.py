"""Genereer archimate-matrix-plat.ttl: de matrix zonder subklassepaden.

`archimate-matrix.ttl` staat op de 44 generieke typen uit Appendix B.5. Een
model draagt concrete typen (`BusinessProcess`), en de SHACL-constraint
overbrugt dat verschil met `rdfs:subClassOf*`. Semantisch is dat de juiste vorm,
en die blijft dan ook staan.

Alleen: dat pad wordt per relatie tegen alle 1.936 cellen uitgerekend, drie keer
per cel. Gemeten met pyshacl op een model van vijftien relaties:

    alleen niveau 1 en 2          1,9 s
    met de matrixshapes         839,7 s

Dit bestand is dezelfde matrix, uitgeschreven naar de concrete typen. De paden
zijn er dan uit gerekend en een controle wordt een gewone opzoeking:

    FILTER NOT EXISTS { ?cel am:sourceType ?brontype ;
                             am:targetType ?doeltype ;
                             am:permitsRelation ?relatietype }

Het is een cache en geen tweede waarheid: gegenereerd uit dezelfde bron, en
SemanticXL (`tests/test_matrix_plat.py`) bewaakt dat beide vormen hetzelfde toestaan. Wie de
matrix wil begrijpen leest `archimate-matrix.ttl`; wie hem snel wil toepassen
laadt deze erbij.

Draai vanuit de repo-wortel:  python scripts/generate_matrix_plat.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ONT = REPO
UIT = ONT / "archimate-matrix-plat.ttl"

AM = "https://w3id.org/archimate#"


def lees() -> tuple[dict, dict]:
    """De matrix en de klassenhiërarchie, met rdflib in plaats van patronen.

    Met de hand door Turtle heen zoeken is breekbaar; rdflib leest elke geldige
    schrijfwijze.
    """
    from rdflib import Graph, RDFS, URIRef

    graaf = Graph()
    for naam in ("archimate.ttl", "archimate-profile-3.2.ttl", "archimate-matrix.ttl"):
        graaf.parse(ONT / naam, format="turtle")

    def kort(term) -> str:
        return str(term).replace(AM, "")

    cellen: dict[tuple[str, str], tuple[set[str], set[str]]] = {}
    for cel in graaf.subjects(URIRef(AM + "sourceType"), None):
        bron = graaf.value(cel, URIRef(AM + "sourceType"))
        doel = graaf.value(cel, URIRef(AM + "targetType"))
        if bron is None or doel is None:
            continue
        toegestaan = {kort(o) for o in graaf.objects(cel, URIRef(AM + "permitsRelation"))}
        direct = {kort(o) for o in graaf.objects(cel, URIRef(AM + "permitsDirectRelation"))}
        if toegestaan:
            cellen[(kort(bron), kort(doel))] = (toegestaan, direct)

    onder: dict[str, set[str]] = defaultdict(set)
    for kind, _p, ouder in graaf.triples((None, RDFS.subClassOf, None)):
        if str(kind).startswith(AM) and str(ouder).startswith(AM):
            onder[kort(ouder)].add(kort(kind))
    return cellen, dict(onder)


def afstammelingen(onder: dict[str, set[str]]) -> dict[str, set[str]]:
    """type → alle typen die eronder vallen, inclusief zichzelf."""
    geheugen: dict[str, set[str]] = {}

    def loop(naam: str, bezig: frozenset) -> set[str]:
        if naam in geheugen:
            return geheugen[naam]
        if naam in bezig:      # een lus hoort niet te kunnen, maar hangen ook niet
            return {naam}
        uit = {naam}
        for kind in onder.get(naam, ()):
            uit |= loop(kind, bezig | {naam})
        geheugen[naam] = uit
        return uit

    namen = set(onder) | {k for v in onder.values() for k in v}
    return {naam: loop(naam, frozenset()) for naam in namen}


def main() -> int:
    if not (ONT / "archimate-matrix.ttl").is_file():
        print("archimate-matrix.ttl ontbreekt", file=sys.stderr)
        return 1
    cellen, onder = lees()
    breed = afstammelingen(onder)

    def spreid(naam: str) -> set[str]:
        return breed.get(naam, {naam})

    plat: dict[tuple[str, str], tuple[set[str], set[str]]] = {}
    for (bron, doel), (toegestaan, direct) in cellen.items():
        rel_toegestaan: set[str] = set()
        for r in toegestaan:
            rel_toegestaan |= spreid(r)
        rel_direct: set[str] = set()
        for r in direct:
            rel_direct |= spreid(r)
        for b in spreid(bron):
            for d in spreid(doel):
                vak = plat.setdefault((b, d), (set(), set()))
                vak[0].update(rel_toegestaan)
                vak[1].update(rel_direct)

    regels = [
        "@prefix am:   <https://w3id.org/archimate#> .",
        "@prefix amp:  <https://w3id.org/archimate/matrix/plat#> .",
        "@prefix owl:  <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "",
        "# GEGENEREERD door scripts/generate_matrix_plat.py",
        "# Bron: archimate-matrix.ttl",
        "# Niet met de hand bewerken.",
        "#",
        "# Dezelfde matrix als archimate-matrix.ttl, uitgeschreven naar de",
        "# concrete typen. Een validatie heeft daarmee geen subklassepaden meer",
        "# nodig. Semantisch voegt dit niets toe: het is een cache voor snelheid,",
        "# en SemanticXL bewaakt dat beide vormen hetzelfde zeggen.",
        "",
        "<https://w3id.org/archimate/matrix/plat>",
        "    a owl:Ontology ;",
        '    rdfs:label "ArchiMate-relatiematrix, platgeslagen"@nl ,',
        '               "ArchiMate relationship matrix, flattened"@en ;',
        '    owl:versionInfo "0.3.0-concept" .',
        "",
    ]
    # Ook de drie overgebleven paden eruit. `?srcType rdfs:subClassOf* am:Concept`
    # bakent de eindpunten af tot ArchiMate-typen, en dat is nodig omdat data in
    # de praktijk meer dan een rdf:type draagt. Als pad kost het per bindingsrij
    # werk; als losse markering is het een opzoeking. Dezelfde afweging als bij
    # de cellen zelf, en dezelfde belofte: het is een cache, geen tweede waarheid.
    concepten: set[str] = set()
    relatieklassen: set[str] = set()
    for (bron, doel), (toegestaan, _direct) in plat.items():
        concepten.update((bron, doel))
        relatieklassen.update(toegestaan)
    regels.append("# Markeringen: welk type is een ArchiMate-concept, welke klasse")
    regels.append("# een relatie. Vervangt `rdfs:subClassOf*`-paden in de shapes.")
    for naam in sorted(concepten):
        regels.append(f"am:{naam} am:isConceptType true .")
    for naam in sorted(relatieklassen):
        regels.append(f"am:{naam} am:isRelationshipType true .")
    regels.append("")

    triples = len(concepten) + len(relatieklassen)
    for (bron, doel), (toegestaan, direct) in sorted(plat.items()):
        regels.append(f"amp:c-{bron}-{doel} a am:MatrixCell ;")
        regels.append(f"    am:sourceType am:{bron} ;")
        regels.append(f"    am:targetType am:{doel} ;")
        rij = " , ".join(f"am:{r}" for r in sorted(toegestaan))
        regels.append(f"    am:permitsRelation {rij}" + (" ;" if direct else " ."))
        triples += 3 + len(toegestaan)
        if direct:
            rij_d = " , ".join(f"am:{r}" for r in sorted(direct))
            regels.append(f"    am:permitsDirectRelation {rij_d} .")
            triples += len(direct)
        regels.append("")

    UIT.write_text("\n".join(regels), encoding="utf-8")
    print(f"{UIT.relative_to(REPO)}: {len(plat)} cellen, {triples} triples "
          f"(uit {len(cellen)} generieke cellen)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
