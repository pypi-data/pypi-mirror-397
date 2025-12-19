#!/usr/bin/env python3
"""
Test SettingsMixin with cache integration.
"""

import unittest
from dataclasses import dataclass

from pypassist.mixin.settings import SettingsMixin
from pypassist.mixin.cachable import Cachable
from pypassist.mixin.cachable import CacheConfig


@dataclass
class DummySettings:
    """Simple settings dataclass for testing."""

    value: int = 10
    name: str = "test"
    threshold: float = 0.5


class CachableWithSettings(Cachable, SettingsMixin):
    """
    Test class combining SettingsMixin and Cachable.
    Mimics the real-world usage pattern in tanat.
    Note: Cachable before SettingsMixin for proper MRO.
    """

    SETTINGS_DATACLASS = DummySettings

    def __init__(self, settings=None):
        if settings is None:
            settings = DummySettings()
        Cachable.__init__(self)
        SettingsMixin.__init__(self, settings)
        self._computed_count = 0
        self._cached_result = None

    @Cachable.caching_property
    def expensive_property(self):
        """Property that should be cleared when settings change."""
        self._computed_count += 1
        return f"computed_{self.settings.value}_{self._computed_count}"

    def compute_something(self):
        """Method that stores a result that should be cleared with cache."""
        self._cached_result = f"result_{self.settings.value}"
        return self._cached_result

    def clear_cache(self):
        """Override to clear additional cached data."""
        super().clear_cache()
        self._cached_result = None


class TestSettingsMixin(unittest.TestCase):
    """
    Test SettingsMixin functionality.
    """

    def setUp(self):
        """Initialize for each test - activate cache."""
        self.cache_config = CacheConfig()  # Store for use in tests

    def test_update_settings_with_kwargs_clears_cache(self):
        """
        Test that update_settings with kwargs clears the cache.
        """
        instance = CachableWithSettings(DummySettings(value=10))
        instance.cache_config = self.cache_config  # Activate cache

        # Access property to populate cache
        result1 = instance.expensive_property
        self.assertEqual(instance._computed_count, 1)

        # Access again - should be cached
        result2 = instance.expensive_property
        self.assertEqual(result1, result2)
        self.assertEqual(instance._computed_count, 1, "Should use cached value")

        # Update settings with kwargs
        instance.update_settings(value=20)

        # Access property - should recompute due to cache clear
        result3 = instance.expensive_property
        self.assertEqual(instance._computed_count, 2, "Cache should be cleared")
        self.assertIn("20", result3, "Should use new settings value")

    def test_update_settings_with_object_clears_cache(self):
        """
        Test that update_settings with a settings object clears the cache.
        This is the bug fix we're testing.
        """
        instance = CachableWithSettings(DummySettings(value=10))
        instance.cache_config = self.cache_config  # Activate cache

        # Access property to populate cache
        result1 = instance.expensive_property
        self.assertEqual(instance._computed_count, 1)

        # Access again - should be cached
        result2 = instance.expensive_property
        self.assertEqual(result1, result2)
        self.assertEqual(instance._computed_count, 1, "Should use cached value")

        # Update settings with a new settings object
        new_settings = DummySettings(value=30)
        instance.update_settings(new_settings)

        # Access property - should recompute due to cache clear
        result3 = instance.expensive_property
        self.assertEqual(
            instance._computed_count,
            2,
            "Cache should be cleared after settings object update",
        )
        self.assertIn("30", result3, "Should use new settings value")

    def test_update_settings_clears_custom_cached_data(self):
        """
        Test that update_settings clears custom cached data via clear_cache override.
        """
        instance = CachableWithSettings(DummySettings(value=10))
        instance.cache_config = self.cache_config  # Activate cache

        # Compute something
        result1 = instance.compute_something()
        self.assertIsNotNone(instance._cached_result)
        self.assertEqual(result1, "result_10")

        # Update settings with kwargs
        instance.update_settings(value=15)

        # Cached result should be cleared
        self.assertIsNone(
            instance._cached_result, "Custom cached data should be cleared"
        )

        # Verify again with settings object
        result2 = instance.compute_something()
        self.assertEqual(result2, "result_15")

        new_settings = DummySettings(value=25)
        instance.update_settings(new_settings)

        # Cached result should be cleared again
        self.assertIsNone(
            instance._cached_result,
            "Custom cached data should be cleared after settings object update",
        )

    def test_update_settings_both_kwargs_and_object(self):
        """
        Test edge case: both settings object and kwargs provided.
        Settings object should be applied first, then kwargs override.
        """
        instance = CachableWithSettings(DummySettings(value=10, name="initial"))
        instance.cache_config = self.cache_config  # Activate cache

        # Populate cache
        _ = instance.expensive_property
        initial_count = instance._computed_count

        # Update with both settings object and kwargs
        new_settings = DummySettings(value=20, name="from_object")
        instance.update_settings(new_settings, name="from_kwargs")

        # Cache should be cleared
        _ = instance.expensive_property
        self.assertGreater(
            instance._computed_count, initial_count, "Cache should be cleared"
        )

        # Kwargs should override settings object
        self.assertEqual(
            instance.settings.value, 20, "Should use value from settings object"
        )
        self.assertEqual(
            instance.settings.name, "from_kwargs", "Should use name from kwargs"
        )

    def test_no_cache_clear_without_settings_change(self):
        """
        Test that cache is not cleared if settings haven't actually changed.
        """
        instance = CachableWithSettings(DummySettings(value=10))
        instance.cache_config = self.cache_config  # Activate cache

        # Populate cache
        _ = instance.expensive_property
        count_before = instance._computed_count

        # "Update" with same settings
        instance.update_settings(DummySettings(value=10, name="test", threshold=0.5))

        # Cache should NOT be cleared (settings unchanged)
        _ = instance.expensive_property
        self.assertEqual(
            instance._computed_count,
            count_before,
            "Cache should not clear for identical settings",
        )

    def test_with_tmp_settings_does_not_clear_cache(self):
        """
        Test that with_tmp_settings does not trigger explicit cache clearing.
        Note: The property may still recompute if it depends on settings.value.
        """
        instance = CachableWithSettings(DummySettings(value=10))
        instance.cache_config = self.cache_config  # Activate cache

        # Compute something that doesn't depend on settings
        result1 = instance.compute_something()

        # Temporary settings change - should not call clear_cache()
        with instance.with_tmp_settings(value=99):
            # The _cached_result should still exist (not cleared by clear_cache)
            self.assertIsNotNone(
                instance._cached_result,
                "clear_cache() should not be called in tmp context",
            )

        # After context, settings restored
        # The _cached_result should still exist
        self.assertIsNotNone(
            instance._cached_result,
            "clear_cache() should not be called after tmp context",
        )


if __name__ == "__main__":
    unittest.main()
