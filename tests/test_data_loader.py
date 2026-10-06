"""Tests for dataset loading service."""

from __future__ import annotations

import io

import pandas as pd
import pytest

from app.services.data_loader import DataLoaderService
from app.utils.exceptions import DataProcessingError, ValidationError


class FakeUpload(io.BytesIO):
    """Simple in-memory upload object compatible with loader expectations."""

    def __init__(self, content: bytes, name: str) -> None:
        super().__init__(content)
        self.name = name
        self.size = len(content)


def test_load_valid_csv() -> None:
    """CSV content should be loaded into a dataframe."""
    upload = FakeUpload(b"a,b\n1,2\n3,4\n", "test.csv")

    result = DataLoaderService().load_uploaded_file(
        upload,
        allowed_extensions=(".csv", ".xlsx"),
        max_size_mb=1,
    )

    assert result.filename == "test.csv"
    assert result.dataframe.shape == (2, 2)


def test_load_valid_excel() -> None:
    """XLSX content should be loaded into a dataframe."""
    dataframe = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    buffer = io.BytesIO()
    dataframe.to_excel(buffer, index=False)
    upload = FakeUpload(buffer.getvalue(), "test.xlsx")

    result = DataLoaderService().load_uploaded_file(
        upload,
        allowed_extensions=(".csv", ".xlsx"),
        max_size_mb=1,
    )

    assert result.filename == "test.xlsx"
    assert result.dataframe.shape == (2, 2)


def test_reject_unsupported_file_type() -> None:
    """Unsupported extension should raise validation error."""
    upload = FakeUpload(b"a,b\n1,2\n", "bad.json")

    with pytest.raises(ValidationError):
        DataLoaderService().load_uploaded_file(
            upload,
            allowed_extensions=(".csv", ".xlsx"),
            max_size_mb=1,
        )


def test_reject_empty_file() -> None:
    """Empty upload should raise a user-safe validation error."""
    upload = FakeUpload(b"", "empty.csv")

    with pytest.raises(ValidationError):
        DataLoaderService().load_uploaded_file(
            upload,
            allowed_extensions=(".csv", ".xlsx"),
            max_size_mb=1,
        )


def test_reject_oversized_file() -> None:
    """Uploads above configured size should be rejected."""
    upload = FakeUpload(b"a,b\n1,2\n", "small.csv")
    upload.size = 2 * 1024 * 1024

    with pytest.raises(ValidationError):
        DataLoaderService().load_uploaded_file(
            upload,
            allowed_extensions=(".csv", ".xlsx"),
            max_size_mb=1,
        )


def test_invalid_excel_content_raises_data_processing_error() -> None:
    """Malformed XLSX content should raise DataProcessingError."""
    upload = FakeUpload(b"not-an-excel-file", "bad.xlsx")

    with pytest.raises(DataProcessingError):
        DataLoaderService().load_uploaded_file(
            upload,
            allowed_extensions=(".csv", ".xlsx"),
            max_size_mb=1,
        )
