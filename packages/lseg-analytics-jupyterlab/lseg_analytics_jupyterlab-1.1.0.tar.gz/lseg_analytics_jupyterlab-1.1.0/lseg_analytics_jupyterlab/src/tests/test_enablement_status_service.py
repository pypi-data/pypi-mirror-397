from unittest.mock import patch

from lseg_analytics_jupyterlab.src.classes.enablementStatusService import (
    EnablementStatusService,
)


@patch("lseg_analytics_jupyterlab.src.classes.enablementStatusService.logger_proxy")
def test_update_and_query_status(mock_logger):
    service = EnablementStatusService()

    service.update_status(True)

    assert service.user_has_lfa_access() is True
    mock_logger.debug.assert_called()


@patch("lseg_analytics_jupyterlab.src.classes.enablementStatusService.logger_proxy")
def test_user_has_lfa_access_defaults_false_when_missing(mock_logger):
    service = EnablementStatusService()

    assert service.user_has_lfa_access() is False
    mock_logger.debug.assert_called()


def test_clear_status_resets_matching_user():
    service = EnablementStatusService()
    service.update_status(True)

    service.clear_status()

    assert service.user_has_lfa_access() is False


def test_reset_clears_cache():
    service = EnablementStatusService()
    service.update_status(True)

    service.reset()

    assert service.user_has_lfa_access() is False
