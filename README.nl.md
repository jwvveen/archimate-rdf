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
| `archisurance.ttl` | **Gegenereerd**: de ArchiSurance-casus van The Open Group (3.2-exchange-format, `sources/archisurance-3.2.xml`) in canonieke vorm: 122 elementen, 178 relaties, 17 views, labels in vijf talen. Converter: `scripts/exchange_to_rdf.py` |
| `validate.py` | Draait de volledige SHACL-validatie op het voorbeeldmodel |
| `scripts/check_matrix.py` | Snelle set-based matrixcheck voor grote modellen (pyshacl's per-node-SPARQL schaalt niet) |

## Valideren

Laad ontologie, profiel en matrix in **dezelfde graaf** als de modeldata;
de ont-graph-optie van pyshacl volstaat niet voor de SPARQL-constraints.

```
pip install pyshacl
python validate.py
```

Voor modellen groter dan enkele tientallen relaties:

```
python scripts/check_matrix.py archisurance.ttl
```

Op ArchiSurance: 1 overtreding (de Realization vanuit een Representation,
precies het element dat 4.0 schrapte) en 53 waarschuwingen (in 3.2 direct
tekenbaar, in de 4.0-matrix alleen afleidbaar). Een net 3.2-model tegen de
4.0-matrix is daarmee zelf een migratierapport.

## Hergenereren

```
python scripts/generate_matrix_ttl.py
python scripts/generate_skos_ttl.py
python scripts/exchange_to_rdf.py sources/archisurance-3.2.xml archisurance.ttl
```

## Licentie

Apache 2.0, zie [LICENSE](LICENSE).
