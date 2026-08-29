"""Fast matrix check for large models.

pyshacl evaluates the two matrix constraints per relationship with a SPARQL
query each, which does not scale beyond a few dozen relationships. This
script does the same check set-based in Python: load the matrix cells into
a dictionary, compute the subclass closure once, and test every
relationship in seconds. Use validate.py for the full SHACL run on small
models; use this for models the size of ArchiSurance.

Usage:  python scripts/check_matrix.py <model.ttl>
"""

from __future__ import annotations

import sys
from pathlib import Path

import rdflib

HERE = Path(__file__).resolve().parent.parent
AM = rdflib.Namespace("https://purl.org/archimate#")


def ancestors(graph: rdflib.Graph, cls: rdflib.URIRef) -> set[rdflib.URIRef]:
    seen, edge = {cls}, {cls}
    while edge:
        nxt = set()
        for c in edge:
            for sup in graph.objects(c, rdflib.RDFS.subClassOf):
                if sup not in seen:
                    seen.add(sup)
                    nxt.add(sup)
        edge = nxt
    return seen


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    model_path = Path(sys.argv[1])

    ont = rdflib.Graph()
    for f in ("archimate.ttl", "archimate-profile-3.2.ttl", "archimate-views.ttl"):
        ont.parse(HERE / f, format="turtle")
    matrix = rdflib.Graph()
    matrix.parse(HERE / "archimate-matrix.ttl", format="turtle")
    model = rdflib.Graph()
    model.parse(model_path, format="turtle")

    permits: dict[tuple, set] = {}
    direct: dict[tuple, set] = {}
    for cell in matrix.subjects(rdflib.RDF.type, AM.MatrixCell):
        src = matrix.value(cell, AM.sourceType)
        tgt = matrix.value(cell, AM.targetType)
        permits[(src, tgt)] = set(matrix.objects(cell, AM.permitsRelation))
        direct[(src, tgt)] = set(matrix.objects(cell, AM.permitsDirectRelation))

    rel_classes = {c for c in ont.subjects(rdflib.RDF.type, None)
                   if AM.Relationship in ancestors(ont, c)} - {AM.Relationship}
    closure_cache: dict = {}

    def anc(cls):
        if cls not in closure_cache:
            closure_cache[cls] = ancestors(ont, cls)
        return closure_cache[cls]

    def allowed(table, rel_type, src_type, tgt_type) -> bool:
        rel_anc = anc(rel_type)
        for s in anc(src_type):
            for t in anc(tgt_type):
                if table.get((s, t), set()) & rel_anc:
                    return True
        return False

    violations, warnings, checked = [], [], 0
    for rel in model.subjects(rdflib.RDF.type, None):
        rel_type = model.value(rel, rdflib.RDF.type)
        if rel_type not in rel_classes:
            continue
        src = model.value(rel, AM.source)
        tgt = model.value(rel, AM.target)
        src_type = model.value(src, rdflib.RDF.type) if src else None
        tgt_type = model.value(tgt, rdflib.RDF.type) if tgt else None
        if not (src_type and tgt_type):
            violations.append((rel, rel_type, "dangling endpoint"))
            continue
        checked += 1
        if not allowed(permits, rel_type, src_type, tgt_type):
            violations.append((rel, rel_type,
                               f"{src_type.split('#')[1]} -> {tgt_type.split('#')[1]} not permitted"))
        elif not allowed(direct, rel_type, src_type, tgt_type):
            warnings.append((rel, rel_type,
                             f"{src_type.split('#')[1]} -> {tgt_type.split('#')[1]} derivable only"))

    print(f"{checked} relationships checked against the matrix")
    print(f"violations: {len(violations)}, warnings (derivable, not drawable): {len(warnings)}")
    for rel, typ, msg in violations[:20]:
        print(f"  VIOLATION {rel.split('/')[-1]} ({typ.split('#')[1]}): {msg}")
    for rel, typ, msg in warnings[:20]:
        print(f"  WARNING   {rel.split('/')[-1]} ({typ.split('#')[1]}): {msg}")
    if len(violations) > 20 or len(warnings) > 20:
        print("  (first 20 of each shown)")
    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
