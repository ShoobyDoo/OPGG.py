import json
from enum import Enum


class Utils:
    """
    ### utils.py
    A collection of static utility helper methods that perform various opgg and league specific tasks such as fetching champions, seasons, etc.\n

    Copyright (c) 2023-2024, ShoobyDoo
    License: BSD-3-Clause, See LICENSE for more details.
    """

    @staticmethod
    def read_local_json(file: str) -> dict[str, any]:
        with open(file, "r") as f:
            return json.loads(f.read())