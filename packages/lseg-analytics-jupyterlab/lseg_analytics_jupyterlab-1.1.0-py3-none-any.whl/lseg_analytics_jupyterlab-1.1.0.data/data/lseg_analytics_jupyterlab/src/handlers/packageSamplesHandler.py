import json
from jupyter_server.base.handlers import APIHandler
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main
from typing import Optional
import sys

if sys.version_info >= (3, 9):
    from importlib.resources import files
else:
    from importlib_resources import files


class PackageSamplesHandler(APIHandler):
    """
    Handler for fetching samples JSON metadata file or retrieving specific sample files (.py, .ipynb) from a specified package.
    """

    def get(self) -> None:
        """
        Handles GET requests to fetch samples JSON metadata file or retrieve specific files from a specified package.

        Query Parameters:
            relative_path_to_samples (str): The relative path to the samples folder within the package from the site-packages directory.
            file_path (str): The relative path of the file to retrieve within the package.

        Responses:
            200: JSON object or file content.
            400: JSON object with an error message if required query parameters are missing or invalid.
            404: JSON object with an error message if the file is not found.
            500: JSON object with an error message if there is an internal server error.
        """
        logger_main.debug("[Server][File Retrieval] GET method started.")

        relative_path_to_samples: Optional[str] = self.get_argument(
            "relative_path_to_samples", None
        )
        file_path: Optional[str] = self.get_argument("file_path", None)

        # Parameter validation
        if not relative_path_to_samples or not file_path:
            self.set_status(400)
            self.finish(
                json.dumps(
                    {
                        "error": "Missing 'relative_path_to_samples' or 'file_path' query parameter"
                    }
                )
            )
            return

        # Validate file extension
        if not file_path.endswith((".json", ".py", ".ipynb")):
            self.set_status(400)
            self.finish(
                json.dumps(
                    {
                        "error": f"Unsupported file type '{file_path}'. Only .json, .py, and .ipynb are allowed."
                    }
                )
            )
            return

        file_full_path = None
        try:

            file_full_path = self._get_full_path_to_package_file(
                relative_path_to_samples, file_path
            )

            # Read and return the file content
            with open(file_full_path, "r", encoding="utf-8") as f:
                if file_path.endswith(".json"):
                    file_content = json.load(f)
                    self.finish(json.dumps(file_content), set_content_type="text/plain")
                else:
                    file_content = f.read()
                    self.finish(file_content, set_content_type="text/plain")

            logger_main.debug(
                f"[Server][File Retrieval] Successfully retrieved file: {file_full_path}"
            )

        except FileNotFoundError:
            logger_main.error(
                f"[Server][File Retrieval] File not found: {file_full_path}"
            )
            self.set_status(404)
            self.finish(json.dumps({"error": "File not found"}))
        except Exception as e:
            logger_main.error(
                f"[Server][File Retrieval] Error processing file {file_path}: {e}"
            )
            self.set_status(500)
            self.finish(json.dumps({"error": "Internal Server Error"}))
        else:
            logger_main.debug(
                "[Server][File Retrieval] GET method completed successfully."
            )

    def _get_full_path_to_package_file(
        self, relative_path_to_samples: str, file_name: str
    ) -> str:
        """
        Constructs the full path to the file within the package samples directory.
        If the package or file cannot be found, raises FileNotFoundError.

        Args:
            relative_path_to_samples (str): The relative path to the samples folder within the package from the site-packages directory.
            file_name (str): The name of the file to retrieve.

        Returns:
            str: The full path to the file within the package samples directory.
        """

        # Sanity checks on the relative path.
        # It should never end with a '/' and should always contain at least one '/' to indicate a sub-folder.
        # This data is hard-coded in SupportedSDKProvider, so it should always be valid.
        if relative_path_to_samples[-1:] == "/":
            error_msg = (
                "[Server][SamplesHandler] - Internal error - invalid relative path to samples. Should not end with a '/'. Actual: "
                + relative_path_to_samples
            )
            raise ValueError(error_msg)

        first_separator = relative_path_to_samples.find("/")

        if first_separator == -1:
            error_msg = (
                "[Server][SamplesHandler] - Internal error - invalid relative path to samples. Should contain a sub-folder. Actual: "
                + relative_path_to_samples
            )
            raise ValueError(error_msg)

        # We are supplied the data in two string e.g. ("package_name/samples", "file name")
        # However, pkg_resources.resource_filename needs the package name and the relative path within the package
        # i.e. "package_name", "samples/file name" so we need to do some string manipulation here.

        package_folder = relative_path_to_samples[:first_separator]
        relative_file_path = (
            relative_path_to_samples[first_separator + 1 :] + "/" + file_name
        )

        # Use importlib.resources - works with namespace packages!
        package_files = files(package_folder)
        file_path = package_files.joinpath(relative_file_path)

        # Convert to string path (works with Path-like objects)
        full_path = str(file_path)

        # Verify file exists
        if not file_path.is_file():
            raise FileNotFoundError(
                f"[Server][File Retrieval] File not found: {full_path}"
            )

        logger_main.debug(f"[Server][File Retrieval] Located file: {full_path}")
        return full_path
