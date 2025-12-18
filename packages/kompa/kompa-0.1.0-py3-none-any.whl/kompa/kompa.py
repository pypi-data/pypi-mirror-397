#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import heapq
import io
import json
import mmap
import os
import tempfile
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import lru_cache
from operator import itemgetter
from typing import Iterable
from typing import Iterator
from typing import NamedTuple

import lz4.frame as lz4

COMMON_SEPARATOR: bytes = b":::"
BATCH_SIZE: int = 1000


class QueryEntry(NamedTuple):
    header: bytes
    seq: bytes
    compressed_seq: bytes
    compressed_seq_len: int


class ClassifyQueryEntryArgs(NamedTuple):
    cache_ref_path: str
    query_header: bytes
    query_seq: bytes
    query_compressed_len: int
    k_nearest: int
    spreading_limit: float


class ClassificationResultEntry(NamedTuple):
    query_header: str
    best_reference_header: str
    normalized_compression_distance: float
    frequency: int
    max_k_nearest: int
    spreading_limit: float


@dataclass
class CLIArgs:
    queries_file: str
    reference_files: list[str]
    max_workers: int
    cache_file_path: str | None
    k_nearest: int
    spreading_limit: float
    output_file: str | None
    json_output: bool

    @classmethod
    def get_arguments(cls) -> CLIArgs:
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description="""
Compression-based k-nearest neighbors classifier for biological sequence classification.
Uses Normalized Compression Distance (NCD) to classify query sequences against reference databases.
            """,
        )
        parser.add_argument(
            "queries_file",
            help="Path to the input queries file (FASTA format, can be gzipped).",
            type=str,
        )
        parser.add_argument(
            "reference_files",
            help="Path(s) to reference database file(s) (FASTA format, can be gzipped).",
            type=str,
            nargs="+",
        )
        parser.add_argument(
            "--max-workers",
            help="Maximum number of worker processes for parallel processing. Default: Dynamically calculated 75%% of total available resources.",
            type=int,
            default=None,
        )
        parser.add_argument(
            "--no-cpu-limit",
            help="Use all available CPU cores (100%%) instead of the default 75%%. Overrides --max-workers.",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--cache-file-path",
            help="Path to cache file for storing processed reference sequences. If not specified, a temporary file is used and deleted after execution.",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-o",
            "--output",
            dest="output_file",
            help="Path to output file. If not specified, results are printed to console.",
            type=str,
            default=None,
        )
        parser.add_argument(
            "--json",
            help="Output results in JSON format instead of TSV.",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--k-nearest",
            help="Number of nearest neighbors to consider for classification. Must be a positive integer. Default: 5",
            type=int,
            default=5,
        )
        parser.add_argument(
            "--spreading-limit",
            help="Maximum spreading threshold for NCD values among k-nearest neighbors. Must be non-negative. Default: 0.05",
            type=float,
            default=0.05,
        )
        args = parser.parse_args()

        # Validate k_nearest
        if args.k_nearest <= 0:
            parser.error("--k-nearest must be a positive integer")

        # Validate spreading_limit
        if args.spreading_limit < 0:
            parser.error("--spreading-limit must be non-negative")

        # Determine max_workers based on flags
        if args.no_cpu_limit:
            max_workers = os.cpu_count() or 1
        elif args.max_workers is not None:
            max_workers = args.max_workers
        else:
            max_workers = _get_max_workers()

        return CLIArgs(
            queries_file=args.queries_file,
            reference_files=args.reference_files,
            max_workers=max_workers,
            cache_file_path=args.cache_file_path,
            k_nearest=args.k_nearest,
            spreading_limit=args.spreading_limit,
            output_file=args.output_file,
            json_output=args.json,
        )


def lz4_compress(data: bytes) -> bytes:
    return lz4.compress(data, compression_level=1)


@lru_cache(maxsize=10000)
def parse_int_cached(s: bytes) -> int:
    return int(s)


def _get_max_workers(fraction: float = 0.75, minimum: int = 1) -> int:
    cpu_count: int = os.cpu_count() or 1
    workers: int = int(cpu_count * fraction)
    return max(workers, minimum)


def _get_file_opener(file_path: str) -> gzip.GzipFile | io.BufferedReader:
    if file_path.endswith((".gzip", ".gz")):
        return gzip.open(file_path, "r")
    return open(file_path, "rb")


def yield_compressed_query_fasta_entries(file_path: str) -> Iterator[QueryEntry]:
    seq: bytes
    with _get_file_opener(file_path) as file:
        current_header: bytes | None = None
        seq_buf = bytearray()
        for line in file:
            line = line.strip()
            if line.startswith(b">"):
                if current_header is not None:
                    seq = bytes(seq_buf)
                    compressed_seq = lz4_compress(seq)
                    compressed_seq_len = len(compressed_seq)
                    yield QueryEntry(
                        header=current_header.lstrip(b">"),
                        seq=seq,
                        compressed_seq=compressed_seq,
                        compressed_seq_len=compressed_seq_len,
                    )
                current_header = line
                seq_buf.clear()
            elif current_header is not None:
                seq_buf.extend(line)

        if current_header is not None:
            seq = bytes(seq_buf)
            compressed_seq = lz4_compress(seq)
            compressed_seq_len = len(compressed_seq)
            yield QueryEntry(
                header=current_header.lstrip(b">"),
                seq=seq,
                compressed_seq=compressed_seq,
                compressed_seq_len=compressed_seq_len,
            )


def get_cache_file_entry(header: bytes, seq_buf: bytearray) -> bytes:
    seq_bytes = bytes(seq_buf)
    compressed_len = len(lz4_compress(seq_bytes))
    # Store raw sequence (not compressed) and the compressed length to avoid
    # per-query decompression and base64 decoding in workers.
    # Use list join for faster concatenation (single allocation)
    parts = [
        header.lstrip(b">"),
        COMMON_SEPARATOR,
        seq_bytes,
        COMMON_SEPARATOR,
        str(compressed_len).encode(),
        b"\n",
    ]
    return b"".join(parts)


def write_shared_ref_entries_cache(
    reference_files: Iterable[str], cache_file_path: str
) -> str:
    current_header: bytes | None = None
    seq_buf = bytearray()
    # Use larger buffer for writing - reduces syscalls
    with open(cache_file_path, "wb", buffering=8 * 1024 * 1024) as cache_file:
        for ref_file in reference_files:
            with _get_file_opener(ref_file) as input_reference_file:
                for line in input_reference_file:
                    line = line.strip()
                    if line.startswith(b">"):
                        if current_header is not None:
                            new_entry = get_cache_file_entry(
                                header=current_header, seq_buf=seq_buf
                            )
                            cache_file.write(new_entry)
                        current_header = line
                        seq_buf.clear()
                    elif current_header is not None:
                        seq_buf.extend(line)

                if current_header is not None:
                    new_entry = get_cache_file_entry(
                        header=current_header, seq_buf=seq_buf
                    )
                    cache_file.write(new_entry)
    return cache_file_path


def classify_query_entry(args: ClassifyQueryEntryArgs) -> ClassificationResultEntry:
    with open(args.cache_ref_path, "rb") as f:
        # Use memory-mapped file for faster access
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
            # We'll stream through the cache and maintain a fixed-size max-heap
            # of the k smallest NCDs to avoid storing all distances in memory.
            query_seq = args.query_seq
            query_compressed_len = args.query_compressed_len

            k = args.k_nearest
            spreading_limit = args.spreading_limit

            # Max-heap via negating NCD values; heap root is current largest NCD
            tops_heap: list[tuple[float, bytes]] = []

            # Cache heap threshold to avoid repeated lookups
            heap_full = False
            current_max_ncd = float("inf")

            current_pos = 0
            file_size = mmapped_file.size()

            while current_pos < file_size:
                newline_pos = mmapped_file.find(b"\n", current_pos)
                if newline_pos == -1:
                    newline_pos = file_size

                ref_line = mmapped_file[current_pos:newline_pos]
                current_pos = newline_pos + 1

                if not ref_line:
                    continue

                # Manual split for better performance - find separator positions
                first_sep = ref_line.find(COMMON_SEPARATOR)
                if first_sep == -1:
                    continue

                second_sep = ref_line.find(
                    COMMON_SEPARATOR, first_sep + 3
                )  # 3 = len(":::")
                if second_sep == -1:
                    continue

                # Extract parts directly without split()
                header = ref_line[:first_sep]
                ref_seq = ref_line[first_sep + 3 : second_sep]

                try:
                    # Use cached int parsing for common lengths
                    compressed_ref_seq_len = parse_int_cached(
                        ref_line[second_sep + 3 :]
                    )
                except (ValueError, TypeError):
                    # malformed compressed length
                    continue

                # Compress concatenated sequences with faster compressor
                compressed_joined_seqs_len = len(lz4_compress(query_seq + ref_seq))

                # Use max/min builtin instead of conditional
                mx = max(query_compressed_len, compressed_ref_seq_len)
                mn = min(query_compressed_len, compressed_ref_seq_len)

                # Avoid division by zero
                if mx == 0:
                    continue

                ncd = (compressed_joined_seqs_len - mn) / mx

                # Maintain top-k (smallest) NCDs using a max-heap of size k
                if not heap_full:
                    heapq.heappush(tops_heap, (-ncd, header))
                    if len(tops_heap) == k:
                        heap_full = True
                        current_max_ncd = -tops_heap[0][0]
                elif ncd < current_max_ncd:
                    heapq.heapreplace(tops_heap, (-ncd, header))
                    current_max_ncd = -tops_heap[0][0]
            # Build sorted list of tops (header, ncd) from heap
            if not tops_heap:
                # no references found; return empty/zeroed result
                return ClassificationResultEntry(
                    query_header=args.query_header.decode("utf-8", errors="replace"),
                    best_reference_header="",
                    normalized_compression_distance=0.0,
                    frequency=0,
                    max_k_nearest=k,
                    spreading_limit=spreading_limit,
                )

            # Convert heap to sorted list - avoid creating intermediate tuples
            tops = [(item[1], -item[0]) for item in tops_heap]
            tops.sort(key=itemgetter(1))

            # Extract headers and values in one pass
            tops_headers = []
            tops_values = []
            for header, ncd in tops:
                tops_headers.append(header)
                tops_values.append(ncd)

            spreading = tops_values[-1] - tops_values[0]  # already sorted

            if spreading >= spreading_limit:
                # entry with lowest NCD (first in sorted list)
                best_reference_header = tops_headers[0]
                best_ncd_score = tops_values[0]
                best_frequency = tops_headers.count(best_reference_header)
            else:
                # Count frequencies manually to avoid "Counter" overhead
                freq_dict: dict[bytes, int] = {}
                for header in tops_headers:
                    freq_dict[header] = freq_dict.get(header, 0) + 1

                best_reference_header = max(freq_dict, key=lambda h: freq_dict[h])
                best_frequency = freq_dict[best_reference_header]

                best_ncd_score = max(
                    tops_values[i]
                    for i, h in enumerate(tops_headers)
                    if h == best_reference_header
                )

            return ClassificationResultEntry(
                query_header=args.query_header.decode("utf-8", errors="replace"),
                best_reference_header=best_reference_header.decode(
                    "utf-8", errors="replace"
                ),
                normalized_compression_distance=best_ncd_score,
                frequency=best_frequency,
                max_k_nearest=k,
                spreading_limit=spreading_limit,
            )


def classify_query_fasta(
    queries_fasta_file: str,
    reference_fasta_files: Iterable[str],
    shared_reference_cache_path: str,
    k_nearest: int,
    spreading_limit: float,
    max_workers: int,
) -> Iterator[ClassificationResultEntry]:
    query_entries: Iterator[QueryEntry] = yield_compressed_query_fasta_entries(
        queries_fasta_file
    )

    cache_ref_path = write_shared_ref_entries_cache(
        reference_files=reference_fasta_files,
        cache_file_path=shared_reference_cache_path,
    )
    compute_args = (
        ClassifyQueryEntryArgs(
            cache_ref_path=cache_ref_path,
            query_header=query_entry.header,
            query_seq=query_entry.seq,
            query_compressed_len=query_entry.compressed_seq_len,
            k_nearest=k_nearest,
            spreading_limit=spreading_limit,
        )
        for query_entry in query_entries
    )
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Use chunksize for better task distribution
        return executor.map(classify_query_entry, compute_args, chunksize=10)


def handle_output_presentation(
    results: Iterable[ClassificationResultEntry],
    is_json_output: bool,
    output_file_path: str | None,
) -> None:
    headers: str = (
        "query_header\t"
        "best_reference_header\t"
        "normalized_compression_distance\t"
        "frequency\t"
        "max_k_nearest\t"
        "spreading_limit"
    )
    if is_json_output:
        # JSON output
        results_list = [
            {
                "query_header": result.query_header,
                "best_reference_header": result.best_reference_header,
                "normalized_compression_distance": result.normalized_compression_distance,
                "frequency": result.frequency,
                "max_k_nearest": result.max_k_nearest,
                "spreading_limit": result.spreading_limit,
            }
            for result in results
        ]

        if output_file_path:
            with open(output_file_path, "w", encoding="utf-8") as out_file:
                json.dump(results_list, out_file, indent=2, ensure_ascii=False)
        else:
            print(json.dumps(results_list, indent=2, ensure_ascii=False))
    elif output_file_path:
        # TSV output to file
        with open(output_file_path, "w", encoding="utf-8") as out_file:
            out_file.write(headers + "\n")
            for result in results:
                result_line = (
                    f"{result.query_header}\t"
                    f"{result.best_reference_header}\t"
                    f"{result.normalized_compression_distance}\t"
                    f"{result.frequency}\t"
                    f"{result.max_k_nearest}\t"
                    f"{result.spreading_limit}\n"
                )
                out_file.write(result_line)

    else:
        # TSV output to console with batched output to reduce syscalls
        output_buffer = [headers]
        buffer_size = 0
        max_buffer_size = 100  # Flush every 100 lines

        for result in results:
            result_line = (
                f"{result.query_header}\t"
                f"{result.best_reference_header}\t"
                f"{result.normalized_compression_distance}\t"
                f"{result.frequency}\t"
                f"{result.max_k_nearest}\t"
                f"{result.spreading_limit}"
            )
            output_buffer.append(result_line)
            buffer_size += 1

            if buffer_size >= max_buffer_size:
                print("\n".join(output_buffer), flush=False)
                output_buffer.clear()
                buffer_size = 0

        # Flush remaining buffer
        if output_buffer:
            print("\n".join(output_buffer), flush=True)


def main() -> int:
    args = CLIArgs.get_arguments()

    # Setup cache file - use user-provided path or create temporary file
    if args.cache_file_path:
        cache_file_path = args.cache_file_path
    else:
        fd, cache_file_path = tempfile.mkstemp(suffix=".cache")
        os.close(fd)

    try:
        results = tuple(
            classify_query_fasta(
                queries_fasta_file=args.queries_file,
                reference_fasta_files=args.reference_files,
                shared_reference_cache_path=cache_file_path,
                k_nearest=args.k_nearest,
                spreading_limit=args.spreading_limit,
                max_workers=args.max_workers,
            )
        )

        handle_output_presentation(
            results=results,
            is_json_output=args.json_output,
            output_file_path=args.output_file,
        )
    finally:
        # Clean up temporary cache file if user didn't specify a path
        if not args.cache_file_path:
            try:
                os.unlink(cache_file_path)
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
