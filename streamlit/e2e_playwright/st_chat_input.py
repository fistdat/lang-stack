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
from streamlit import config, runtime

# Set file max upload size to 1MB
config.set_option("server.maxUploadSize", 1)

v1 = st.container().chat_input("Chat input 1 (inline)")
st.write("Chat input 1 (inline) - value:", v1)

col1, _ = st.columns(2)

v2 = col1.chat_input(
    "Chat input 2 (in column, disabled)", accept_file=True, disabled=True
)
st.write("Chat input 2 (in column, disabled) - value:", v2)

if st.button("Set Value"):
    st.session_state["chat_input_3"] = "Hello, world!"

if runtime.exists():
    st.write(
        "Chat input 3 - session state value before execution:",
        st.session_state.get("chat_input_3"),
    )

    def on_submit():
        st.markdown("chat input submitted")

    v3 = st.container().chat_input(
        "Chat input 3 (callback)", key="chat_input_3", on_submit=on_submit
    )
    st.write(
        "Chat input 3 (callback) - session state value:",
        st.session_state["chat_input_3"],
    )
    st.write("Chat input 3 (callback) - return value:", v3)


v4 = st.container().chat_input(
    "Chat input 4 (single file)", accept_file=True, file_type="txt"
)
st.write("Chat input 4 (single file) - value:", v4)

v5 = st.container().chat_input("Chat input 5 (multiple files)", accept_file="multiple")
st.write("Chat input 5 (multiple files) - value:", v5)

v6 = st.container().chat_input("Chat input 7 (width=300px)", width=300)
v7 = st.container().chat_input("Chat input 8 (width='stretch')", width="stretch")


v8 = st.chat_input(
    "Chat input 8 (bottom, max_chars, long placeholder) "
    "This is a very long placeholder text that should span multiple lines "
    "and cause the chat input to grow vertically to accommodate all the "
    "text properly when displayed in the UI",
    max_chars=200,
)
st.write("Chat input 8 (bottom, max_chars) - value:", v8)

# Directory upload tests
v9 = st.container().chat_input(
    "Chat input 9 (directory upload)", accept_file="directory"
)
st.write("Chat input 9 (directory upload) - value:", v9)

v10 = st.container().chat_input(
    "Chat input 10 (directory upload disabled)", accept_file="directory", disabled=True
)
st.write("Chat input 10 (directory upload disabled) - value:", v10)
