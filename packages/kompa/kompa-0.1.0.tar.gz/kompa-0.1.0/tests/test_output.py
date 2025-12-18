"""
Unit tests for output handling and formatting.
Tests for: handle_output_presentation
"""

import json
import os
import tempfile
from io import StringIO
from unittest.mock import patch

import pytest

from kompa.kompa import ClassificationResultEntry, handle_output_presentation


class TestHandleOutputPresentation:
    """Test suite for handle_output_presentation function."""

    def test_tsv_output_to_file(self):
        """Test TSV output to file."""
        results = [
            ClassificationResultEntry(
                query_header="query1",
                best_reference_header="ref1",
                normalized_compression_distance=0.5,
                frequency=3,
                max_k_nearest=5,
                spreading_limit=0.05,
            ),
            ClassificationResultEntry(
                query_header="query2",
                best_reference_header="ref2",
                normalized_compression_distance=0.3,
                frequency=2,
                max_k_nearest=5,
                spreading_limit=0.05,
            ),
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".tsv") as f:
            output_file = f.name

        try:
            handle_output_presentation(
                results=results,
                is_json_output=False,
                output_file_path=output_file,
            )

            with open(output_file, "r") as f:
                content = f.read()
                lines = content.strip().split("\n")

                # Check header
                assert "query_header" in lines[0]
                assert "best_reference_header" in lines[0]
                assert "normalized_compression_distance" in lines[0]

                # Check data rows
                assert len(lines) == 3  # header + 2 results
                assert "query1" in lines[1]
                assert "ref1" in lines[1]
                assert "0.5" in lines[1]
                assert "query2" in lines[2]
                assert "ref2" in lines[2]
                assert "0.3" in lines[2]
        finally:
            os.unlink(output_file)

    def test_tsv_output_to_console(self):
        """Test TSV output to console."""
        results = [
            ClassificationResultEntry(
                query_header="query1",
                best_reference_header="ref1",
                normalized_compression_distance=0.5,
                frequency=3,
                max_k_nearest=5,
                spreading_limit=0.05,
            ),
        ]

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            handle_output_presentation(
                results=results,
                is_json_output=False,
                output_file_path=None,
            )

            output = mock_stdout.getvalue()
            assert "query_header" in output
            assert "query1" in output
            assert "ref1" in output
            assert "0.5" in output

    def test_json_output_to_file(self):
        """Test JSON output to file."""
        results = [
            ClassificationResultEntry(
                query_header="query1",
                best_reference_header="ref1",
                normalized_compression_distance=0.5,
                frequency=3,
                max_k_nearest=5,
                spreading_limit=0.05,
            ),
            ClassificationResultEntry(
                query_header="query2",
                best_reference_header="ref2",
                normalized_compression_distance=0.3,
                frequency=2,
                max_k_nearest=5,
                spreading_limit=0.05,
            ),
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            output_file = f.name

        try:
            handle_output_presentation(
                results=results,
                is_json_output=True,
                output_file_path=output_file,
            )

            with open(output_file, "r") as f:
                data = json.load(f)

                assert isinstance(data, list)
                assert len(data) == 2

                # Check first entry
                assert data[0]["query_header"] == "query1"
                assert data[0]["best_reference_header"] == "ref1"
                assert data[0]["normalized_compression_distance"] == 0.5
                assert data[0]["frequency"] == 3
                assert data[0]["max_k_nearest"] == 5
                assert data[0]["spreading_limit"] == 0.05

                # Check second entry
                assert data[1]["query_header"] == "query2"
                assert data[1]["best_reference_header"] == "ref2"
        finally:
            os.unlink(output_file)

    def test_json_output_to_console(self):
        """Test JSON output to console."""
        results = [
            ClassificationResultEntry(
                query_header="query1",
                best_reference_header="ref1",
                normalized_compression_distance=0.5,
                frequency=3,
                max_k_nearest=5,
                spreading_limit=0.05,
            ),
        ]

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            handle_output_presentation(
                results=results,
                is_json_output=True,
                output_file_path=None,
            )

            output = mock_stdout.getvalue()
            data = json.loads(output)

            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["query_header"] == "query1"
            assert data[0]["best_reference_header"] == "ref1"

    def test_empty_results_tsv(self):
        """Test handling empty results with TSV output."""
        results = []

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".tsv") as f:
            output_file = f.name

        try:
            handle_output_presentation(
                results=results,
                is_json_output=False,
                output_file_path=output_file,
            )

            with open(output_file, "r") as f:
                content = f.read()
                lines = content.strip().split("\n")
                # Should have header only
                assert len(lines) == 1
                assert "query_header" in lines[0]
        finally:
            os.unlink(output_file)

    def test_empty_results_json(self):
        """Test handling empty results with JSON output."""
        results = []

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            output_file = f.name

        try:
            handle_output_presentation(
                results=results,
                is_json_output=True,
                output_file_path=output_file,
            )

            with open(output_file, "r") as f:
                data = json.load(f)
                assert isinstance(data, list)
                assert len(data) == 0
        finally:
            os.unlink(output_file)

    def test_unicode_in_output(self):
        """Test handling Unicode characters in output."""
        results = [
            ClassificationResultEntry(
                query_header="quéry1",
                best_reference_header="réf1",
                normalized_compression_distance=0.5,
                frequency=1,
                max_k_nearest=5,
                spreading_limit=0.05,
            ),
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json", encoding="utf-8"
        ) as f:
            output_file = f.name

        try:
            handle_output_presentation(
                results=results,
                is_json_output=True,
                output_file_path=output_file,
            )

            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                assert data[0]["query_header"] == "quéry1"
                assert data[0]["best_reference_header"] == "réf1"
        finally:
            os.unlink(output_file)

    def test_large_result_set(self):
        """Test handling large number of results."""
        # Create 1000 results
        results = [
            ClassificationResultEntry(
                query_header=f"query{i}",
                best_reference_header=f"ref{i}",
                normalized_compression_distance=0.1 * (i % 10),
                frequency=i % 5 + 1,
                max_k_nearest=5,
                spreading_limit=0.05,
            )
            for i in range(1000)
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            output_file = f.name

        try:
            handle_output_presentation(
                results=results,
                is_json_output=True,
                output_file_path=output_file,
            )

            with open(output_file, "r") as f:
                data = json.load(f)
                assert len(data) == 1000
        finally:
            os.unlink(output_file)

    def test_tsv_tab_separation(self):
        """Test that TSV output uses tabs for separation."""
        results = [
            ClassificationResultEntry(
                query_header="query1",
                best_reference_header="ref1",
                normalized_compression_distance=0.5,
                frequency=3,
                max_k_nearest=5,
                spreading_limit=0.05,
            ),
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".tsv") as f:
            output_file = f.name

        try:
            handle_output_presentation(
                results=results,
                is_json_output=False,
                output_file_path=output_file,
            )

            with open(output_file, "r") as f:
                content = f.read()
                lines = content.strip().split("\n")
                # Check that lines use tabs
                assert "\t" in lines[0]
                assert "\t" in lines[1]
                # Count tabs in data row
                assert lines[1].count("\t") == 5  # 6 columns = 5 tabs
        finally:
            os.unlink(output_file)
