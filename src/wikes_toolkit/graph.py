from __future__ import annotations

import networkx as nx


class Entity:
    def __init__(self, wikidata_id: str, wikidata_label: str | None = None, wikidata_description: str | None = None,
                 wikipdia_id: int | None = None, wikipdia_title: str | None = None, is_root: bool = False):
        self.__wikidata_id = wikidata_id
        self.__wikidata_label = wikidata_label
        self.__wikidata_description = wikidata_description
        self.__wikipdia_id = wikipdia_id
        self.__wikipdia_title = wikipdia_title
        self.__is_root = is_root

    @property
    def is_root(self) -> bool:
        return self.__is_root

    @property
    def wikidata_id(self) -> str:
        return self.__wikidata_id

    @property
    def wikidata_label(self) -> str | None:
        return self.__wikidata_label

    @property
    def wikidata_description(self) -> str | None:
        return self.__wikidata_description

    @property
    def wikipdia_id(self) -> int | None:
        return self.__wikipdia_id

    @property
    def wikipdia_title(self) -> str | None:
        return self.__wikipdia_title


class RootEntity(Entity):
    def __init__(self, wikidata_id: str, wikidata_label: str | None = None, wikidata_description: str | None = None,
                 wikipdia_id: int | None = None, wikipdia_title: str | None = None, category: str | None = None):
        super().__init__(wikidata_id, wikidata_label, wikidata_description, wikipdia_id, wikipdia_title, is_root=True, )
        self.__category = category

    @property
    def category(self) -> str:
        return self.__category


class Predicate:

    def __init__(self, predicate_id: str, predicate_label: str | None = None, predicate_description: str | None = None):
        self.__predicate_id = predicate_id
        self.__predicate_label = predicate_label
        self.__predicate_description = predicate_description

    @property
    def predicate_id(self) -> str:
        return self.__predicate_id

    @property
    def predicate_label(self) -> str:
        return self.__predicate_label

    @property
    def predicate_description(self) -> str:
        return self.__predicate_description


class Triple:

    def __init__(self, subject_entity: Entity | RootEntity, predicate: Predicate, object_entity: Entity | RootEntity):
        self.__subject_entity = subject_entity
        self.__predicate = predicate
        self.__object_entity = object_entity

    @property
    def subject_entity(self) -> Entity | RootEntity:
        return self.__subject_entity

    @property
    def predicate(self) -> Predicate:
        return self.__predicate

    @property
    def object_entity(self) -> Entity | RootEntity:
        return self.__object_entity


class WikESGraph:
    def __init__(self, G: nx.MultiDiGraph):
        self.__entities: dict[str, Entity] = {}
        self.__root_entities: dict[str, RootEntity] = {}

        self.__predicates: dict[str, Predicate] = {}
        self.__triples: dict[tuple[str, str, str], Triple] = {}
        self.__ground_truths: dict[str, set[Triple]] = {}

        self.__predicted_summaries: dict[str | RootEntity, set[Triple]] = {}
        self.__G: nx.MultiDiGraph = G
        self.__initialize()

    def __initialize(self):
        for node, data in self.__G.nodes(data=True):
            wikidata_label = data.get('wikidata_label', None)
            wikidata_description = data.get('wikidata_desc', None)
            wikipedia_id = data.get('wikipedia_id', None)
            wikipedia_title = data.get('wikipedia_title', None)
            category = data.get('category', None)
            if data.get('is_root', False):
                self.__root_entities[node] = RootEntity(
                    node, wikidata_label, wikidata_description, wikipedia_id, wikipedia_title, category
                )
                self.__entities[node] = self.__root_entities[node]
            else:
                self.__entities[node] = Entity(
                    node, wikidata_label, wikidata_description, wikipedia_id, wikipedia_title
                )

        for u, v, data in self.__G.edges(data=True):
            predicate = data.get('predicate')
            if predicate not in self.__predicates:
                predicate_label = data.get('predicate_label', None)
                predicate_description = data.get('predicate_desc', None)
                self.__predicates[predicate] = Predicate(
                    predicate, predicate_label, predicate_description
                )

            triple = Triple(
                self.__entities[u],
                self.__predicates[predicate],
                self.__entities[v]
            )
            self.__triples[(u, predicate, v)] = triple
            if 'summary_for' in data:
                summary_for_entity = data['summary_for']
                if summary_for_entity not in self.__ground_truths:
                    self.__ground_truths[summary_for_entity] = set()
                self.__ground_truths[summary_for_entity].add(triple)

    def root_entities(self) -> list[RootEntity]:
        return list(self.__root_entities.values())

    def entities(self) -> list[Entity]:
        return list(self.__entities.values())

    def triples(self) -> list[Triple]:
        return list(self.__triples.values())

    def predicates(self) -> list[Predicate]:
        return list(self.__predicates.values())

    def count_entities(self) -> int:
        return len(self.__entities)

    def count_triples(self) -> int:
        return len(self.__triples)

    def fetch_entity(self, wikidata_id: str) -> Entity | RootEntity:
        entity = self.__entities.get(wikidata_id, None)
        if entity is None:
            raise ValueError(f"Entity with wikidata_id: {wikidata_id} not found")
        return entity

    def fetch_triple(
            self,
            subject_entity: Entity | RootEntity | str,
            predicate: Predicate | str,
            object_entity: Entity | RootEntity | str) -> Triple:
        if isinstance(subject_entity, (Entity, RootEntity)):
            entity_id = subject_entity.wikidata_id
        else:
            entity_id = subject_entity
        if entity_id not in self.__entities:
            raise ValueError(f"Subject entity with wikidata_id: {entity_id} not found")
        subject_entity = self.__entities[entity_id]

        if isinstance(object_entity, (Entity, RootEntity)):
            entity_id = object_entity.wikidata_id
        else:
            entity_id = object_entity
        if entity_id not in self.__entities:
            raise ValueError(f"Object Entity with wikidata_id: {entity_id} not found")
        object_entity = self.__entities[entity_id]

        if isinstance(predicate, Predicate):
            predicate_id = predicate.predicate_id
        else:
            predicate_id = predicate
        if predicate_id not in self.__predicates:
            raise ValueError(f"Predicate with predicate_id: {predicate_id} not found")
        predicate = self.__predicates[predicate_id]

        if (subject_entity.wikidata_id, predicate.predicate_id, object_entity.wikidata_id) not in self.__triples:
            raise ValueError(
                f"Triple ({subject_entity.wikidata_id}, {predicate.predicate_id}, {object_entity.wikidata_id}) not found.")
        return self.__triples[(subject_entity.wikidata_id, predicate.predicate_id, object_entity.wikidata_id)]

    def neighbors(self, entity: Entity | RootEntity | str) -> list[Triple]:
        if isinstance(entity, (Entity, RootEntity)):
            entity_id = entity.wikidata_id
        else:
            entity_id = entity
        if entity_id not in self.__entities:
            raise ValueError(f"Entity with wikidata_id: {entity_id} not found")

        neighbors = [
            self.__triples[
                self.__entities[u].wikidata_id, data['predicate'], self.__entities[v].wikidata_id
            ] for u, v, data in self.__G.edges(entity_id, data=True)
        ]
        neighbors.extend([
            self.__triples[
                self.__entities[u].wikidata_id, data['predicate'], self.__entities[v].wikidata_id
            ] for u, v, data in self.__G.in_edges(entity_id, data=True)
        ])
        return neighbors

    def ground_truth_summaries(self, root_entity: RootEntity | str) -> set[Triple]:
        if isinstance(root_entity, RootEntity):
            root_entity_id = root_entity.wikidata_id
        elif isinstance(root_entity, str):
            root_entity_id = root_entity
        else:
            raise ValueError(
                "root_entity should be of type RootEntity or str (wikidata_id) but a non-root entity provided."
            )

        if root_entity_id not in self.__ground_truths:
            raise ValueError(
                f"No ground truth summaries found for root_entity: {root_entity_id}."
                f"Make sure the requested entity is a root entity."
            )
        return self.__ground_truths.get(root_entity_id)

    def mark_triple_as_summary(self, root_entity: RootEntity | str, triple: Triple | tuple[str, str, str]):
        if isinstance(root_entity, RootEntity):
            root_entity_id = root_entity.wikidata_id
        elif isinstance(root_entity, str):
            root_entity_id = root_entity
        else:
            raise ValueError(
                "root_entity should be of type RootEntity or str (wikidata_id) but non-root entity provided."
            )

        if root_entity_id not in self.__root_entities:
            raise ValueError(
                f"To mark a triple as summary, a root entity should be passed but the given entity is not a root."
            )

        if isinstance(triple, Triple):
            if ((triple.subject_entity.wikidata_id, triple.predicate.predicate_id, triple.object_entity.wikidata_id) not
                    in self.__triples):
                raise ValueError(f"Triple {triple} not found in the graph.")
        else:
            t = self.fetch_triple(triple[0], triple[1], triple[2])
            if not t:
                raise ValueError(f"Triple ({triple[0], triple[1], triple[2]}) not found in the graph.")
            triple = t

        if root_entity_id != triple.subject_entity.wikidata_id and root_entity_id != triple.object_entity.wikidata_id:
            raise ValueError(
                f"Root entity: {root_entity_id} should be either subject or object of the triple to be marked"
                f" as summary. Make sure the first hop neighbors of the root entity is being marked.")

        if root_entity_id not in self.__predicted_summaries:
            self.__predicted_summaries[root_entity_id] = set()
        self.__predicted_summaries[root_entity_id].add(triple)

    def mark_triples_as_summaries(self, root_entity: RootEntity | str, triples: list[Triple | tuple[str, str, str]]):
        for triple in triples:
            self.mark_triple_as_summary(root_entity, triple)
