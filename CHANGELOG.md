# Changelog

All notable changes to this ontology. Versions follow `owl:versionInfo` in every
module; the namespace `https://w3id.org/archimate#` stays the same.

## 0.4.0-concept (2026-11-15)

Added, in the views module (`archimate-views.ttl`, `https://w3id.org/archimate/views`):

* `am:Model`: an ArchiMate model, the whole of concepts, views, and folders
  that is managed and exchanged as one (the `model` element of the Model
  Exchange File Format).
* `am:Folder`: a folder in the organization of a model (an `item` in the
  `organizations` of the exchange format). A folder says nothing about the
  meaning of its contents.
* `am:inModel`: the model that a concept, view, or folder belongs to.
* `am:inFolder`: the folder that contains a concept, view, or other folder.

Why: a source graph that holds a model without loss (SemanticXL keeps its
models in a triplestore, one graph per model, one node per element,
relationship, view, and folder) needs to say which model a node belongs to,
and needs folders that can be empty. Like views, these terms describe how a
model is organized, not what its concepts mean, so they live in the views
module and not in the core. No existing IRI changed.

Also:

* SKOS definitions (Dutch and English) for the two new classes in
  `archimate-skos.ttl`, from `scripts/generate_skos_ttl.py`.
* `archimate-alignments.ttl` regenerated: `am:Model skos:exactMatch` the
  `Model` class of the ArchiMate 3.2 ontology by Alberto D. Mendoza.
* All modules at `0.4.0-concept`.

## 0.3.0-concept (2026-11-03)

* Own namespace `https://w3id.org/archimate#` (was `https://purl.org/archimate#`),
  registered in perma-id/w3id.org#7063.
* Alignments to the ArchiMate 3.2 ontology by Alberto D. Mendoza and to
  bp4mc2 archimate2rdf; the flattened matrix and its shapes.
