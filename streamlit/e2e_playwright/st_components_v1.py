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

import streamlit as st
import streamlit.components.v1 as components

html = r"<h1>Hello, Streamlit!</h1>"
components.html(html, width=200, height=500, scrolling=False)

src = "http://not.a.real.url"
components.iframe(src, width=200, height=500, scrolling=True)

# Different tab_index examples for testing
st.markdown("### IFrames with different tab_index values")

# Default - no tab_index specified
components.iframe(src, width=200, height=100, scrolling=True)

# Positive tab_index
components.iframe(src, width=200, height=100, scrolling=True, tab_index=5)

# Negative tab_index
components.iframe(src, width=200, height=100, scrolling=True, tab_index=-1)

# Zero tab_index
components.iframe(src, width=200, height=100, scrolling=True, tab_index=0)

data_url = """data:text/html,
<h1>Iframe Test</h1>
<p>This content is stable for snapshot testing.</p>
<div style='background-color: lightblue; padding: 10px;'>
    Fixed content for reliable snapshots
</div>
""".replace("\n", "")
long_html = """<h1>HTML Test</h1>
<p>This content is stable for snapshot testing.</p>
<div style='background-color: lightblue; padding: 10px;'>
    Fixed content for reliable snapshots
</div>
""".replace("\n", "")
# Dimensions tests
components.iframe(data_url)
components.iframe(data_url, width=200, height=100)
components.html(long_html)

with st.container(key="html-iframe-in-vertical-container"):
    components.html(long_html)
    components.iframe(data_url)

if st.toggle("Show custom component"):
    # Set a query parameter to ensure that it doesn't affect the path of the custom component,
    # since that would trigger a reload if the query param changes
    st.query_params["hello"] = "world"

    url = "http://not.a.real.url"
    test_component = components.declare_component("test_component", url=url)

    test_component(key="component_1")
