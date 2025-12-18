"""
Unit tests for kompa compression and utility functions.
Tests for: lz4_compress, parse_int_cached, _get_max_workers, _get_file_opener
"""

import gzip
import io
import os
import tempfile
from unittest.mock import patch

import pytest

from kompa.kompa import (
    _get_file_opener,
    _get_max_workers,
    lz4_compress,
    parse_int_cached,
)


class TestLZ4Compress:
    """Test suite for lz4_compress function."""

    def test_compress_basic_data(self):
        """Test compression of basic byte data."""
        data = b"Hello World!"
        result = lz4_compress(data)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_compress_empty_data(self):
        """Test compression of empty data."""
        data = b""
        result = lz4_compress(data)
        assert isinstance(result, bytes)
        # LZ4 frame format has overhead even for empty data
        assert len(result) > 0

    def test_compress_large_data(self):
        """Test compression of large data."""
        # Create repetitive data that should compress well
        data = b"A" * 10000
        result = lz4_compress(data)
        assert isinstance(result, bytes)
        # Should compress significantly
        assert len(result) < len(data)

    def test_compress_random_data(self):
        """Test compression of random (incompressible) data."""
        data = os.urandom(1000)
        result = lz4_compress(data)
        assert isinstance(result, bytes)
        # Random data may not compress well
        assert len(result) > 0

    def test_compress_dna_sequence(self):
        """Test compression of DNA sequence data."""
        data = b"ATCGATCGATCGATCG" * 100
        result = lz4_compress(data)
        assert isinstance(result, bytes)
        # Repetitive DNA should compress
        assert len(result) < len(data)


class TestParseIntCached:
    """Test suite for parse_int_cached function."""

    def test_parse_valid_integer(self):
        """Test parsing valid integer bytes."""
        assert parse_int_cached(b"123") == 123
        assert parse_int_cached(b"0") == 0
        assert parse_int_cached(b"999999") == 999999

    def test_parse_negative_integer(self):
        """Test parsing negative integers."""
        assert parse_int_cached(b"-123") == -123
        assert parse_int_cached(b"-1") == -1

    def test_parse_invalid_integer(self):
        """Test parsing invalid integer raises ValueError."""
        with pytest.raises(ValueError):
            parse_int_cached(b"abc")

        with pytest.raises(ValueError):
            parse_int_cached(b"12.34")

        with pytest.raises(ValueError):
            parse_int_cached(b"")

    def test_caching_behavior(self):
        """Test that the LRU cache works correctly."""
        # Clear cache first
        parse_int_cached.cache_clear()

        # First call
        result1 = parse_int_cached(b"12345")
        cache_info1 = parse_int_cached.cache_info()

        # Second call with same value should hit cache
        result2 = parse_int_cached(b"12345")
        cache_info2 = parse_int_cached.cache_info()

        assert result1 == result2 == 12345
        assert cache_info2.hits == cache_info1.hits + 1


class TestGetMaxWorkers:
    """Test suite for _get_max_workers function."""

    @patch("os.cpu_count")
    def test_default_fraction(self, mock_cpu_count):
        """Test default 75% fraction of CPU cores."""
        mock_cpu_count.return_value = 8
        workers = _get_max_workers()
        assert workers == 6  # 75% of 8

    @patch("os.cpu_count")
    def test_custom_fraction(self, mock_cpu_count):
        """Test custom fraction."""
        mock_cpu_count.return_value = 8
        workers = _get_max_workers(fraction=0.5)
        assert workers == 4  # 50% of 8

    @patch("os.cpu_count")
    def test_minimum_workers(self, mock_cpu_count):
        """Test minimum workers is enforced."""
        mock_cpu_count.return_value = 2
        workers = _get_max_workers(fraction=0.1, minimum=1)
        assert workers == 1  # minimum is 1

    @patch("os.cpu_count")
    def test_cpu_count_none(self, mock_cpu_count):
        """Test behavior when cpu_count returns None."""
        mock_cpu_count.return_value = None
        workers = _get_max_workers()
        assert workers == 1  # fallback to 1

    @patch("os.cpu_count")
    def test_single_core_system(self, mock_cpu_count):
        """Test single core system."""
        mock_cpu_count.return_value = 1
        workers = _get_max_workers()
        assert workers == 1

    @patch("os.cpu_count")
    def test_many_cores(self, mock_cpu_count):
        """Test system with many cores."""
        mock_cpu_count.return_value = 64
        workers = _get_max_workers()
        assert workers == 48  # 75% of 64


class TestGetFileOpener:
    """Test suite for _get_file_opener function."""

    def test_open_regular_file(self):
        """Test opening regular (non-gzipped) file."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".txt") as f:
            test_file = f.name
            f.write(b"Test content")

        try:
            opener = _get_file_opener(test_file)
            assert isinstance(opener, io.BufferedReader)
            content = opener.read()
            opener.close()
            assert content == b"Test content"
        finally:
            os.unlink(test_file)

    def test_open_gzip_file(self):
        """Test opening gzipped file with .gz extension."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".gz") as f:
            test_file = f.name

        try:
            with gzip.open(test_file, "wb") as gz:
                gz.write(b"Gzipped content")

            opener = _get_file_opener(test_file)
            assert isinstance(opener, gzip.GzipFile)
            content = opener.read()
            opener.close()
            assert content == b"Gzipped content"
        finally:
            os.unlink(test_file)

    def test_open_gzip_file_alternate_extension(self):
        """Test opening gzipped file with .gzip extension."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".gzip") as f:
            test_file = f.name

        try:
            with gzip.open(test_file, "wb") as gz:
                gz.write(b"Gzipped content")

            opener = _get_file_opener(test_file)
            assert isinstance(opener, gzip.GzipFile)
            content = opener.read()
            opener.close()
            assert content == b"Gzipped content"
        finally:
            os.unlink(test_file)

    def test_file_not_found(self):
        """Test opening non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            _get_file_opener("/nonexistent/file.txt")
