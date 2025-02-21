import os
import pytest
from random import randrange

from ingest_igaps import run as run_igaps
from ingest_ptf_matchfiles import run as run_ptf_matchfiles
from ingest_vlass import run as run_vlass
from ingest_ztf_matchfiles import run as run_ztf_matchfiles
from ingest_ztf_public import run as run_ztf_public
from ingest_ztf_source_features import run as run_ztf_source_features
from ingest_ztf_source_classifications import run as run_ztf_source_classifications
from utils import get_default_args, load_config, log, Mongo


""" load config and secrets """
KOWALSKI_APP_PATH = os.environ.get("KOWALSKI_APP_PATH", "/app")
KOWALSKI_DATA_PATH = os.environ.get("KOWALSKI_DATA_PATH", "/app/data")
config = load_config(path=KOWALSKI_APP_PATH, config_file="config.yaml")["kowalski"]


@pytest.fixture(autouse=True, scope="class")
def mongo_fixture(request):
    log("Connecting to DB")
    mongo = Mongo(
        host=config["database"]["host"],
        port=config["database"]["port"],
        replica_set=config["database"]["replica_set"],
        username=config["database"]["username"],
        password=config["database"]["password"],
        db=config["database"]["db"],
        verbose=True,
    )
    log("Successfully connected")

    request.cls.mongo = mongo


class TestTools:
    """
    Test (mostly data ingestion) tools
    """

    def test_ingest_ztf_source_features(self):
        tag = get_default_args(run_ztf_source_features).get("tag")
        collection = f"ZTF_source_features_{tag}"

        run_ztf_source_features(
            path=f"{KOWALSKI_DATA_PATH}/ztf_source_features",
            tag=tag,
            xmatch=False,
            num_processes=1,
        )

        ingested_entries = list(self.mongo.db[collection].find({}, {"_id": 1}))
        log(f"Ingested features of {len(ingested_entries)} sources")

        assert len(ingested_entries) == 123

    def test_ingest_ztf_source_classifications(self):
        tag = get_default_args(run_ztf_source_classifications).get("tag")
        collection = f"ZTF_source_classifications_{tag}"

        run_ztf_source_classifications(
            path=f"{KOWALSKI_DATA_PATH}/ztf_source_classifications/",
            tag=tag,
            num_processes=1,
        )

        ingested_entries = list(self.mongo.db[collection].find({}, {"_id": 1}))
        log(f"Ingested classifications of {len(ingested_entries)} sources")

        assert len(ingested_entries) == 9875

    def test_ingest_ztf_matchfiles(self):
        tag = str(randrange(10000000, 99999999, 1))
        sources_collection = f"ZTF_sources_{tag}"
        exposures_collection = f"ZTF_exposures_{tag}"
        run_ztf_matchfiles(
            path=f"{KOWALSKI_DATA_PATH}/ztf_matchfiles",
            tag=tag,
            num_proc=1,
        )

        ingested_sources = list(self.mongo.db[sources_collection].find({}, {"_id": 1}))
        ingested_exposures = list(
            self.mongo.db[exposures_collection].find({}, {"_id": 1})
        )
        log(f"Ingested lightcurves for {len(ingested_sources)} sources")
        log(f"Ingested {len(ingested_exposures)} exposures")

        assert len(ingested_sources) == 16
        assert len(ingested_exposures) == 10

    def test_ingest_vlass(self):
        collection = "VLASS_DR1"

        run_vlass(
            path=f"{KOWALSKI_DATA_PATH}/catalogs",
            num_processes=1,
        )

        ingested_entries = list(self.mongo.db[collection].find({}, {"_id": 1}))
        log(f"Ingested features of {len(ingested_entries)} sources")

        assert len(ingested_entries) == 27

    def test_ingest_igaps(self):
        collection = "IGAPS_DR2"

        run_igaps(
            path=f"{KOWALSKI_DATA_PATH}/catalogs",
            num_processes=1,
        )

        ingested_entries = list(self.mongo.db[collection].find({}, {"_id": 1}))
        log(f"Ingested features of {len(ingested_entries)} sources")

        assert len(ingested_entries) == 100

    def test_ingest_ztf_public(self):
        tag = get_default_args(run_ztf_public).get("tag")
        collection = f"ZTF_public_sources_{tag}"

        run_ztf_public(path=f"{KOWALSKI_DATA_PATH}/catalogs", num_proc=1)

        ingested_entries = list(self.mongo.db[collection].find({}, {"_id": 1}))
        log(f"Ingested features of {len(ingested_entries)} sources")

        assert len(ingested_entries) == 5449

    def test_ingest_ptf(self):
        sources_collection = "PTF_sources"
        exposures_collection = "PTF_exposures"
        run_ptf_matchfiles(
            path=f"{KOWALSKI_DATA_PATH}/catalogs",
            num_proc=1,
        )

        ingested_sources = list(self.mongo.db[sources_collection].find({}, {"_id": 1}))
        ingested_exposures = list(
            self.mongo.db[exposures_collection].find({}, {"_id": 1})
        )
        log(f"Ingested lightcurves for {len(ingested_sources)} sources")
        log(f"Ingested {len(ingested_exposures)} exposures")

        assert len(ingested_sources) == 1145
        assert len(ingested_exposures) == 2
