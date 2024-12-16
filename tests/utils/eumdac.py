"""Module to mock the ``eumdac`` package for testing purposes."""

import sys
from contextlib import contextmanager
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


class AccessToken(MagicMock):
    expiration = datetime.now() + timedelta(hours=1)

    def __str__(self):
        return "not-ok"


class EumdacPackage:
    eumdac = None
    access_token = AccessToken

    @staticmethod
    def _get_eumdac_namespace():
        modules = [
            "",
            ".token",
            ".collection",
            ".product",
            ".tailor_models"
        ]
        return {f"eumdac{k}": MagicMock() for k in modules}

    @classmethod
    def __add_data_store(cls):
        cls.eumdac.DataStore = MagicMock()
        cls.eumdac.DataStore.get_collection = MagicMock()

    @classmethod
    def __add_product(cls):
        cls.eumdac.Product = MagicMock()

    @classmethod
    def __add_access_token(cls):
        cls.eumdac.token.AccessToken = MagicMock()
        cls.eumdac.AccessToken = cls.eumdac.token.AccessToken

    @classmethod
    def __add_details(cls):
        cls.__add_data_store()
        cls.__add_product()
        cls.__add_access_token()

    @classmethod
    def _add_sub_packages(cls, _namespace):
        cls.eumdac = _namespace["eumdac"]
        cls.eumdac.token = _namespace["eumdac.token"]
        cls.eumdac.collection = _namespace["eumdac.collection"]
        cls.eumdac.product = _namespace["eumdac.product"]
        cls.eumdac.tailor_models = _namespace["eumdac.tailor_models"]
        cls.__add_details()

    @classmethod
    @contextmanager
    def mocked(cls):
        try:
            with patch.dict(sys.modules, EumdacPackage._get_eumdac_namespace()) as _namespace:
                EumdacPackage._add_sub_packages(_namespace)
                yield EumdacPackage.eumdac
        finally:
            pass
