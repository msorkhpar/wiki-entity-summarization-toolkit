import logging
import os
import pickle

import networkx as nx
import pandas as pd

logger = logging.getLogger(__name__)


def assign_ids(df, new_identifier_col_name=None):
    df['id'] = range(len(df))
    df.reset_index(inplace=True)
    df.set_index('id', inplace=True)
    if new_identifier_col_name:
        df.rename(columns={'identifier': new_identifier_col_name}, inplace=True)


def map_column_to_ids(df, column, mapping):
    df[column] = df[column].map(mapping)


def export(output_path: str, dataset_name: str, G: nx.MultiDiGraph, entities: pd.DataFrame, root_nodes: pd.DataFrame,
           triples: pd.DataFrame, predicates: pd.DataFrame, ground_truths: pd.DataFrame):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    assign_ids(entities, 'entity')
    assign_ids(root_nodes, 'entity')
    assign_ids(predicates, 'predicate')
    assign_ids(ground_truths, 'root_entity')

    map_entity_to_id = {v: k for k, v in entities['entity'].to_dict().items()}
    map_predicate_to_id = {v: k for k, v in predicates['predicate'].to_dict().items()}

    map_column_to_ids(root_nodes, 'entity', map_entity_to_id)
    map_column_to_ids(triples, 'subject', map_entity_to_id)
    map_column_to_ids(triples, 'object', map_entity_to_id)
    map_column_to_ids(triples, 'predicate', map_predicate_to_id)
    map_column_to_ids(ground_truths, 'root_entity', map_entity_to_id)
    map_column_to_ids(ground_truths, 'subject', map_entity_to_id)
    map_column_to_ids(ground_truths, 'object', map_entity_to_id)
    map_column_to_ids(ground_truths, 'predicate', map_predicate_to_id)

    root_nodes.drop(
        columns=['wikidata_label', 'wikidata_description', 'wikipedia_id', 'wikipedia_title'],
        inplace=True
    )

    output_path_dir = os.path.join(output_path, dataset_name)
    os.makedirs(output_path_dir, exist_ok=True)

    logger.info(f"Exporting to {output_path_dir}")

    entities.to_csv(os.path.join(output_path_dir, f'{dataset_name}__entities.csv'))
    predicates.to_csv(os.path.join(output_path_dir, f'{dataset_name}__predicates.csv'))
    root_nodes.to_csv(os.path.join(output_path_dir, f'{dataset_name}__root_entities.csv'), index=False)
    triples.to_csv(os.path.join(output_path_dir, f'{dataset_name}__triples.csv'), index=False)
    ground_truths.to_csv(os.path.join(output_path_dir, f'{dataset_name}__ground_truths.csv'), index=False)

    nx.write_graphml(G, os.path.join(output_path, f'{dataset_name}.graphml'))

    with open(os.path.join(output_path, f'{dataset_name}.pkl'), 'wb') as f:
        pickle.dump(G, f)

    logger.debug(f"Exported {dataset_name} to {output_path_dir} successfully.")
