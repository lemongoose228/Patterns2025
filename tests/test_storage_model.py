import unittest
import uuid

from src.models.storage_model import StorageModel


class TestStorageModel(unittest.TestCase):

    def test_equals_storage_model_same_guid_models_equal(self):
        # Подготовка
        test_id = str(uuid.uuid4())
        storage1 = StorageModel()
        storage2 = StorageModel()

        # Действие
        storage1.id = test_id
        storage2.id = test_id

        # Проверка
        assert storage1 == storage2