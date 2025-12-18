from pathlib import Path
import os
import argparse
import logging

import yaml

from ichec_django_core.utils.test_utils.portal_client import PortalClient, Paginated
from ichec_django_core.utils.test_utils.models import MemberDetail, FormDetail

from marinerg_facility.utils.test_utils.models import FacilityDetail
from marinerg_data_access.utils.test_utils.models import DatasetDetail

from marinerg_test_access.utils.test_utils.models import AccessCallCreate


logger = logging.getLogger(__name__)


class MarinergTestAccessClient(PortalClient):

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        endpoint: str = "http://localhost:8000/",
    ):
        super().__init__(endpoint, username, password)

    def get_facilities(self, search_term="", page: int = 1) -> Paginated:
        return self.get_items(FacilityDetail, page)

    def get_members(self) -> Paginated:
        return self.get_items(MemberDetail)

    def get_datasets(self, query: dict | None = None, page: int = 1) -> Paginated:
        return self.get_items(DatasetDetail, page)

    def get_form_field_id(self, field_key: str, form: FormDetail):
        for group in form.groups:
            for field in group.fields:
                if field.key == field_key:
                    return field.id
        raise RuntimeError("Requested field not found")

    def create_access_call(
        self, call: AccessCallCreate, field_files: tuple[tuple[str, ...], ...] = ()
    ):
        response = self.create_item(call)
        for field_key, file_path in field_files:

            with open(file_path, "rb") as f:
                content = f.read()

            field_id = self.get_form_field_id(field_key, response.form)
            self.put_file(
                f"form_fields/{field_id}/template/upload", content, str(file_path)
            )
        return response


def commom_init(args):

    username = os.getenv("MARINERG_USERNAME", "consortium_admin")
    password = os.getenv("MARINERG_PASSWORD", "abc123")
    endpoint = os.getenv("MARINERG_ENDPOINT", "http://localhost:8000/")
    return username, password, endpoint


def cli_access_call_create(args):
    username, password, endpoint = commom_init(args)

    client = MarinergTestAccessClient(username, password, endpoint)

    with open(args.path.resolve(), "r", encoding="utf-8") as f:
        call_yaml = yaml.safe_load(f)

    members = client.get_members()
    call_yaml["status"] = "DRAFT"
    call_yaml["coordinator"] = members.results[0].url
    call_yaml["board_chair"] = members.results[1].url

    if args.media_dir:
        media_dir = Path(args.media_dir).resolve()
    else:
        media_dir = Path(os.getcwd())

    media_files = []
    for group in call_yaml["form"]["groups"]:
        if "fields" not in group:
            continue
        for field in group["fields"]:
            if field["field_type"] == "FILE" and field["template"]:
                media_files.append((field["key"], media_dir / field["template"]))
            field["template"] = None

    call = AccessCallCreate(**call_yaml)

    client.create_access_call(call, tuple(media_files))


def main_cli():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(required=True)

    access_call_parser = subparsers.add_parser("access_call")
    access_call_subparsers = access_call_parser.add_subparsers(required=True)

    access_call_create_parser = access_call_subparsers.add_parser("create")

    access_call_create_parser.add_argument(
        "path",
        type=Path,
        help="Path to the call file",
    )

    access_call_create_parser.add_argument(
        "--media_dir",
        type=str,
        default="",
        help="Path to a directory with media to include",
    )

    access_call_parser.set_defaults(func=cli_access_call_create)

    args = parser.parse_args()
    args.func(args)
