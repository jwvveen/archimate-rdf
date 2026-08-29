# ArchiMate 4.0 in RDF (draft)

A draft OWL ontology and SHACL validation set for the ArchiMate 4.0
specification (The Open Group, C260), written as input for a shared, openly
governed ArchiMate ontology. It follows up on the "ArchiMate 3.2 in RDF"
blog series and takes a few deliberately different turns; the accompanying
blog post explains the reasoning.

*Nederlandse versie: [README.nl.md](README.nl.md).*

Status: **0.2.0-concept**. Everything here is a discussion piece for the
"ArchiMate in RDF" working group, not a standard. ArchiMate is a registered
trademark of The Open Group; this is not a publication of The Open Group.
The `https://purl.org/archimate#` namespace connects to the existing 3.2
ontology in that namespace; shared governance is an open agenda item.

## Files

| File | Role |
|---|---|
| `archimate.ttl` | Core ontology: exactly the 42 concepts of Appendix B.5 plus the junction, the 11 relationship types in 4 categories, the aspect and layer axes, properties, the sugar layer, and the matrix vocabulary. All labels and comments in English and Dutch |
| `archimate-profile-3.2.ttl` | 3.2 compatibility profile: layer-specific types as subclasses (BusinessProcess under Process), plus types removed in 4.0 (Interaction, Representation, Gap) marked `owl:deprecated` |
| `archimate-views.ttl` | Views module: view, shows, viewpoint; deliberately without geometry |
| `archimate-matrix.ttl` | **Generated**: the 1,936 matrix cells with `am:permitsRelation` (permitted, including derived) and `am:permitsDirectRelation` (drawable). Source: `sources/relationships-4.0.xml`, generator `scripts/generate_matrix_ttl.py` |
| `archimate-skos.ttl` | **Generated**: SKOS annotations (English and Dutch definitions, scope notes, icons) for every class, partly from a Dutch concept scheme in `sources/`, curated in `scripts/generate_skos_ttl.py` |
| `shacl/archimate-shapes.ttl` | SHACL levels 1+2: graph integrity (complete relationships, no dangling endpoints, value lists) and metamodel rules outside the matrix (composition uniqueness, label rules) |
| `shacl/archimate-matrix-shapes.ttl` | SHACL level 3: two generic SPARQL constraints that read the matrix cells as data; a matrix change requires no shape regeneration |
| `example.ttl` | Small, deliberately half-broken example model; yields exactly four findings |
| `validate.py` | Runs the validation on the example model |

## Design choices

* **The relationship is a resource; direct predicates are sugar.** The
  canonical form of every relationship is a resource with `am:source` and
  `am:target`. This works in every triplestore, keeps parallel
  relationships apart, and carries metadata without RDF-Star. The direct
  predicates (`am:serves`, ...) are a derived layer, materialized with one
  SPARQL CONSTRUCT:

  ```sparql
  CONSTRUCT { ?s ?p ?t }
  WHERE {
      ?r am:source ?s ; am:target ?t ; a ?class .
      ?p am:relationshipClass ?class .
  }
  ```

* **4.0 is the target; 3.2 is a profile.** The core contains exactly the
  concepts of Appendix B.5; everything 3.2 had on top lives in the profile
  and resolves to the right matrix cells through `rdfs:subClassOf`, so a
  3.2 model needs zero extra validation rules.

* **The matrix is data; the validation is two rules.** The permitted-
  relationship matrix ships as triples, generated from a machine-readable
  file. Two generic SHACL-SPARQL constraints check models against it: a
  violation when a relationship is not permitted at all, and a warning
  when it is permitted but not directly drawable (a drawn relationship
  that is only derivable is usually a modeling smell).

* **Ontology and validation are strictly separated.** The ontology says
  what terms mean and is usable without any validation; the SHACL files
  say when a model is sound and load separately.

* **Multilingual from day one.** Every label, definition, comment, and
  validation message ships in English and Dutch.

## Validating

Load the ontology, the profile, and the matrix into the **same graph** as
your model data. pyshacl's ont-graph option is not enough: that mix-in is
invisible to the SPARQL constraints, and every relationship is then falsely
reported as a matrix violation.

```
pip install pyshacl
python validate.py
```

Expected findings on `example.ttl`:

1. **Violation** `ex:fout`: Serving from BusinessObject to BusinessActor
   is not in the matrix.
2. **Violation** `ex:zwevend`: target does not exist in the graph.
3. **Violation** `ex:api2`: target of two compositions.
4. **Warning** `ex:afleiding`: Serving between these types is derivable
   but not directly drawable.

## Regenerating

```
python scripts/generate_matrix_ttl.py
python scripts/generate_skos_ttl.py
```

The generated files are committed; the scripts are the only way to change
them.

## Contributing

Disagreement is welcome, especially on the design choices above. Open an
issue, or join the working group discussion.

## License

Apache 2.0, see [LICENSE](LICENSE).
