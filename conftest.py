"""Root conftest — re-exports everything from tests/conftest.py for pytest discovery."""
# pytest automatically picks up conftest.py at the root; the real fixtures live
# in tests/conftest.py and are available to all test modules.
