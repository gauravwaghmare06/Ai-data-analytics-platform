"""Reusable dataset loading service for CSV and XLSX files."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, BinaryIO

import pandas as pd
from pandas.errors import EmptyDataError, ParserError

from app.utils.exceptions import DataProcessingError, ValidationError
from app.utils.logger import get_logger
from app.utils.validators import validate_file_size, validate_uploaded_file_type


@dataclass(frozen=True)
class LoadedDataset:
    """Container for loaded dataset and related metadata."""

    filename: str
    extension: str
    dataframe: pd.DataFrame


class DataLoaderService:
    """Service for validating and loading tabular datasets."""

    def __init__(self) -> None:
        self._logger = get_logger(__name__)

    def load_uploaded_file(
        self,
        uploaded_file: Any,
        *,
        allowed_extensions: tuple[str, ...],
        max_size_mb: int,
    ) -> LoadedDataset:
        """Load and validate an uploaded Streamlit file object."""
        if uploaded_file is None:
            raise ValidationError("Please upload a CSV or XLSX file.")

        filename = getattr(uploaded_file, "name", "")
        file_size = int(getattr(uploaded_file, "size", 0))

        extension = validate_uploaded_file_type(filename, allowed_extensions)
        validate_file_size(file_size, max_size_mb)

        dataframe = self._read_dataframe(uploaded_file, extension, filename)
        return LoadedDataset(filename=filename, extension=extension, dataframe=dataframe)

    def _read_dataframe(
        self, file_obj: BinaryIO, extension: str, filename: str
    ) -> pd.DataFrame:
        """Read dataframe from file object and convert loader errors to app errors."""
        try:
            file_obj.seek(0)
            if extension == ".csv":
                dataframe = pd.read_csv(file_obj)
            elif extension == ".xlsx":
                dataframe = pd.read_excel(file_obj, engine="openpyxl")
            else:
                raise ValidationError(f"Unsupported file type '{extension}'.")
        except ValidationError:
            raise
        except EmptyDataError as exc:
            self._logger.warning("Empty dataset uploaded: %s", filename)
            raise ValidationError("The uploaded file is empty.") from exc
        except ParserError as exc:
            self._logger.warning("Malformed dataset uploaded: %s", filename)
            raise DataProcessingError(
                "Could not parse the uploaded file. Please verify its format."
            ) from exc
        except ValueError as exc:
            self._logger.warning("Invalid dataset content in file: %s", filename)
            raise DataProcessingError(
                "Invalid file content. Please upload a valid CSV or XLSX dataset."
            ) from exc
        except Exception as exc:  # pragma: no cover - defensive fallback
            self._logger.exception("Unexpected dataset load failure for file: %s", filename)
            raise DataProcessingError(
                "Failed to load dataset due to an unexpected error."
            ) from exc

        if dataframe.empty:
            raise ValidationError("The uploaded dataset has no rows to analyze.")

        if dataframe.columns.empty:
            raise ValidationError("The uploaded dataset does not contain columns.")

        return dataframe
