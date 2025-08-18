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

from playwright.sync_api import Page, expect

from e2e_playwright.conftest import ImageCompareFunction
from e2e_playwright.shared.app_utils import check_top_level_class, get_expander


def test_tabs_render_correctly(themed_app: Page, assert_snapshot: ImageCompareFunction):
    st_tabs = themed_app.get_by_test_id("stTabs")
    expect(st_tabs).to_have_count(7)

    assert_snapshot(st_tabs.nth(0), name="st_tabs-sidebar")
    assert_snapshot(st_tabs.nth(1), name="st_tabs-text_input")
    assert_snapshot(st_tabs.nth(2), name="st_tabs-many")
    assert_snapshot(st_tabs.nth(3), name="st_tabs-markdown_labels")
    assert_snapshot(st_tabs.nth(5), name="st_tabs-fixed_width")


def test_displays_correctly_in_sidebar(app: Page):
    expect(app.get_by_test_id("stSidebar").get_by_test_id("stTab")).to_have_count(2)
    expect(app.get_by_text("I am in the sidebar")).to_have_count(1)
    expect(app.get_by_text("I am in the sidebarI'm also in the sidebar")).to_have_count(
        1
    )


def test_contains_all_tabs_when_overflowing(app: Page):
    expect(get_expander(app, "Expander").get_by_test_id("stTab")).to_have_count(25)


def test_check_top_level_class(app: Page):
    """Check that the top level class is correctly set."""
    check_top_level_class(app, "stTabs")


def test_tabs_with_html(app: Page):
    tabs = app.get_by_test_id("stTabs").nth(4)

    expect(app.get_by_text("This is HTML tab 1")).to_be_visible()
    tabs.get_by_role("tab", name="HTML Tab 2").click()
    expect(app.get_by_text("This is HTML tab 2")).to_be_visible()
    tabs.get_by_role("tab", name="HTML Tab 3").click()
    expect(app.get_by_text("This is HTML tab 3")).to_be_visible()
    tabs.get_by_role("tab", name="HTML Tab 1").click()
    expect(app.get_by_text("This is HTML tab 1")).to_be_visible()


def test_tabs_with_code_layouts(app: Page, assert_snapshot: ImageCompareFunction):
    """Test that tabs with code blocks and different height configurations render correctly."""
    tabs_with_code = app.get_by_test_id("stTabs").nth(6)

    # Test Tab 1 with container and stretched code
    tabs_with_code.scroll_into_view_if_needed()
    assert_snapshot(tabs_with_code, name="st_tabs-code_stretch_height_in_container")

    # Switch to Tab 2 and test fixed height and stretched code
    tabs_with_code.get_by_role("tab", name="Tab 2").click()
    assert_snapshot(tabs_with_code, name="st_tabs-fixed_height_stretch_height")
