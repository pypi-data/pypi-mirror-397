import json
import os
from pathlib import Path
from typing import BinaryIO, Union
from abc import ABC, abstractmethod

import fitz  # PyMuPDF
import pandas as pd
from AIFoundationKit.base.exception.custom_exception import AppException
from AIFoundationKit.base.logger.custom_logger import logger as log
from bs4 import BeautifulSoup
from docx import Document


class BaseFileManager(ABC):
    """
    Abstract Base Class for File Managers.
    Provides methods for reading and saving files.
    """

    def read_file(self, file_path: str) -> str:
        """
        Reads the content of various file formats and returns it as a string.
        Supported formats: .pdf, .docx, .html, .xml, .json, .csv, .txt

        Args:
            file_path (str): The absolute path to the file.

        Returns:
            str: The extracted text content of the file.

        Raises:
            AppException: If file format is unsupported or reading fails.
            FileNotFoundError: If the file does not exist.
        """
        if not os.path.exists(file_path):
            log.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        file_ext = Path(file_path).suffix.lower()
        text_content = ""

        try:
            if file_ext == ".pdf":
                doc = fitz.open(file_path)
                for i, page in enumerate(doc):
                    text_content += f"Page {i + 1}:\n{page.get_text()}\n"
                doc.close()

            elif file_ext == ".docx":
                doc = Document(file_path)
                for para in doc.paragraphs:
                    text_content += para.text + "\n"

            elif file_ext in [".html", ".xml"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f, "lxml" if file_ext ==
                                         ".xml" else "html.parser")
                    text_content = soup.get_text(separator=" ", strip=True)

            elif file_ext == ".json":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                text_content = json.dumps(data, indent=2)

            elif file_ext == ".csv":
                df = pd.read_csv(file_path)
                text_content = df.to_string(index=False)

            elif file_ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    text_content = f.read()

            else:
                raise AppException(f"Unsupported file format: {file_ext}")

            return text_content.strip()

        except Exception as e:
            log.error(f"Error reading file {file_path}: {e}")
            raise AppException(f"Failed to read file {file_path}: {str(e)}") from e

    def save_file(
        self, file_obj: Union[BinaryIO, bytes], save_dir: str, file_name: str = None
    ) -> str:
        """
        Saves an uploaded file to the specified directory.

        Args:
            file_obj (Union[BinaryIO, bytes]): The file object (like from Streamlit/Flask) or bytes.
            save_dir (str): The directory to save the file in.
            file_name (str, optional): The name of the file. Required if file_obj is bytes.
                                       If file_obj has a 'name' attribute, it will be used if file_name is None.

        Returns:
            str: The absolute path of the saved file.

        Raises:
            AppException: If saving fails or file name cannot be determined.
        """
        try:
            Path(save_dir).mkdir(parents=True, exist_ok=True)

            if file_name is None:
                if hasattr(file_obj, "name"):
                    file_name = file_obj.name
                else:
                    raise AppException(
                        "File name must be provided if file object does not have a name attribute."
                    )

            # Handle full paths in file_name (just in case)
            file_name = os.path.basename(file_name)
            save_path = os.path.join(save_dir, file_name)

            if isinstance(file_obj, bytes):
                with open(save_path, "wb") as f:
                    f.write(file_obj)
            else:
                # Assume it's a file-like object
                with open(save_path, "wb") as f:
                    # Check if the object has a read method
                    if hasattr(file_obj, "read"):
                        # If it's a file-like object, we might need to reset position or just read
                        # If it's bytesIO or opened file.
                        # Some frameworks pass a wrapper.
                        # Most reliably: read content
                        content = file_obj.read()
                        f.write(content)
                    else:
                        raise AppException("Provided file object is not readable.")

            log.info(f"File saved successfully at {save_path}")
            return str(Path(save_path).resolve())

        except Exception as e:
            log.error(f"Error saving file: {e}")
            raise AppException(f"Failed to save file: {str(e)}") from e
