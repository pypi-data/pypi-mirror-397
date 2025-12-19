#!/usr/bin/env python3
"""Unit tests for the @registry decorator."""

import unittest
from abc import ABC, abstractmethod
from typing import Dict, Any

from pydantic.dataclasses import dataclass

from pypassist.mixin.registrable import Registrable
from pypassist.dataclass.decorators.registry import registry, RegistrySetupError


class TestRegistryDecorator(unittest.TestCase):
    """Test cases for the @registry decorator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        pass  # Setup method - variables defined in individual tests

    def test_basic_decoration(self):
        """Test basic decoration of a dataclass."""

        class _BaseProcessor(ABC, Registrable):  # pylint: disable=unused-variable
            """Base class for testing registry."""

            _REGISTER = {}

            @abstractmethod
            def process(self, data: str) -> str:
                """Process the data."""

        @registry(base_cls=_BaseProcessor)
        @dataclass
        class ProcessorConfig:
            """Test configuration class."""

            type: str = "test"
            settings: Dict[str, Any] = None

        # Create an instance
        _config = ProcessorConfig(
            type="test", settings={"param": "value"}
        )  # pylint: disable=unused-variable

        # Verify the class is properly decorated
        self.assertTrue(hasattr(ProcessorConfig, "_SETUP_"))
        self.assertTrue(hasattr(ProcessorConfig, "_REG_BASE_CLASS_"))
        self.assertTrue(hasattr(ProcessorConfig, "_REGISTRY_"))
        self.assertTrue(hasattr(ProcessorConfig, "reload_registry"))

    def test_invalid_setup(self):
        """Test handling of invalid setup configuration."""

        class _BaseProcessor2(ABC, Registrable):  # pylint: disable=unused-variable
            """Base class for testing registry."""

            _REGISTER = {}

            @abstractmethod
            def process(self, data: str) -> str:
                """Process the data."""

        with self.assertRaises(RegistrySetupError):

            @registry(
                base_cls=_BaseProcessor2, register_name_attr=123
            )  # Should be string
            @dataclass
            class _ProcessorConfig:  # pylint: disable=unused-variable
                """Test configuration class."""

                type: str = "test"
                settings: Dict[str, Any] = None


if __name__ == "__main__":
    unittest.main()
