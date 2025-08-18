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

from typing import TYPE_CHECKING

from playwright.sync_api import Page, expect

from e2e_playwright.shared.react18_utils import (
    take_stable_snapshot,
)

if TYPE_CHECKING:
    from e2e_playwright.conftest import ImageCompareFunction


def assert_fullscreen_toolbar_button_interactions(
    app: Page,
    assert_snapshot: ImageCompareFunction,
    widget_test_id: str,
    filename_prefix: str = "",
    nth: int = 0,
    pixel_threshold: float = 0.05,
    fullscreen_wrapper_nth: int | None = None,
) -> None:
    """
    Shared test function to assert that clicking on fullscreen toolbar button
    expands the map into fullscreen.
    """

    widget_element = app.get_by_test_id(widget_test_id).nth(nth)
    widget_toolbar = widget_element.get_by_test_id("stElementToolbar")
    if fullscreen_wrapper_nth is not None:
        fullscreen_wrapper = app.get_by_test_id("stFullScreenFrame").nth(
            fullscreen_wrapper_nth
        )
    else:
        fullscreen_wrapper = app.get_by_test_id("stFullScreenFrame").nth(nth)

    fullscreen_toolbar_button = widget_toolbar.get_by_test_id(
        "stElementToolbarButton"
    ).last

    # Activate toolbar:
    widget_element.hover()
    # Check that it is visible
    expect(widget_toolbar).to_have_css("opacity", "1")

    # Click on expand to fullscreen button:
    fullscreen_toolbar_button.click()

    # Make sure that the button shows the close fullscreen button
    expect(
        widget_toolbar.get_by_role("button", name="Close fullscreen")
    ).to_be_visible()

    # Check that it is visible
    take_stable_snapshot(
        app,
        app,
        assert_snapshot=assert_snapshot,
        name=f"{filename_prefix if filename_prefix != '' else widget_test_id}-fullscreen_expanded",
        pixel_threshold=pixel_threshold,
    )

    # Click again on fullscreen button to close fullscreen mode:
    fullscreen_toolbar_button.click()

    # Make sure that the button shows the open fullscreen button
    expect(widget_toolbar.get_by_role("button", name="Fullscreen")).to_be_visible()

    take_stable_snapshot(
        app,
        fullscreen_wrapper,
        assert_snapshot=assert_snapshot,
        name=f"{filename_prefix if filename_prefix != '' else widget_test_id}-fullscreen_collapsed",
        pixel_threshold=pixel_threshold,
    )
