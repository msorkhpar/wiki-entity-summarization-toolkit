# wiki-entity-summarization-toolkit

![PyPI - Status](https://img.shields.io/pypi/status/wikes-toolkit)![PyPI - Downloads](https://img.shields.io/pypi/dm/wikes-toolkit)![GitHub License](https://img.shields.io/github/license/msorkhpar/wiki-entity-summarization-toolkit)[![arXiv](https://img.shields.io/badge/arXiv-2406.08435-B31B1B.svg)](https://doi.org/10.48550/arXiv.2406.08435)

A user-friendly toolkit for the Wiki-Entity-Summarization (WikES) and ESBM datasets.

## Parent project

This toolkit is part of the
[Wiki-Entity-Summarization project (WikES)](https://github.com/msorkhpar/wiki-entity-summarization).

## Installation

```bash
pip install wikes-toolkit
```

## Usage

### WikES usage (object based)

Using this toolkit with Object-Oriented Programming (OOP) is straightforward. </br>

Here is an example of how to use it:

```python
from wikes_toolkit import WikESToolkit, WikESVersions, WikESGraph

toolkit = WikESToolkit(save_path="./data")  # save_path is optional
G = toolkit.load_graph(
    WikESGraph,
    WikESVersions.V1.WikiCinema.SMALL,
    entity_formatter=lambda e: f"Entity({e.wikidata_label})",
    predicate_formatter=lambda p: f"Predicate({p.label})",
    triple_formatter=lambda
        t: f"({t.subject_entity.wikidata_label})-[{t.predicate.label}]-> ({t.object_entity.wikidata_label})"
)

root_nodes = G.root_entities()
nodes = G.entities()
nx_graph = G._G
edges = G.triples()
labels = G.predicates()
number_of_nodes = G.total_entities()
number_of_directed_edges = G.total_triples()
node = G.fetch_entity('Q303')
node_degree = G.degree('Q303')
neighbors = G.ground_truths(node)
ground_truth_summaries = G.ground_truths(root_nodes[0])
G.mark_triple_as_summary(edges[0].subject_entity, edges[0])

for root in G.root_entities():
    print(f"Neighbors of [{root}]:")
    for triple in G.neighbors(root):
        print(triple)

    for _ in range(5):
        print("*" * 40)

    print("Ground truth summaries:")
    for summary in G.ground_truths(root):
        print(summary)
    G.mark_triples_as_summaries(root, G.neighbors(root))
    break

f1 = G.f1_score()
f1_5 = G.f1_score(5)
f1_10 = G.f1_score(10)
map = G.map_score()
map_5 = G.map_score(5)
map_10 = G.map_score(10)
""" Output of the above code:
Neighbors of [Entity(Elvis Presley)]:
(Elvis Presley)-[military unit]-> (32nd Cavalry Regiment)
(Elvis Presley)-[genre]-> (blues)
...
(Jim Morrison)-[influenced by]-> (Elvis Presley)
(Elvis Country – I'm 10,000 Years Old)-[performer]-> (Elvis Presley)
(The King)-[main subject]-> (Elvis Presley)
****************************************
Ground truth summaries:
(Elvis Presley)-[genre]-> (rockabilly)
(Million Dollar Quartet)-[has part(s)]-> (Elvis Presley)
(Jailhouse Rock)-[cast member]-> (Elvis Presley)
...
(Viva Las Vegas)-[cast member]-> (Elvis Presley)
(Elvis Presley)-[genre]-> (rhythm and blues)
(Elvis Presley)-[record label]-> (Sun Records)
(Elvis Presley)-[genre]-> (pop music)
"""
```

To load all graphs, you can use the `load_all_graphs` method:

```python
from wikes_toolkit import WikESToolkit, WikESVersions, WikESGraph

for dataset_name, G in WikESToolkit(save_path="./data").load_all_graphs(WikESGraph, WikESVersions.V1):
    print(f"Dataset [{dataset_name}:")
    print(G.total_entities())
```

### Pandas usage

There is another version of this toolkit that uses Pandas DataFrame to store the graph data. To use this version, you
can change the first parameter of the `load_graph` method to `PandasWikESGraph`:

```python
from wikes_toolkit import WikESToolkit, PandasWikESGraph, WikESVersions

toolkit = WikESToolkit()
G = toolkit.load_graph(PandasWikESGraph, WikESVersions.V1.WikiLitArt.SMALL, entity_formatter=lambda e: e.identifier)

root_nodes = G.root_entities()
first_root_node = G.root_entity_ids()[0]
nodes = G.entities()
edges = G.triples()
first_edge = G.fetch_triple(edges.iloc[0])
labels = G.predicates()
number_of_nodes = G.total_entities()
number_of_directed_edges = G.total_triples()
node = G.fetch_entity('Q303')
node_degree = G.degree('Q303')
ground_truths = G.ground_truths(node)
neighbors = G.neighbors(node)
ground_truth_summaries = G.ground_truths(first_root_node)
G.mark_triple_as_summary(
    ground_truths.iloc[0].name,
    (ground_truths.iloc[0]['subject'], ground_truths.iloc[0]['predicate'], ground_truths.iloc[0]['object'])
)
G.mark_triples_as_summaries(node, neighbors.iloc[0:2])
f1 = G.f1_score()
f1_5 = G.f1_score(5)
f1_10 = G.f1_score(10)
map = G.map_score()
map_norel = G.map_score(no_rel=True)
map_5 = G.map_score(5)
map_10 = G.map_score(10)
G.clear_summaries()

```

### Export WikESGraphs as CSV files

You can export the graphs as CSV files using the `export_as_csv` method. This method exports the graph as three CSV
files:

```python
from wikes_toolkit import WikESToolkit, WikESVersions, PandasWikESGraph

toolkit = WikESToolkit()

for dataset, G in toolkit.load_all_graphs(PandasWikESGraph, WikESVersions.V1):
    G.export_as_csv("./data")
```

**Note: This method has been implemented for WikESPandasGraph, others yet to be implemented.**

## ESBM

We also cover ESBM datasets with almost the same functionalities and syntax as before. If you want to check how we have
converted ESBM datasets to NetworkX format, or if you want to use GraphML formats of this dataset,
check [ESBM-to-nx-format](https://github.com/msorkhpar/ESBM-to-nx-format) repository.</br>

Here is an example of loading ESBM and ESM_Plus datasets with this toolkit:

```python
from wikes_toolkit import WikESToolkit, ESBMGraph, ESBMVersions

toolkit = WikESToolkit()
G = toolkit.load_graph(
    ESBMGraph,
    ESBMVersions.Plus.DBPEDIA_FULL,  # or ESBMVersions.Plus.DBPEDIA_FULL, ESBMVersions.V1Dot2.LMDB_TRAIN_1, etc.
    entity_formatter=lambda e: e.identifier
)

root_nodes = G.root_entities()
first_root_node = G.root_entity_ids()[0]
nodes = G.entities()
edges = G.triples()
labels = G.predicates()
number_of_nodes = G.total_entities()
number_of_directed_edges = G.total_triples()
node = G.fetch_entity('http://dbpedia.org/resource/Adrian_Griffin')
node_degree = G.degree('http://dbpedia.org/resource/Adrian_Griffin')
gold_top5_0 = G.gold_top_5(node, 0)
gold_top10_0 = G.gold_top_10(node, 0)
neighbors = G.neighbors(node)  # or G.neighbors('http://dbpedia.org/resource/Adrian_Griffin')

G.mark_triples_as_summaries(
    "http://dbpedia.org/resource/3WAY_FM",
    [
        (
            'http://dbpedia.org/resource/3WAY_FM',
            'http://purl.org/dc/terms/subject',
            'http://dbpedia.org/resource/Category:Radio_stations_in_Victoria'
        ),
        (
            'http://dbpedia.org/resource/3WAY_FM',
            'http://xmlns.com/foaf/0.1/homepage',
            'http://3wayfm.org.au'
        ),
        (
            'http://dbpedia.org/resource/3WAY_FM',
            'http://dbpedia.org/ontology/broadcastArea',
            'http://dbpedia.org/resource/Victoria_(Australia)'
        ),
        (
            'http://dbpedia.org/resource/3WAY_FM',
            'http://dbpedia.org/ontology/callsignMeaning',
            '3 - Victoria'
        ),
        (
            'http://dbpedia.org/resource/3WAY_FM',
            'http://xmlns.com/foaf/0.1/name',
            '3WAY FM@en'
        ),
        (
            'http://dbpedia.org/resource/3WAY_FM',
            'http://www.w3.org/2000/01/rdf-schema#label',
            '3WAY FM@en'
        ),
        (
            'http://dbpedia.org/resource/3WAY_FM',
            'http://dbpedia.org/ontology/callsignMeaning',
            'Warrnambool And You'
        ),
        (
            'http://dbpedia.org/resource/3WAY_FM',
            'http://dbpedia.org/ontology/broadcastArea',
            'http://dbpedia.org/resource/Warrnambool'
        ),
        (
            'http://dbpedia.org/resource/3WAY_FM',
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
            'http://schema.org/RadioStation'
        ),
        (
            'http://dbpedia.org/resource/3WAY_FM',
            'http://purl.org/dc/terms/subject',
            'http://dbpedia.org/resource/Category:Radio_stations_established_in_1990'
        )]
)

G.clear_summaries()

G.mark_triples_as_summaries(
    "http://dbpedia.org/resource/3WAY_FM",
    [(
        'http://dbpedia.org/resource/3WAY_FM',
        'http://purl.org/dc/terms/subject',
        'http://dbpedia.org/resource/Category:Radio_stations_in_Victoria'
    )]
)

G.mark_triples_as_summaries(
    "http://dbpedia.org/resource/Adrian_Griffin",
    [
        (
            'http://dbpedia.org/resource/Adrian_Griffin',
            'http://dbpedia.org/ontology/activeYearsEndYear',
            '2008'
        ),
        (
            'http://dbpedia.org/resource/Adrian_Griffin',
            'http://purl.org/dc/terms/subject',
            'http://dbpedia.org/resource/Category:Orlando_Magic_assistant_coaches'
        ),
        (
            'http://dbpedia.org/resource/Adrian_Griffin',
            'http://dbpedia.org/ontology/birthDate',
            '1974-07-04'
        ),
        (
            'http://dbpedia.org/resource/Adrian_Griffin',
            'http://dbpedia.org/ontology/height',
            '1.9558'
        ),
        (
            'http://dbpedia.org/resource/Adrian_Griffin',
            'http://dbpedia.org/ontology/weight',
            '98431.2'
        ),
        (
            'http://dbpedia.org/resource/Adrian_Griffin',
            'http://dbpedia.org/ontology/team',
            'http://dbpedia.org/resource/Orlando_Magic'
        ),
        (
            'http://dbpedia.org/resource/Adrian_Griffin',
            'http://purl.org/dc/terms/subject',
            'http://dbpedia.org/resource/Category:Basketball_players_from_Kansas'
        ),
        (
            'http://dbpedia.org/resource/Adrian_Griffin',
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
            'http://dbpedia.org/class/yago/BasketballPlayersFromKansas'
        ),
        (
            'http://dbpedia.org/resource/Adrian_Griffin',
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
            'http://dbpedia.org/class/yago/BasketballCoach109841955'
        ),
        (
            'http://dbpedia.org/resource/Adrian_Griffin',
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
            'http://dbpedia.org/class/yago/BasketballPlayer109842047'
        ),
    ]
)

f1_5 = G.f1_score(5)
f1_10 = G.f1_score(10)
map_5 = G.map_score(5)
map_10 = G.map_score(10)
```

#### Using Ranked NT File as Summary (Legacy Support)

Although this toolkit can process triples marked with `.nt` ranked files, we don't recommend using this feature as it
doesn't align with our toolkit's core approach.


```python
from wikes_toolkit import WikESToolkit, PandasESBMGraph, ESBMGraph, ESBMVersions

toolkit = WikESToolkit()
G = toolkit.load_graph(
    ESBMGraph, # or PandasESBMGraph
    ESBMVersions.V1Dot2.DBPEDIA_FULL,
    entity_formatter=lambda e: e.identifier,
)

# Mark summaries for '3WAY_FM'
G.mark_nt_file_as_summary(
    1,  # '3WAY_FM' eid
    './result/dbpedia/1/1_rank.nt'  # .nt file path
)

# Mark summaries for 'Adrian_Griffin'
G.mark_nt_file_as_summary(
    'http://dbpedia.org/resource/Adrian_Griffin',  # ESBM entity name
    './result/dbpedia/2/2_rank.nt'  # .nt file path
)

f1_5 = G.f1_score(5)
f1_10 = G.f1_score(10)

```

### ESBM Pandas usage

For Pandas version of ESBM datasets, you can use `PandasESBMGraph` instead of `ESBMGraph`:

```python
from wikes_toolkit import WikESToolkit, PandasESBMGraph, ESBMVersions
import pandas as pd

toolkit = WikESToolkit()
G = toolkit.load_graph(PandasESBMGraph, ESBMVersions.V1Dot2.DBPEDIA_FULL, entity_formatter=lambda e: e.identifier)

first_root_node_id = G.root_entity_ids()[0]
root_nodes = G.root_entities()
first_root_node = G.root_entities().iloc[0]
nodes = G.entities()
edges = G.triples()
labels = G.predicates()
number_of_nodes = G.total_entities()
number_of_directed_edges = G.total_triples()
node = G.fetch_entity('http://dbpedia.org/resource/Adrian_Griffin')
node_degree = G.degree('http://dbpedia.org/resource/Adrian_Griffin')
gold_top5_0 = G.gold_top_5(node, 0)
gold_top10_0 = G.gold_top_10(node, 0)
neighbors = G.neighbors(node)
all_golds = G.all_gold_top_k(5)
golds = G.gold_top_5(G.root_entities().iloc[0], 4)

G.mark_triples_as_summaries(
    "http://dbpedia.org/resource/Adrian_Griffin",
    pd.Series(
        [
            'http://dbpedia.org/resource/Adrian_Griffin',
            'http://dbpedia.org/ontology/activeYearsEndYear',
            '2008'
        ],
        index=['subject', 'predicate', 'object']
    )
)
f1_5 = G.f1_score(5)

```

## Citation

If you use this project in your research, please cite the following paper:

```bibtex
@misc{javadi2024wiki,
    title = {Wiki Entity Summarization Benchmark},
    author = {Saeedeh Javadi and Atefeh Moradan and Mohammad Sorkhpar and Klim Zaporojets and Davide Mottin and Ira Assent},
    year = {2024},
    eprint = {2406.08435},
    archivePrefix = {arXiv},
    primaryClass = {cs.IR}
}
```

In case you use ESBM datasets, please cite their paper as well ours:

```bibtex
@inproceedings{esbm,
    author = {Qingxia Liu and
 Gong Cheng and
 Kalpa Gunaratna and
 Yuzhong Qu},
    title = {ESBM: An Entity Summarization Benchmark},
    booktitle = {ESWC},
    year = {2020}
}
``` 

## License

This project is licensed under the CC-BY-4.0 License. See the [LICENSE](LICENSE) file for details.
Also, you can check ESBM license [here](https://github.com/nju-websoft/ESBM/blob/master/LICENSE.txt)
or [here](https://opendatacommons.org/licenses/by/1-0/index.html).
