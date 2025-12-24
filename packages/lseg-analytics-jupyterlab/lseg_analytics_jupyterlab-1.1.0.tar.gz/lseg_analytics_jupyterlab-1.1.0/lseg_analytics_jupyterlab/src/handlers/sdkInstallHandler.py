import json
import sys
import subprocess
import asyncio
from typing import List, Optional
from jupyter_server.base.handlers import APIHandler
from lseg_analytics_jupyterlab.src.classes.loggers import logger_main
from lseg_analytics_jupyterlab.src.utils.serverUtils import create_response


class SdkInstallHandler(APIHandler):
    """
    API handler for installing the LSEG Analytics Python SDK.
    SDK is installed into the Python environment being used by the JupyterLab instance.
    Simplified version that only supports silent installation.
    """

    async def post(self) -> None:
        """
        Silently install the LSEG Analytics SDK.

        Expected JSON payload:
        {
            "package_name": "lseg-analytics-pricing",
            "version_rules": [">=1.0.0", "<2.0.0"]
        }
        """
        package_name = None
        try:
            # Parse request data
            request_data = self._parse_request_body()

            # Extract parameters
            package_name = request_data.get("package_name")
            version_rules = request_data.get("version_rules", [])

            # Validate input
            if not package_name or not version_rules:
                logger_main.debug(
                    f"[SdkInstallHandler] Package name or version rules are not provided."
                )
                response = create_response(
                    "error",
                    "Package name and version rules must be provided.",
                    "Missing required parameters",
                )
                self.set_status(400)
                self.finish(response)
                return

            logger_main.debug(
                f"[SdkInstallHandler] Starting installation of {package_name}"
            )

            # Install the SDK
            await self._install_sdk(package_name, version_rules)

            logger_main.debug(
                f"[SdkInstallHandler] Successfully installed {package_name}"
            )

            # Success response using create_response
            response = create_response(
                "success",
                f"Successfully installed {package_name}",
                {"package_name": package_name, "version_rules": version_rules},
            )
            self.set_status(200)
            self.finish(response)

        except Exception as e:
            self._handle_installation_error(
                e, package_name or "unknown", "SDK installation"
            )

    async def _install_sdk(self, package_name: str, version_rules: List[str]) -> None:
        """
        Silently install the SDK package with version constraints.
        """
        # Convert version rules to pip constraint format
        rules = [r.strip() for r in (version_rules or []) if r and r.strip()]
        version_constraint = ",".join(rules)
        # Build package specification with version constraint
        package_spec = (
            f"{package_name}{version_constraint}"
            if version_constraint
            else package_name
        )

        # Build pip install command
        command = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--disable-pip-version-check",
            "--no-input",
            package_spec,
        ]
        cmd_str = " ".join(command)
        logger_main.debug(f"[SdkInstallHandler] Executing: {cmd_str}")

        try:
            # Run pip in a thread to avoid Windows ProactorEventLoop subprocess limitation
            loop = asyncio.get_running_loop()

            def _run():
                return subprocess.run(command, capture_output=True, text=True)

            result = await asyncio.wait_for(
                loop.run_in_executor(None, _run), timeout=300
            )

            out = (result.stdout or "").strip()
            err = (result.stderr or "").strip()

            if out:
                logger_main.debug(f"[SdkInstallHandler] pip stdout:\n{out}")
            if err:
                logger_main.debug(f"[SdkInstallHandler] pip stderr:\n{err}")

            if result.returncode != 0:
                raise Exception(
                    f"pip failed (code {result.returncode}) cmd: {cmd_str} "
                    f"stderr: {err or '<empty>'} stdout: {out or '<empty>'}"
                )

            logger_main.debug(
                f"[SdkInstallHandler] Installation completed successfully"
            )

        except asyncio.TimeoutError as e:
            logger_main.error(
                f"[SdkInstallHandler] pip install timed out after 300s: {e}"
            )
            raise

        except Exception as e:
            logger_main.error(f"[SdkInstallHandler] Installation failed: {e}")
            raise

    def _handle_installation_error(
        self, error: Exception, package_name: str, context: str
    ) -> None:
        """
        Handle errors during installation using create_response.
        """
        error_message = str(error)
        logger_main.debug(f"Failed to install {package_name}. Error: {error_message}")

        # Error response using create_response
        response = create_response(
            "error",
            f"Failed to install {package_name}",
            {"error_details": error_message, "context": context},
        )
        self.set_status(500)
        self.finish(response)

    def _parse_request_body(self) -> dict:
        """Parse the JSON request body."""
        try:
            if not self.request.body:
                return {}
            return json.loads(self.request.body.decode("utf-8"))
        except json.JSONDecodeError as e:
            logger_main.error(f"[SdkInstallHandler] Invalid JSON in request body: {e}")
            response = create_response(
                "error", "Invalid JSON format in request body", str(e)
            )
            self.set_status(400)
            self.finish(response)
            return {}
