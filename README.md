# ArchiMate 4.0 in RDF (draft)

A draft OWL ontology and SHACL validation set for the ArchiMate 4.0
specification (The Open Group, C260), written as input for a shared, openly
governed ArchiMate ontology. It follows up on the "ArchiMate 3.2 in RDF"
blog series and takes a few deliberately different turns; the accompanying
blog post explains the reasoning.

*Nederlandse versie: [README.nl.md](README.nl.md).*

Status: **0.3.0-concept**. Everything here is a discussion piece for the
"ArchiMate in RDF" working group, not a standard. ArchiMate is a registered
trademark of The Open Group; this is not a publication of The Open Group.

Sibling project: [BPMN 2.0 in RDF](https://github.com/jwvveen/bpmn-rdf), built
the same way and bridged to this ontology (`bpmn-archimate.ttl` there).

## Namespace

`https://w3id.org/archimate#`, with content negotiation through
[w3id.org](https://w3id.org/): RDF clients get the Turtle files, browsers this
repository (registration requested in
[perma-id/w3id.org#7063](https://github.com/perma-id/w3id.org/pull/7063);
until it is merged the IRIs do not resolve yet). Modules live under the same base: `/profile-3.2`, `/views`,
`/matrix`, `/matrix/plat`, `/skos`, `/alignments`, `/shapes`,
`/shapes/matrix` and `/shapes/matrix-plat`.

**ArchiMate 4.0 is the main work; 3.2 is a compatibility profile.**

Up to version 0.2.0 these terms lived under `https://purl.org/archimate#`.
That namespace belongs to the ArchiMate 3.2 ontology by Alberto D. Mendoza
(`https://purl.org/archimate/owl`). 56 of our terms (the layer-generic 4.0
types, the relationship as a resource, the matrix vocabulary) did not exist
there, so they did not resolve, and adding them would have mixed a 4.0 draft
into a 3.2 ontology. Hence an own namespace, and a bridge instead:
`archimate-alignments.ttl` maps every term that has a counterpart to
Mendoza's 3.2 ontology (81 mappings) and to bp4mc2 archimate2rdf (68), only
to terms that exist in their files. Data published with the old namespace
needs to be republished.

## Files

| File | Role |
|---|---|
| `archimate.ttl` | Core ontology: exactly the 42 concepts of Appendix B.5 plus the junction, the 11 relationship types in 4 categories, the aspect and layer axes, properties, the sugar layer, and the matrix vocabulary. All labels and comments in English and Dutch |
| `archimate-profile-3.2.ttl` | 3.2 compatibility profile: layer-specific types as subclasses (BusinessProcess under Process), plus types removed in 4.0 (Interaction, Representation, Gap) marked `owl:deprecated` |
| `archimate-views.ttl` | Views module: view, shows, viewpoint; deliberately without geometry |
| `archimate-matrix.ttl` | **Generated**: the 1,936 matrix cells with `am:permitsRelation` (permitted, including derived) and `am:permitsDirectRelation` (drawable). Source: `sources/relationships-4.0.xml`, generator `scripts/generate_matrix_ttl.py` |
| `archimate-skos.ttl` | **Generated**: SKOS annotations (English and Dutch definitions, scope notes, icons) for every class, partly from a Dutch concept scheme in `sources/`, curated in `scripts/generate_skos_ttl.py` |
| `archimate-matrix-plat.ttl` | **Generated**: the same matrix spelled out over the concrete types (7,056 cells), so a check is a plain lookup instead of `rdfs:subClassOf*` paths. A cache, not a second truth. Generator `scripts/generate_matrix_plat.py` |
| `archimate-alignments.ttl` | **Generated**: `skos:exactMatch` and `skos:closeMatch` to the ArchiMate 3.2 ontology by Alberto D. Mendoza and to bp4mc2 archimate2rdf, sources pinned to a commit. Generator `scripts/generate_alignments.py` |
| `shacl/archimate-shapes.ttl` | SHACL levels 1+2: graph integrity (complete relationships, no dangling endpoints, value lists) and metamodel rules outside the matrix (composition uniqueness, label rules) |
| `shacl/archimate-matrix-shapes.ttl` | SHACL level 3: two generic SPARQL constraints that read the matrix cells as data; a matrix change requires no shape regeneration |
| `shacl/archimate-matrix-plat-shapes.ttl` | The same two constraints against the flattened matrix: the example in about a second, ArchiSurance (178 relationships) in about 20 s, where the generic shapes take minutes to hours. Load either this one or the generic one, not both |
| `example.ttl` | Small, deliberately half-broken example model; yields exactly four findings |
| `archisurance.ttl` | **Generated**: the Open Group's ArchiSurance case study (3.2 exchange format, `sources/archisurance-3.2.xml`) converted to the canonical form: 122 elements, 178 relationships, 17 views, labels in five languages. Converter: `scripts/exchange_to_rdf.py` |
| `validate.py` | Runs the full SHACL validation on a model (default: the example); `--fast` uses the flattened matrix |
| `scripts/check_matrix.py` | Fast set-based matrix check for large models (pyshacl's per-node SPARQL does not scale) |

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

* **Multilingual from day one.** Every label, definition and comment
  ships in English and Dutch; every validation message in English, Dutch,
  German and French.

## Validating

Load the ontology, the profile, and the matrix into the **same graph** as
your model data. pyshacl's ont-graph option is not enough: that mix-in is
invisible to the SPARQL constraints, and every relationship is then falsely
reported as a matrix violation.

```
pip install pyshacl
python validate.py          # generic matrix
python validate.py --fast   # flattened matrix, same findings
```

Expected findings on `example.ttl`:

1. **Violation** `ex:fout`: Serving from BusinessObject to BusinessActor
   is not in the matrix.
2. **Violation** `ex:zwevend`: target does not exist in the graph.
3. **Violation** `ex:api2`: target of two compositions.
4. **Warning** `ex:afleiding`: Serving between these types is derivable
   but not directly drawable.

For models beyond a few dozen relationships, run the matrix check
set-based instead (same rules, seconds instead of hours):

```
python scripts/check_matrix.py archisurance.ttl
```

On ArchiSurance this reports one violation and 53 warnings, and both are
telling. The violation is the Realization from a Representation, the one
element in the model that 4.0 removed. The warnings are relationships that
were directly drawable in 3.2 but are derivable-only in the 4.0 matrix,
such as Access from an ApplicationComponent to a DataObject: in 4.0,
behavior accesses data, and the component's access is a derivation. A
textbook 3.2 model against the 4.0 matrix is itself a migration report.

## Regenerating

```
python scripts/generate_matrix_ttl.py
python scripts/generate_skos_ttl.py
python scripts/generate_matrix_plat.py
python scripts/generate_alignments.py
python scripts/exchange_to_rdf.py sources/archisurance-3.2.xml archisurance.ttl
```

The generated files are committed; the scripts are the only way to change
them.

## Earlier work

* [ArchiMate 3.2 ontology](https://github.com/AlbertoDMendoza/archimate_ontology)
  by Alberto D. Mendoza (`https://purl.org/archimate#`, Apache-2.0), with
  SHACL validation and derivation rules. The 3.2 profile here follows the same
  type names, and `archimate-alignments.ttl` maps to it.
* [bp4mc2 archimate2rdf](https://github.com/bp4mc2/archimate2rdf)
  (`http://bp4mc2.org/def/archimate#`), a converter from the exchange format
  to RDF.

## Contributing

Disagreement is welcome, especially on the design choices above. Open an
issue, or join the working group discussion.

## License

Apache 2.0, see [LICENSE](LICENSE). The ArchiSurance case study in
`sources/` is by The Open Group and is included here as widely
redistributed example material; ArchiMate is a registered trademark of
The Open Group.
