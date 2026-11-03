# ArchiMate 4.0 in RDF (concept)

Een concept-OWL-ontologie met SHACL-validatie voor de ArchiMate
4.0-specificatie (The Open Group, C260), geschreven als input voor een
gezamenlijke, open beheerde ArchiMate-ontologie. Vervolg op de blogserie
"ArchiMate 3.2 in RDF", met een paar bewust andere keuzes; de bijbehorende
blogpost legt de afwegingen uit.

*English version: [README.md](README.md).*

Status: **0.3.0-concept**. Alles hier is een discussiestuk voor de
werkgroep "ArchiMate in RDF", geen standaard. ArchiMate is een
geregistreerd merk van The Open Group; dit is geen publicatie van The Open
Group.

Zusterproject: [BPMN 2.0 in RDF](https://github.com/jwvveen/bpmn-rdf), op
dezelfde manier gebouwd en met een brug naar deze ontologie
(`bpmn-archimate.ttl` daar).

## Namespace

`https://w3id.org/archimate#`, met content negotiation via
[w3id.org](https://w3id.org/): een RDF-client krijgt de Turtle-bestanden, een
browser deze repository (geregistreerd in
[perma-id/w3id.org#7063](https://github.com/perma-id/w3id.org/pull/7063)). De modules staan onder dezelfde basis:
`/profile-3.2`, `/views`, `/matrix`, `/matrix/plat`, `/skos`, `/alignments`,
`/shapes`, `/shapes/matrix` en `/shapes/matrix-plat`.

**ArchiMate 4.0 is het hoofdwerk; 3.2 is een compatibiliteitsprofiel.**

Tot versie 0.2.0 stonden deze termen onder `https://purl.org/archimate#`. Die
namespace hoort bij de ArchiMate 3.2-ontologie van Alberto D. Mendoza
(`https://purl.org/archimate/owl`). 56 van onze termen (de laag-generieke
4.0-typen, de relatie als resource, de matrixwoorden) bestonden daar niet en
waren dus niet opvraagbaar; ze toevoegen zou een 4.0-concept in een
3.2-ontologie mengen. Daarom een eigen namespace, met een brug:
`archimate-alignments.ttl` koppelt elke term met een tegenhanger aan de
3.2-ontologie van Mendoza (81 koppelingen) en aan bp4mc2 archimate2rdf (68),
alleen naar termen die in hun bestanden bestaan. Gegevens die met de oude
namespace zijn gepubliceerd, moeten opnieuw gepubliceerd worden.

## Bestanden

| Bestand | Rol |
|---|---|
| `archimate.ttl` | Kernontologie: precies de 42 concepten uit Appendix B.5 plus de junction, de 11 relatietypen in 4 categorieën, aspect- en laag-as, eigenschappen, suikerlaag en matrixvocabulaire. Alle labels en toelichtingen in het Engels en Nederlands |
| `archimate-profile-3.2.ttl` | 3.2-profiel: laag-specifieke typen als subklassen (BusinessProcess onder Process), plus in 4.0 geschrapte typen (Interaction, Representation, Gap) met `owl:deprecated` |
| `archimate-views.ttl` | Views-module: view, toont, gezichtspunt; bewust zonder geometrie |
| `archimate-matrix.ttl` | **Gegenereerd**: de 1.936 matrixcellen met `am:permitsRelation` (toegestaan, incl. afgeleid) en `am:permitsDirectRelation` (tekenbaar). Bron `sources/relationships-4.0.xml`, generator `scripts/generate_matrix_ttl.py` |
| `archimate-skos.ttl` | **Gegenereerd**: SKOS-annotaties (Engelse en Nederlandse definities, toelichtingen, iconen) voor elke klasse, deels uit een Nederlands begrippenkader in `sources/`, gecureerd in `scripts/generate_skos_ttl.py` |
| `archimate-matrix-plat.ttl` | **Gegenereerd**: dezelfde matrix uitgeschreven naar de concrete typen (7.056 cellen), zodat een controle een gewone opzoeking is in plaats van `rdfs:subClassOf*`-paden. Een cache, geen tweede waarheid. Generator `scripts/generate_matrix_plat.py` |
| `archimate-alignments.ttl` | **Gegenereerd**: `skos:exactMatch` en `skos:closeMatch` naar de ArchiMate 3.2-ontologie van Alberto D. Mendoza en naar bp4mc2 archimate2rdf, bronnen vast op een commit. Generator `scripts/generate_alignments.py` |
| `shacl/archimate-shapes.ttl` | SHACL niveau 1+2: graafintegriteit en metamodelregels buiten de matrix |
| `shacl/archimate-matrix-shapes.ttl` | SHACL niveau 3: twee generieke SPARQL-constraints die de matrixcellen als data lezen |
| `shacl/archimate-matrix-plat-shapes.ttl` | Dezelfde twee constraints tegen de platte matrix: het voorbeeld in ongeveer een seconde, ArchiSurance (178 relaties) in ongeveer 20 s, waar de generieke shapes minuten tot uren nodig hebben. Laad deze óf de generieke, niet allebei |
| `example.ttl` | Klein, bewust half fout voorbeeldmodel; levert precies vier meldingen op |
| `archisurance.ttl` | **Gegenereerd**: de ArchiSurance-casus van The Open Group (3.2-exchange-format, `sources/archisurance-3.2.xml`) in canonieke vorm: 122 elementen, 178 relaties, 17 views, labels in vijf talen. Converter: `scripts/exchange_to_rdf.py` |
| `validate.py` | Draait de volledige SHACL-validatie op een model (standaard het voorbeeld); `--fast` gebruikt de platte matrix |
| `scripts/check_matrix.py` | Snelle set-based matrixcheck voor grote modellen (pyshacl's per-node-SPARQL schaalt niet) |

## Valideren

Laad ontologie, profiel en matrix in **dezelfde graaf** als de modeldata;
de ont-graph-optie van pyshacl volstaat niet voor de SPARQL-constraints.

```
pip install pyshacl
python validate.py          # generieke matrix
python validate.py --fast   # platte matrix, dezelfde meldingen
```

De meldingen staan in het Nederlands, Engels, Duits en Frans.

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
python scripts/generate_matrix_plat.py
python scripts/generate_alignments.py
python scripts/exchange_to_rdf.py sources/archisurance-3.2.xml archisurance.ttl
```

## Eerder werk

* [ArchiMate 3.2-ontologie](https://github.com/AlbertoDMendoza/archimate_ontology)
  van Alberto D. Mendoza (`https://purl.org/archimate#`, Apache-2.0), met
  SHACL-validatie en afleidingsregels. Het 3.2-profiel hier volgt dezelfde
  typenamen, en `archimate-alignments.ttl` koppelt ernaar.
* [bp4mc2 archimate2rdf](https://github.com/bp4mc2/archimate2rdf)
  (`http://bp4mc2.org/def/archimate#`), een converter van het exchange-formaat
  naar RDF.

## Licentie

Apache 2.0, zie [LICENSE](LICENSE).
