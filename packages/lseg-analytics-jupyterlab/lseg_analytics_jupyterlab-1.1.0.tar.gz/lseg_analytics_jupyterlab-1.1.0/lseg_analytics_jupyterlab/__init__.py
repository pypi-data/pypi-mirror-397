try:
    from ._version import __version__
except ImportError:
    # Fallback when using the package in dev mode without installing
    # in editable mode with pip. It is highly recommended to install
    # the package from a stable release or in editable mode: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
    import warnings

    warnings.warn(
        "Importing 'lseg_analytics_jupyterlab' outside a proper installation."
    )
    __version__ = "dev"

try:
    from lseg_analytics_jupyterlab.main import main
except ImportError as e:
    import warnings

    warnings.warn(f"Failed to import 'main'. Please check the module.: {str(e)}")

    def main():
        warnings.warn("Please ensure 'main' is properly defined.")


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "lseg-analytics-jupyterlab"}]


def _jupyter_server_extension_points():
    return [{"module": "lseg_analytics_jupyterlab"}]


def _load_jupyter_server_extension(server_app):
    """
    This function loads the Jupyter server extension.

    Parameters:
    server_app (object): The Jupyter server application instance.

    Returns:
    None
    """
    try:
        main(server_app.web_app)
        server_app.log.info("Jupyter Server extension loaded.")
    except Exception as e:
        server_app.log.error(f"An error occurred: {e}")
