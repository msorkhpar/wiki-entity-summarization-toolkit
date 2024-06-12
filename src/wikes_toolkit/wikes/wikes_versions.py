from wikes_toolkit.base.versions import DatasetName, DatasetVersion


class WikESVersions:

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

        get_all_subclasses(WikESVersions)
        return tuple(subclasses)

    class V1(DatasetVersion):
        version = '1.0.5'
        base_url = f'https://github.com/msorkhpar/wiki-entity-summarization/releases/download/{version}/'

        @staticmethod
        def get_dataset_url(dataset: DatasetName) -> str:
            return WikESVersions.V1.base_url + dataset.value + ".pkl"

        @staticmethod
        def get_version() -> str:
            return WikESVersions.V1.version

        class WikiLitArt(DatasetName):
            SMALL = 'WikiLitArt-s'
            SMALL_TRAIN = 'WikiLitArt-s-train'
            SMALL_VALIDATION = 'WikiLitArt-s-val'
            SMALL_TEST = 'WikiLitArt-s-test'
            MEDIUM = 'WikiLitArt-m'
            MEDIUM_TRAIN = 'WikiLitArt-m-train'
            MEDIUM_VALIDATION = 'WikiLitArt-m-val'
            MEDIUM_TEST = 'WikiLitArt-m-test'
            LARGE = 'WikiLitArt-l'
            LARGE_TRAIN = 'WikiLitArt-l-train'
            LARGE_VALIDATION = 'WikiLitArt-l-val'
            LARGE_TEST = 'WikiLitArt-l-test'

            def get_dataset_url(self):
                return WikESVersions.V1.get_dataset_url(self)

            def get_version(self):
                return WikESVersions.V1.get_version()

        class WikiCinema(DatasetName):
            SMALL = 'WikiCinema-s'
            SMALL_TRAIN = 'WikiCinema-s-train'
            SMALL_VALIDATION = 'WikiCinema-s-val'
            SMALL_TEST = 'WikiCinema-s-test'
            MEDIUM = 'WikiCinema-m'
            MEDIUM_TRAIN = 'WikiCinema-m-train'
            MEDIUM_VALIDATION = 'WikiCinema-m-val'
            MEDIUM_TEST = 'WikiCinema-m-test'
            LARGE = 'WikiCinema-l'
            LARGE_TRAIN = 'WikiCinema-l-train'
            LARGE_VALIDATION = 'WikiCinema-l-val'
            LARGE_TEST = 'WikiCinema-l-test'

            def get_dataset_url(self):
                return WikESVersions.V1.get_dataset_url(self)

            def get_version(self):
                return WikESVersions.V1.get_version()

        class WikiPro(DatasetName):
            SMALL = 'WikiPro-s'
            SMALL_TRAIN = 'WikiPro-s-train'
            SMALL_VALIDATION = 'WikiPro-s-val'
            SMALL_TEST = 'WikiPro-s-test'
            MEDIUM = 'WikiPro-m'
            MEDIUM_TRAIN = 'WikiPro-m-train'
            MEDIUM_VALIDATION = 'WikiPro-m-val'
            MEDIUM_TEST = 'WikiPro-m-test'
            LARGE = 'WikiPro-l'
            LARGE_TRAIN = 'WikiPro-l-train'
            LARGE_VALIDATION = 'WikiPro-l-val'
            LARGE_TEST = 'WikiPro-l-test'

            def get_dataset_url(self):
                return WikESVersions.V1.get_dataset_url(self)

            def get_version(self):
                return WikESVersions.V1.get_version()

        class WikiProFem(DatasetName):
            SMALL = 'WikiProFem-s'
            SMALL_TRAIN = 'WikiProFem-s-train'
            SMALL_VALIDATION = 'WikiProFem-s-val'
            SMALL_TEST = 'WikiProFem-s-test'
            MEDIUM = 'WikiProFem-m'
            MEDIUM_TRAIN = 'WikiProFem-m-train'
            MEDIUM_VALIDATION = 'WikiProFem-m-val'
            MEDIUM_TEST = 'WikiProFem-m-test'
            LARGE = 'WikiProFem-l'
            LARGE_TRAIN = 'WikiProFem-l-train'
            LARGE_VALIDATION = 'WikiProFem-l-val'
            LARGE_TEST = 'WikiProFem-l-test'

            def get_dataset_url(self):
                return WikESVersions.V1.get_dataset_url(self)

            def get_version(self):
                return WikESVersions.V1.get_version()
