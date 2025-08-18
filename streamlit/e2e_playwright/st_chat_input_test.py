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

from playwright.sync_api import FilePayload, Locator, Page, expect

from e2e_playwright.conftest import (
    ImageCompareFunction,
    rerun_app,
    wait_for_app_run,
)
from e2e_playwright.shared.app_utils import (
    check_top_level_class,
    click_button,
    expect_markdown,
    get_element_by_key,
    goto_app,
)


def file_upload_helper(app: Page, chat_input: Locator, files: list[FilePayload]):
    upload_button = chat_input.get_by_test_id("stChatInputFileUploadButton")

    expect(upload_button).to_be_visible()
    upload_button.scroll_into_view_if_needed()

    with app.expect_file_chooser() as fc_info:
        upload_button.click()
        file_chooser = fc_info.value
        file_chooser.set_files(files=files)

    # take away hover focus of button
    app.keyboard.press("Escape")
    app.get_by_test_id("stApp").click(position={"x": 0, "y": 0}, force=True)

    wait_for_app_run(app, 500)


def directory_upload_helper(app: Page, chat_input: Locator):
    """Helper function for directory upload tests."""
    upload_button = chat_input.get_by_test_id("stChatInputFileUploadButton")

    expect(upload_button).to_be_visible()
    upload_button.scroll_into_view_if_needed()

    # For directory upload, we simulate the interaction without actual files
    # since we don't want to snapshot test with real directory uploads
    with app.expect_file_chooser() as fc_info:
        upload_button.click()
        file_chooser = fc_info.value
        # Set directory flag (this would be a directory selection in real usage)
        file_chooser.set_files(files=[])  # Empty for simulation

    # Take away hover focus of button
    app.keyboard.press("Escape")
    app.get_by_test_id("stApp").click(position={"x": 0, "y": 0}, force=True)

    wait_for_app_run(app, 500)


def test_chat_input_rendering(app: Page, assert_snapshot: ImageCompareFunction):
    """Test that the st.chat_input widgets are correctly rendered via screenshot matching."""
    # set taller height to ensure inputs do not overlap
    app.set_viewport_size({"width": 750, "height": 2000})

    chat_input_widgets = app.get_by_test_id("stChatInput")
    expect(chat_input_widgets).to_have_count(10)

    assert_snapshot(chat_input_widgets.nth(0), name="st_chat_input-inline")
    assert_snapshot(chat_input_widgets.nth(1), name="st_chat_input-in_column_disabled")
    assert_snapshot(chat_input_widgets.nth(2), name="st_chat_input-callback")
    assert_snapshot(chat_input_widgets.nth(3), name="st_chat_input-single-file")
    assert_snapshot(chat_input_widgets.nth(4), name="st_chat_input-multiple-files")
    assert_snapshot(chat_input_widgets.nth(5), name="st_chat_input-width_300px")
    assert_snapshot(chat_input_widgets.nth(6), name="st_chat_input-width_stretch")
    # The bottom chat input appears last in DOM order because st.chat_input() renders at bottom
    assert_snapshot(chat_input_widgets.nth(9), name="st_chat_input-bottom")
    assert_snapshot(chat_input_widgets.nth(7), name="st_chat_input-directory")
    assert_snapshot(chat_input_widgets.nth(8), name="st_chat_input-directory_disabled")


def test_max_characters_enforced(app: Page, assert_snapshot: ImageCompareFunction):
    """Test that the max_chars parameter is enforced."""
    app.set_viewport_size({"width": 750, "height": 2000})

    long_text = (
        "Lorem ipsum dolor amet, consectetur adipiscing elit. Mauris tristique est at "
        "tincidunt pul vinar. Nam pulvinar neque sapien, eu pellentesque metus pellentesque "
        "at. Ut et dui molestie, iaculis magna sed. This text should not appear in the input."
    )
    chat_input = app.get_by_test_id("stChatInput").nth(9)
    chat_input_area = chat_input.locator("textarea")

    chat_input_area.type(long_text)

    expected_text = (
        "Lorem ipsum dolor amet, consectetur adipiscing elit. Mauris tristique est at "
        "tincidunt pul vinar. Nam pulvinar neque sapien, eu pellentesque metus pellentesque "
        "at. Ut et dui molestie, iaculis magna se"
    )
    expect(chat_input_area).to_have_value(expected_text)
    assert_snapshot(chat_input, name="st_chat_input-max_chars")


def test_embedded_app_with_bottom_chat_input(
    app: Page, app_port: int, assert_snapshot: ImageCompareFunction
):
    """Test that an embedded app with bottom chat input renders correctly."""
    app.set_viewport_size({"width": 750, "height": 2000})

    goto_app(app, f"http://localhost:{app_port}/?embed=true")

    app_view_block = app.get_by_test_id("stMainBlockContainer")
    # Bottom padding should be 16px (1rem):
    expect(app_view_block).to_have_css("padding-bottom", "16px")
    bottom_block = app.get_by_test_id("stBottomBlockContainer")
    # Bottom padding should be 32px (2rem):
    expect(bottom_block).to_have_css("padding-bottom", "32px")
    # Top padding should be 16px (1rem):
    expect(bottom_block).to_have_css("padding-top", "16px")

    # There shouldn't be an iframe resizer anchor:
    expect(app.get_by_test_id("stAppIframeResizerAnchor")).to_be_hidden()
    # The scroll container should be switched to scroll to bottom:
    expect(app.get_by_test_id("stAppScrollToBottomContainer")).to_be_attached()

    assert_snapshot(
        app.get_by_test_id("stAppViewContainer"),
        name="st_chat_input-app_embedded_with_bottom",
    )


def test_app_with_bottom_chat_input(app: Page, assert_snapshot: ImageCompareFunction):
    """Test that an app with bottom chat input renders correctly."""
    app.set_viewport_size({"width": 750, "height": 2000})

    app_view_block = app.get_by_test_id("stMainBlockContainer")
    # Bottom padding should be 16px (1rem):
    expect(app_view_block).to_have_css("padding-bottom", "16px")

    bottom_block = app.get_by_test_id("stBottomBlockContainer")
    # Bottom padding should be 56px (3.5rem):
    expect(bottom_block).to_have_css("padding-bottom", "56px")
    # Top padding should be 16px (1rem):
    expect(bottom_block).to_have_css("padding-top", "16px")

    # There shouldn't be an iframe resizer anchor:
    expect(app.get_by_test_id("stAppIframeResizerAnchor")).to_be_hidden()
    # The scroll container should be switched to scroll to bottom:
    expect(app.get_by_test_id("stAppScrollToBottomContainer")).to_be_attached()

    assert_snapshot(app.get_by_test_id("stBottom"), name="st_chat_input-app_bottom")


def test_submit_hover_state_with_input_value(
    app: Page, assert_snapshot: ImageCompareFunction
):
    """Test the submit button's hover state when input value is present."""
    app.set_viewport_size({"width": 750, "height": 2000})

    chat_input = app.get_by_test_id("stChatInput").nth(9)
    chat_input_area = chat_input.locator("textarea")
    chat_input_area.type("Corgi")

    submit_button = chat_input.get_by_test_id("stChatInputSubmitButton")
    submit_button.hover()
    assert_snapshot(chat_input, name="st_chat_input-submit_hover")


def test_enter_submits_clears_input(app: Page):
    """Test that pressing Enter submits and clears the input."""
    expect_markdown(app, "Chat input 8 (bottom, max_chars) - value: None")

    chat_input_area = app.get_by_test_id("stChatInputTextArea").nth(9)
    chat_input_area.type("Corgi")
    chat_input_area.press("Enter")
    wait_for_app_run(app)

    expect(chat_input_area).to_have_value("")

    expect_markdown(app, "Chat input 8 (bottom, max_chars) - value: Corgi")


def test_shift_enter_creates_new_line(app: Page, assert_snapshot: ImageCompareFunction):
    """Test that Shift+Enter creates a new line."""
    app.set_viewport_size({"width": 750, "height": 2000})

    chat_input = app.get_by_test_id("stChatInput").nth(9)
    chat_input_area = chat_input.locator("textarea")
    chat_input_area.fill("")  # Clear the input first
    chat_input_area.press("Shift+Enter")
    chat_input_area.type("New Line")
    assert_snapshot(chat_input, name="st_chat_input-shift_enter_new_line")

    chat_input = app.get_by_test_id("stChatInput").nth(3)
    chat_input_area = chat_input.locator("textarea")
    chat_input_area.fill("")  # Clear the input first
    chat_input_area.press("Shift+Enter")
    chat_input_area.type("New Line")
    assert_snapshot(chat_input, name="st_chat_input-file_upload_shift_enter_new_line")


def test_click_button_to_submit_clears_input(app: Page):
    """Test that clicking the button submits and clears the input."""
    chat_input = app.get_by_test_id("stChatInput").nth(0)
    submit_button = chat_input.get_by_test_id("stChatInputSubmitButton")
    chat_input_area = chat_input.locator("textarea")

    chat_input_area.type("Corgi")
    submit_button.click()

    expect(chat_input_area).to_have_value("")

    expect_markdown(app, "Chat input 1 (inline) - value: Corgi")


def test_chat_input_focus_state(app: Page, assert_snapshot: ImageCompareFunction):
    """Test that st.chat_input renders the focus state correctly."""
    app.set_viewport_size({"width": 750, "height": 2000})

    chat_input = app.get_by_test_id("stChatInput").nth(9)
    chat_input_area = chat_input.locator("textarea")
    chat_input_area.click()
    expect(chat_input_area).to_be_focused()
    assert_snapshot(chat_input, name="st_chat_input-focused")


def test_grows_shrinks_input_text(app: Page, assert_snapshot: ImageCompareFunction):
    """Test that input grows with long text and shrinks when text is deleted."""
    app.set_viewport_size({"width": 750, "height": 2000})

    chat_input = app.get_by_test_id("stChatInput").nth(9)
    chat_input_area = chat_input.locator("textarea")
    chat_input_area.type(
        "Lorem ipsum dolor amet, consectetur adipiscing elit. "
        "Mauris tristique est at tincidunt pul vinar. Nam pulvinar neque sapien, "
        "eu pellentesque metus pellentesque at. Ut et dui molestie, iaculis magna."
    )
    assert_snapshot(chat_input, name="st_chat_input-grows")
    for _ in range(20):
        chat_input_area.press("Backspace", delay=10)
    assert_snapshot(chat_input, name="st_chat_input-shrinks")


def test_calls_callback_on_submit(app: Page):
    """Test that it correctly calls the callback on submit."""
    chat_input_area = app.get_by_test_id("stChatInputTextArea").nth(2)

    chat_input_area.type("hello world")
    chat_input_area.press("Enter")
    wait_for_app_run(app)

    expect_markdown(app, "chat input submitted")
    expect_markdown(app, "Chat input 3 (callback) - session state value: hello world")
    expect_markdown(app, "Chat input 3 (callback) - return value: hello world")

    rerun_app(app)

    # Expect the callback to not be triggered:
    expect(app.get_by_text("chat input submitted")).not_to_be_attached()
    # And the session state value to be reset
    expect_markdown(app, "Chat input 3 (callback) - session state value: None")
    # Also expect the return value to be None
    expect_markdown(app, "Chat input 3 (callback) - return value: None")


def test_uploads_and_deletes_single_file(
    app: Page, assert_snapshot: ImageCompareFunction
):
    """Test that it correctly uploads and deletes a single file."""
    app.set_viewport_size({"width": 750, "height": 2000})
    chat_input = app.get_by_test_id("stChatInput").nth(3)

    file_name1 = "file1.txt"
    file1 = FilePayload(name=file_name1, mimeType="text/plain", buffer=b"file1content")

    file_name2 = "file2.txt"
    file2 = FilePayload(name=file_name2, mimeType="text/plain", buffer=b"file2content")

    file_upload_helper(app, chat_input, [file1])

    uploaded_files = app.get_by_test_id("stChatUploadedFiles").nth(1)
    expect(uploaded_files.get_by_text(file_name1)).to_be_visible()
    assert_snapshot(uploaded_files, name="st_chat_input-single_file_uploaded")

    # Upload a second file. This one will replace the first.
    file_upload_helper(app, chat_input, [file2])

    expect(uploaded_files.get_by_text(file_name1)).not_to_be_visible()
    expect(uploaded_files.get_by_text(file_name2)).to_be_visible()

    # Delete the uploaded file
    uploaded_files.get_by_test_id("stChatInputDeleteBtn").nth(0).click()

    wait_for_app_run(app)

    expect(uploaded_files).not_to_have_text(file_name2, use_inner_text=True)


def test_uploads_and_deletes_multiple_files(
    app: Page, assert_snapshot: ImageCompareFunction
):
    """Test that uploading multiple files at once works correctly."""
    app.set_viewport_size({"width": 750, "height": 2000})
    chat_input = app.get_by_test_id("stChatInput").nth(4)

    file_name1 = "file1.txt"
    file_content1 = b"file1content"

    file_name2 = "file2.txt"
    file_content2 = b"file2content"

    files = [
        FilePayload(name=file_name1, mimeType="text/plain", buffer=file_content1),
        FilePayload(name=file_name2, mimeType="text/plain", buffer=file_content2),
    ]

    file_upload_helper(app, chat_input, files)

    uploaded_files = app.get_by_test_id("stChatUploadedFiles").nth(2)
    assert_snapshot(uploaded_files, name="st_chat_input-multiple_files_uploaded")

    uploaded_file_names = uploaded_files.get_by_test_id("stChatInputFileName")
    expect(uploaded_file_names).to_have_count(2)

    # Delete one uploaded file
    uploaded_files.get_by_test_id("stChatInputDeleteBtn").nth(0).click()

    wait_for_app_run(app)

    uploaded_file_names = uploaded_files.get_by_test_id("stChatInputFileName")
    expect(uploaded_file_names).to_have_count(1)

    expect(uploaded_file_names).to_have_text(files[1]["name"], use_inner_text=True)


def test_file_upload_error_message_disallowed_files(
    app: Page, assert_snapshot: ImageCompareFunction
):
    """Test that shows error message for disallowed files."""
    app.set_viewport_size({"width": 750, "height": 2000})

    file_name1 = "file1.json"
    file1 = FilePayload(
        name=file_name1,
        mimeType="application/json",
        buffer=b"{}",
    )

    file_upload_helper(app, app.get_by_test_id("stChatInput").nth(3), [file1])

    uploaded_files = app.get_by_test_id("stChatUploadedFiles").nth(1)
    expect(uploaded_files.get_by_text(file_name1)).to_be_visible()
    assert_snapshot(uploaded_files, name="st_chat_input-file_uploaded_error")

    uploaded_files.get_by_test_id("stTooltipHoverTarget").nth(0).hover()
    expect(app.get_by_text("json files are not allowed.")).to_be_visible()


def test_file_upload_error_message_file_too_large(app: Page):
    """Test that shows error message for files exceeding max size limit."""
    app.set_viewport_size({"width": 750, "height": 2000})

    file_name1 = "large.txt"
    file1 = FilePayload(
        name=file_name1,
        mimeType="text/plain",
        buffer=b"x" * (2 * 1024 * 1024),  # 2MB
    )

    expect(app.get_by_text(file_name1)).not_to_be_attached()

    file_upload_helper(app, app.get_by_test_id("stChatInput").nth(3), [file1])

    expect(app.get_by_text(file_name1)).to_be_visible()

    uploaded_files = app.get_by_test_id("stChatUploadedFiles").nth(1)
    uploaded_files.get_by_test_id("stTooltipHoverTarget").nth(0).hover()
    expect(app.get_by_text("File must be 1.0MB or smaller.")).to_be_visible()


def test_single_file_upload_button_tooltip(app: Page):
    """Test that the single file upload button tooltip renders correctly."""
    chat_input_upload_button = (
        app.get_by_test_id("stChatInput")
        .nth(3)
        .get_by_test_id("stChatInputFileUploadButton")
    )
    expect(chat_input_upload_button).to_be_visible()
    chat_input_upload_button.scroll_into_view_if_needed()

    # Hover on the tooltip hover target
    hover_target = chat_input_upload_button.get_by_test_id("stTooltipHoverTarget")
    hover_target.hover()

    # The tooltip has a 500ms delay, so we need to wait for it to appear
    expect(app.get_by_test_id("stTooltipContent")).to_have_text(
        "Upload or drag and drop a file"
    )


def test_multi_file_upload_button_tooltip(app: Page):
    """Test that the multi file upload button tooltip renders correctly."""
    chat_input_upload_button = (
        app.get_by_test_id("stChatInput")
        .nth(4)
        .get_by_test_id("stChatInputFileUploadButton")
    )
    expect(chat_input_upload_button).to_be_visible()
    chat_input_upload_button.scroll_into_view_if_needed()

    # Hover on the tooltip hover target
    hover_target = chat_input_upload_button.get_by_test_id("stTooltipHoverTarget")
    hover_target.hover()

    # The tooltip has a 500ms delay, so we need to wait for it to appear
    expect(app.get_by_test_id("stTooltipContent")).to_have_text(
        "Upload or drag and drop files"
    )


def test_directory_upload_button_tooltip(app: Page):
    """Test that the directory upload button tooltip renders correctly."""
    chat_input_upload_button = (
        app.get_by_test_id("stChatInput")
        .nth(7)
        .get_by_test_id("stChatInputFileUploadButton")
    )
    expect(chat_input_upload_button).to_be_visible()
    chat_input_upload_button.scroll_into_view_if_needed()

    # Hover on the tooltip hover target
    hover_target = chat_input_upload_button.get_by_test_id("stTooltipHoverTarget")
    hover_target.hover()

    # The tooltip has a 500ms delay, so we need to wait for it to appear
    expect(app.get_by_test_id("stTooltipContent")).to_have_text(
        "Upload or drag and drop a directory"
    )


def test_directory_upload_disabled_state(app: Page):
    """Test that disabled directory upload input cannot be interacted with."""
    disabled_chat_input = app.get_by_test_id("stChatInput").nth(8)
    disabled_upload_button = disabled_chat_input.get_by_test_id(
        "stChatInputFileUploadButton"
    )

    # Check that the upload button has disabled attribute (div elements don't use standard disabled behavior)
    expect(disabled_upload_button).to_have_attribute("disabled", "")

    # Check that the text area is also disabled
    disabled_text_area = disabled_chat_input.locator("textarea")
    expect(disabled_text_area).to_be_disabled()


def test_directory_upload_button_interaction(app: Page):
    """Test directory upload button can be clicked when enabled."""
    chat_input = app.get_by_test_id("stChatInput").nth(7)
    upload_button = chat_input.get_by_test_id("stChatInputFileUploadButton")

    expect(upload_button).to_be_visible()
    expect(upload_button).to_be_enabled()

    # Just verify that the button is clickable without interacting with file chooser
    # Directory uploads require actual directory paths which we can't simulate
    expect(upload_button).to_have_attribute("tabindex", "0")


def test_chat_input_adjusts_for_long_placeholder(
    app: Page, assert_snapshot: ImageCompareFunction
):
    """Test that chat input properly adjusts its height for long placeholder text."""
    app.set_viewport_size({"width": 750, "height": 2000})

    chat_input = app.get_by_test_id("stChatInput").nth(9)
    expect(chat_input).to_be_visible()

    # Take a snapshot of the initial state with the long placeholder
    assert_snapshot(chat_input, name="st_chat_input-long_placeholder")

    # Type some text to verify the input maintains proper height
    chat_input_area = chat_input.locator("textarea")
    expect(chat_input_area).to_be_visible()
    chat_input_area.type("Some input text")
    assert_snapshot(chat_input, name="st_chat_input-long_placeholder_with_text")

    # Clear the text and verify it returns to placeholder height
    chat_input_area.fill("")
    assert_snapshot(chat_input, name="st_chat_input-long_placeholder_after_clear")


def test_check_top_level_class(app: Page):
    """Check that the top level class is correctly set."""
    check_top_level_class(app, "stChatInput")


def test_custom_css_class_via_key(app: Page):
    """Test that the element can have a custom css class via the key argument."""
    expect(get_element_by_key(app, "chat_input_3")).to_be_visible()


def test_programmatically_set_value_in_session_state(app: Page):
    """Test that the value is correctly set in session state."""
    chat_input = get_element_by_key(app, "chat_input_3")

    click_button(app, "Set Value")
    expect(chat_input.locator("textarea")).to_have_value("Hello, world!")

    # And the session state value should be reset to None after widget execution:
    expect_markdown(
        app, "Chat input 3 - session state value before execution: Hello, world!"
    )
    expect_markdown(app, "Chat input 3 (callback) - session state value: None")
    # Also expect the return value to be None
    expect_markdown(app, "Chat input 3 (callback) - return value: None")

    # Submit value
    submit_button = chat_input.get_by_test_id("stChatInputSubmitButton")
    expect(submit_button).to_be_visible()
    submit_button.click()

    wait_for_app_run(app)

    expect_markdown(app, "chat input submitted")

    expect_markdown(
        app, "Chat input 3 - session state value before execution: Hello, world!"
    )
    expect_markdown(app, "Chat input 3 (callback) - session state value: Hello, world!")
    expect_markdown(app, "Chat input 3 (callback) - return value: Hello, world!")


def test_height_resets_after_submit(app: Page, assert_snapshot: ImageCompareFunction):
    """Test that chat input height resets to compact state after submission."""
    chat_input = app.get_by_test_id("stChatInput").nth(0)
    chat_input_area = chat_input.locator("textarea")

    assert_snapshot(chat_input, name="st_chat_input-initial_compact_state")

    multiline_text = (
        "This is line one\n"
        "This is line two\n"
        "This is line three\n"
        "This is line four with some longer text to ensure expansion"
    )
    chat_input_area.fill(multiline_text)

    assert_snapshot(chat_input, name="st_chat_input-expanded_multiline_state")

    chat_input_area.press("Enter")
    wait_for_app_run(app)

    expect(chat_input_area).to_have_value("")
    assert_snapshot(chat_input, name="st_chat_input-reset_after_submit")
