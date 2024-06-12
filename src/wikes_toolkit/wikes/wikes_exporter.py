import logging
import os
import shutil

import networkx as nx
import pandas as pd
from filehash import FileHash

from wikes_toolkit.base.versions import DatasetName

logger = logging.getLogger(__name__)


def assign_ids(df, new_identifier_col_name=None):
    df['id'] = range(len(df))
    df.reset_index(inplace=True)
    df.set_index('id', inplace=True)
    if new_identifier_col_name:
        df.rename(columns={'identifier': new_identifier_col_name}, inplace=True)


def map_column_to_ids(df, column, mapping):
    df[column] = df[column].map(mapping)


def export(
        output_path: str,
        license_path: str,
        G: nx.MultiDiGraph,
        dataset: DatasetName,
        entities: pd.DataFrame,
        root_nodes: pd.DataFrame,
        triples: pd.DataFrame, predicates: pd.DataFrame, ground_truths: pd.DataFrame) -> str:
    dataset_name = dataset.value
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

    output_csv_path = os.path.join(output_path, dataset_name)
    os.makedirs(output_csv_path, exist_ok=True)

    logger.info(f"Exporting to {output_csv_path}")

    entities.to_csv(os.path.join(output_csv_path, f'{dataset_name}-entities.csv'))
    predicates.to_csv(os.path.join(output_csv_path, f'{dataset_name}-predicates.csv'))
    root_nodes.to_csv(os.path.join(output_csv_path, f'{dataset_name}-root-entities.csv'), index=False)
    triples.to_csv(os.path.join(output_csv_path, f'{dataset_name}-triples.csv'), index=False)
    ground_truths.to_csv(os.path.join(output_csv_path, f'{dataset_name}-ground-truths.csv'),
                         index=False)
    shutil.copy(license_path, os.path.join(output_csv_path, 'LICENSE'))
    shutil.make_archive(output_csv_path, 'zip', output_csv_path)
    shutil.rmtree(output_csv_path)
    nx.write_graphml(G, os.path.join(output_path, f'{dataset_name}.graphml'))

    logger.debug(f"Exported {dataset_name} to {output_csv_path} successfully.")
    return FileHash('sha256').hash_file(os.path.join(output_path, f'{dataset_name}.zip'))
