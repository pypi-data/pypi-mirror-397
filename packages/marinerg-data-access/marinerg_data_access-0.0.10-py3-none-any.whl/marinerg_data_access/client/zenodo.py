import os
from pathlib import Path

import requests


class ZenodoClient:

    def __init__(self, token: str | None = None):
        self.token = token
        self.api_root = "https://zenodo.org/api/"

    def get_data_by_url(self, url: str) -> list[Path]:

        record_id = url.split("/")[-1]
        # search = f"{self.zenodo_root}records/
        # ?q=doi:{doi}&size=10&page=1&all_versions=1"

        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
        else:
            headers = {}
        r = requests.get(f"{self.api_root}records/{record_id}", headers=headers)

        record = r.json()
        paths: list = []
        for file_record in record["files"]:
            key = file_record["key"]
            paths.append(Path(os.getcwd()) / key)
            link = file_record["links"]["self"]

            with requests.get(link, stream=True) as r:
                r.raise_for_status()
                with open(key, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        return paths
