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

st.set_page_config(layout="wide")
st.chat_input("input here")
st.toast("This is a default toast message", icon="🐶")
st.toast(
    "Random toast message that is a really really really really really really "
    "really long message, going way past the 3 line limit",
    icon="🦄",
)

st.toast("Your edited image was saved!", icon=":material/cabin:")

if st.button("Show duration toasts"):
    st.toast("I am a toast with a short duration", duration=2)
    st.toast("I am a toast with a long duration", duration="long")
    st.toast("I am a persistent toast", duration="infinite")


@st.dialog("Streamlit Toast Notification")
def toast_notification():
    activate_toast = st.button(label="Toast from dialog")
    if activate_toast:
        st.toast("Toast above dialog", icon="🎉")


st.button("Trigger dialog", on_click=toast_notification)
