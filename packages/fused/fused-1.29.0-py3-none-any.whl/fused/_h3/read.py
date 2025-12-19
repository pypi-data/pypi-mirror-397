"""Read H3-indexed tables by hex ranges."""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    import pyarrow as pa

# Check for nest_asyncio availability
try:
    import nest_asyncio

    HAS_NEST_ASYNCIO = True
except ImportError:
    HAS_NEST_ASYNCIO = False


def _require_job2(func_name: str) -> None:
    """Raise RuntimeError if job2 is not available."""
    try:
        import job2  # noqa: F401
    except ImportError as e:
        raise RuntimeError(
            f"{func_name} requires the job2 module. "
            "This function is only available in the Fused execution environment."
        ) from e


def read_hex_table_slow(
    dataset_path: str,
    hex_ranges_list: List[List[int]],
    columns: Optional[List[str]] = None,
    base_url: Optional[str] = None,
    verbose: bool = False,
    return_timing_info: bool = False,
    metadata_batch_size: int = 50,
) -> "pa.Table" | tuple["pa.Table", Dict[str, Any]]:
    """
    Read data from an H3-indexed dataset by querying hex ranges.

    This function queries the dataset index for row groups that match the given
    H3 hex ranges, downloads them in parallel with optimized batching, and returns
    a concatenated table.

    Adjacent row groups from the same file are combined into single downloads
    for better S3 performance. The batch size is controlled by
    `fused.options.row_group_batch_size` (default: 32KB).

    Args:
        dataset_path: Path to the H3-indexed dataset (e.g., "s3://bucket/dataset/")
        hex_ranges_list: List of [min_hex, max_hex] pairs as integers.
            Example: [[622236719905341439, 622246719905341439]]
        columns: Optional list of column names to read. If None, reads all columns.
        base_url: Base URL for API. If None, uses current environment.
        verbose: If True, print progress information. Default is False.
        return_timing_info: If True, return a tuple of (table, timing_info) instead of just the table.
            Default is False for backward compatibility.
        metadata_batch_size: Maximum number of row group metadata requests to batch together
            in a single API call. Larger batches reduce API overhead. Default is 50.
            Consider MongoDB's 16KB document limit when adjusting this value.

    Returns:
        PyArrow Table containing the concatenated data from all matching row groups.
        If return_timing_info is True, returns a tuple of (table, timing_info dict).

    Example:
        import fused

        # Read data for a specific H3 hex range
        table = fused.h3.read_hex_table_slow(
            dataset_path="s3://my-bucket/my-h3-dataset/",
            hex_ranges_list=[[622236719905341439, 622246719905341439]]
        )
        df = table.to_pandas()
    """
    import pyarrow as pa

    from fused._fasttortoise._api import get_row_groups_for_dataset
    from fused._options import options as OPTIONS

    # Use current environment's base URL if not specified
    if base_url is None:
        base_url = OPTIONS.base_url

    if not hex_ranges_list:
        return pa.table({})

    # Convert integer hex ranges to the format expected by get_row_groups_for_dataset
    geographical_regions = []
    for hex_range in hex_ranges_list:
        if len(hex_range) != 2:
            raise ValueError(
                f"Each hex range must be a list of [min, max], got {hex_range}"
            )
        min_hex, max_hex = hex_range
        geographical_regions.append({"min": f"{min_hex:x}", "max": f"{max_hex:x}"})

    # Query the dataset index to find matching row groups
    t0 = time.perf_counter()
    row_groups = get_row_groups_for_dataset(
        dataset_path=dataset_path,
        geographical_regions=geographical_regions,
        base_url=base_url,
    )
    t_api = time.perf_counter()

    if verbose:
        print(f"  API query: {(t_api - t0) * 1000:.1f}ms")
        print(f"  Found {len(row_groups)} row groups matching geo query")

    if not row_groups:
        # No matching row groups for the given hex ranges
        # This is normal - just return an empty table
        return pa.table({})

    # Get the batch size from options
    batch_size = OPTIONS.row_group_batch_size

    if verbose:
        print(f"  Using batch size: {batch_size} bytes")
        print(f"  Using metadata batch size: {metadata_batch_size}")

    # Run the pipelined fetch and download
    _require_job2("read_hex_table_slow")
    from job2.fasttortoise._h3_read import _fetch_with_combining

    tables, timing_info = _run_async(
        _fetch_with_combining(
            row_groups, base_url, columns, batch_size, verbose, metadata_batch_size
        )
    )
    t_fetch = time.perf_counter()

    if verbose:
        print(f"  Metadata + download: {(t_fetch - t_api) * 1000:.1f}ms")
        if timing_info:
            print(
                f"    Metadata fetch: {timing_info.get('metadata_wall_ms', 0):.1f}ms wall-clock, "
                f"{timing_info.get('metadata_ms', 0):.1f}ms cumulative"
            )
            print(
                f"      Longest metadata fetch: {timing_info.get('longest_metadata_fetch_ms', 0):.1f}ms"
            )
            print(
                f"    Data download: {timing_info.get('download_wall_ms', 0):.1f}ms wall-clock, "
                f"{timing_info.get('download_ms', 0):.1f}ms cumulative"
            )
            print(
                f"      Longest download: {timing_info.get('longest_download_ms', 0):.1f}ms"
            )
            print(f"    Download groups: {timing_info.get('num_groups', 0)}")

    # Concatenate all tables into one
    if not tables:
        return pa.table({})
    if len(tables) == 1:
        return tables[0]

    t_concat_start = time.perf_counter()
    # Use promote_options to handle schema mismatches (e.g., float vs double)
    # "permissive" allows type promotion like float->double
    result = pa.concat_tables(tables, promote_options="permissive")
    t_concat = time.perf_counter()

    if verbose:
        print(f"  Concat tables: {(t_concat - t_concat_start) * 1000:.1f}ms")

    if return_timing_info:
        return result, timing_info
    return result


def _run_async(coro):
    """Run an async coroutine, handling existing event loops."""

    async def _run_with_cleanup():
        """Run coroutine and clean up shared S3 client afterwards.

        Only cleans up when we own the event loop (not when nested via nest_asyncio).
        Note: We no longer clean up the aiohttp session here because _fetch_with_combining
        creates and manages its own session.
        """
        try:
            return await coro
        finally:
            # Clean up shared S3 client (job2) to prevent "Unclosed" warnings
            # This is safe because we own this event loop
            try:
                from job2.fasttortoise._reconstruction import (
                    _async_s3_client_loop,
                    _shared_async_s3_client,
                )

                # Only clean up if the client belongs to this event loop
                current_loop = asyncio.get_running_loop()
                if (
                    _shared_async_s3_client is not None
                    and _async_s3_client_loop is current_loop
                ):
                    await _shared_async_s3_client.close()
            except Exception:
                pass

    # Handle running inside an existing event loop (e.g., Jupyter, UDF runner)
    try:
        asyncio.get_running_loop()
        # We're inside an event loop - apply nest_asyncio if available
        if HAS_NEST_ASYNCIO:
            nest_asyncio.apply()
            # DON'T clean up here - the outer loop owns the session
            return asyncio.run(coro)
        else:
            # Fallback: create a new thread to run the async code
            # Clean up since we own this isolated event loop
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _run_with_cleanup())
                return future.result()
    except RuntimeError:
        # No event loop running - use asyncio.run directly
        # Clean up since we own this event loop
        return asyncio.run(_run_with_cleanup())


def read_hex_table(
    dataset_path: str,
    hex_ranges_list: List[List[int]],
    columns: Optional[List[str]] = None,
    base_url: Optional[str] = None,
    verbose: bool = False,
    return_timing_info: bool = False,
    batch_size: Optional[int] = None,
    max_concurrent_downloads: Optional[int] = None,
) -> "pa.Table" | tuple["pa.Table", Dict[str, Any]]:
    """
    Read data from an H3-indexed dataset by querying hex ranges.

    This is an optimized version that assumes the server always provides full metadata
    (start_offset, end_offset, metadata_json, and row_group_bytes) for all row groups.
    If any row group is missing required metadata, this function will raise an error
    indicating that the dataset needs to be re-indexed.

    This function eliminates all metadata API calls by using prefetched metadata from
    the /datasets/items-with-metadata endpoint.

    This function imports the implementation from job2 at runtime,
    similar to how read_parquet_row_group works.

    Args:
        dataset_path: Path to the H3-indexed dataset (e.g., "s3://bucket/dataset/")
        hex_ranges_list: List of [min_hex, max_hex] pairs as integers.
            Example: [[622236719905341439, 622246719905341439]]
        columns: Optional list of column names to read. If None, reads all columns.
        base_url: Base URL for API. If None, uses current environment.
        verbose: If True, print progress information. Default is False.
        return_timing_info: If True, return a tuple of (table, timing_info) instead of just the table.
            Default is False for backward compatibility.
        batch_size: Target size in bytes for combining row groups. If None, uses
            `fused.options.row_group_batch_size` (default: 32KB).
        max_concurrent_downloads: Maximum number of simultaneous download operations. If None,
            uses a default based on the number of files. Default is None.

    Returns:
        PyArrow Table containing the concatenated data from all matching row groups.
        If return_timing_info is True, returns a tuple of (table, timing_info dict).

    Raises:
        ValueError: If any row group is missing required metadata (start_offset, end_offset,
            metadata_json, or row_group_bytes). This indicates the dataset needs to be re-indexed.

    Example:
        import fused

        # Read data for a specific H3 hex range
        table = fused.h3.read_hex_table(
            dataset_path="s3://my-bucket/my-h3-dataset/",
            hex_ranges_list=[[622236719905341439, 622246719905341439]]
        )
        df = table.to_pandas()
    """
    _require_job2("read_hex_table")
    from job2.fasttortoise import read_hex_table as _job2_read_hex_table

    return _job2_read_hex_table(
        dataset_path=dataset_path,
        hex_ranges_list=hex_ranges_list,
        columns=columns,
        base_url=base_url,
        verbose=verbose,
        return_timing_info=return_timing_info,
        batch_size=batch_size,
        max_concurrent_downloads=max_concurrent_downloads,
    )


def read_hex_table_with_persisted_metadata(
    dataset_path: str,
    hex_ranges_list: List[List[int]],
    columns: Optional[List[str]] = None,
    metadata_path: Optional[str] = None,
    verbose: bool = False,
    return_timing_info: bool = False,
    batch_size: Optional[int] = None,
    max_concurrent_downloads: Optional[int] = None,
    use_local_cache: bool = False,
    local_cache_dir: Optional[str] = None,
) -> "pa.Table" | tuple["pa.Table", Dict[str, Any]]:
    """
    Read data from an H3-indexed dataset using persisted metadata parquet.

    This function reads from per-file metadata parquet files instead of
    querying a server. Each source parquet file has a corresponding
    .metadata.parquet file stored at:
    {source_dir}/.fused/{source_filename}.metadata.parquet

    Or at the specified metadata_path if provided:
    {metadata_path}/{full_source_path}.metadata.parquet

    Supports subdirectory queries - if dataset_path points to a subdirectory,
    the function will look for metadata files for files in that subdirectory.

    Args:
        dataset_path: Path to the H3-indexed dataset (e.g., "s3://bucket/dataset/")
            Can also be a subdirectory path for filtering (e.g., "s3://bucket/dataset/year=2024/")
        hex_ranges_list: List of [min_hex, max_hex] pairs as integers.
            Example: [[622236719905341439, 622246719905341439]]
        columns: Optional list of column names to read. If None, reads all columns.
        metadata_path: Directory path where metadata files are stored.
                      If None, looks for metadata at {source_dir}/.fused/ for each source file.
                      If provided, reads metadata files from this location using full source paths.
                      This allows reading metadata from a different location when
                      you don't have access to the original dataset directory.
        verbose: If True, print progress information. Default is False.
        return_timing_info: If True, return a tuple of (table, timing_info) instead of just the table.
            Default is False for backward compatibility.
        batch_size: Target size in bytes for combining row groups. If None, uses
            `fused.options.row_group_batch_size` (default: 32KB).
        max_concurrent_downloads: Maximum number of simultaneous download operations. If None,
            uses a default based on the number of files. Default is None.
        use_local_cache: If True, download metadata files to local cache first and read from there.
                         This removes S3 download overhead for benchmarking. Default is False.
        local_cache_dir: Directory path for local cache. If None and use_local_cache is True,
                        uses a temporary directory. Metadata files are cached by their S3 path.

    Returns:
        PyArrow Table containing the concatenated data from all matching row groups.
        If return_timing_info is True, returns a tuple of (table, timing_info dict).

    Raises:
        FileNotFoundError: If the metadata parquet file is not found.
        ValueError: If any row group is missing required metadata.

    Example:
        import fused

        # First, persist metadata (one-time operation)
        fused.h3.persist_hex_table_metadata("s3://my-bucket/my-dataset/")

        # Then read using persisted metadata (no server required)
        table = fused.h3.read_hex_table_with_persisted_metadata(
            dataset_path="s3://my-bucket/my-dataset/",
            hex_ranges_list=[[622236719905341439, 622246719905341439]]
        )
        df = table.to_pandas()

        # Read from subdirectory (filters by path prefix)
        table = fused.h3.read_hex_table_with_persisted_metadata(
            dataset_path="s3://my-bucket/my-dataset/year=2024/",
            hex_ranges_list=[[622236719905341439, 622246719905341439]]
        )

        # Read with metadata in alternate location
        table = fused.h3.read_hex_table_with_persisted_metadata(
            dataset_path="s3://my-bucket/my-dataset/",
            metadata_path="s3://my-bucket/metadata/",
            hex_ranges_list=[[622236719905341439, 622246719905341439]]
        )

        # Benchmark with local cache (removes S3 download overhead)
        table, timing = fused.h3.read_hex_table_with_persisted_metadata(
            dataset_path="s3://my-bucket/my-dataset/",
            hex_ranges_list=[[622236719905341439, 622246719905341439]],
            use_local_cache=True,
            return_timing_info=True,
        )
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    from fused._options import options as OPTIONS

    # Lazy import from job2
    _require_job2("read_hex_table_with_persisted_metadata")
    from job2.fasttortoise._h3_index import (
        _get_metadata_file_path,
        _list_parquet_files,
        is_single_parquet_file,
    )

    if not hex_ranges_list:
        return pa.table({})

    t0 = time.perf_counter()

    import hashlib
    import os
    import tempfile
    from pathlib import Path

    import fsspec

    # Initialize timing breakdown and data size tracking
    timing_breakdown = {
        "file_listing_ms": 0.0,
        "cache_setup_ms": 0.0,
        "s3_exists_check_ms": 0.0,
        "s3_download_ms": 0.0,
        "s3_open_ms": 0.0,
        "parquet_file_init_ms": 0.0,
        "row_group_filter_ms": 0.0,  # Time to filter row groups using statistics
        "read_table_ms": 0.0,
        "schema_extract_ms": 0.0,
        "json_decode_ms": 0.0,
        "filter_ms": 0.0,
        "convert_to_row_groups_ms": 0.0,
        "validation_ms": 0.0,
        "download_ms": 0.0,
        "concat_ms": 0.0,
        "row_group_stats": {
            "total": 0,
            "matched": 0,
        },  # Track row group filtering stats
    }

    # Track data sizes
    data_sizes = {
        "metadata_bytes_downloaded": 0,  # Total metadata files downloaded (full files)
        "metadata_bytes_read": 0,  # Bytes actually read from parquet
        "metadata_bytes_used": 0,  # Total metadata bytes actually used (after filtering)
        "data_bytes": 0,  # Total row group data downloaded
        "metadata_files_count": 0,
    }

    # Set up local cache if requested
    cache_dir = None
    if use_local_cache:
        t_cache_setup = time.perf_counter()
        if local_cache_dir is None:
            cache_dir = tempfile.mkdtemp(prefix="fused_metadata_cache_")
        else:
            cache_dir = local_cache_dir
            Path(cache_dir).mkdir(parents=True, exist_ok=True)
        timing_breakdown["cache_setup_ms"] = (
            time.perf_counter() - t_cache_setup
        ) * 1000
        if verbose:
            print(f"Using local cache directory: {cache_dir}")

    t_listing = time.perf_counter()
    # Determine source files to query
    if dataset_split := is_single_parquet_file(dataset_path):
        # Single file case
        dataset_root = dataset_split[0]
        source_files = [dataset_split[1]]
    else:
        # Directory case - list all parquet files
        dataset_root = dataset_path.rstrip("/")
        source_files = _list_parquet_files(dataset_path)
    timing_breakdown["file_listing_ms"] = (time.perf_counter() - t_listing) * 1000

    if not source_files:
        raise FileNotFoundError(f"No parquet files found in {dataset_path}")

    if verbose:
        print(f"Found {len(source_files)} source files to query")

    # Read metadata for each source file and collect row groups
    all_row_groups = []
    metadata_read_time = 0.0

    for rel_path in source_files:
        full_source_path = f"{dataset_root}/{rel_path}"

        # Determine metadata file path
        metadata_file_path = _get_metadata_file_path(
            full_source_path, dataset_root, metadata_path
        )

        try:
            # Handle local caching
            t_exists = time.perf_counter()
            original_fs, original_fs_path = fsspec.core.url_to_fs(metadata_file_path)

            # If using local cache, check if file is cached or download it
            if use_local_cache and cache_dir:
                # Create a hash-based filename for the cache
                path_hash = hashlib.md5(metadata_file_path.encode()).hexdigest()
                cached_file_path = os.path.join(cache_dir, f"{path_hash}.parquet")

                if os.path.exists(cached_file_path):
                    if verbose:
                        print(f"  Using cached metadata file: {cached_file_path}")
                    # Use local file instead
                    fs, fs_path = fsspec.core.url_to_fs(f"file://{cached_file_path}")
                    # Track cached file size (downloaded previously)
                    try:
                        cached_size = os.path.getsize(cached_file_path)
                        data_sizes["metadata_bytes_downloaded"] += cached_size
                        data_sizes["metadata_files_count"] += 1
                    except Exception:
                        pass
                else:
                    # Check if original file exists first
                    if not original_fs.exists(original_fs_path):
                        if verbose:
                            print(
                                f"  Skipping {rel_path} - metadata file not found: {metadata_file_path}"
                            )
                        continue

                    # Download to cache first
                    if verbose:
                        print(
                            f"  Downloading metadata to cache: {metadata_file_path} -> {cached_file_path}"
                        )
                    t_download = time.perf_counter()
                    metadata_size = 0
                    with original_fs.open(original_fs_path, "rb") as src:
                        with open(cached_file_path, "wb") as dst:
                            while True:
                                chunk = src.read(8192)  # 8KB chunks
                                if not chunk:
                                    break
                                dst.write(chunk)
                                metadata_size += len(chunk)
                    timing_breakdown["s3_download_ms"] += (
                        time.perf_counter() - t_download
                    ) * 1000
                    data_sizes["metadata_bytes_downloaded"] += metadata_size
                    data_sizes["metadata_files_count"] += 1
                    fs, fs_path = fsspec.core.url_to_fs(f"file://{cached_file_path}")
            else:
                # Not using cache - check if file exists
                if not original_fs.exists(original_fs_path):
                    if verbose:
                        print(
                            f"  Skipping {rel_path} - metadata file not found: {metadata_file_path}"
                        )
                    continue
                fs, fs_path = original_fs, original_fs_path
                # Get metadata file size if available (we download the whole file)
                try:
                    if hasattr(fs, "info"):
                        file_info = fs.info(fs_path)
                        if "size" in file_info:
                            data_sizes["metadata_bytes_downloaded"] += file_info["size"]
                            data_sizes["metadata_files_count"] += 1
                except Exception:
                    pass  # Ignore if we can't get file size

            timing_breakdown["s3_exists_check_ms"] += (
                time.perf_counter() - t_exists
            ) * 1000

            # Read metadata file with row group filtering
            read_start = time.perf_counter()
            t_open = time.perf_counter()

            with fs.open(fs_path, "rb") as f:
                timing_breakdown["s3_open_ms"] += (time.perf_counter() - t_open) * 1000

                t_parquet_init = time.perf_counter()
                parquet_file = pq.ParquetFile(f)
                timing_breakdown["parquet_file_init_ms"] += (
                    time.perf_counter() - t_parquet_init
                ) * 1000

                # Extract metadata_json from schema metadata
                t_schema = time.perf_counter()
                schema = parquet_file.schema_arrow
                metadata_json_bytes = schema.metadata.get(b"metadata_json")
                if not metadata_json_bytes:
                    if verbose:
                        print(
                            f"  Warning: {rel_path} metadata file missing metadata_json in schema"
                        )
                    continue
                timing_breakdown["schema_extract_ms"] += (
                    time.perf_counter() - t_schema
                ) * 1000

                t_json = time.perf_counter()
                metadata_json_str = metadata_json_bytes.decode()
                timing_breakdown["json_decode_ms"] += (
                    time.perf_counter() - t_json
                ) * 1000

                # Filter row groups using statistics before reading
                t_rg_filter = time.perf_counter()
                matching_row_groups = []
                metadata = parquet_file.metadata
                total_row_groups = metadata.num_row_groups

                for rg_idx in range(total_row_groups):
                    rg = metadata.row_group(rg_idx)

                    # Get h3_min and h3_max statistics from row group
                    # Find the column indices for h3_min and h3_max
                    h3_min_col_idx = None
                    h3_max_col_idx = None
                    for col_idx in range(rg.num_columns):
                        # Get column name from schema
                        col_name = schema.names[col_idx]
                        if col_name == "h3_min":
                            h3_min_col_idx = col_idx
                        elif col_name == "h3_max":
                            h3_max_col_idx = col_idx

                    # Check if this row group could match any query range
                    if h3_min_col_idx is not None and h3_max_col_idx is not None:
                        h3_min_col = rg.column(h3_min_col_idx)
                        h3_max_col = rg.column(h3_max_col_idx)

                        # Get min/max statistics
                        rg_h3_min = None
                        rg_h3_max = None
                        if (
                            h3_min_col.statistics
                            and h3_min_col.statistics.min is not None
                        ):
                            rg_h3_min = (
                                h3_min_col.statistics.min.as_py()
                                if hasattr(h3_min_col.statistics.min, "as_py")
                                else int(h3_min_col.statistics.min)
                            )
                        if (
                            h3_max_col.statistics
                            and h3_max_col.statistics.max is not None
                        ):
                            rg_h3_max = (
                                h3_max_col.statistics.max.as_py()
                                if hasattr(h3_max_col.statistics.max, "as_py")
                                else int(h3_max_col.statistics.max)
                            )

                        if rg_h3_min is not None and rg_h3_max is not None:
                            # Check if row group range overlaps with any query range
                            matches = False
                            for q_min, q_max in hex_ranges_list:
                                # Range overlap: rg_h3_min <= q_max AND rg_h3_max >= q_min
                                if rg_h3_min <= q_max and rg_h3_max >= q_min:
                                    matches = True
                                    break

                            if matches:
                                matching_row_groups.append(rg_idx)
                        else:
                            # No statistics available - include this row group to be safe
                            matching_row_groups.append(rg_idx)
                    else:
                        # Can't filter - include this row group to be safe
                        matching_row_groups.append(rg_idx)

                timing_breakdown["row_group_filter_ms"] += (
                    time.perf_counter() - t_rg_filter
                ) * 1000

                # Store row group filtering stats for verbose output
                matching_row_groups_count = len(matching_row_groups)
                timing_breakdown["row_group_stats"]["total"] += total_row_groups
                timing_breakdown["row_group_stats"]["matched"] += (
                    matching_row_groups_count
                )

                # Read only matching row groups
                t_read_table = time.perf_counter()
                if matching_row_groups:
                    metadata_table = parquet_file.read_row_groups(matching_row_groups)
                else:
                    # No matching row groups - skip this file
                    if verbose:
                        print(
                            f"  No matching row groups in {rel_path} (checked {total_row_groups} row groups)"
                        )
                    continue

                timing_breakdown["read_table_ms"] += (
                    time.perf_counter() - t_read_table
                ) * 1000
                data_sizes["metadata_bytes_read"] += metadata_table.nbytes

            # Filter by H3 ranges on the read data (in case row group stats weren't precise)
            t_filter = time.perf_counter()
            filtered_table = _filter_by_h3_ranges(metadata_table, hex_ranges_list)
            timing_breakdown["filter_ms"] += (time.perf_counter() - t_filter) * 1000

            # Store reference table for size calculations
            reference_table = metadata_table

            if len(filtered_table) == 0:
                continue

            metadata_read_time += time.perf_counter() - read_start

            # Track actual bytes used (size of filtered table)
            if len(filtered_table) > 0:
                try:
                    # Calculate size of filtered table in bytes
                    filtered_size = filtered_table.nbytes
                    data_sizes["metadata_bytes_used"] += filtered_size
                except Exception:
                    # Fallback: estimate based on number of rows
                    # Approximate size per row (rough estimate)
                    if len(reference_table) > 0:
                        avg_row_size = reference_table.nbytes / len(reference_table)
                        data_sizes["metadata_bytes_used"] += avg_row_size * len(
                            filtered_table
                        )

            if len(filtered_table) == 0:
                continue

            # Convert to row group format
            # Add file_path and metadata_json to each row group
            # Vectorized conversion: convert entire columns to lists at once
            t_convert = time.perf_counter()
            row_group_indices = filtered_table["row_group_index"].to_pylist()
            start_offsets = filtered_table["start_offset"].to_pylist()
            end_offsets = filtered_table["end_offset"].to_pylist()
            row_group_bytes_list = filtered_table["row_group_bytes"].to_pylist()

            # Create all row groups at once using list comprehension
            new_row_groups = [
                {
                    "path": full_source_path,
                    "row_group_index": idx,
                    "start_offset": start,
                    "end_offset": end,
                    "metadata_json": metadata_json_str,  # Use the JSON string directly
                    "row_group_bytes": bytes_str,
                }
                for idx, start, end, bytes_str in zip(
                    row_group_indices, start_offsets, end_offsets, row_group_bytes_list
                )
            ]
            all_row_groups.extend(new_row_groups)
            timing_breakdown["convert_to_row_groups_ms"] += (
                time.perf_counter() - t_convert
            ) * 1000

        except Exception as e:
            if verbose:
                print(f"  Warning: Failed to read metadata for {rel_path}: {e}")
            continue

    # Calculate total data size from row groups
    for rg in all_row_groups:
        start_offset = rg.get("start_offset")
        end_offset = rg.get("end_offset")
        if start_offset is not None and end_offset is not None:
            data_sizes["data_bytes"] += end_offset - start_offset

    t_read = time.perf_counter()

    # Calculate download rates
    metadata_download_rate = 0.0
    if (
        timing_breakdown["s3_download_ms"] > 0
        and data_sizes["metadata_bytes_downloaded"] > 0
    ):
        metadata_download_rate = (
            data_sizes["metadata_bytes_downloaded"] / 1024 / 1024
        ) / (timing_breakdown["s3_download_ms"] / 1000)  # MB/s

    if verbose:
        print(
            f"  Read metadata: {(t_read - t0) * 1000:.1f}ms ({len(all_row_groups)} row groups from {len(source_files)} files)"
        )
        print("    Data sizes:")
        if data_sizes["metadata_bytes_downloaded"] > 0:
            metadata_downloaded_mb = (
                data_sizes["metadata_bytes_downloaded"] / 1024 / 1024
            )
            metadata_read_mb = data_sizes["metadata_bytes_read"] / 1024 / 1024
            metadata_used_mb = data_sizes["metadata_bytes_used"] / 1024 / 1024
            print(
                f"      Metadata files downloaded: {metadata_downloaded_mb:.2f} MB ({data_sizes['metadata_files_count']} files)"
            )
            if metadata_read_mb > 0:
                read_efficiency = (
                    (metadata_read_mb / metadata_downloaded_mb * 100)
                    if metadata_downloaded_mb > 0
                    else 0
                )
                print(
                    f"      Metadata bytes read (row group filtered): {metadata_read_mb:.2f} MB ({read_efficiency:.1f}% of downloaded)"
                )
            if metadata_used_mb > 0:
                efficiency = (
                    (metadata_used_mb / metadata_downloaded_mb * 100)
                    if metadata_downloaded_mb > 0
                    else 0
                )
                print(
                    f"      Metadata bytes used (after filtering): {metadata_used_mb:.2f} MB ({efficiency:.1f}% of downloaded)"
                )
            if timing_breakdown["s3_download_ms"] > 0:
                print(
                    f"      Metadata download rate: {metadata_download_rate:.2f} MB/s"
                )
        data_mb = data_sizes["data_bytes"] / 1024 / 1024
        print(
            f"      Row group data: {data_mb:.2f} MB ({len(all_row_groups)} row groups)"
        )
        print("    Timing breakdown:")
        print(f"      File listing: {timing_breakdown['file_listing_ms']:.1f}ms")
        if use_local_cache:
            print(f"      Cache setup: {timing_breakdown['cache_setup_ms']:.1f}ms")
        print(f"      S3 exists check: {timing_breakdown['s3_exists_check_ms']:.1f}ms")
        if use_local_cache:
            print(
                f"      S3 download (to cache): {timing_breakdown['s3_download_ms']:.1f}ms"
            )
        print(f"      S3 open: {timing_breakdown['s3_open_ms']:.1f}ms")
        print(
            f"      ParquetFile init: {timing_breakdown['parquet_file_init_ms']:.1f}ms"
        )
        if timing_breakdown["row_group_filter_ms"] > 0:
            # Get row group stats from timing_breakdown if available
            rg_stats = timing_breakdown.get("row_group_stats", {})
            total_rgs = rg_stats.get("total", 0)
            matched_rgs = rg_stats.get("matched", 0)
            if total_rgs > 0:
                efficiency = (matched_rgs / total_rgs * 100) if total_rgs > 0 else 0
                skipped_rgs = total_rgs - matched_rgs
                print(
                    f"      Row group filter (stats): {timing_breakdown['row_group_filter_ms']:.1f}ms"
                )
                print(
                    f"        Total row groups: {total_rgs:,}, Matched: {matched_rgs:,}, Skipped: {skipped_rgs:,} ({efficiency:.1f}% match rate)"
                )
            else:
                print(
                    f"      Row group filter (stats): {timing_breakdown['row_group_filter_ms']:.1f}ms"
                )
        print(f"      Read table: {timing_breakdown['read_table_ms']:.1f}ms")
        print(f"      Schema extract: {timing_breakdown['schema_extract_ms']:.1f}ms")
        print(f"      JSON decode: {timing_breakdown['json_decode_ms']:.1f}ms")
        print(f"      Filter: {timing_breakdown['filter_ms']:.1f}ms")
        print(
            f"      Convert to row groups: {timing_breakdown['convert_to_row_groups_ms']:.1f}ms"
        )

    if len(all_row_groups) == 0:
        if return_timing_info:
            timing_info = {
                "metadata_ms": (t_read - t0) * 1000,
                "download_ms": 0,
                "num_groups": 0,
                "timing_breakdown": timing_breakdown,
                "data_sizes": data_sizes,
                "metadata_download_rate_mb_s": metadata_download_rate,
                "data_download_rate_mb_s": 0.0,
                "data_download_wall_rate_mb_s": 0.0,
            }
            return pa.table({}), timing_info
        return pa.table({})

    # Validate that all row groups have required metadata
    t_validate = time.perf_counter()
    for rg in all_row_groups:
        missing_fields = []
        if rg.get("start_offset") is None:
            missing_fields.append("start_offset")
        if rg.get("end_offset") is None:
            missing_fields.append("end_offset")
        if not rg.get("metadata_json"):
            missing_fields.append("metadata_json")
        if not rg.get("row_group_bytes"):
            missing_fields.append("row_group_bytes")

        if missing_fields:
            raise ValueError(
                f"Row group {rg.get('row_group_index')} in {rg.get('path')} is missing required metadata: "
                f"{', '.join(missing_fields)}. The dataset needs to be re-indexed with persist_hex_table_metadata()."
            )
    timing_breakdown["validation_ms"] = (time.perf_counter() - t_validate) * 1000

    # Get the batch size from options if not provided
    if batch_size is None:
        batch_size = OPTIONS.row_group_batch_size

    if verbose:
        print(f"  Using batch size: {batch_size} bytes")
        print("  Using persisted metadata (no API calls)")

    # Run the prefetched fetch and download
    async def _run_with_cleanup():
        """Run coroutine and clean up shared S3 client afterwards."""
        from job2.fasttortoise._h3_read import _fetch_with_combining_prefetched

        try:
            return await _fetch_with_combining_prefetched(
                all_row_groups,
                "",  # base_url not used for persisted metadata
                columns,
                batch_size,
                verbose,
                max_concurrent_downloads,
            )
        finally:
            # Clean up shared S3 client to prevent "Unclosed" warnings
            try:
                from job2.fasttortoise._reconstruction import _shared_async_s3_client

                if _shared_async_s3_client is not None:
                    await _shared_async_s3_client.close()
            except Exception:
                pass

    tables, download_timing_info = _run_async(_run_with_cleanup())
    t_fetch = time.perf_counter()
    timing_breakdown["download_ms"] = (t_fetch - t_read) * 1000

    # Calculate data download rate
    data_download_rate = 0.0
    data_download_wall_rate = 0.0
    if download_timing_info:
        download_wall_ms = download_timing_info.get("download_wall_ms", 0)
        if download_wall_ms > 0 and data_sizes["data_bytes"] > 0:
            data_download_wall_rate = (data_sizes["data_bytes"] / 1024 / 1024) / (
                download_wall_ms / 1000
            )  # MB/s
        download_cumulative_ms = download_timing_info.get("download_ms", 0)
        if download_cumulative_ms > 0 and data_sizes["data_bytes"] > 0:
            data_download_rate = (data_sizes["data_bytes"] / 1024 / 1024) / (
                download_cumulative_ms / 1000
            )  # MB/s

    if verbose:
        print(f"  Download: {(t_fetch - t_read) * 1000:.1f}ms")
        if data_sizes["data_bytes"] > 0:
            data_mb = data_sizes["data_bytes"] / 1024 / 1024
            print(f"    Data downloaded: {data_mb:.2f} MB")
            if data_download_wall_rate > 0:
                print(
                    f"    Effective download rate: {data_download_wall_rate:.2f} MB/s (wall-clock)"
                )
            if data_download_rate > 0 and data_download_rate != data_download_wall_rate:
                print(f"    Cumulative download rate: {data_download_rate:.2f} MB/s")
        if download_timing_info:
            print(
                f"    Data download: {download_timing_info.get('download_wall_ms', 0):.1f}ms wall-clock, "
                f"{download_timing_info.get('download_ms', 0):.1f}ms cumulative"
            )
            print(f"    Download groups: {download_timing_info.get('num_groups', 0)}")

    # Concatenate all tables into one
    if not tables:
        if return_timing_info:
            timing_info = {
                "metadata_ms": (t_read - t0) * 1000,
                "download_ms": timing_breakdown["download_ms"],
                "num_groups": download_timing_info.get("num_groups", 0)
                if download_timing_info
                else 0,
                "timing_breakdown": timing_breakdown,
                "data_sizes": data_sizes,
                "metadata_download_rate_mb_s": metadata_download_rate,
                "data_download_rate_mb_s": data_download_rate,
                "data_download_wall_rate_mb_s": data_download_wall_rate,
            }
            if download_timing_info:
                timing_info.update(download_timing_info)
            return pa.table({}), timing_info
        return pa.table({})
    if len(tables) == 1:
        if return_timing_info:
            timing_info = {
                "metadata_ms": (t_read - t0) * 1000,
                "download_ms": timing_breakdown["download_ms"],
                "num_groups": download_timing_info.get("num_groups", 0)
                if download_timing_info
                else 0,
                "timing_breakdown": timing_breakdown,
                "data_sizes": data_sizes,
                "metadata_download_rate_mb_s": metadata_download_rate,
                "data_download_rate_mb_s": data_download_rate,
                "data_download_wall_rate_mb_s": data_download_wall_rate,
            }
            if download_timing_info:
                timing_info.update(download_timing_info)
            return tables[0], timing_info
        return tables[0]

    t_concat_start = time.perf_counter()
    result = pa.concat_tables(tables, promote_options="permissive")
    t_concat = time.perf_counter()
    timing_breakdown["concat_ms"] = (t_concat - t_concat_start) * 1000

    if verbose:
        print(f"  Concat tables: {(t_concat - t_concat_start) * 1000:.1f}ms")

    if return_timing_info:
        timing_info = {
            "metadata_ms": (t_read - t0) * 1000,
            "download_ms": timing_breakdown["download_ms"],
            "num_groups": download_timing_info.get("num_groups", 0)
            if download_timing_info
            else 0,
            "timing_breakdown": timing_breakdown,
            "total_ms": (t_concat - t0) * 1000,
            "data_sizes": data_sizes,
            "metadata_download_rate_mb_s": metadata_download_rate,
            "data_download_rate_mb_s": data_download_rate,
            "data_download_wall_rate_mb_s": data_download_wall_rate,
        }
        if download_timing_info:
            timing_info.update(download_timing_info)
        return result, timing_info
    return result


def _filter_by_h3_ranges(table: "pa.Table", hex_ranges: List[List[int]]) -> "pa.Table":
    """Filter metadata table by H3 range overlap.

    For each query range [q_min, q_max], finds rows where:
    h3_min <= q_max AND h3_max >= q_min (range overlap)

    Args:
        table: PyArrow table with h3_min and h3_max columns
        hex_ranges: List of [min, max] integer pairs

    Returns:
        Filtered table with only matching row groups
    """
    import pyarrow.compute as pc

    if not hex_ranges:
        return table

    masks = []
    for q_min, q_max in hex_ranges:
        # Range overlap: h3_min <= q_max AND h3_max >= q_min
        mask = pc.and_(
            pc.less_equal(table["h3_min"], q_max),
            pc.greater_equal(table["h3_max"], q_min),
        )
        masks.append(mask)

    # Combine all masks with OR
    combined = masks[0]
    for m in masks[1:]:
        combined = pc.or_(combined, m)

    return table.filter(combined)
