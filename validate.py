"""Validate the example model against the SHACL shapes.

Loads ontology, profile, and matrix into the same graph as the model data;
pyshacl's ont-graph option is not enough, because that mix-in is invisible
to the SPARQL constraints in shacl/.

Usage:  python validate.py [model.ttl]
"""

import sys
from pathlib import Path

import rdflib
from pyshacl import validate

HERE = Path(__file__).resolve().parent
MODEL = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "example.ttl"

data = rdflib.Graph()
for f in ("archimate.ttl", "archimate-profile-3.2.ttl", "archimate-matrix.ttl"):
    data.parse(HERE / f, format="turtle")
data.parse(MODEL, format="turtle")

shapes = rdflib.Graph()
shapes.parse(HERE / "shacl" / "archimate-shapes.ttl", format="turtle")
shapes.parse(HERE / "shacl" / "archimate-matrix-shapes.ttl", format="turtle")

conforms, _, text = validate(data, shacl_graph=shapes,
                             inference="none", advanced=True)
print(text)
sys.exit(0 if conforms else 1)
