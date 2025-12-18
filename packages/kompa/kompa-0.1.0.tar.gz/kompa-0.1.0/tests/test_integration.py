"""
Integration tests for the kompa CLI and end-to-end workflows.
Tests for: CLIArgs, main function, full pipeline
"""

import gzip
import os
import sys
import tempfile
from unittest.mock import patch

import pytest

from kompa.kompa import CLIArgs, main


class TestCLIArgs:
    """Test suite for CLI argument parsing."""

    def test_minimal_args(self):
        """Test parsing minimal required arguments."""
        test_args = [
            "kompa",
            "query.fasta",
            "ref1.fasta",
        ]

        with patch.object(sys, "argv", test_args):
            args = CLIArgs.get_arguments()

            assert args.queries_file == "query.fasta"
            assert args.reference_files == ["ref1.fasta"]
            assert args.max_workers > 0
            assert args.k_nearest == 5  # default
            assert args.spreading_limit == 0.05  # default
            assert args.cache_file_path is None
            assert args.output_file is None
            assert args.json_output is False

    def test_multiple_reference_files(self):
        """Test parsing multiple reference files."""
        test_args = [
            "kompa",
            "query.fasta",
            "ref1.fasta",
            "ref2.fasta",
            "ref3.fasta",
        ]

        with patch.object(sys, "argv", test_args):
            args = CLIArgs.get_arguments()

            assert len(args.reference_files) == 3
            assert "ref1.fasta" in args.reference_files
            assert "ref2.fasta" in args.reference_files
            assert "ref3.fasta" in args.reference_files

    def test_max_workers_flag(self):
        """Test --max-workers flag."""
        test_args = [
            "kompa",
            "query.fasta",
            "ref.fasta",
            "--max-workers",
            "4",
        ]

        with patch.object(sys, "argv", test_args):
            args = CLIArgs.get_arguments()

            assert args.max_workers == 4

    def test_no_cpu_limit_flag(self):
        """Test --no-cpu-limit flag."""
        test_args = [
            "kompa",
            "query.fasta",
            "ref.fasta",
            "--no-cpu-limit",
        ]

        with patch.object(sys, "argv", test_args):
            with patch("os.cpu_count", return_value=8):
                args = CLIArgs.get_arguments()

                assert args.max_workers == 8

    def test_cache_file_path_flag(self):
        """Test --cache-file-path flag."""
        test_args = [
            "kompa",
            "query.fasta",
            "ref.fasta",
            "--cache-file-path",
            "/tmp/my_cache.cache",
        ]

        with patch.object(sys, "argv", test_args):
            args = CLIArgs.get_arguments()

            assert args.cache_file_path == "/tmp/my_cache.cache"

    def test_k_nearest_flag(self):
        """Test --k-nearest flag."""
        test_args = [
            "kompa",
            "query.fasta",
            "ref.fasta",
            "--k-nearest",
            "10",
        ]

        with patch.object(sys, "argv", test_args):
            args = CLIArgs.get_arguments()

            assert args.k_nearest == 10

    def test_k_nearest_invalid_value(self):
        """Test --k-nearest with invalid value."""
        test_args = [
            "kompa",
            "query.fasta",
            "ref.fasta",
            "--k-nearest",
            "0",
        ]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit):
                CLIArgs.get_arguments()

    def test_k_nearest_negative_value(self):
        """Test --k-nearest with negative value."""
        test_args = [
            "kompa",
            "query.fasta",
            "ref.fasta",
            "--k-nearest",
            "-5",
        ]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit):
                CLIArgs.get_arguments()

    def test_spreading_limit_flag(self):
        """Test --spreading-limit flag."""
        test_args = [
            "kompa",
            "query.fasta",
            "ref.fasta",
            "--spreading-limit",
            "0.1",
        ]

        with patch.object(sys, "argv", test_args):
            args = CLIArgs.get_arguments()

            assert args.spreading_limit == 0.1

    def test_spreading_limit_negative_value(self):
        """Test --spreading-limit with negative value."""
        test_args = [
            "kompa",
            "query.fasta",
            "ref.fasta",
            "--spreading-limit",
            "-0.1",
        ]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit):
                CLIArgs.get_arguments()

    def test_output_file_flag(self):
        """Test -o/--output flag."""
        test_args = [
            "kompa",
            "query.fasta",
            "ref.fasta",
            "-o",
            "output.tsv",
        ]

        with patch.object(sys, "argv", test_args):
            args = CLIArgs.get_arguments()

            assert args.output_file == "output.tsv"

    def test_output_file_long_flag(self):
        """Test --output long flag."""
        test_args = [
            "kompa",
            "query.fasta",
            "ref.fasta",
            "--output",
            "output.tsv",
        ]

        with patch.object(sys, "argv", test_args):
            args = CLIArgs.get_arguments()

            assert args.output_file == "output.tsv"

    def test_json_flag(self):
        """Test --json flag."""
        test_args = [
            "kompa",
            "query.fasta",
            "ref.fasta",
            "--json",
        ]

        with patch.object(sys, "argv", test_args):
            args = CLIArgs.get_arguments()

            assert args.json_output is True

    def test_all_flags_combined(self):
        """Test all flags together."""
        test_args = [
            "kompa",
            "query.fasta",
            "ref1.fasta",
            "ref2.fasta",
            "--max-workers",
            "4",
            "--cache-file-path",
            "/tmp/cache.cache",
            "--k-nearest",
            "10",
            "--spreading-limit",
            "0.1",
            "-o",
            "output.json",
            "--json",
        ]

        with patch.object(sys, "argv", test_args):
            args = CLIArgs.get_arguments()

            assert args.queries_file == "query.fasta"
            assert args.reference_files == ["ref1.fasta", "ref2.fasta"]
            assert args.max_workers == 4
            assert args.cache_file_path == "/tmp/cache.cache"
            assert args.k_nearest == 10
            assert args.spreading_limit == 0.1
            assert args.output_file == "output.json"
            assert args.json_output is True


class TestMainFunction:
    """Test suite for main() function - integration tests."""

    def test_basic_classification(self):
        """Test basic end-to-end classification."""
        # Create query file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">query1\n")
            f.write("ATCGATCG\n")
            query_file = f.name

        # Create reference file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">ref1\n")
            f.write("ATCGATCG\n")
            f.write(">ref2\n")
            f.write("GCTAGCTA\n")
            ref_file = f.name

        # Create output file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".tsv") as f:
            output_file = f.name

        try:
            test_args = [
                "kompa",
                query_file,
                ref_file,
                "-o",
                output_file,
                "--max-workers",
                "1",
            ]

            with patch.object(sys, "argv", test_args):
                exit_code = main()

                assert exit_code == 0
                assert os.path.exists(output_file)

                # Check output content
                with open(output_file, "r") as f:
                    content = f.read()
                    assert "query1" in content
                    assert "ref" in content  # Should match one of the refs
        finally:
            os.unlink(query_file)
            os.unlink(ref_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_json_output(self):
        """Test JSON output format."""
        import json

        # Create query file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">query1\n")
            f.write("ATCG\n")
            query_file = f.name

        # Create reference file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">ref1\n")
            f.write("ATCG\n")
            ref_file = f.name

        # Create output file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            output_file = f.name

        try:
            test_args = [
                "kompa",
                query_file,
                ref_file,
                "-o",
                output_file,
                "--json",
                "--max-workers",
                "1",
            ]

            with patch.object(sys, "argv", test_args):
                exit_code = main()

                assert exit_code == 0

                # Verify JSON format
                with open(output_file, "r") as f:
                    data = json.load(f)
                    assert isinstance(data, list)
                    assert len(data) > 0
                    assert "query_header" in data[0]
                    assert "best_reference_header" in data[0]
        finally:
            os.unlink(query_file)
            os.unlink(ref_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_gzipped_input_files(self):
        """Test with gzipped input files."""
        # Create gzipped query file
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".fasta.gz"
        ) as f:
            query_file = f.name
        with gzip.open(query_file, "wt") as gz:
            gz.write(">query1\n")
            gz.write("ATCG\n")

        # Create gzipped reference file
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".fasta.gz"
        ) as f:
            ref_file = f.name
        with gzip.open(ref_file, "wt") as gz:
            gz.write(">ref1\n")
            gz.write("ATCG\n")

        # Create output file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".tsv") as f:
            output_file = f.name

        try:
            test_args = [
                "kompa",
                query_file,
                ref_file,
                "-o",
                output_file,
                "--max-workers",
                "1",
            ]

            with patch.object(sys, "argv", test_args):
                exit_code = main()

                assert exit_code == 0
                assert os.path.exists(output_file)
        finally:
            os.unlink(query_file)
            os.unlink(ref_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_persistent_cache_file(self):
        """Test using a persistent cache file."""
        # Create files
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">query1\n")
            f.write("ATCG\n")
            query_file = f.name

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">ref1\n")
            f.write("ATCG\n")
            ref_file = f.name

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".tsv") as f:
            output_file = f.name

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".cache") as f:
            cache_file = f.name

        try:
            test_args = [
                "kompa",
                query_file,
                ref_file,
                "-o",
                output_file,
                "--cache-file-path",
                cache_file,
                "--max-workers",
                "1",
            ]

            with patch.object(sys, "argv", test_args):
                exit_code = main()

                assert exit_code == 0
                # Cache file should still exist
                assert os.path.exists(cache_file)
                # Cache file should have content
                assert os.path.getsize(cache_file) > 0
        finally:
            os.unlink(query_file)
            os.unlink(ref_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
            if os.path.exists(cache_file):
                os.unlink(cache_file)

    def test_temporary_cache_cleanup(self):
        """Test that temporary cache is cleaned up."""
        # Create files
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">query1\n")
            f.write("ATCG\n")
            query_file = f.name

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">ref1\n")
            f.write("ATCG\n")
            ref_file = f.name

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".tsv") as f:
            output_file = f.name

        try:
            test_args = [
                "kompa",
                query_file,
                ref_file,
                "-o",
                output_file,
                "--max-workers",
                "1",
            ]

            # Track temporary files created during execution
            temp_dir = tempfile.gettempdir()
            files_before = set(os.listdir(temp_dir))

            with patch.object(sys, "argv", test_args):
                exit_code = main()

                assert exit_code == 0

            files_after = set(os.listdir(temp_dir))

            # Temporary cache files should be cleaned up
            # (allowing some tolerance for system temp files)
            new_files = files_after - files_before
            cache_files = [f for f in new_files if f.endswith(".cache")]
            assert len(cache_files) == 0
        finally:
            os.unlink(query_file)
            os.unlink(ref_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
