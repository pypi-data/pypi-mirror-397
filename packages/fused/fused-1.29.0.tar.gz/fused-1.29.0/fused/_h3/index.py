"""Index H3-indexed datasets for serverless queries.

This module provides functions to create metadata parquet files that enable
fast H3 range queries without requiring a server connection.
"""


def persist_hex_table_metadata(
    dataset_path: str,
    output_path: str | None = None,
    metadata_path: str | None = None,
    verbose: bool = False,
    row_group_size: int = 1,
    indexed_columns: list[str] | None = None,
    pool_size: int = 10,
) -> str:
    """Persist metadata for a hex table to enable serverless queries.

    Scans all parquet files in the dataset, extracts metadata needed for
    fast reconstruction, and writes one .metadata.parquet file per source file.

    Each metadata file contains:
    - Row group metadata (offsets, H3 ranges, etc.)
    - Full metadata_json stored as custom metadata in the parquet schema

    Requires a 'hex' column (or variant like h3, h3_index) in all files.
    Raises ValueError if no hex column is found.

    Args:
        dataset_path: Path to the dataset directory (e.g., "s3://bucket/dataset/")
        output_path: Deprecated - use metadata_path instead
        metadata_path: Directory path where metadata files should be written.
                      If None, writes to {source_dir}/.fused/{source_filename}.metadata.parquet
                      for each source file. If provided, writes to
                      {metadata_path}/{full_source_path}.metadata.parquet using the full
                      source path as the filename. This allows storing metadata in a
                      different location when you don't have write access to the dataset directory.
        verbose: If True, print timing/progress information.
        row_group_size: Number of rows per row group in output parquet file.
                       Default is 1 (one row per row group). Larger values
                       reduce file size but may increase memory usage during writes.
        indexed_columns: List of column names to index. If None (default),
                         indexes only the first identified indexed column
                         (typically the hex column). If an empty list, indexes
                         all detected indexed columns.
        pool_size: Number of parallel workers to use for processing files.
                   Default is 10 (parallel processing enabled by default).
                   Set to 1 for sequential processing. This can significantly speed up
                   metadata extraction for large datasets with many files.

    Returns:
        Path to metadata directory (if metadata_path provided) or first metadata file path

    Raises:
        ImportError: If job2 package is not available
        ValueError: If no hex column is found in any file
        FileNotFoundError: If no parquet files are found in the dataset

    Example:
        >>> fused.h3.persist_hex_table_metadata("s3://my-bucket/my-dataset/")
        's3://my-bucket/my-dataset/.fused/file1.metadata.parquet'
        >>> fused.h3.persist_hex_table_metadata("s3://my-bucket/my-dataset/", metadata_path="s3://my-bucket/metadata/")
        's3://my-bucket/metadata/'
        >>> fused.h3.persist_hex_table_metadata("s3://my-bucket/my-dataset/", pool_size=4)
        's3://my-bucket/my-dataset/.fused/file1.metadata.parquet'
    """
    try:
        from job2.fasttortoise._h3_index import persist_hex_table_metadata_impl
    except ImportError as e:
        raise RuntimeError(
            "The H3 index functionality requires the job2 module. "
            "This function is only available in the Fused execution environment."
        ) from e

    return persist_hex_table_metadata_impl(
        dataset_path=dataset_path,
        metadata_path=metadata_path,
        verbose=verbose,
        row_group_size=row_group_size,
        indexed_columns=indexed_columns,
        pool_size=pool_size,
    )


__all__ = [
    "persist_hex_table_metadata",
]
