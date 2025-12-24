from typing import Dict, Any, Optional
import json
import os
from jupyter_server.base.handlers import APIHandler
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main
from lseg_analytics_jupyterlab.src.utils.serverUtils import (
    create_response,
)


class PackageMetadataHandler(APIHandler):
    """
    Handler for fetching and combining JSON metadata files from a specified package.

    The user could have multiple different Python environments, with different a version
    of lseg_analytics installed in each. The client extension knows which environment a
    notebook/file is using; the server extension does not -> the client extension is
    responsible for providing the full path to the package installed in that environment.
    This handler does not need to find the package, just to find and load the data from
    within it.
    """

    def get(self) -> None:
        """
        Handles GET requests to fetch and combine JSON metadata files from a specified package.
        The client knows where the package is installed on disc; this server method does not need
        to find the package, just to find and load the data.

        Query Parameters:
            packageRootFolderPath (str): The absolute path to the root folder of the package on disc for which to fetch metadata e.g. c:\\project\\.env\\Lib\\site-packages\\lseg_analytics

        Responses:
            200: JSON object containing the combined metadata files.
            400: JSON object with an error message if the 'packageRootFolderPath' query parameter is missing.
            404: JSON object with an error message if the specified folder is not found.
            500: JSON object with an error message if there is an internal server error.
        """
        package_root_folder_path: Optional[str] = self.get_argument(
            "packageRootFolderPath", None
        )
        if not package_root_folder_path:
            self.set_status(400)
            error_msg: str = "Missing 'packageRootFolderPath' query parameter"
            self.finish(create_response("error", error_msg))
            return

        try:
            combined_metadata: Dict[str, Any] = self.read_and_combine_json_files(
                package_root_folder_path
            )

            if not combined_metadata:
                logger_main.warn(
                    f"[Server][ICC Metadata] No metadata files found for package: {package_root_folder_path}"
                )
                error_msg: str = "No metadata files found"
                additional_info: str = f"location: {package_root_folder_path}"
                self.finish(create_response("error", error_msg, additional_info))
                return

            logger_main.debug(
                f"[Server][ICC Metadata] Found {len(combined_metadata)} metadata files"
            )

            # Send the combined JSON to the client
            success_msg: str = "Metadata fetched successfully"
            self.finish(create_response("success", success_msg, combined_metadata))

            logger_main.debug(
                "[Server][ICC Metadata] Metadata successfully sent to client"
            )

        except Exception as e:
            logger_main.error(
                f"[Server][ICC Metadata] Error processing metadata files: {e}"
            )
            self.set_status(500)
            error_msg: str = "Internal Server Error"
            self.finish(create_response("error", error_msg, str(e)))

    def read_and_combine_json_files(
        self, package_root_folder_path: str
    ) -> Dict[str, Any]:
        combined_metadata: Dict[str, Any] = {}
        try:
            # Get the metadata directory path
            metadata_dir = os.path.join(
                package_root_folder_path,
                "metadata",
            )
            logger_main.debug(
                f"[Server][ICC Metadata] Metadata directory path: {metadata_dir}"
            )

            # Check if metadata directory exists
            if not os.path.exists(metadata_dir):
                logger_main.warn(
                    f"[Server][ICC Metadata] Metadata directory not found at {metadata_dir}"
                )
                return combined_metadata

            # List JSON files in the metadata directory
            for filename in os.listdir(metadata_dir):
                if filename.endswith(".json"):
                    try:
                        file_path = os.path.join(metadata_dir, filename)
                        with open(file_path, "r") as f:
                            file_content = json.load(f)
                            combined_metadata[filename] = file_content
                            logger_main.debug(
                                f"[Server][ICC Metadata] Processed file: {file_path}"
                            )
                    except Exception as e:
                        logger_main.error(
                            f"[Server][ICC Metadata] Error reading file {filename}: {e}"
                        )
        except Exception as e:
            logger_main.error(
                f"[Server][ICC Metadata] Error accessing metadata directory: {e}"
            )

        return combined_metadata
