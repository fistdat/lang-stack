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

"""Unit tests for cache's show_spinner option."""

import time

import streamlit as st
from streamlit.elements.spinner import DELAY_SECS
from tests.delta_generator_test_case import DeltaGeneratorTestCase

# Wait needs to be longer than the spinner delay timeout:
TEST_DELAY_SECS = DELAY_SECS + 0.2


@st.cache_data(show_spinner=False)
def function_without_spinner():
    return 3


@st.cache_data(show_spinner=True)
def function_with_spinner():
    return 3


class CacheSpinnerTest(DeltaGeneratorTestCase):
    """
    We test the ability to turn on and off the spinner with the show_spinner
    option by inspecting the report queue.
    """

    def test_with_spinner(self):
        """If the show_spinner flag is set, there should be one element in the
        report queue.
        """
        function_with_spinner()
        assert not self.forward_msg_queue.is_empty()

    def test_without_spinner(self):
        """If the show_spinner flag is not set, the report queue should be
        empty.
        """
        function_without_spinner()
        assert self.forward_msg_queue.is_empty()

    def test_cache_data_with_spinner_and_time(self):
        """If show_time is true, the spinner should show the elapsed time."""

        @st.cache_data(show_spinner=True, show_time=True)
        def function_with_spinner_and_time():
            time.sleep(TEST_DELAY_SECS)
            el = self.get_delta_from_queue().new_element
            assert el.spinner.show_time is True
            return 3

        function_with_spinner_and_time()

    def test_cache_data_with_spinner_and_no_time(self):
        """If show_time is false, the spinner should not show the elapsed time."""

        @st.cache_data(show_spinner=True, show_time=False)
        def function_with_spinner_and_no_time():
            time.sleep(TEST_DELAY_SECS)
            el = self.get_delta_from_queue().new_element
            assert el.spinner.show_time is False
            return 3

        function_with_spinner_and_no_time()

    def test_cache_resource_with_spinner_and_time(self):
        """If show_time is true, the spinner should show the elapsed time."""

        @st.cache_resource(show_spinner=True, show_time=True)
        def function_with_spinner_and_time():
            time.sleep(TEST_DELAY_SECS)
            el = self.get_delta_from_queue().new_element
            assert el.spinner.show_time is True
            return 3

        function_with_spinner_and_time()

    def test_cache_resource_with_spinner_and_no_time(self):
        """If show_time is false, the spinner should not show the elapsed time."""

        @st.cache_resource(show_spinner=True, show_time=False)
        def function_with_spinner_and_no_time():
            time.sleep(TEST_DELAY_SECS)
            el = self.get_delta_from_queue().new_element
            assert el.spinner.show_time is False
            return 3

        function_with_spinner_and_no_time()
