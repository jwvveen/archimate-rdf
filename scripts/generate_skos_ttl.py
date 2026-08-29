"""Genereer archimate-skos.ttl uit het BegrippenXL-begrippenkader.

Het kader (ontology/archimate/sources/begrippenxl-archimate.ttl) beschrijft
de ArchiMate 3.x-concepten als skos:Concept met Nederlandse definities en
toelichtingen, Engelse specificatieteksten en iconen. Dit script hangt die
als SKOS-annotaties aan de klassen van de 4.0-ontologie en het 3.2-profiel.

De Nederlandse definities komen niet uit de bron maar uit de gecureerde
tabel hieronder: de bronteksten stammen uit 2023, zijn wollig en wijken op
punten inhoudelijk van de specificatie af. De bron levert wat de tabel niet
kan: de Engelse specificatiezinnen, de toelichtingen (ontdaan van hun
gegenereerde slotalinea's) en de iconen. De zeven laag-generieke 4.0-typen
staan niet in de bron en krijgen hun teksten volledig uit dit script.

Zelfde regel als bij de matrix (principe P3): dit script is de enige weg
naar archimate-skos.ttl; met de hand bijwerken is altijd fout.

Draai vanuit de repo-wortel:  python scripts/generate_skos_ttl.py
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import rdflib

REPO = Path(__file__).resolve().parents[1]
BRON = REPO / "sources" / "begrippenxl-archimate.ttl"
ONT = REPO
UIT = ONT / "archimate-skos.ttl"

AM = rdflib.Namespace("https://purl.org/archimate#")
SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
FOAF = rdflib.Namespace("http://xmlns.com/foaf/0.1/")

# Bron-localname -> am-klassenaam waar die afwijkt van 1-op-1.
HERNOEMD = {
    "ConceptArchiMate": "Concept",
    "AccessRelationship": "Access",
    "AggregationRelationship": "Aggregation",
    "AssignmentRelationship": "Assignment",
    "AssociationRelationship": "Association",
    "CompositionRelationship": "Composition",
    "FlowRelationship": "Flow",
    "InfluenceRelationship": "Influence",
    "RealizationRelationship": "Realization",
    "ServingRelationship": "Serving",
    "SpecializationRelationship": "Specialization",
    "TriggeringRelationship": "Triggering",
}

# Bronconcepten zonder tegenhanger in de ontologie: de intern/extern-as en
# hulpabstracties die 4.0 (en onze kern) niet als klasse kent.
OVERSLAAN = {
    "InternalActiveStructureElement", "ExternalActiveStructureElement",
    "InternalBehaviorElement", "ExternalBehaviorElement",
    "StrategyBehaviorElement", "StructureElement",
}

# Gecureerde Nederlandse definities, spec-conform en compact. Volledige
# dekking is een harde eis: een gemapt bronconcept zonder regel hier laat
# de generator stoppen, zodat een nieuw concept nooit stilletjes met een
# ongeredigeerde brontekst het bestand in glipt.
DEFINITIE_NL = {
    # Toplaag en aspecten
    "Concept": "Het gemeenschappelijke supertype van elementen, relaties en relatieconnectoren.",
    "Element": "Een element is een bouwsteen van een ArchiMate-model; relaties verbinden elementen.",
    "Relationship": "Een relatie verbindt twee concepten en typeert hun samenhang.",
    "RelationshipConnector": "Een relatieconnector verbindt relaties van hetzelfde type, zoals een junction.",
    "ActiveStructureElement": "Een actief structuurelement is een element dat gedrag kan uitvoeren.",
    "BehaviorElement": "Een gedragselement is een eenheid van activiteit, uitgevoerd door een of meer actieve structuurelementen.",
    "PassiveStructureElement": "Een passief structuurelement is een element waarop gedrag wordt uitgevoerd.",
    "MotivationElement": "Een motivatie-element geeft de context of reden achter de architectuur weer.",
    "CompositeElement": "Een samengesteld element aggregeert of groepeert concepten uit meerdere aspecten en lagen.",
    # Bedrijfslaag
    "BusinessActor": "Een bedrijfsactor is een bedrijfsentiteit die gedrag kan uitvoeren, zoals een persoon, afdeling of organisatie.",
    "BusinessRole": "Een bedrijfsrol is de verantwoordelijkheid om specifiek bedrijfsgedrag uit te voeren, waaraan een bedrijfsactor kan worden toegewezen.",
    "BusinessCollaboration": "Een bedrijfssamenwerking is een geheel van twee of meer bedrijfsrollen dat gezamenlijk bedrijfsgedrag uitvoert.",
    "BusinessInterface": "Een bedrijfsinterface is een toegangspunt waar bedrijfsdiensten beschikbaar worden gesteld aan de omgeving.",
    "BusinessProcess": "Een bedrijfsproces is een reeks bedrijfsgedragingen die een specifiek resultaat bereikt, zoals een gedefinieerde verzameling producten of diensten.",
    "BusinessFunction": "Een bedrijfsfunctie is een verzameling samenhangend bedrijfsgedrag, gegroepeerd naar bijvoorbeeld benodigde vaardigheden, kennis of middelen.",
    "BusinessInteraction": "Een bedrijfsinteractie is een eenheid van gezamenlijk bedrijfsgedrag, uitgevoerd door (een samenwerking van) twee of meer bedrijfsrollen of bedrijfsactoren.",
    "BusinessEvent": "Een bedrijfsgebeurtenis is een toestandsverandering op bedrijfsniveau.",
    "BusinessService": "Een bedrijfsdienst is expliciet gedefinieerd bedrijfsgedrag dat aan de omgeving wordt aangeboden.",
    "BusinessObject": "Een bedrijfsobject is een concept dat binnen een bedrijfsdomein wordt gebruikt of geproduceerd.",
    "Contract": "Een contract is een formele of informele specificatie van een overeenkomst tussen een aanbieder en een afnemer.",
    "Representation": "Een representatie is een waarneembare vorm van de informatie in een bedrijfsobject.",
    "Product": "Een product is een samenhangende verzameling diensten en/of passieve structuurelementen, met een contract, die als geheel aan afnemers wordt aangeboden.",
    # Applicatielaag
    "ApplicationComponent": "Een applicatiecomponent is een modulaire, vervangbare inkapseling van applicatiefunctionaliteit, uitgelijnd met de implementatiestructuur. Hij kapselt zijn gedrag en gegevens in en stelt diensten beschikbaar via interfaces.",
    "ApplicationCollaboration": "Een applicatiesamenwerking is een geheel van twee of meer applicatiecomponenten dat gezamenlijk applicatiegedrag uitvoert.",
    "ApplicationInterface": "Een applicatie-interface is een toegangspunt waar applicatiediensten beschikbaar worden gesteld aan een gebruiker, een andere applicatiecomponent of een knooppunt.",
    "ApplicationFunction": "Een applicatiefunctie is geautomatiseerd gedrag dat door een applicatiecomponent kan worden uitgevoerd.",
    "ApplicationInteraction": "Een applicatie-interactie is een eenheid van gezamenlijk applicatiegedrag, uitgevoerd door (een samenwerking van) twee of meer applicatiecomponenten.",
    "ApplicationProcess": "Een applicatieproces is een reeks applicatiegedragingen die een specifiek resultaat bereikt.",
    "ApplicationEvent": "Een applicatiegebeurtenis is een toestandsverandering op applicatieniveau.",
    "ApplicationService": "Een applicatiedienst is expliciet gedefinieerd, extern zichtbaar applicatiegedrag.",
    "DataObject": "Een gegevensobject vertegenwoordigt gegevens die gestructureerd zijn voor geautomatiseerde verwerking.",
    # Technologielaag
    "Node": "Een knooppunt is een reken- of fysiek middel dat andere reken- of fysieke middelen host, manipuleert of ermee interacteert.",
    "Device": "Een apparaat is een fysiek IT-middel waarop systeemsoftware en artefacten kunnen worden opgeslagen of ingezet voor uitvoering.",
    "SystemSoftware": "Systeemsoftware biedt een omgeving voor het opslaan, uitvoeren en gebruiken van software of gegevens die erop zijn ingezet.",
    "TechnologyCollaboration": "Een technologiesamenwerking is een geheel van twee of meer knooppunten dat gezamenlijk technologiegedrag uitvoert.",
    "TechnologyInterface": "Een technologie-interface is een toegangspunt waar technologiediensten door een knooppunt worden aangeboden aan de omgeving.",
    "Path": "Een pad is een verbinding tussen twee of meer knooppunten waarover die knooppunten gegevens, energie of materiaal kunnen uitwisselen.",
    "CommunicationNetwork": "Een communicatienetwerk is een verzameling structuren die knooppunten verbindt voor overdracht, routering en ontvangst van gegevens.",
    "TechnologyFunction": "Een technologiefunctie is een verzameling samenhangend technologiegedrag dat door een knooppunt kan worden uitgevoerd.",
    "TechnologyProcess": "Een technologieproces is een reeks technologiegedragingen die een specifiek resultaat bereikt.",
    "TechnologyInteraction": "Een technologie-interactie is een eenheid van gezamenlijk technologiegedrag, uitgevoerd door (een samenwerking van) twee of meer knooppunten.",
    "TechnologyEvent": "Een technologiegebeurtenis is een toestandsverandering op technologieniveau.",
    "TechnologyService": "Een technologiedienst is expliciet gedefinieerd, extern zichtbaar technologiegedrag.",
    "Artifact": "Een artefact is een stuk gegevens dat wordt gebruikt of geproduceerd in een softwareontwikkelproces of door inzet en beheer van een IT-systeem.",
    # Fysiek
    "Equipment": "Een bedrijfsmiddel is een of meer fysieke machines, gereedschappen of instrumenten die fysiek materiaal kunnen maken, gebruiken, opslaan, verplaatsen of transformeren.",
    "Facility": "Een faciliteit is een fysieke voorziening of omgeving, zoals een fabriek, magazijn of kantoor.",
    "DistributionNetwork": "Een distributienetwerk is een fysiek netwerk voor het transporteren van materialen of energie.",
    "Material": "Materiaal is tastbare fysieke materie of energie.",
    # Motivatie
    "Stakeholder": "Een belanghebbende is de rol van een persoon, team of organisatie met belangen in de effecten van de architectuur.",
    "Driver": "Een drijfveer is een externe of interne conditie die een organisatie motiveert om doelen te stellen en veranderingen door te voeren.",
    "Assessment": "Een beoordeling is een uitkomst van een analyse van de stand van zaken rond een of meer drijfveren.",
    "Goal": "Een doel is een verklaring van intentie, richting of gewenste eindtoestand van een belanghebbende.",
    "Outcome": "Een resultaat is een bereikt eindresultaat.",
    "Principle": "Een principe is een uitspraak over intentie of algemene eigenschap die geldt voor elk systeem in een bepaalde context.",
    "Requirement": "Een vereiste is een uitspraak over een behoefte waaraan de architectuur moet voldoen.",
    "Constraint": "Een randvoorwaarde is een beperking op de manier waarop het systeem wordt gerealiseerd.",
    "Meaning": "Een betekenis is de kennis, expertise of interpretatie die aan een concept wordt gegeven in een bepaalde context.",
    "Value": "Een waarde is het relatieve nut, belang of voordeel van een concept voor een belanghebbende.",
    # Strategie
    "Resource": "Een middel is een bezitting die een organisatie in eigendom of beheer heeft.",
    "Capability": "Een vermogen is een vaardigheid die een actief structuurelement, zoals een organisatie, persoon of systeem, bezit.",
    "CourseOfAction": "Een koers is een aanpak of plan om met bepaalde vermogens en middelen doelen te bereiken.",
    "ValueStream": "Een waardestroom is een reeks activiteiten die een totaalresultaat creëert voor een klant, belanghebbende of eindgebruiker.",
    # Implementatie en migratie
    "WorkPackage": "Een werkpakket is een reeks acties met een bepaald doel en een gedefinieerd begin en einde, zoals een project.",
    "Deliverable": "Een op te leveren resultaat is een nauwkeurig gedefinieerde uitkomst van een werkpakket.",
    "ImplementationEvent": "Een implementatiegebeurtenis is een toestandsverandering in het implementatie- of migratieproces.",
    "Plateau": "Een plateau is een relatief stabiele toestand van de architectuur gedurende een bepaalde periode.",
    "Gap": "Een kloof is een uitspraak over het verschil tussen twee plateaus.",
    # Samengesteld
    "Grouping": "Een groepering verzamelt concepten die een gemeenschappelijke eigenschap delen.",
    "Location": "Een locatie is een conceptuele of fysieke plaats of positie waar concepten zich bevinden of worden uitgevoerd.",
    # Relatietypen
    "Composition": "De compositierelatie drukt uit dat een element bestaat uit een of meer andere concepten; het deel hoort bij precies één geheel.",
    "Aggregation": "De aggregatierelatie drukt uit dat een element een of meer andere concepten groepeert.",
    "Assignment": "De toewijzingsrelatie drukt de verdeling van verantwoordelijkheid uit: welk actief element voert gedrag uit, of welke actor vervult een rol.",
    "Realization": "De realisatierelatie drukt uit dat een concreter element een abstracter element waarmaakt.",
    "Serving": "De bedieningsrelatie drukt uit dat een element functionaliteit levert aan een ander element.",
    "Access": "De toegangsrelatie drukt uit dat gedrag een passief structuurelement waarneemt of erop inwerkt, bijvoorbeeld lezend of schrijvend.",
    "Influence": "De beïnvloedingsrelatie drukt uit dat een element een ander element beïnvloedt, met een optionele sterkte; vooral gebruikt tussen motivatie-elementen.",
    "Association": "De associatierelatie drukt een niet nader getypeerde samenhang tussen concepten uit.",
    "Triggering": "De triggerrelatie drukt een tijdelijke of causale opvolging tussen elementen uit.",
    "Flow": "De stroomrelatie drukt overdracht van bijvoorbeeld informatie, goederen of geld tussen elementen uit.",
    "Specialization": "De specialisatierelatie drukt uit dat een concept een bijzondere vorm van een ander concept is.",
    "StructuralRelationship": "Structurele relaties leggen de statische samenhang van elementen vast.",
    "DependencyRelationship": "Afhankelijkheidsrelaties drukken uit dat een element gebruikmaakt van of afhankelijk is van een ander element.",
    "DynamicRelationship": "Dynamische relaties drukken tijdelijke afhankelijkheden tussen gedragingen uit.",
    "OtherRelationship": "Relaties die niet structureel, afhankelijk of dynamisch zijn: specialisatie en associatie.",
    "AndJunction": "Een en-junction: alle inkomende of uitgaande relaties gelden gezamenlijk.",
    "OrJunction": "Een of-junction: een of meer van de inkomende of uitgaande relaties gelden.",
}

# Engelse definities voor de concepten waar de bron geen specificatiezin
# (rdfs:comment) voor heeft: de abstracties en relatiecategorieën.
DEFINITIE_EN = {
    "Concept": "The common supertype of elements, relationships, and relationship connectors.",
    "Element": "An element is a building block of an ArchiMate model; relationships connect elements.",
    "Relationship": "A relationship connects two concepts and types their association.",
    "RelationshipConnector": "A relationship connector connects relationships of the same type, such as a junction.",
    "ActiveStructureElement": "An active structure element is an element that can perform behavior.",
    "BehaviorElement": "A behavior element is a unit of activity performed by one or more active structure elements.",
    "PassiveStructureElement": "A passive structure element is an element on which behavior is performed.",
    "MotivationElement": "A motivation element provides the context of or reason behind the architecture.",
    "CompositeElement": "A composite element aggregates or groups concepts from multiple aspects and layers.",
    "StructuralRelationship": "Structural relationships model the static construction or composition of elements.",
    "DependencyRelationship": "Dependency relationships model how elements are used to support other elements.",
    "DynamicRelationship": "Dynamic relationships model temporal dependencies between behaviors.",
    "OtherRelationship": "Relationships that are neither structural, dependency, nor dynamic: specialization and association.",
}

# De laag-generieke 4.0-typen staan niet in de 3.x-bron; teksten (nl, en)
# volledig uit dit script.
AANVULLING_40 = {
    "Process": (
        "Een proces is een reeks gedragingen die een specifiek resultaat bereikt.",
        "A process represents a sequence of behaviors that achieves a specific outcome."),
    "Function": (
        "Een functie is een verzameling samenhangend gedrag, gegroepeerd naar bijvoorbeeld benodigde middelen, kennis of vaardigheden.",
        "A function represents a collection of coherent behavior, grouped by, for example, required resources, knowledge, or skills."),
    "Service": (
        "Een dienst is expliciet gedefinieerd, extern zichtbaar gedrag.",
        "A service represents explicitly defined exposed behavior."),
    "Event": (
        "Een gebeurtenis is een toestandsverandering.",
        "An event represents a state change."),
    "Role": (
        "Een rol is de verantwoordelijkheid om specifiek gedrag uit te voeren, waaraan een actor kan worden toegewezen.",
        "A role represents the responsibility for performing specific behavior, to which an actor can be assigned."),
    "Collaboration": (
        "Een samenwerking is een geheel van twee of meer actieve structuurelementen dat gezamenlijk gedrag uitvoert.",
        "A collaboration represents an aggregate of two or more active structure elements that work together to perform collective behavior."),
    "Junction": (
        "Een junction splitst of bundelt relaties van hetzelfde type.",
        "A junction is used to connect relationships of the same type."),
}

# Hulpklassen en lagen uit kern- en views-module die niet in de bron staan;
# ook die horen een definitie te hebben (compleetheidseis, zie test).
EXTRA = {
    "View": (
        "Een view is een geselecteerd deel van het model, gericht op een belanghebbende of vraag.",
        "A view is a selected part of the model, addressing a stakeholder or question."),
    "Layer": (
        "Een laag is een indeling van het model naar abstractieniveau, van strategie tot implementatie.",
        "A layer partitions the model by level of abstraction, from strategy to implementation."),
    "MatrixCell": (
        "Een matrixcel legt vast welke relatietypen tussen een bron- en doeltype zijn toegestaan en welke daarvan direct tekenbaar zijn.",
        "A matrix cell records which relationship types are permitted between a source and target type, and which of those may be drawn directly."),
    "AccessTypeValue": (
        "Een toegangstype-waarde geeft de richting van een toegangsrelatie aan: lezen, schrijven, beide of niet gespecificeerd.",
        "An access type value indicates the direction of an access relationship: read, write, both, or unspecified."),
    "StrategyLayer": (
        "De strategielaag beschrijft koersen, vermogens, waardestromen en middelen van de organisatie.",
        "The strategy layer describes the organization's courses of action, capabilities, value streams, and resources."),
    "BusinessLayer": (
        "De bedrijfslaag beschrijft de producten en diensten voor klanten, gerealiseerd door bedrijfsprocessen van actoren en rollen.",
        "The business layer describes the products and services offered to customers, realized by business processes performed by actors and roles."),
    "ApplicationLayer": (
        "De applicatielaag beschrijft de applicaties die de bedrijfslaag met applicatiediensten ondersteunen.",
        "The application layer describes the applications that support the business layer with application services."),
    "TechnologyLayer": (
        "De technologielaag beschrijft de infrastructuur van knooppunten, systeemsoftware en netwerken die de applicaties draagt.",
        "The technology layer describes the infrastructure of nodes, system software, and networks that supports the applications."),
    "PhysicalLayer": (
        "De fysieke laag beschrijft bedrijfsmiddelen, faciliteiten, distributienetwerken en materiaal in de fysieke wereld.",
        "The physical layer describes equipment, facilities, distribution networks, and material in the physical world."),
    "MotivationLayer": (
        "De motivatielaag beschrijft waarom de architectuur is zoals hij is: belanghebbenden, drijfveren, doelen, principes en vereisten.",
        "The motivation layer describes why the architecture is the way it is: stakeholders, drivers, goals, principles, and requirements."),
    "ImplementationLayer": (
        "De implementatie- en migratielaag beschrijft de verandering: werkpakketten, op te leveren resultaten en plateaus.",
        "The implementation and migration layer describes change: work packages, deliverables, and plateaus."),
}

# Slotalinea's die in vrijwel elke bron-toelichting staan en niets toevoegen.
BOILERPLATE_START = ("Over het algemeen wordt", "Over het algemeen worden")


def _lit(waarde: str, taal: str = "") -> str:
    uit = waarde.replace("\\", "\\\\").replace('"', '\\"')
    uit = uit.replace("\r", "").replace("\n", "\\n")
    return f'"{uit}"' + (f"@{taal}" if taal else "")


def _zonder_boilerplate(tekst: str) -> str:
    alineas = [a for a in tekst.split("\n")
               if not a.strip().startswith(BOILERPLATE_START)]
    return "\n".join(alineas).strip()


def genereer() -> str:
    bron = rdflib.Graph()
    bron.parse(BRON, format="turtle")

    ont = rdflib.Graph()
    ont.parse(ONT / "archimate.ttl", format="turtle")
    ont.parse(ONT / "archimate-profile-3.2.ttl", format="turtle")
    ont.parse(ONT / "archimate-views.ttl", format="turtle")
    bekend = {str(s).rsplit("#", 1)[-1]
              for s in ont.subjects(rdflib.RDF.type, None)
              if str(s).startswith(str(AM))}

    regels = [
        "@prefix am:   <https://purl.org/archimate#> .",
        "@prefix owl:  <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix foaf: <http://xmlns.com/foaf/0.1/> .",
        "@prefix dcterms: <http://purl.org/dc/terms/> .",
        "",
        "# GEGENEREERD BESTAND; niet met de hand bewerken.",
        f"# Bron: sources/{BRON.name} (BegrippenXL-begrippenkader ArchiMate, 2023)",
        f"# Generator: scripts/{Path(__file__).name}, {date.today().isoformat()}",
        "#",
        "# SKOS-annotatiemodule. De Nederlandse definities zijn gecureerd in",
        "# de generator (spec-conform); de bron levert de Engelse",
        "# specificatiezinnen, de toelichtingen en de iconen. De zeven",
        "# laag-generieke 4.0-typen komen volledig uit de generator.",
        "",
        "<https://purl.org/archimate/skos>",
        "    a owl:Ontology ;",
        '    rdfs:label "ArchiMate SKOS-annotaties"@nl , "ArchiMate SKOS annotations"@en ;',
        '    dcterms:source "BegrippenXL-begrippenkader ArchiMate (www.begrippenxl.nl/archimate)" ;',
        '    owl:versionInfo "0.2.0-concept" .',
        "",
    ]

    overgeslagen: list[str] = []
    problemen: list[str] = []
    telling = 0
    for concept in sorted(bron.subjects(rdflib.RDF.type, SKOS.Concept)):
        lokaal = str(concept).rsplit("/", 1)[-1]
        if lokaal in OVERSLAAN:
            overgeslagen.append(lokaal)
            continue
        naam = HERNOEMD.get(lokaal, lokaal)
        if naam not in bekend:
            problemen.append(f"geen am-klasse: {lokaal}")
            continue
        if naam not in DEFINITIE_NL:
            problemen.append(f"geen gecureerde definitie: {naam}")
            continue

        paren = ["skos:definition " + _lit(DEFINITIE_NL[naam], "nl")]
        # De Engelse rdfs:comment in de bron is de definitiezin uit de
        # specificatie; die hoort als Engelse definitie naast de Nederlandse.
        # Waar de bron er geen heeft, levert DEFINITIE_EN hem.
        en_gedaan = False
        for c in sorted(bron.objects(concept, rdflib.RDFS.comment), key=str):
            if (getattr(c, "language", None) or "en") == "en":
                paren.append("skos:definition " + _lit(str(c), "en"))
                en_gedaan = True
        if not en_gedaan and naam in DEFINITIE_EN:
            paren.append("skos:definition " + _lit(DEFINITIE_EN[naam], "en"))
        for n in sorted(bron.objects(concept, SKOS.scopeNote), key=str):
            taal = getattr(n, "language", None) or "nl"
            schoon = _zonder_boilerplate(str(n))
            if schoon:
                paren.append("skos:scopeNote " + _lit(schoon, taal))
        for img in sorted(bron.objects(concept, FOAF.img), key=str):
            paren.append(f"foaf:img <{img}>")
        paren.append(f"rdfs:seeAlso <{concept}>")

        telling += 1
        lijf = " ;\n    ".join(paren)
        regels.append(f"am:{naam}\n    {lijf} .\n")

    for naam in sorted(AANVULLING_40.keys() | EXTRA.keys()):
        if naam not in bekend:
            problemen.append(f"aanvulling zonder am-klasse: {naam}")
            continue
        nl, en = AANVULLING_40.get(naam) or EXTRA[naam]
        telling += 1
        regels.append(f"am:{naam}\n    skos:definition {_lit(nl, 'nl')} ;\n"
                      f"    skos:definition {_lit(en, 'en')} .\n")

    regels.insert(10, f"# {telling} klassen geannoteerd; overgeslagen "
                      f"(geen tegenhanger): {', '.join(sorted(overgeslagen))}.")
    if problemen:
        raise SystemExit("; ".join(sorted(problemen)))
    return "\n".join(regels)


def main() -> None:
    ttl = genereer()
    UIT.write_text(ttl, encoding="utf-8", newline="\n")
    print(f"geschreven: {UIT} ({len(ttl.splitlines())} regels)")


if __name__ == "__main__":
    main()
