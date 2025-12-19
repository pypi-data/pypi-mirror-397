from datacore_sdk import DataCoreClient


def test_import_and_init_client():
    client = DataCoreClient(base_url="https://api.example.com", api_key="test")
    assert client is not None
    assert hasattr(client, "projects")
