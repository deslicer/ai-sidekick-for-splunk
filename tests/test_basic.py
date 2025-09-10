"""Basic tests to ensure the package can be imported and works correctly."""

import pytest


def test_package_import():
    """Test that the main package can be imported successfully."""
    try:
        import ai_sidekick_for_splunk
        assert ai_sidekick_for_splunk is not None
    except ImportError as e:
        pytest.fail(f"Failed to import ai_sidekick_for_splunk: {e}")


def test_package_has_version():
    """Test that the package has a version attribute."""
    import ai_sidekick_for_splunk
    
    # Check if the package has version info
    assert hasattr(ai_sidekick_for_splunk, '__version__') or hasattr(ai_sidekick_for_splunk, '__version_info__'), \
        "Package should have version information"


def test_basic_functionality():
    """Test basic package functionality."""
    # This is a placeholder test - add actual functionality tests as needed
    assert True, "Basic functionality test placeholder"


if __name__ == "__main__":
    pytest.main([__file__])
