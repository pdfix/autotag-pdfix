import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Optional

from constants import LATEST_SDK_VERSION
from exceptions import PdfixException
from logger import get_logger

logger: logging.Logger = get_logger(__name__)


class Autotag:
    """
    Class that runs inputs with proper SDK.
    """

    def __init__(
        self,
        license_name: Optional[str],
        license_key: Optional[str],
        input_path: str,
        output_path: str,
        tempalte_path: str,
    ) -> None:
        """
        Initialize class for tagging pdf.

        Args:
            license_name (Optional[str]): Pdfix SDK license name (e-mail).
            license_key (Optional[str]): Pdfix SDK license key.
            input_path (str): Path to PDF document.
            output_path (str): Path where tagged PDF should be saved.
            tempalte_path (str): Path to layout template JSON file.
        """
        self.license_name = license_name
        self.license_key = license_key
        self.input_path_str = input_path
        self.output_path_str = output_path
        self.template_path_str = tempalte_path

    def run(self) -> None:
        """
        Run PDFix SDK autotagging.
        """
        sdk_folder: str = self._get_sdk_version()
        sdk_executable: Path = Path(__file__).parent.parent.joinpath("sdk", sdk_folder, "pdfix_app")

        command: list[str] = [sdk_executable.as_posix()]

        # PDFix license name
        if self.license_name:
            command.append("--email")
            command.append(self.license_name)

        # PDFix license name
        if self.license_key:
            command.append("--key")
            command.append(self.license_key)

        # Subcommand for autotagging
        command.append("add-tags")

        # Input
        command.append("-i")
        input_path: Path = Path(self.input_path_str).resolve()
        command.append(input_path.as_posix())

        # Template
        command.append("-c")
        template_path: Path = Path(self.template_path_str).resolve()
        command.append(template_path.as_posix())

        # Output
        command.append("-o")
        output_path: Path = Path(self.output_path_str).resolve()
        command.append(output_path.as_posix())

        logger.info(f"Running:\n{' '.join(command)}")

        result: subprocess.CompletedProcess[str] = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )

        logger.debug(f"Return code: {result.returncode}\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")

        if result.returncode != 0:
            raise PdfixException(result.returncode, result.stderr)

    def _get_sdk_version(self) -> str:
        """
        Get SDK version from template JSON file.

        Returns:
            SDK version or latest version if template is not provided.
        """
        template_path: Path = Path(self.template_path_str)

        if template_path.exists():
            logger.debug("Searching for SDK version in template file.")
            with open(template_path, "r", encoding="utf-8") as file:
                template: dict[str, Any] = json.load(file)
                metadata: dict[str, Any] = template.get("metadata", {})
                version: str = metadata.get("sdk_version", "")
                if version:
                    logger.info(f"Found SDK version in template file: {version}")
                else:
                    logger.debug("No SDK version found in template file. Using latest version.")
                    return LATEST_SDK_VERSION

                teoretical_path_to_sdk_folder: Path = Path(__file__).parent.parent.joinpath("sdk", version)
                if teoretical_path_to_sdk_folder.exists():
                    logger.debug("Verified existence of SDK folder in docker image.")
                    return version

                version = f"v{version}"

                teoretical_path_to_sdk_folder = Path(__file__).parent.parent.joinpath("sdk", version)
                if teoretical_path_to_sdk_folder.exists():
                    logger.debug("Verified existence of SDK folder in docker image.")
                    return version

        return LATEST_SDK_VERSION
