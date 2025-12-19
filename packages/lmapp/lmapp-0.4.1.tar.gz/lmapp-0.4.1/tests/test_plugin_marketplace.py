from unittest.mock import patch, MagicMock
from lmapp.plugins.plugin_marketplace import PluginRegistry, PluginMarketplaceEntry


def test_registry_fetch_remote():
    registry = PluginRegistry(name="test", url="http://example.com/registry.json", description="Test Registry")

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = b"""
    {
        "name": "test",
        "url": "http://example.com/registry.json",
        "description": "Test Registry",
        "plugins": {
            "test.plugin": {
                "name": "Test Plugin",
                "version": "1.0.0",
                "author": "Tester",
                "description": "A test plugin",
                "repository": "http://github.com/test/plugin",
                "install_url": "http://example.com/plugin.py",
                "tags": ["test"],
                "verified": true
            }
        }
    }
    """

    # Mock urlopen to return a context manager that yields mock_response
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = mock_response

        assert registry.fetch_remote() is True
        assert "Test Plugin" in registry.plugins
        assert registry.plugins["Test Plugin"].verified is True


def test_registry_search():
    registry = PluginRegistry(name="test", url="", description="")
    entry = PluginMarketplaceEntry(
        name="Test Plugin", version="1.0.0", author="Tester", description="A test plugin for searching", repository="", install_url="", tags=["searchable"]
    )
    registry.add_plugin(entry)

    results = registry.search("searchable")
    assert len(results) == 1
    assert results[0].name == "Test Plugin"

    results = registry.search("missing")
    assert len(results) == 0
