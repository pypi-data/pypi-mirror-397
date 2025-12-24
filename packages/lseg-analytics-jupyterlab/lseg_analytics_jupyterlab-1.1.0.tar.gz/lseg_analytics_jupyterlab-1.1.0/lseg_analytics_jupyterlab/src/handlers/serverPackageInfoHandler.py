from typing import Dict, Any, Optional
import importlib.metadata
from jupyter_server.base.handlers import APIHandler
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main
from lseg_analytics_jupyterlab.src.utils.serverUtils import (
    create_response,
)


class ServerPackageInfoHandler(APIHandler):
    """
    Handler for locating a package in the Python environment used by JupyterLab, and returning
    information about the installed package (name, location and version)
    """

    def get(self) -> None:
        """
        Handles GET requests to fetch information about a specified package.

        Query Parameters:
            package (str): The name of the package containing the metadata files.

        Responses:
            200: JSON object containing the combined metadata files.
            400: JSON object with an error message if the 'package' query parameter is missing.
            404: JSON object with an error message if the specified package is not found.
            500: JSON object with an error message if there is an internal server error.
        """
        package_name: Optional[str] = self.get_argument("package", None)
        if not package_name:
            self.set_status(400)
            error_msg: str = "Missing 'package' query parameter"
            self.finish(create_response("error", error_msg))
            return

        try:
            logger_main.debug(
                f"[Server][ServerPackageInfo] Attempting to find package: {package_name}"
            )

            # Check package existence
            found_distribution = self._find_distribution(package_name)

            if not found_distribution:
                self.set_status(404)
                error_msg: str = f"Package '{package_name}' not found"
                self.finish(create_response("error", error_msg))
                return

            package_info = self._create_package_info(package_name, found_distribution)

            success_msg: str = "Server package info fetched successfully"
            self.finish(create_response("success", success_msg, package_info))

            logger_main.debug(
                "[Server][ServerPackageInfo] Server package info successfully sent to client"
            )

        except Exception as e:
            logger_main.error(
                f"[Server][ServerPackageInfo] Error fetching package info: {e}"
            )
            self.set_status(500)
            error_msg: str = "Internal Server Error"
            self.finish(create_response("error", error_msg, str(e)))

    def _find_distribution(
        self, package_name: str
    ) -> Optional[importlib.metadata.Distribution]:
        try:
            # Note: "from_name" handles both hyphenated and non-hyphenated package names
            # e.g. it will find both lseg-analytics and lseg_analytics
            dist = importlib.metadata.Distribution.from_name(package_name)
            logger_main.debug(
                f"[Server][ServerPackageInfo] Package found: {package_name}"
            )
            return dist
        except importlib.metadata.PackageNotFoundError:
            logger_main.debug(
                f"[Server][ServerPackageInfo] Package not found: {package_name}"
            )
            return None

    # Helper function to create package info
    def _create_package_info(
        self, package_name: str, distribution: importlib.metadata.Distribution
    ) -> Dict[str, str]:

        package_info: Dict[str, str] = {
            "name": package_name,
            "version": distribution.version,
            "location": "",
        }

        # Try to get package location from distribution
        locate_file_result = distribution.locate_file("")
        if locate_file_result:
            package_info["location"] = str(locate_file_result.parent)

        return package_info
