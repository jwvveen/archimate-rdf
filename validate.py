"""Validate a model against the SHACL shapes.

Loads ontology, profile, and matrix into the same graph as the model data;
pyshacl's ont-graph option is not enough, because that mix-in is invisible
to the SPARQL constraints in shacl/.

Usage:  python validate.py [--fast] [model.ttl]

--fast  uses the flattened matrix (archimate-matrix-plat.ttl with
        shacl/archimate-matrix-plat-shapes.ttl): same rules, a plain lookup
        instead of rdfs:subClassOf* paths, minutes become seconds.
"""

import sys
from pathlib import Path

import rdflib
from pyshacl import validate

HERE = Path(__file__).resolve().parent
args = sys.argv[1:]
FAST = "--fast" in args
args = [a for a in args if a != "--fast"]
MODEL = Path(args[0]) if args else HERE / "example.ttl"
MATRIX = "archimate-matrix-plat.ttl" if FAST else "archimate-matrix.ttl"
MATRIX_SHAPES = "archimate-matrix-plat-shapes.ttl" if FAST else "archimate-matrix-shapes.ttl"

data = rdflib.Graph()
for f in ("archimate.ttl", "archimate-profile-3.2.ttl", MATRIX):
    data.parse(HERE / f, format="turtle")
data.parse(MODEL, format="turtle")

shapes = rdflib.Graph()
shapes.parse(HERE / "shacl" / "archimate-shapes.ttl", format="turtle")
shapes.parse(HERE / "shacl" / MATRIX_SHAPES, format="turtle")

conforms, _, text = validate(data, shacl_graph=shapes,
                             inference="none", advanced=True)
print(text)
sys.exit(0 if conforms else 1)
