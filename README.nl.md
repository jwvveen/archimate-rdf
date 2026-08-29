# ArchiMate 4.0 in RDF (concept)

Een concept-OWL-ontologie met SHACL-validatie voor de ArchiMate
4.0-specificatie (The Open Group, C260), geschreven als input voor een
gezamenlijke, open beheerde ArchiMate-ontologie. Vervolg op de blogserie
"ArchiMate 3.2 in RDF", met een paar bewust andere keuzes; de bijbehorende
blogpost legt de afwegingen uit.

*English version: [README.md](README.md).*

Status: **0.2.0-concept**. Alles hier is een discussiestuk voor de
werkgroep "ArchiMate in RDF", geen standaard. ArchiMate is een
geregistreerd merk van The Open Group; dit is geen publicatie van The Open
Group. De namespace `https://purl.org/archimate#` sluit aan op de bestaande
3.2-ontologie in die namespace; gezamenlijk beheer is een open agendapunt.

## Bestanden

| Bestand | Rol |
|---|---|
| `archimate.ttl` | Kernontologie: precies de 42 concepten uit Appendix B.5 plus de junction, de 11 relatietypen in 4 categorieën, aspect- en laag-as, eigenschappen, suikerlaag en matrixvocabulaire. Alle labels en toelichtingen in het Engels en Nederlands |
| `archimate-profile-3.2.ttl` | 3.2-profiel: laag-specifieke typen als subklassen (BusinessProcess onder Process), plus in 4.0 geschrapte typen (Interaction, Representation, Gap) met `owl:deprecated` |
| `archimate-views.ttl` | Views-module: view, toont, gezichtspunt; bewust zonder geometrie |
| `archimate-matrix.ttl` | **Gegenereerd**: de 1.936 matrixcellen met `am:permitsRelation` (toegestaan, incl. afgeleid) en `am:permitsDirectRelation` (tekenbaar). Bron `sources/relationships-4.0.xml`, generator `scripts/generate_matrix_ttl.py` |
| `archimate-skos.ttl` | **Gegenereerd**: SKOS-annotaties (Engelse en Nederlandse definities, toelichtingen, iconen) voor elke klasse, deels uit een Nederlands begrippenkader in `sources/`, gecureerd in `scripts/generate_skos_ttl.py` |
| `shacl/archimate-shapes.ttl` | SHACL niveau 1+2: graafintegriteit en metamodelregels buiten de matrix |
| `shacl/archimate-matrix-shapes.ttl` | SHACL niveau 3: twee generieke SPARQL-constraints die de matrixcellen als data lezen |
| `example.ttl` | Klein, bewust half fout voorbeeldmodel; levert precies vier meldingen op |
| `validate.py` | Draait de validatie op het voorbeeldmodel |

## Valideren

Laad ontologie, profiel en matrix in **dezelfde graaf** als de modeldata;
de ont-graph-optie van pyshacl volstaat niet voor de SPARQL-constraints.

```
pip install pyshacl
python validate.py
```

## Hergenereren

```
python scripts/generate_matrix_ttl.py
python scripts/generate_skos_ttl.py
```

## Licentie

Apache 2.0, zie [LICENSE](LICENSE).
