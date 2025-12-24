

Machine-translated Dutch version below:

## InstaGibbs

Instagibbs is a software project aimed at fast and interactive analysis and visualiztion of HDX-MS datasets. 

HDX-MS is one of the few experimental techniques which can identify with high resolution which parts of a protein are flexible or rather rigid. Moreover, when the experiment is carried out in the presence of drug candidates, it can be measured how the dynamics of the protein are altered in response to the drug. This gives information is critical in drug discovery and therefore HDX-MS is a ubiquitous analytical tool employed across the pharmaceutical industry.

HDX-MS datasets, however, don't provide direct residue-level information but instead requires processing steps to be visualized and interpreted. Current processing pipelines are nonstandardized, require long computational times or require user parameter input. 

InstaGibbs solves these problems by calculating a standard Gibbs free energy per residue within approximately 100 milliseconds for a single protein dataset. The results are directly visualized in an interactive web applications, linked to a database such that available datasets can be directly visualized. 

The project is my independent work and at the moment I am the sole author. It is at the stage of a working alpha-version where algorithms are implemented and there is a working although not polished web application interface. 

Data processing algorithms are based on work previously published by others, and they might become co-author of an academic publication at some point. 

At the moment the code is closed source, and because of the wide applicabilty in pharmaceutical companies I'm exploring the option of releasing (part) of the project under a commercial license. For example, data-processing backend code could be released under MIT while front-end webapplication is free only for academic use. There can then be a hosted free version which connects to a public database of HDX-MS datasets (see below), but for commercial parties to host their own and/or connect their own databases would require a commercial license.  

## HDX-MS datasets

'HDX-MS datasets' (needs a name) is aimed to provide a standardized format for HDX-MS datasets. It aims to collect HDX-MS datasets at the peptide level, after preprocessing steps determining deuterium uptake per peptide per timepoint has been completed. These datasets will be catalogues together with metadata containing all information relating to experimental condition as well as link to related publications and raw data. 

This database would be open for researchers to submit their data which should be/will be formatted to the database specifications. My questions here are:

1. There are datasets already published, for example under the Create Commons Public Domain. Is it allowed to take these datasets, reformat them, of course keep author attributions / backlinks to original deposited dataset, and put them in the 'HDX-MS datasets' database?

2. What license should be added when other submit datasets to 'HDX-MS datasets'; should there be several to choose from, should there be the possibility to for example opt-out from training AI models? 


-----


## InstaGibbs

InstaGibbs is een softwareproject gericht op snelle en interactieve analyse en visualisatie van HDX-MS datasets.

HDX-MS is een van de weinige experimentele technieken die met hoge resolutie kunnen identificeren welke delen van een eiwit flexibel of juist star zijn. Bovendien kan, wanneer het experiment wordt uitgevoerd in aanwezigheid van kandidaat-geneesmiddelen, worden gemeten hoe de dynamiek van het eiwit verandert in reactie op het geneesmiddel. Deze informatie is cruciaal bij geneesmiddelenonderzoek en daarom is HDX-MS een alomtegenwoordig analytisch instrument dat in de hele farmaceutische industrie wordt gebruikt.

HDX-MS datasets leveren echter geen directe informatie op residuniveau, maar vereisen verwerkingsstappen om gevisualiseerd en geïnterpreteerd te worden. Huidige verwerkingspijplijnen zijn niet gestandaardiseerd, vereisen lange rekentijden of vereisen invoer van gebruikersparameters.

InstaGibbs lost deze problemen op door een standaard Gibbs vrije energie per residu te berekenen binnen ongeveer 100 milliseconden voor een enkele eiwitdataset. De resultaten worden direct gevisualiseerd in interactieve webapplicaties, gekoppeld aan een database zodat beschikbare datasets direct kunnen worden gevisualiseerd.

Het project is mijn onafhankelijke werk en op dit moment ben ik de enige auteur. Het bevindt zich in het stadium van een werkende alfa-versie waarbij algoritmen zijn geïmplementeerd en er een werkende, zij het niet gepolijste, webapplicatie-interface is.

Dataverwerkingsalgoritmen zijn gebaseerd op eerder gepubliceerd werk van anderen, en zij kunnen op een gegeven moment co-auteur worden van een academische publicatie.

Op dit moment is de code closed source, en vanwege de brede toepasbaarheid in farmaceutische bedrijven onderzoek ik de mogelijkheid om (een deel van) het project onder een commerciële licentie uit te brengen. Bijvoorbeeld, de backend-code voor dataverwerking zou kunnen worden vrijgegeven onder MIT, terwijl de frontend-webapplicatie alleen gratis is voor academisch gebruik. Er kan dan een gehoste gratis versie zijn die verbinding maakt met een publieke database van HDX-MS datasets (zie hieronder), maar voor commerciële partijen om hun eigen databases te hosten en/of er verbinding mee te maken, zou een commerciële licentie vereist zijn.

## HDX-MS datasets

'HDX-MS datasets' (heeft een naam nodig) is gericht op het bieden van een gestandaardiseerd formaat voor HDX-MS datasets. Het doel is om HDX-MS datasets op peptidenniveau te verzamelen, nadat de voorverwerkingsstappen voor het bepalen van de deuteriumopname per peptide per tijdspunt zijn voltooid. Deze datasets zullen worden gecatalogiseerd samen met metadata die alle informatie bevatten met betrekking tot de experimentele condities, evenals links naar gerelateerde publicaties en ruwe data.

Deze database zou open zijn voor onderzoekers om hun gegevens in te dienen, die moeten worden/zullen worden geformatteerd volgens de databasespecificaties. Mijn vragen hierbij zijn:

1. Er zijn al datasets gepubliceerd, bijvoorbeeld onder de Creative Commons Public Domain. Is het toegestaan om deze datasets te nemen, ze te herformatteren, uiteraard met behoud van auteursattributies / backlinks naar de oorspronkelijk gedeponeerde dataset, en ze in de 'HDX-MS datasets' database te plaatsen?

2. Welke licentie moet worden toegevoegd wanneer anderen datasets indienen bij 'HDX-MS datasets'; moeten er meerdere zijn om uit te kiezen, moet er de mogelijkheid zijn om bijvoorbeeld te kiezen voor opt-out van training van AI-modellen?

