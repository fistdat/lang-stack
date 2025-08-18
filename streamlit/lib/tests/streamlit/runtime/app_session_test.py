# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2025)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import asyncio
import gc
import threading
import unittest
from asyncio import AbstractEventLoop
from typing import Any, Callable, cast
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch

import pytest

from streamlit import config
from streamlit.proto.AppPage_pb2 import AppPage
from streamlit.proto.BackMsg_pb2 import BackMsg
from streamlit.proto.ClientState_pb2 import ClientState
from streamlit.proto.Common_pb2 import FileURLs, FileURLsRequest, FileURLsResponse
from streamlit.proto.ForwardMsg_pb2 import ForwardMsg
from streamlit.proto.NewSession_pb2 import FontFace
from streamlit.runtime import Runtime, app_session
from streamlit.runtime.app_session import AppSession, AppSessionState
from streamlit.runtime.caching.storage.dummy_cache_storage import (
    MemoryCacheStorageManager,
)
from streamlit.runtime.forward_msg_queue import ForwardMsgQueue
from streamlit.runtime.fragment import MemoryFragmentStorage
from streamlit.runtime.media_file_manager import MediaFileManager
from streamlit.runtime.memory_media_file_storage import MemoryMediaFileStorage
from streamlit.runtime.pages_manager import PagesManager
from streamlit.runtime.script_data import ScriptData
from streamlit.runtime.scriptrunner import (
    RerunData,
    ScriptRunContext,
    ScriptRunner,
    ScriptRunnerEvent,
    add_script_run_ctx,
    get_script_run_ctx,
)
from streamlit.runtime.state import SessionState
from streamlit.runtime.uploaded_file_manager import (
    UploadedFileManager,
    UploadFileUrlInfo,
)
from streamlit.watcher.local_sources_watcher import LocalSourcesWatcher
from tests.testutil import patch_config_options


@pytest.fixture
def del_path(monkeypatch):
    monkeypatch.setenv("PATH", "")


def _create_test_session(
    event_loop: AbstractEventLoop | None = None,
    session_id_override: str | None = None,
) -> AppSession:
    """Create an AppSession instance with some default mocked data."""
    if event_loop is None:
        event_loop = MagicMock()

    with (
        patch(
            "streamlit.runtime.app_session.asyncio.get_running_loop",
            return_value=event_loop,
        ),
        patch(
            "streamlit.runtime.app_session.LocalSourcesWatcher",
            MagicMock(spec=LocalSourcesWatcher),
        ),
    ):
        return AppSession(
            script_data=ScriptData("/fake/script_path.py", is_hello=False),
            uploaded_file_manager=MagicMock(spec=UploadedFileManager),
            script_cache=MagicMock(),
            message_enqueued_callback=None,
            user_info={"email": "test@example.com"},
            session_id_override=session_id_override,
        )


class AppSessionTest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        mock_runtime = MagicMock(spec=Runtime)
        mock_runtime.media_file_mgr = MediaFileManager(
            MemoryMediaFileStorage("/mock/media")
        )
        mock_runtime.cache_storage_manager = MemoryCacheStorageManager()
        Runtime._instance = mock_runtime

    def tearDown(self) -> None:
        super().tearDown()
        Runtime._instance = None

    @patch(
        "streamlit.runtime.app_session.uuid.uuid4", MagicMock(return_value="some_uuid")
    )
    def test_generates_uuid_for_session_id_if_no_override(self):
        session = _create_test_session()

        assert session.id == "some_uuid"

    def test_uses_session_id_override_if_set(self):
        session = _create_test_session(session_id_override="some_custom_session_id")

        assert session.id == "some_custom_session_id"

    @patch(
        "streamlit.runtime.app_session.secrets_singleton.file_change_listener.disconnect"
    )
    def test_shutdown(self, patched_disconnect):
        """Test that AppSession.shutdown behaves sanely."""
        session = _create_test_session()

        mock_file_mgr = MagicMock(spec=UploadedFileManager)
        session._uploaded_file_mgr = mock_file_mgr

        session.shutdown()
        assert session._state == AppSessionState.SHUTDOWN_REQUESTED
        mock_file_mgr.remove_session_files.assert_called_once_with(session.id)
        patched_disconnect.assert_called_once_with(session._on_secrets_file_changed)

        # A 2nd shutdown call should have no effect.
        session.shutdown()
        assert session._state == AppSessionState.SHUTDOWN_REQUESTED

        mock_file_mgr.remove_session_files.assert_called_once_with(session.id)

    def test_shutdown_with_running_scriptrunner(self):
        """If we have a running ScriptRunner, shutting down should stop it."""
        session = _create_test_session()
        mock_scriptrunner = MagicMock(spec=ScriptRunner)
        session._scriptrunner = mock_scriptrunner

        session.shutdown()
        mock_scriptrunner.request_stop.assert_called_once()

        mock_scriptrunner.reset_mock()

        # A 2nd shutdown call should have no effect.
        session.shutdown()
        mock_scriptrunner.request_stop.assert_not_called()

    def test_request_script_stop(self):
        """Verify that request_script_stop forwards the request to the scriptrunner."""
        session = _create_test_session()
        mock_scriptrunner = MagicMock(spec=ScriptRunner)
        session._scriptrunner = mock_scriptrunner

        session.request_script_stop()
        mock_scriptrunner.request_stop.assert_called()

    def test_request_script_stop_no_scriptrunner(self):
        """Test that calling request_script_stop when there is no scriptrunner doesn't
        result in an error.
        """
        session = _create_test_session()
        session._scriptrunner = None

        # Nothing else to do here aside from ensuring that no exception is thrown.
        session.request_script_stop()

    def test_unique_id(self):
        """Each AppSession should have a unique ID"""
        session1 = _create_test_session()
        session2 = _create_test_session()
        assert session1.id != session2.id

    def test_creates_session_state_on_init(self):
        session = _create_test_session()
        assert isinstance(session.session_state, SessionState)

    def test_creates_fragment_storage_on_init(self):
        session = _create_test_session()
        # NOTE: We only call assertIsNotNone here because protocols can't be used with
        # isinstance (there's no need to as the static type checker already ensures
        # the field has the correct type), and we don't want to mark
        # MemoryFragmentStorage as @runtime_checkable.
        assert session._fragment_storage is not None

    def test_clear_cache_resets_session_state(self):
        session = _create_test_session()
        session._session_state["foo"] = "bar"
        session._handle_clear_cache_request()
        assert "foo" not in session._session_state

    @patch("streamlit.runtime.caching.cache_data.clear")
    @patch("streamlit.runtime.caching.cache_resource.clear")
    def test_clear_cache_all_caches(self, clear_resource_caches, clear_data_caches):
        session = _create_test_session()
        session._handle_clear_cache_request()
        clear_resource_caches.assert_called_once()
        clear_data_caches.assert_called_once()

    @patch(
        "streamlit.runtime.app_session.secrets_singleton.file_change_listener.connect"
    )
    def test_request_rerun_on_secrets_file_change(self, patched_connect):
        """AppSession should add a secrets listener on creation."""
        session = _create_test_session()
        patched_connect.assert_called_once_with(session._on_secrets_file_changed)

    @patch_config_options({"runner.fastReruns": False})
    @patch("streamlit.runtime.app_session.AppSession._create_scriptrunner")
    def test_rerun_with_no_scriptrunner(self, mock_create_scriptrunner: MagicMock):
        """If we don't have a ScriptRunner, a rerun request will result in
        one being created."""
        session = _create_test_session()
        session.request_rerun(None)
        mock_create_scriptrunner.assert_called_once_with(RerunData())

    @patch_config_options({"runner.fastReruns": False})
    @patch("streamlit.runtime.app_session.AppSession._create_scriptrunner")
    def test_rerun_with_active_scriptrunner(self, mock_create_scriptrunner: MagicMock):
        """If we have an active ScriptRunner, it receives rerun requests."""
        session = _create_test_session()

        mock_active_scriptrunner = MagicMock(spec=ScriptRunner)
        mock_active_scriptrunner.request_rerun = MagicMock(return_value=True)
        session._scriptrunner = mock_active_scriptrunner

        session.request_rerun(None)

        # The active ScriptRunner will accept the rerun request...
        mock_active_scriptrunner.request_rerun.assert_called_once_with(RerunData())

        # So _create_scriptrunner should not be called.
        mock_create_scriptrunner.assert_not_called()

    @patch_config_options({"runner.fastReruns": False})
    @patch("streamlit.runtime.app_session.AppSession._create_scriptrunner")
    def test_rerun_with_stopped_scriptrunner(self, mock_create_scriptrunner: MagicMock):
        """If have a ScriptRunner but it's shutting down and cannot handle
        new rerun requests, we'll create a new ScriptRunner."""
        session = _create_test_session()

        mock_stopped_scriptrunner = MagicMock(spec=ScriptRunner)
        mock_stopped_scriptrunner.request_rerun = MagicMock(return_value=False)
        session._scriptrunner = mock_stopped_scriptrunner

        session.request_rerun(None)

        # The stopped ScriptRunner will reject the request...
        mock_stopped_scriptrunner.request_rerun.assert_called_once_with(RerunData())

        # So we'll create a new ScriptRunner.
        mock_create_scriptrunner.assert_called_once_with(RerunData())

    @patch_config_options({"runner.fastReruns": True})
    @patch("streamlit.runtime.app_session.AppSession._create_scriptrunner")
    def test_fast_rerun(self, mock_create_scriptrunner: MagicMock):
        """If runner.fastReruns is enabled, a rerun request will stop the
        existing ScriptRunner and immediately create a new one.
        """
        session = _create_test_session()

        mock_active_scriptrunner = MagicMock(spec=ScriptRunner)
        session._scriptrunner = mock_active_scriptrunner

        session.request_rerun(None)

        # The active ScriptRunner should be shut down.
        mock_active_scriptrunner.request_rerun.assert_not_called()
        mock_active_scriptrunner.request_stop.assert_called_once()

        # And a new ScriptRunner should be created.
        mock_create_scriptrunner.assert_called_once()

    @patch_config_options({"runner.fastReruns": True})
    @patch("streamlit.runtime.app_session.AppSession._create_scriptrunner")
    def test_rerun_fragment_requests_existing_scriptrunner(
        self, mock_create_scriptrunner: MagicMock
    ):
        session = _create_test_session()
        fragment_id = "my_fragment_id"
        session._fragment_storage.set(fragment_id, lambda: None)

        mock_active_scriptrunner = MagicMock(spec=ScriptRunner)
        session._scriptrunner = mock_active_scriptrunner

        session.request_rerun(ClientState(fragment_id=fragment_id))

        # The active ScriptRunner should *not* be shut down or stopped.
        mock_active_scriptrunner.request_rerun.assert_called_once()
        mock_active_scriptrunner.request_stop.assert_not_called()

        # And a new ScriptRunner should *not* be created.
        mock_create_scriptrunner.assert_not_called()

    @patch_config_options({"runner.fastReruns": True})
    @patch("streamlit.runtime.app_session.AppSession._create_scriptrunner")
    def test_rerun_fragment_does_not_request_existing_scriptrunner_when_not_existing(
        self, mock_create_scriptrunner: MagicMock
    ):
        """In case the fragment was removed by a preceding full app run, we want to exit
        early and not request a rerun on the existing ScriptRunner.
        """
        session = _create_test_session()
        fragment_id = "my_fragment_id"

        # leaving the following code line in to show that the fragment id
        # is not set in the fragment storage!
        # session._fragment_storage.set(fragment_id, lambda: None)  # noqa: ERA001

        mock_active_scriptrunner = MagicMock(spec=ScriptRunner)
        session._scriptrunner = mock_active_scriptrunner

        session.request_rerun(ClientState(fragment_id=fragment_id))

        # The active ScriptRunner should *not* be requested at all.
        mock_active_scriptrunner.request_rerun.assert_not_called()
        mock_active_scriptrunner.request_stop.assert_not_called()

        # And a new ScriptRunner should *not* be created.
        mock_create_scriptrunner.assert_not_called()

    @patch("streamlit.runtime.app_session.ScriptRunner")
    def test_create_scriptrunner(self, mock_scriptrunner: MagicMock):
        """Test that _create_scriptrunner does what it should."""
        session = _create_test_session()
        assert session._scriptrunner is None

        session._create_scriptrunner(initial_rerun_data=RerunData())

        # Assert that the ScriptRunner constructor was called.
        mock_scriptrunner.assert_called_once_with(
            session_id=session.id,
            main_script_path=session._script_data.main_script_path,
            session_state=session._session_state,
            uploaded_file_mgr=session._uploaded_file_mgr,
            script_cache=session._script_cache,
            initial_rerun_data=RerunData(),
            user_info={"email": "test@example.com"},
            fragment_storage=session._fragment_storage,
            pages_manager=session._pages_manager,
        )

        assert session._scriptrunner is not None

        # And that the ScriptRunner was initialized and started.
        scriptrunner: MagicMock = cast("MagicMock", session._scriptrunner)
        scriptrunner.on_event.connect.assert_called_once_with(
            session._on_scriptrunner_event
        )
        scriptrunner.start.assert_called_once()

    @patch("streamlit.runtime.app_session.ScriptRunner", MagicMock(spec=ScriptRunner))
    @patch("streamlit.runtime.app_session.AppSession._enqueue_forward_msg")
    def test_ignore_events_from_noncurrent_scriptrunner(self, mock_enqueue: MagicMock):
        """If we receive ScriptRunnerEvents from anything other than our
        current ScriptRunner, we should silently ignore them.
        """
        session = _create_test_session()
        session._create_scriptrunner(initial_rerun_data=RerunData())

        # Our test AppSession is created with a mock EventLoop, so
        # we pretend that this function is called on that same mock EventLoop.
        with patch(
            "streamlit.runtime.app_session.asyncio.get_running_loop",
            return_value=session._event_loop,
        ):
            session._handle_scriptrunner_event_on_event_loop(
                sender=session._scriptrunner,
                event=ScriptRunnerEvent.ENQUEUE_FORWARD_MSG,
                forward_msg=ForwardMsg(),
            )
            mock_enqueue.assert_called_once_with(ForwardMsg())

            mock_enqueue.reset_mock()

            non_current_scriptrunner = MagicMock(spec=ScriptRunner)
            session._handle_scriptrunner_event_on_event_loop(
                sender=non_current_scriptrunner,
                event=ScriptRunnerEvent.ENQUEUE_FORWARD_MSG,
                forward_msg=ForwardMsg(),
            )
            mock_enqueue.assert_not_called()

    @patch("streamlit.runtime.app_session.ScriptRunner", MagicMock(spec=ScriptRunner))
    @patch("streamlit.runtime.app_session.AppSession._enqueue_forward_msg", MagicMock())
    def test_resets_debug_last_backmsg_id_on_script_finished(self):
        session = _create_test_session()
        session._create_scriptrunner(initial_rerun_data=RerunData())
        session._debug_last_backmsg_id = "some_backmsg_id"

        with patch(
            "streamlit.runtime.app_session.asyncio.get_running_loop",
            return_value=session._event_loop,
        ):
            session._handle_scriptrunner_event_on_event_loop(
                sender=session._scriptrunner,
                event=ScriptRunnerEvent.SCRIPT_STOPPED_WITH_SUCCESS,
                forward_msg=ForwardMsg(),
            )

            assert session._debug_last_backmsg_id is None

    @patch("streamlit.runtime.app_session.ScriptRunner", MagicMock(spec=ScriptRunner))
    @patch("streamlit.runtime.app_session.AppSession._enqueue_forward_msg", MagicMock())
    def test_sets_state_to_not_running_on_rerun_event(self):
        session = _create_test_session()
        session._create_scriptrunner(initial_rerun_data=RerunData())
        session._state = AppSessionState.APP_IS_RUNNING

        with patch(
            "streamlit.runtime.app_session.asyncio.get_running_loop",
            return_value=session._event_loop,
        ):
            session._handle_scriptrunner_event_on_event_loop(
                sender=session._scriptrunner,
                event=ScriptRunnerEvent.SCRIPT_STOPPED_FOR_RERUN,
                forward_msg=ForwardMsg(),
            )

            assert session._state == AppSessionState.APP_NOT_RUNNING

    def test_passes_client_state_on_run_on_save(self):
        session = _create_test_session()
        session._run_on_save = True
        session.request_rerun = MagicMock()
        session._on_source_file_changed()

        session._script_cache.clear.assert_called_once()
        session.request_rerun.assert_called_once_with(session._client_state)

    @patch(
        "streamlit.runtime.app_session.AppSession._should_rerun_on_file_change",
        MagicMock(return_value=False),
    )
    def test_does_not_rerun_if_not_current_page(self):
        session = _create_test_session()
        session._run_on_save = True
        session.request_rerun = MagicMock()
        session._on_source_file_changed("/fake/script_path.py")

        # Clearing the cache should still have been called
        session._script_cache.clear.assert_called_once()

        assert not session.request_rerun.called

    @patch.object(
        PagesManager,
        "get_pages",
        MagicMock(
            return_value={
                "hash1": {"page_name": "page_1", "icon": "", "script_path": "script1"},
                "hash2": {
                    "page_name": "page_2",
                    "icon": "🎉",
                    "script_path": "script2",
                },
            }
        ),
    )
    def test_tags_fwd_msgs_with_last_backmsg_id_if_set(self):
        session = _create_test_session()
        session._debug_last_backmsg_id = "some backmsg id"

        msg = ForwardMsg()
        session._enqueue_forward_msg(msg)

        assert msg.debug_last_backmsg_id == "some backmsg id"

    @patch("streamlit.runtime.app_session.config.on_config_parsed")
    @patch(
        "streamlit.runtime.app_session.secrets_singleton.file_change_listener.connect"
    )
    @patch.object(
        PagesManager,
        "get_pages",
        MagicMock(return_value={}),
    )
    def test_registers_file_watchers(
        self,
        patched_secrets_connect,
        patched_on_config_parsed,
    ):
        session = _create_test_session()

        session._local_sources_watcher.register_file_change_callback.assert_called_once_with(
            session._on_source_file_changed
        )
        patched_on_config_parsed.assert_called_once_with(
            session._on_source_file_changed, force_connect=True
        )
        patched_secrets_connect.assert_called_once_with(
            session._on_secrets_file_changed
        )

    @patch.object(
        PagesManager,
        "get_pages",
        MagicMock(return_value={}),
    )
    def test_recreates_local_sources_watcher_if_none(self):
        session = _create_test_session()
        session._local_sources_watcher = None

        session.register_file_watchers()
        assert session._local_sources_watcher

    @patch_config_options({"server.fileWatcherType": "none"})
    def test_no_local_sources_watcher_if_file_watching_disabled(self):
        session = _create_test_session()
        assert not session._local_sources_watcher

    @patch(
        "streamlit.runtime.app_session.secrets_singleton.file_change_listener.disconnect"
    )
    def test_disconnect_file_watchers(self, patched_secrets_disconnect):
        session = _create_test_session()

        with (
            patch.object(
                session._local_sources_watcher, "close"
            ) as patched_close_local_sources_watcher,
            patch.object(
                session, "_stop_config_listener"
            ) as patched_stop_config_listener,
            patch.object(
                session, "_stop_pages_listener"
            ) as patched_stop_pages_listener,
        ):
            session.disconnect_file_watchers()

            patched_close_local_sources_watcher.assert_called_once()
            patched_stop_config_listener.assert_called_once()
            patched_stop_pages_listener.assert_called_once()
            patched_secrets_disconnect.assert_called_once_with(
                session._on_secrets_file_changed
            )

            assert session._local_sources_watcher is None
            assert session._stop_config_listener is None
            assert session._stop_pages_listener is None

    def test_disconnect_file_watchers_removes_refs(self):
        """Test that calling disconnect_file_watchers on the AppSession
        removes references to it so it is eligible to be garbage collected after the
        method is called.
        """
        session = _create_test_session()

        # Various listeners should have references to session file/pages/secrets changed
        # handlers.
        assert len(gc.get_referrers(session)) > 0

        session.disconnect_file_watchers()

        # Run the gc to ensure that we don't count refs to session from an object that
        # would have been garbage collected along with the session. We run the gc a few
        # times for good measure as otherwise we've previously seen weirdness in CI
        # where this test would fail for certain Python versions (exact reasons
        # unknown), so it seems like the first gc sweep may not always pick up the
        # session.
        gc.collect(2)
        gc.collect(2)
        gc.collect(2)

        assert len(gc.get_referrers(session)) == 0

    @patch("streamlit.runtime.app_session.AppSession._enqueue_forward_msg")
    def test_handle_file_urls_request(self, mock_enqueue):
        session = _create_test_session()

        upload_file_urls = [
            UploadFileUrlInfo(
                file_id="file_1",
                upload_url="upload_file_url_1",
                delete_url="delete_file_url_1",
            ),
            UploadFileUrlInfo(
                file_id="file_2",
                upload_url="upload_file_url_2",
                delete_url="delete_file_url_2",
            ),
            UploadFileUrlInfo(
                file_id="file_3",
                upload_url="upload_file_url_3",
                delete_url="delete_file_url_3",
            ),
        ]
        session._uploaded_file_mgr.get_upload_urls.return_value = upload_file_urls

        session._handle_file_urls_request(
            FileURLsRequest(
                request_id="my_id",
                file_names=["file_1", "file_2", "file_3"],
                session_id=session.id,
            )
        )

        session._uploaded_file_mgr.get_upload_urls.assert_called_once_with(
            session.id, ["file_1", "file_2", "file_3"]
        )

        expected_msg = ForwardMsg(
            file_urls_response=FileURLsResponse(
                response_id="my_id",
                file_urls=[
                    FileURLs(
                        file_id=url.file_id,
                        upload_url=url.upload_url,
                        delete_url=url.delete_url,
                    )
                    for url in upload_file_urls
                ],
            )
        )

        mock_enqueue.assert_called_once_with(expected_msg)

    def test_manual_rerun_preserves_context_info(self):
        """Test that manual reruns preserve context info."""
        session = _create_test_session()

        # Create a client state with context info (simulating a manual rerun from frontend)
        client_state = ClientState()
        client_state.context_info.timezone = "Europe/Berlin"
        client_state.context_info.locale = "de-DE"
        client_state.query_string = "test_query"
        client_state.page_script_hash = "test_hash"
        client_state.is_auto_rerun = False

        session._create_scriptrunner = MagicMock()
        session.request_rerun(client_state)

        # Verify that _create_scriptrunner was called
        session._create_scriptrunner.assert_called_once()

        # Get the RerunData that was passed to _create_scriptrunner
        rerun_data = session._create_scriptrunner.call_args[0][0]

        # Verify that context_info was preserved
        assert rerun_data.context_info is not None
        assert rerun_data.context_info.timezone == "Europe/Berlin"
        assert rerun_data.context_info.locale == "de-DE"
        assert rerun_data.query_string == "test_query"
        assert rerun_data.page_script_hash == "test_hash"
        assert rerun_data.is_auto_rerun is False

    def test_context_info_preserved_in_client_state_on_shutdown(self):
        """Test that context_info is preserved in client_state during SHUTDOWN event."""
        session = _create_test_session()

        # Set up initial context info in client state
        session._client_state.context_info.timezone = "America/New_York"
        session._client_state.context_info.locale = "en-US"
        session._client_state.query_string = "initial_query"
        session._client_state.page_script_hash = "initial_hash"

        # Create a mock ScriptRunner and simulate SHUTDOWN event
        mock_scriptrunner = MagicMock(spec=ScriptRunner)
        session._scriptrunner = mock_scriptrunner

        # Create client state with context info (as would be sent in SHUTDOWN event)
        shutdown_client_state = ClientState()
        shutdown_client_state.context_info.timezone = "Europe/London"
        shutdown_client_state.context_info.locale = "en-GB"
        shutdown_client_state.query_string = "shutdown_query"
        shutdown_client_state.page_script_hash = "shutdown_hash"

        with patch(
            "streamlit.runtime.app_session.asyncio.get_running_loop",
            return_value=session._event_loop,
        ):
            session._handle_scriptrunner_event_on_event_loop(
                sender=mock_scriptrunner,
                event=ScriptRunnerEvent.SHUTDOWN,
                client_state=shutdown_client_state,
            )

        # Verify that the client state was updated with the shutdown data
        assert session._client_state.context_info.timezone == "Europe/London"
        assert session._client_state.context_info.locale == "en-GB"
        assert session._client_state.query_string == "shutdown_query"
        assert session._client_state.page_script_hash == "shutdown_hash"


def _mock_get_options_for_section(
    overrides: dict[str, Any] | None = None,
) -> Callable[..., Any]:
    if not overrides:
        overrides = {}

    sidebar_theme_opts = {
        "backgroundColor": "white",
        "baseRadius": "1.2rem",
        "buttonRadius": "medium",
        "borderColor": "#ff0000",
        "dataframeBorderColor": "#280f63",
        "codeFont": "Monaspace Argon",
        "codeFontSize": "12px",
        "codeFontWeight": 500,
        "font": "Inter",
        "headingFont": "Inter Bold",
        "headingFontSizes": ["2.125rem", "2rem", "1.875rem"],
        "headingFontWeights": [700, 700, 600],
        "linkColor": "#2EC163",
        "linkUnderline": False,
        "primaryColor": "red",
        "secondaryBackgroundColor": "blue",
        "showWidgetBorder": True,
        "textColor": "black",
        "codeBackgroundColor": "blue",
        "dataframeHeaderBackgroundColor": "purple",
    }

    if overrides.get("sidebar") is not None:
        for k, v in overrides.get("sidebar").items():
            sidebar_theme_opts[k] = v

    theme_opts = {
        "backgroundColor": "white",
        "base": "dark",
        "baseFontSize": 14,
        "baseFontWeight": 300,
        "baseRadius": "1.2rem",
        "buttonRadius": "medium",
        "borderColor": "#ff0000",
        "dataframeBorderColor": "#280f63",
        "codeFont": "Monaspace Argon",
        "codeFontSize": "12px",
        "codeFontWeight": 300,
        "headingFontSizes": [
            "2.875rem",
            "2.75rem",
            "2rem",
            "1.75rem",
            "1.5rem",
            "1.25rem",
        ],
        "headingFontWeights": [700, 700, 600, 600],
        "font": "Inter",
        "fontFaces": [
            {
                "family": "Inter Bold",
                "url": "https://raw.githubusercontent.com/rsms/inter/refs/heads/master/docs/font-files/Inter-Bold.woff2",
            },
            {
                "family": "Inter",
                "url": "https://raw.githubusercontent.com/rsms/inter/refs/heads/master/docs/font-files/Inter-Regular.woff2",
                "weight": 400,
            },
            {
                "family": "Monaspace Argon",
                "url": "https://raw.githubusercontent.com/githubnext/monaspace/refs/heads/main/fonts/webfonts/MonaspaceArgon-Regular.woff2",
                "weight": 400,
            },
        ],
        "headingFont": "Inter Bold",
        "linkColor": "#2EC163",
        "linkUnderline": False,
        "primaryColor": "coral",
        "secondaryBackgroundColor": "blue",
        "showWidgetBorder": True,
        "showSidebarBorder": True,
        "textColor": "black",
        "codeBackgroundColor": "blue",
        "dataframeHeaderBackgroundColor": "purple",
        "chartCategoricalColors": [
            "#7fc97f",
            "#beaed4",
            "#fdc086",
            "#ffff99",
            "#386cb0",
            "#f0027f",
            "#bf5b17",
            "#666666",
        ],
        "chartSequentialColors": [
            "#dffde9",
            "#c0fcd3",
            "#9ef6bb",
            "#7defa1",
            "#5ce488",
            "#3dd56d",
            "#21c354",
            "#09ab3b",
            "#158237",
            "#177233",
        ],
    }

    for k, v in overrides.items():
        if k != "sidebar":
            theme_opts[k] = v

    def get_options_for_section(section):
        if section == "theme":
            return theme_opts
        if section == "theme.sidebar":
            return sidebar_theme_opts
        return config.get_options_for_section(section)

    return get_options_for_section


class AppSessionScriptEventTest(IsolatedAsyncioTestCase):
    """Tests for AppSession's ScriptRunner event handling."""

    @patch(
        "streamlit.runtime.app_session.config.get_options_for_section",
        MagicMock(side_effect=_mock_get_options_for_section()),
    )
    @patch.object(
        PagesManager,
        "get_pages",
        MagicMock(
            return_value={
                "hash1": {"page_name": "page_1", "icon": "", "script_path": "script1"},
                "hash2": {
                    "page_name": "page_2",
                    "icon": "🎉",
                    "script_path": "script2",
                },
            }
        ),
    )
    @patch(
        "streamlit.runtime.app_session._generate_scriptrun_id",
        MagicMock(return_value="mock_scriptrun_id"),
    )
    async def test_enqueue_new_session_message(self):
        """The SCRIPT_STARTED event should enqueue a 'new_session' message."""
        session = _create_test_session(asyncio.get_running_loop())

        orig_ctx = get_script_run_ctx()
        ctx = ScriptRunContext(
            session_id="TestSessionID",
            _enqueue=session._enqueue_forward_msg,
            query_string="",
            session_state=MagicMock(),
            uploaded_file_mgr=MagicMock(),
            main_script_path="",
            user_info={"email": "test@example.com"},
            fragment_storage=MemoryFragmentStorage(),
            pages_manager=PagesManager(""),
        )
        add_script_run_ctx(ctx=ctx)

        mock_scriptrunner = MagicMock(spec=ScriptRunner)
        session._scriptrunner = mock_scriptrunner
        session._clear_queue = MagicMock()

        # Send a mock SCRIPT_STARTED event.
        session._on_scriptrunner_event(
            sender=mock_scriptrunner,
            event=ScriptRunnerEvent.SCRIPT_STARTED,
            page_script_hash="",
        )

        # Yield to let the AppSession's callbacks run.
        await asyncio.sleep(0)

        sent_messages = session._browser_queue._queue
        assert len(sent_messages) == 2  # NewApp and SessionState messages
        session._clear_queue.assert_called_once()

        # Note that we're purposefully not very thoroughly testing new_session
        # fields below to avoid getting to the point where we're just
        # duplicating code in tests.
        new_session_msg = sent_messages[0].new_session
        assert new_session_msg.script_run_id == "mock_scriptrun_id"

        assert new_session_msg.HasField("config")
        assert (
            config.get_option("server.allowRunOnSave")
            == new_session_msg.config.allow_run_on_save
        )

        assert new_session_msg.HasField("custom_theme")
        assert new_session_msg.custom_theme.text_color == "black"

        init_msg = new_session_msg.initialize
        assert init_msg.HasField("user_info")

        assert list(new_session_msg.app_pages) == [
            AppPage(
                page_script_hash="hash1",
                page_name="page 1",
                icon="",
                url_pathname="page_1",
            ),
            AppPage(
                page_script_hash="hash2",
                page_name="page 2",
                icon="🎉",
                url_pathname="page_2",
            ),
        ]

        add_script_run_ctx(ctx=orig_ctx)

    @patch(
        "streamlit.runtime.app_session._generate_scriptrun_id",
        MagicMock(return_value="mock_scriptrun_id"),
    )
    async def test_new_session_message_includes_fragment_ids(self):
        session = _create_test_session(asyncio.get_running_loop())

        orig_ctx = get_script_run_ctx()
        ctx = ScriptRunContext(
            session_id="TestSessionID",
            _enqueue=session._enqueue_forward_msg,
            query_string="",
            session_state=MagicMock(),
            uploaded_file_mgr=MagicMock(),
            main_script_path="",
            user_info={"email": "test@example.com"},
            fragment_storage=MemoryFragmentStorage(),
            pages_manager=PagesManager(""),
        )
        add_script_run_ctx(ctx=ctx)

        mock_scriptrunner = MagicMock(spec=ScriptRunner)
        session._scriptrunner = mock_scriptrunner
        session._clear_queue = MagicMock()

        # Send a mock SCRIPT_STARTED event.
        session._on_scriptrunner_event(
            sender=mock_scriptrunner,
            event=ScriptRunnerEvent.SCRIPT_STARTED,
            page_script_hash="",
            fragment_ids_this_run=["my_fragment_id"],
        )

        # Yield to let the AppSession's callbacks run.
        await asyncio.sleep(0)

        sent_messages = session._browser_queue._queue
        assert len(sent_messages) == 2  # NewApp and SessionState messages
        session._clear_queue.assert_called_once()

        new_session_msg = sent_messages[0].new_session
        assert new_session_msg.fragment_ids_this_run == ["my_fragment_id"]

        add_script_run_ctx(ctx=orig_ctx)

    async def test_updates_page_script_hash_in_client_state_on_script_start(self):
        session = _create_test_session(asyncio.get_running_loop())
        session._client_state.page_script_hash = "some_page_script_hash"

        mock_scriptrunner = MagicMock(spec=ScriptRunner)
        session._scriptrunner = mock_scriptrunner
        session._clear_queue = MagicMock()

        # Send a mock SCRIPT_STARTED event.
        session._on_scriptrunner_event(
            sender=mock_scriptrunner,
            event=ScriptRunnerEvent.SCRIPT_STARTED,
            page_script_hash="some_other_page_script_hash",
            fragment_ids_this_run=None,
        )

        # Yield to let the AppSession's callbacks run.
        await asyncio.sleep(0)

        assert session._client_state.page_script_hash == "some_other_page_script_hash"

    async def test_events_handled_on_event_loop(self):
        """ScriptRunner events should be handled on the main thread only."""
        session = _create_test_session(asyncio.get_running_loop())

        handle_event_spy = MagicMock(
            side_effect=session._handle_scriptrunner_event_on_event_loop
        )
        session._handle_scriptrunner_event_on_event_loop = handle_event_spy

        # Send a ScriptRunner event from another thread
        thread = threading.Thread(
            target=lambda: session._on_scriptrunner_event(
                sender=MagicMock(), event=ScriptRunnerEvent.SCRIPT_STARTED
            )
        )
        thread.start()
        thread.join()

        # _handle_scriptrunner_event_on_event_loop won't have been called
        # yet, because we haven't yielded the eventloop.
        handle_event_spy.assert_not_called()

        # Yield to let the AppSession's callbacks run.
        # _handle_scriptrunner_event_on_event_loop will be called here.
        await asyncio.sleep(0)

        handle_event_spy.assert_called_once()

    async def test_event_handler_asserts_if_called_off_event_loop(self):
        """AppSession._handle_scriptrunner_event_on_event_loop will assert
        if it's called from another event loop (or no event loop).
        """
        event_loop = asyncio.get_running_loop()
        session = _create_test_session(event_loop)

        # Pretend we're calling this function from a thread with another event_loop.
        with (
            patch(
                "streamlit.runtime.app_session.asyncio.get_running_loop",
                return_value=MagicMock(),
            ),
            pytest.raises(
                RuntimeError,
                match="This function must only be called on the eventloop thread "
                "the AppSession was created on. This should never happen.",
            ),
        ):
            session._handle_scriptrunner_event_on_event_loop(
                sender=MagicMock(), event=ScriptRunnerEvent.SCRIPT_STARTED
            )

    @patch(
        "streamlit.runtime.app_session.config.get_options_for_section",
        MagicMock(side_effect=_mock_get_options_for_section()),
    )
    @patch(
        "streamlit.runtime.app_session._generate_scriptrun_id",
        MagicMock(return_value="mock_scriptrun_id"),
    )
    async def test_handle_backmsg_exception(self):
        """handle_backmsg_exception is a bit of a hack. Test that it does
        what it says.
        """
        session = _create_test_session(asyncio.get_running_loop())

        # Create a mocked ForwardMsgQueue that tracks "enqueue" and "clear"
        # function calls together in a list. We'll assert the content
        # and order of these calls.
        forward_msg_queue_events: list[Any] = []
        CLEAR_QUEUE = object()

        mock_queue = MagicMock(spec=ForwardMsgQueue)
        mock_queue.enqueue = MagicMock(
            side_effect=lambda msg: forward_msg_queue_events.append(msg)
        )
        mock_queue.clear = MagicMock(
            side_effect=lambda retain_lifecycle_msgs,
            fragment_ids_this_run: forward_msg_queue_events.append(CLEAR_QUEUE)
        )

        session._browser_queue = mock_queue

        # Create an exception and have the session handle it.
        FAKE_EXCEPTION = RuntimeError("I am error")
        session.handle_backmsg_exception(FAKE_EXCEPTION)

        # Messages get sent in an eventloop callback, which hasn't had a chance
        # to run yet. Our message queue should be empty.
        assert forward_msg_queue_events == []

        # Run callbacks
        await asyncio.sleep(0)

        # Build our "expected events" list. We need to mock different
        # AppSessionState values for our AppSession to build the list.
        expected_events = []

        with patch.object(session, "_state", new=AppSessionState.APP_IS_RUNNING):
            expected_events.extend(
                [
                    session._create_script_finished_message(
                        ForwardMsg.FINISHED_SUCCESSFULLY
                    ),
                    CLEAR_QUEUE,
                    session._create_new_session_message(page_script_hash=""),
                    session._create_session_status_changed_message(),
                ]
            )

        with patch.object(session, "_state", new=AppSessionState.APP_NOT_RUNNING):
            expected_events.extend(
                [
                    session._create_script_finished_message(
                        ForwardMsg.FINISHED_SUCCESSFULLY
                    ),
                    session._create_session_status_changed_message(),
                    session._create_exception_message(FAKE_EXCEPTION),
                ]
            )

        assert expected_events == forward_msg_queue_events

    async def test_handle_backmsg_handles_exceptions(self):
        """Exceptions raised in handle_backmsg should be sent to
        handle_backmsg_exception.
        """
        session = _create_test_session(asyncio.get_running_loop())
        with (
            patch.object(
                session, "handle_backmsg_exception"
            ) as handle_backmsg_exception,
            patch.object(
                session, "_handle_clear_cache_request"
            ) as handle_clear_cache_request,
        ):
            error = Exception("explode!")
            handle_clear_cache_request.side_effect = error

            msg = BackMsg()
            msg.clear_cache = True
            session.handle_backmsg(msg)

            handle_clear_cache_request.assert_called_once()
            handle_backmsg_exception.assert_called_once_with(error)

    @patch("streamlit.runtime.app_session.AppSession._create_scriptrunner", MagicMock())
    async def test_handle_backmsg_handles_debug_ids(self):
        session = _create_test_session(asyncio.get_running_loop())
        msg = BackMsg(
            rerun_script=session._client_state, debug_last_backmsg_id="some backmsg"
        )
        session.handle_backmsg(msg)
        assert session._debug_last_backmsg_id == "some backmsg"

    @patch("streamlit.runtime.app_session._LOGGER")
    async def test_handles_app_heartbeat_backmsg(self, patched_logger):
        session = _create_test_session(asyncio.get_running_loop())
        with (
            patch.object(
                session, "handle_backmsg_exception"
            ) as handle_backmsg_exception,
            patch.object(
                session, "_handle_app_heartbeat_request"
            ) as handle_app_heartbeat_request,
        ):
            msg = BackMsg()
            msg.app_heartbeat = True
            session.handle_backmsg(msg)

            handle_app_heartbeat_request.assert_called_once()
            handle_backmsg_exception.assert_not_called()
            patched_logger.warning.assert_not_called()

    async def test_event_handler_raises_error_if_page_hash_none_on_script_started(
        self,
    ):
        """Test that _handle_scriptrunner_event_on_event_loop raises RuntimeError
        if page_script_hash is None when event is SCRIPT_STARTED.
        """
        session = _create_test_session(asyncio.get_running_loop())
        mock_scriptrunner = MagicMock(spec=ScriptRunner)
        session._scriptrunner = mock_scriptrunner

        with pytest.raises(
            RuntimeError,
            match="page_script_hash must be set for the SCRIPT_STARTED event. This should never happen.",
        ):
            session._handle_scriptrunner_event_on_event_loop(
                sender=mock_scriptrunner,
                event=ScriptRunnerEvent.SCRIPT_STARTED,
                page_script_hash=None,  # This is the condition we're testing
            )

    async def test_event_handler_raises_error_if_exception_none_on_compile_error(
        self,
    ):
        """Test that _handle_scriptrunner_event_on_event_loop raises RuntimeError
        if exception is None when event is SCRIPT_STOPPED_WITH_COMPILE_ERROR.
        """
        session = _create_test_session(asyncio.get_running_loop())
        mock_scriptrunner = MagicMock(spec=ScriptRunner)
        session._scriptrunner = mock_scriptrunner

        with pytest.raises(
            RuntimeError,
            match="exception must be set for the SCRIPT_STOPPED_WITH_COMPILE_ERROR event. This should never happen.",
        ):
            session._handle_scriptrunner_event_on_event_loop(
                sender=mock_scriptrunner,
                event=ScriptRunnerEvent.SCRIPT_STOPPED_WITH_COMPILE_ERROR,
                exception=None,  # This is the condition we're testing
            )

    async def test_event_handler_raises_error_if_client_state_none_on_shutdown(
        self,
    ):
        """Test that _handle_scriptrunner_event_on_event_loop raises RuntimeError
        if client_state is None when event is SHUTDOWN.
        """
        session = _create_test_session(asyncio.get_running_loop())
        mock_scriptrunner = MagicMock(spec=ScriptRunner)
        session._scriptrunner = mock_scriptrunner

        with pytest.raises(
            RuntimeError,
            match="client_state must be set for the SHUTDOWN event. This should never happen.",
        ):
            session._handle_scriptrunner_event_on_event_loop(
                sender=mock_scriptrunner,
                event=ScriptRunnerEvent.SHUTDOWN,
                client_state=None,  # This is the condition we're testing
            )

    async def test_event_handler_raises_error_if_forward_msg_none_on_enqueue(
        self,
    ):
        """Test that _handle_scriptrunner_event_on_event_loop raises RuntimeError
        if forward_msg is None when event is ENQUEUE_FORWARD_MSG.
        """
        session = _create_test_session(asyncio.get_running_loop())
        mock_scriptrunner = MagicMock(spec=ScriptRunner)
        session._scriptrunner = mock_scriptrunner

        with pytest.raises(
            RuntimeError,
            match="null forward_msg in ENQUEUE_FORWARD_MSG event. This should never happen.",
        ):
            session._handle_scriptrunner_event_on_event_loop(
                sender=mock_scriptrunner,
                event=ScriptRunnerEvent.ENQUEUE_FORWARD_MSG,
                forward_msg=None,  # This is the condition we're testing
            )


class PopulateCustomThemeMsgTest(unittest.TestCase):
    @patch("streamlit.runtime.app_session.config")
    def test_no_custom_theme_prop_if_no_theme(self, patched_config):
        patched_config.get_options_for_section.side_effect = (
            _mock_get_options_for_section(
                {
                    "backgroundColor": None,
                    "base": None,
                    "baseFontSize": None,
                    "baseFontWeight": None,
                    "baseRadius": None,
                    "buttonRadius": None,
                    "borderColor": None,
                    "dataframeBorderColor": None,
                    "codeFont": None,
                    "codeFontSize": None,
                    "codeFontWeight": None,
                    "font": None,
                    "fontFaces": None,
                    "headingFont": None,
                    "headingFontSizes": None,
                    "headingFontWeights": None,
                    "linkColor": None,
                    "linkUnderline": None,
                    "primaryColor": None,
                    "secondaryBackgroundColor": None,
                    "showWidgetBorder": None,
                    "showSidebarBorder": None,
                    "textColor": None,
                    "sidebar": None,
                    "codeBackgroundColor": None,
                    "dataframeHeaderBackgroundColor": None,
                    "chartCategoricalColors": None,
                    "chartSequentialColors": None,
                }
            )
        )

        msg = ForwardMsg()
        new_session_msg = msg.new_session
        app_session._populate_theme_msg(new_session_msg.custom_theme)

        assert not new_session_msg.HasField("custom_theme")

    @patch("streamlit.runtime.app_session.config")
    def test_can_specify_false_options(self, patched_config):
        patched_config.get_options_for_section.side_effect = (
            _mock_get_options_for_section(
                {
                    "backgroundColor": None,
                    "base": None,
                    "baseFontSize": None,
                    "baseFontWeight": None,
                    "baseRadius": None,
                    "buttonRadius": None,
                    "borderColor": None,
                    "dataframeBorderColor": None,
                    "codeFont": None,
                    "codeFontSize": None,
                    "codeFontWeight": None,
                    "font": None,
                    "fontFaces": None,
                    "headingFont": None,
                    "headingFontSizes": None,
                    "headingFontWeights": None,
                    "linkColor": None,
                    "linkUnderline": None,
                    "primaryColor": None,
                    "secondaryBackgroundColor": None,
                    "showWidgetBorder": False,
                    "showSidebarBorder": None,
                    "textColor": None,
                    "sidebar": None,
                    "codeBackgroundColor": None,
                    "dataframeHeaderBackgroundColor": None,
                    "chartCategoricalColors": None,
                    "chartSequentialColors": None,
                }
            )
        )

        msg = ForwardMsg()
        new_session_msg = msg.new_session
        app_session._populate_theme_msg(new_session_msg.custom_theme)

        assert new_session_msg.HasField("custom_theme")
        assert new_session_msg.custom_theme.show_widget_border is False

    @patch("streamlit.runtime.app_session.config")
    def test_can_specify_some_options(self, patched_config):
        patched_config.get_options_for_section.side_effect = (
            _mock_get_options_for_section(
                {
                    # base and primaryColor are not set to None, since we want to
                    # test here if we can set only a few selected options.
                    "backgroundColor": None,
                    "baseRadius": None,
                    "buttonRadius": None,
                    "baseFontSize": None,
                    "baseFontWeight": None,
                    "borderColor": None,
                    "dataframeBorderColor": None,
                    "codeFont": None,
                    "codeFontSize": None,
                    "codeFontWeight": None,
                    "headingFontSizes": None,
                    "headingFontWeights": None,
                    "font": None,
                    "fontFaces": None,
                    "headingFont": None,
                    "linkColor": None,
                    "linkUnderline": None,
                    "secondaryBackgroundColor": None,
                    "showWidgetBorder": None,
                    "showSidebarBorder": None,
                    "textColor": None,
                    "codeBackgroundColor": None,
                    "dataframeHeaderBackgroundColor": None,
                    "chartCategoricalColors": None,
                    "chartSequentialColors": None,
                    "sidebar": {
                        # primaryColor not set to None
                        "backgroundColor": None,
                        "baseRadius": None,
                        "buttonRadius": None,
                        "borderColor": None,
                        "dataframeBorderColor": None,
                        "codeFont": None,
                        "codeFontSize": None,
                        "codeFontWeight": None,
                        "font": None,
                        "headingFont": None,
                        "headingFontSizes": None,
                        "headingFontWeights": None,
                        "linkColor": None,
                        "linkUnderline": None,
                        "secondaryBackgroundColor": None,
                        "showWidgetBorder": None,
                        "textColor": None,
                        "codeBackgroundColor": None,
                        "dataframeHeaderBackgroundColor": None,
                    },
                }
            )
        )

        msg = ForwardMsg()
        new_session_msg = msg.new_session
        app_session._populate_theme_msg(new_session_msg.custom_theme)

        assert new_session_msg.HasField("custom_theme")
        assert new_session_msg.custom_theme.primary_color == "coral"
        # In proto3, primitive fields are technically always required and are
        # set to the type's zero value when undefined.
        assert new_session_msg.custom_theme.background_color == ""
        assert new_session_msg.custom_theme.heading_font == ""
        assert new_session_msg.custom_theme.code_font == ""
        # The value from `theme.font` will be placed in body_font since
        # font field uses a deprecated enum:
        assert new_session_msg.custom_theme.body_font == ""
        assert not new_session_msg.custom_theme.font_faces

        # Fields that are marked as optional in proto:
        assert not new_session_msg.custom_theme.HasField("base_radius")
        assert not new_session_msg.custom_theme.HasField("button_radius")
        assert not new_session_msg.custom_theme.HasField("border_color")
        assert not new_session_msg.custom_theme.HasField("dataframe_border_color")
        assert not new_session_msg.custom_theme.HasField("show_widget_border")
        assert not new_session_msg.custom_theme.HasField("link_color")
        assert not new_session_msg.custom_theme.HasField("link_underline")
        assert not new_session_msg.custom_theme.HasField("base_font_size")
        assert not new_session_msg.custom_theme.HasField("base_font_weight")
        assert not new_session_msg.custom_theme.HasField("code_font_size")
        assert not new_session_msg.custom_theme.HasField("code_font_weight")
        assert not new_session_msg.custom_theme.HasField("show_sidebar_border")
        assert not new_session_msg.custom_theme.HasField("code_background_color")
        assert not new_session_msg.custom_theme.HasField(
            "dataframe_header_background_color"
        )

        # Fields that are marked as repeated in proto:
        assert not new_session_msg.custom_theme.heading_font_sizes
        assert not new_session_msg.custom_theme.heading_font_weights
        assert not new_session_msg.custom_theme.chart_categorical_colors
        assert not new_session_msg.custom_theme.chart_sequential_colors

        app_session._populate_theme_msg(
            new_session_msg.custom_theme.sidebar,
            "theme.sidebar",
        )

        assert new_session_msg.custom_theme.HasField("sidebar")
        assert new_session_msg.custom_theme.sidebar.primary_color == "red"
        assert new_session_msg.custom_theme.sidebar.background_color == ""
        assert new_session_msg.custom_theme.sidebar.heading_font == ""
        assert new_session_msg.custom_theme.sidebar.code_font == ""
        assert new_session_msg.custom_theme.sidebar.body_font == ""

        # Fields that are marked as optional in proto:
        assert not new_session_msg.custom_theme.sidebar.HasField("base_radius")
        assert not new_session_msg.custom_theme.sidebar.HasField("button_radius")
        assert not new_session_msg.custom_theme.sidebar.HasField("border_color")
        assert not new_session_msg.custom_theme.sidebar.HasField(
            "dataframe_border_color"
        )
        assert not new_session_msg.custom_theme.sidebar.HasField("show_widget_border")
        assert not new_session_msg.custom_theme.sidebar.HasField("link_color")
        assert not new_session_msg.custom_theme.sidebar.HasField("link_underline")
        assert not new_session_msg.custom_theme.sidebar.HasField("base_font_size")
        assert not new_session_msg.custom_theme.sidebar.HasField("base_font_weight")
        assert not new_session_msg.custom_theme.sidebar.HasField("code_font_size")
        assert not new_session_msg.custom_theme.sidebar.HasField("code_font_weight")
        assert not new_session_msg.custom_theme.sidebar.HasField("show_sidebar_border")
        assert not new_session_msg.custom_theme.sidebar.HasField(
            "code_background_color"
        )
        assert not new_session_msg.custom_theme.sidebar.HasField(
            "dataframe_header_background_color"
        )

        # Fields that are marked as repeated in proto:
        assert not new_session_msg.custom_theme.sidebar.heading_font_sizes
        assert not new_session_msg.custom_theme.sidebar.heading_font_weights
        assert not new_session_msg.custom_theme.sidebar.chart_categorical_colors
        assert not new_session_msg.custom_theme.sidebar.chart_sequential_colors

    @patch("streamlit.runtime.app_session.config")
    def test_can_specify_all_options(self, patched_config):
        patched_config.get_options_for_section.side_effect = (
            # Specifies all options by default.
            _mock_get_options_for_section()
        )

        msg = ForwardMsg()
        new_session_msg = msg.new_session
        app_session._populate_theme_msg(new_session_msg.custom_theme)

        assert new_session_msg.HasField("custom_theme")
        assert new_session_msg.custom_theme.primary_color == "coral"
        assert new_session_msg.custom_theme.background_color == "white"
        assert new_session_msg.custom_theme.text_color == "black"
        assert new_session_msg.custom_theme.secondary_background_color == "blue"
        assert new_session_msg.custom_theme.base_radius == "1.2rem"
        assert new_session_msg.custom_theme.button_radius == "medium"
        assert new_session_msg.custom_theme.border_color == "#ff0000"
        assert new_session_msg.custom_theme.dataframe_border_color == "#280f63"
        assert new_session_msg.custom_theme.show_widget_border is True
        assert new_session_msg.custom_theme.link_color == "#2EC163"
        assert new_session_msg.custom_theme.link_underline is False
        assert new_session_msg.custom_theme.base_font_size == 14
        assert new_session_msg.custom_theme.base_font_weight == 300
        assert new_session_msg.custom_theme.code_font_size == "12px"
        assert new_session_msg.custom_theme.code_font_weight == 300
        assert new_session_msg.custom_theme.show_sidebar_border is True
        assert new_session_msg.custom_theme.code_background_color == "blue"
        assert (
            new_session_msg.custom_theme.dataframe_header_background_color == "purple"
        )
        assert new_session_msg.custom_theme.heading_font_sizes == [
            "2.875rem",
            "2.75rem",
            "2rem",
            "1.75rem",
            "1.5rem",
            "1.25rem",
        ]
        # app_session sets the default value (600) for the missing values, so even with only
        # 4 values set in the config, we should have 6 values
        assert new_session_msg.custom_theme.heading_font_weights == [
            700,
            700,
            600,
            600,
            600,
            600,
        ]

        # The value from `theme.font` will be placed in body_font since
        # font uses a deprecated enum:
        assert new_session_msg.custom_theme.heading_font == "Inter Bold"
        assert new_session_msg.custom_theme.body_font == "Inter"
        assert new_session_msg.custom_theme.code_font == "Monaspace Argon"
        assert list(new_session_msg.custom_theme.chart_categorical_colors) == [
            "#7fc97f",
            "#beaed4",
            "#fdc086",
            "#ffff99",
            "#386cb0",
            "#f0027f",
            "#bf5b17",
            "#666666",
        ]
        assert list(new_session_msg.custom_theme.chart_sequential_colors) == [
            "#dffde9",
            "#c0fcd3",
            "#9ef6bb",
            "#7defa1",
            "#5ce488",
            "#3dd56d",
            "#21c354",
            "#09ab3b",
            "#158237",
            "#177233",
        ]
        assert list(new_session_msg.custom_theme.font_faces) == [
            FontFace(
                family="Inter Bold",
                url="https://raw.githubusercontent.com/rsms/inter/refs/heads/master/docs/font-files/Inter-Bold.woff2",
            ),
            FontFace(
                family="Inter",
                url="https://raw.githubusercontent.com/rsms/inter/refs/heads/master/docs/font-files/Inter-Regular.woff2",
                weight_range="400",
            ),
            FontFace(
                family="Monaspace Argon",
                url="https://raw.githubusercontent.com/githubnext/monaspace/refs/heads/main/fonts/webfonts/MonaspaceArgon-Regular.woff2",
                weight_range="400",
            ),
        ]

        app_session._populate_theme_msg(
            new_session_msg.custom_theme.sidebar,
            "theme.sidebar",
        )
        assert new_session_msg.custom_theme.HasField("sidebar")
        assert new_session_msg.custom_theme.sidebar.primary_color == "red"
        assert new_session_msg.custom_theme.sidebar.background_color == "white"
        assert new_session_msg.custom_theme.sidebar.text_color == "black"
        assert new_session_msg.custom_theme.sidebar.secondary_background_color == "blue"
        assert new_session_msg.custom_theme.sidebar.base_radius == "1.2rem"
        assert new_session_msg.custom_theme.sidebar.button_radius == "medium"
        assert new_session_msg.custom_theme.sidebar.border_color == "#ff0000"
        assert new_session_msg.custom_theme.sidebar.dataframe_border_color == "#280f63"
        assert new_session_msg.custom_theme.sidebar.show_widget_border is True
        assert new_session_msg.custom_theme.sidebar.link_color == "#2EC163"
        assert new_session_msg.custom_theme.sidebar.link_underline is False
        assert new_session_msg.custom_theme.sidebar.code_font_size == "12px"
        assert new_session_msg.custom_theme.sidebar.code_font_weight == 500
        assert new_session_msg.custom_theme.sidebar.heading_font == "Inter Bold"
        assert new_session_msg.custom_theme.sidebar.heading_font_sizes == [
            "2.125rem",
            "2rem",
            "1.875rem",
        ]
        assert new_session_msg.custom_theme.sidebar.heading_font_weights == [
            700,
            700,
            600,
            600,  # default value
            600,  # default value
            600,  # default value
        ]
        assert new_session_msg.custom_theme.sidebar.body_font == "Inter"
        assert new_session_msg.custom_theme.sidebar.code_font == "Monaspace Argon"
        assert new_session_msg.custom_theme.sidebar.code_background_color == "blue"
        assert (
            new_session_msg.custom_theme.sidebar.dataframe_header_background_color
            == "purple"
        )

        # Default values for unsupported fields in sidebar
        assert new_session_msg.custom_theme.sidebar.base == 0
        assert not new_session_msg.custom_theme.sidebar.font_faces
        assert not new_session_msg.custom_theme.sidebar.HasField("base_font_size")
        assert not new_session_msg.custom_theme.sidebar.HasField("base_font_weight")
        assert not new_session_msg.custom_theme.sidebar.HasField("show_sidebar_border")

    @patch("streamlit.runtime.app_session._LOGGER")
    @patch("streamlit.runtime.app_session.config")
    def test_logs_warning_if_base_invalid(self, patched_config, patched_logger):
        patched_config.get_options_for_section.side_effect = (
            _mock_get_options_for_section({"base": "blah"})
        )

        msg = ForwardMsg()
        new_session_msg = msg.new_session
        app_session._populate_theme_msg(new_session_msg.custom_theme)

        patched_logger.warning.assert_called_once()


@patch.object(
    PagesManager,
    "get_pages",
    MagicMock(
        return_value={
            "hash1": {"page_name": "page1", "script_path": "page1.py"},
            "hash2": {"page_name": "page2", "script_path": "page2.py"},
        }
    ),
)
class ShouldRerunOnFileChangeTest(unittest.TestCase):
    def test_returns_true_if_current_page_changed(self):
        session = _create_test_session()
        session._client_state.page_script_hash = "hash2"

        assert session._should_rerun_on_file_change("page2.py")

    def test_returns_true_if_changed_file_is_not_page(self):
        session = _create_test_session()
        session._client_state.page_script_hash = "hash1"

        assert session._should_rerun_on_file_change("some_other_file.py")

    def test_returns_false_if_different_page_changed(self):
        session = _create_test_session()
        session._client_state.page_script_hash = "hash2"

        assert not session._should_rerun_on_file_change("page1.py")
