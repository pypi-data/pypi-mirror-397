from pathlib import Path
import os
import argparse
import logging

import requests
import yaml

from ichec_django_core.utils.test_utils.portal_client import PortalClient, Paginated
from ichec_django_core.utils.test_utils.models import (
    FormFieldValueCreate,
    PopulatedFormCreate,
)

from marinerg_facility.utils.test_utils.models import FacilityDetail

from marinerg_data_access.utils.test_utils.models import (
    DatasetDetail,
    DatasetTemplateCreate,
    DatasetTemplateDetail,
    DatasetCreate,
    PrimitivePopulatedForm,
)

from .zenodo import ZenodoClient

logger = logging.getLogger(__name__)


class MarinergDataAccessClient(PortalClient):

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        endpoint: str = "http://localhost:8000/",
        zenodo_token: str | None = None,
    ):

        super().__init__(endpoint, username, password)
        self.zenodo_client = ZenodoClient(zenodo_token)
        self.doi_base = "https://doi.org/"

    def get_facilities(self, search_term="", page: int = 1) -> Paginated:
        return self.get_items(FacilityDetail, page)

    def get_datasets(self, query: dict | None = None, page: int = 1) -> Paginated:
        return self.get_items(DatasetDetail, page)

    def get_facility_datasets(
        self, facility: FacilityDetail, page: int = 1
    ) -> Paginated:
        return self.get_datasets({"facility": facility.id}, page)

    def get_data(self, dataset: DatasetDetail, output_dir: Path | None = None):
        if dataset.uri:
            self.get_data_by_doi(dataset.uri)

    def get_data_by_id(self, dataset_id: int):
        dataset = self.get_item(dataset_id, DatasetDetail)
        self.get_data(dataset)

    def create_schema(self, schema: DatasetTemplateCreate):
        self.create_item(schema)

    def get_schema(self, id) -> DatasetTemplateDetail:
        return self.get_item(id, DatasetTemplateDetail)

    def create_dataset(self, dataset: DatasetCreate):
        self.create_item(dataset)

    def get_data_by_doi(self, doi: str) -> list[Path]:

        r = requests.get(self.doi_base + doi)

        # Rely on doi.org redirect to get the real host and assign to a suitable
        # client for that host
        if "zenodo.org" in r.url:
            return self.zenodo_client.get_data_by_url(r.url)
        else:
            raise RuntimeError(f"Host '{r.url}' not currently supported.")


def commom_init(args):

    zenodo_token = os.getenv("ZENODO_TOKEN")
    username = os.getenv("MARINERG_USERNAME", "consortium_admin")
    password = os.getenv("MARINERG_PASSWORD", "abc123")
    endpoint = os.getenv("MARINERG_ENDPOINT", "http://localhost:8000/")
    return username, password, endpoint, zenodo_token


def cli_schema_create(args):
    username, password, endpoint, _ = commom_init(args)

    client = MarinergDataAccessClient(username, password, endpoint)

    with open(args.path.resolve(), "r", encoding="utf-8") as f:
        schema_yaml = yaml.safe_load(f)
    schema = DatasetTemplateCreate(**schema_yaml)

    client.create_schema(schema)


def populate_dataset_form(
    dataset: DatasetCreate,
    primitive_form: PrimitivePopulatedForm,
    schema: DatasetTemplateDetail,
) -> DatasetCreate:
    values = []
    for value in primitive_form.values:
        for group in schema.form.groups:
            for field in group.fields:
                if field.key == value.field:
                    values.append(
                        FormFieldValueCreate(field=field.id, value=value.value)
                    )
    return dataset.copy(update={"form": PopulatedFormCreate(values=values)})


def cli_dataset_create(args):
    username, password, endpoint, _ = commom_init(args)

    client = MarinergDataAccessClient(username, password, endpoint)

    with open(args.dataset.resolve(), "r", encoding="utf-8") as f:
        dataset_yaml = yaml.safe_load(f)

    if args.template:
        with open(args.template.resolve(), "r", encoding="utf-8") as f:
            template_yaml = yaml.safe_load(f)
        dataset_yaml = dataset_yaml | template_yaml

    schema_id = dataset_yaml["template"].split("/")[-2]
    schema = client.get_schema(schema_id)

    form_yaml = dataset_yaml.pop("form")
    primitive_form = PrimitivePopulatedForm(**form_yaml)

    dataset = DatasetCreate(**dataset_yaml)
    dataset_with_form = populate_dataset_form(dataset, primitive_form, schema)

    client.create_dataset(dataset_with_form)


def cli_data_download(args):
    username, password, endpoint, zenodo_token = commom_init(args)

    client = MarinergDataAccessClient(username, password, endpoint, zenodo_token)
    client.get_data_by_id(args.dataset)


def main_cli():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(required=True)

    schema_parser = subparsers.add_parser("schema")
    schema_subparsers = schema_parser.add_subparsers(required=True)

    schema_upload_parser = schema_subparsers.add_parser("create")

    schema_upload_parser.add_argument(
        "path",
        type=Path,
        help="Path to the schema file",
    )

    schema_upload_parser.set_defaults(func=cli_schema_create)

    data_parser = subparsers.add_parser("data")
    data_subparsers = data_parser.add_subparsers(required=True)

    data_download_parser = data_subparsers.add_parser("download")

    data_download_parser.add_argument(
        "dataset",
        type=int,
        help="Dataset id",
    )
    data_download_parser.set_defaults(func=cli_data_download)

    dataset_parser = subparsers.add_parser("dataset")
    dataset_subparsers = dataset_parser.add_subparsers(required=True)

    dataset_create_parser = dataset_subparsers.add_parser("create")

    dataset_create_parser.add_argument(
        "dataset",
        type=Path,
        help="Path to dataset",
    )

    dataset_create_parser.add_argument(
        "--template",
        type=Path,
        help="Path to dataset template",
    )
    dataset_create_parser.set_defaults(func=cli_dataset_create)

    args = parser.parse_args()
    args.func(args)
