from wikes_toolkit.base.versions import DatasetVersion, DatasetName


class ESBMVersions(DatasetVersion):
    base_url = 'https://github.com/msorkhpar/ESBM-to-nx-format/releases/download/ESBM/'

    @staticmethod
    def available_versions():
        subclasses = set()

        def get_all_subclasses(cls):
            for attr_name in dir(cls):
                attr = getattr(cls, attr_name)
                if isinstance(attr, type) and issubclass(attr, DatasetVersion):
                    get_all_subclasses(attr)
                elif isinstance(attr, type) and issubclass(attr, DatasetName):
                    subclasses.add(attr)

        get_all_subclasses(ESBMVersions)
        return tuple(subclasses)

    @staticmethod
    def get_dataset_url(dataset: DatasetName) -> str:
        return ESBMVersions.base_url + dataset.value + ".pkl"

    class V1Dot0(DatasetName):
        DBPEDIA_FULL = 'v1_0_dbpedia_full'
        LMDB_FULL = 'v1_0_lmdb_full'

        def get_dataset_url(self):
            return ESBMVersions.get_dataset_url(self)

    class V1Dot1(DatasetName):
        DBPEDIA_FULL = 'v1_1_dbpedia_full'
        LMDB_FULL = 'v1_1_lmdb_full'

        def get_dataset_url(self):
            return ESBMVersions.get_dataset_url(self)

    class V1Dot2(DatasetName):
        DBPEDIA_FULL = 'v1_2_dbpedia_full'
        LMDB_FULL = 'v1_2_linkedmdb_full'

        DBPEDIA_TRAIN_0 = 'v1_2_dbpedia_train_0'
        DBPEDIA_VALIDATION_0 = 'v1_2_dbpedia_val_0'
        DBPEDIA_TEST_0 = 'v1_2_dbpedia_test_0'
        LMDB_TRAIN_0 = 'v1_2_linkedmdb_train_0'
        LMDB_VALIDATION_0 = 'v1_2_linkedmdb_val_0'
        LMDB_TEST_0 = 'v1_2_linkedmdb_test_0'

        DBPEDIA_TRAIN_1 = 'v1_2_dbpedia_train_1'
        DBPEDIA_VALIDATION_1 = 'v1_2_dbpedia_val_1'
        DBPEDIA_TEST_1 = 'v1_2_dbpedia_test_1'
        LMDB_TRAIN_1 = 'v1_2_lmdb_full_1'
        LMDB_VALIDATION_1 = 'v1_2_linkedmdb_val_1'
        LMDB_TEST_1 = 'v1_2_linkedmdb_test_1'

        DBPEDIA_TRAIN_2 = 'v1_2_dbpedia_train_2'
        DBPEDIA_VALIDATION_2 = 'v1_2_dbpedia_val_2'
        DBPEDIA_TEST_2 = 'v1_2_dbpedia_test_2'
        LMDB_TRAIN_2 = 'v1_2_linkedmdb_train_2'
        LMDB_VALIDATION_2 = 'v1_2_linkedmdb_val_2'
        LMDB_TEST_2 = 'v1_2_linkedmdb_test_2'

        DBPEDIA_TRAIN_3 = 'v1_2_dbpedia_train_3'
        DBPEDIA_VALIDATION_3 = 'v1_2_dbpedia_val_3'
        DBPEDIA_TEST_3 = 'v1_2_dbpedia_test_3'
        LMDB_TRAIN_3 = 'v1_2_linkedmdb_train_3'
        LMDB_VALIDATION_3 = 'v1_2_linkedmdb_val_3'
        LMDB_TEST_3 = 'v1_2_linkedmdb_test_3'

        DBPEDIA_TRAIN_4 = 'v1_2_dbpedia_train_4'
        DBPEDIA_VALIDATION_4 = 'v1_2_dbpedia_val_4'
        DBPEDIA_TEST_4 = 'v1_2_dbpedia_test_4'
        LMDB_TRAIN_4 = 'v1_2_linkedmdb_train_4'
        LMDB_VALIDATION_4 = 'v1_2_linkedmdb_val_4'
        LMDB_TEST_4 = 'v1_2_linkedmdb_test_4'

        def get_dataset_url(self):
            return ESBMVersions.get_dataset_url(self)
