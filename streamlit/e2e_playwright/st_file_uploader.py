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
from streamlit import runtime

single_file = st.file_uploader("Drop a file:", type=["txt"], key="single")
if single_file is None:
    st.text("No upload")
else:
    st.text(single_file.read())

# Here and throughout this file, we use `if runtime.is_running():`
# since we also run e2e python files in "bare Python mode" as part of our
# Python tests, and this doesn't work in that circumstance
# st.session_state can only be accessed while running with streamlit
if runtime.exists():
    st.write(repr(st.session_state.single) == repr(single_file))

disabled = st.file_uploader(
    "Can't drop a file:", type=["txt"], key="disabled", disabled=True
)
if disabled is None:
    st.text("No upload")
else:
    st.text(disabled.read())

if runtime.exists():
    st.write(repr(st.session_state.disabled) == repr(disabled))

multiple_files = st.file_uploader(
    "Drop multiple files:",
    type=["txt"],
    accept_multiple_files=True,
    key="multiple",
)
if not multiple_files:
    st.text("No upload")
else:
    files = [file.read().decode() for file in multiple_files]
    st.text("\n".join(files))

if runtime.exists():
    st.write(repr(st.session_state.multiple) == repr(multiple_files))

# Add directory upload test scenario
directory_files = st.file_uploader(
    "Drop a directory:",
    type=["txt", "py", "md"],
    accept_multiple_files="directory",
    key="directory",
)
if not directory_files:
    st.text("No directory upload")
else:
    st.text(f"Directory contains {len(directory_files)} files:")
    for file in directory_files:
        st.text(f"- {file.name}: {len(file.read())} bytes")
        file.seek(0)  # Reset file pointer for potential reuse

if runtime.exists():
    st.write(repr(st.session_state.directory) == repr(directory_files))

with st.form("foo"):
    form_file = st.file_uploader("Inside form:", type=["txt"])
    st.form_submit_button("Submit")
    if form_file is None:
        st.text("No upload")
    else:
        st.text(form_file.read())


hidden_label = st.file_uploader(
    "Hidden label:",
    key="hidden_label",
    label_visibility="hidden",
)

if hidden_label is None:
    st.text("No upload")
else:
    st.text(hidden_label.read())

if runtime.exists():
    st.write(repr(st.session_state.hidden_label) == repr(hidden_label))

collapsed_label = st.file_uploader(
    "Collapsed label:",
    key="collapsed_label",
    label_visibility="collapsed",
)

if collapsed_label is None:
    st.text("No upload")
else:
    st.text(collapsed_label.read())

if runtime.exists():
    st.write(repr(st.session_state.collapsed_label) == repr(collapsed_label))

if not st.session_state.get("counter"):
    st.session_state["counter"] = 0


def file_uploader_on_change():
    st.session_state.counter += 1


st.file_uploader(
    "Drop a file:",
    type=["txt"],
    key="on_change_file_uploader_key",
    on_change=file_uploader_on_change,
)

st.text(st.session_state.counter)


@st.fragment
def test_file_fragment():
    file_uploader_in_fragment = st.file_uploader(label="file uploader")
    st.write("File uploader in Fragment:", bool(file_uploader_in_fragment))


test_file_fragment()

st.file_uploader(":material/check: :rainbow[Fancy] _**markdown** `label` _support_")

col1, col2 = st.columns([0.35, 0.65])
with col1:
    st.file_uploader(
        "Uses compact file uploader", type=["txt", "pdf"], accept_multiple_files=True
    )

st.file_uploader("Width Stretch", width="stretch", key="uploader_stretch")
st.file_uploader("Width 300px", width=300, key="uploader_300px")

# Add directory upload with specific file type restrictions
restricted_directory = st.file_uploader(
    "Restricted directory (only .txt files):",
    type=["txt"],
    accept_multiple_files="directory",
    key="restricted_directory",
)
if not restricted_directory:
    st.text("No restricted directory upload")
else:
    st.text(f"Restricted directory contains {len(restricted_directory)} .txt files:")
    for file in restricted_directory:
        st.text(f"- {file.name}")

if runtime.exists():
    st.write(repr(st.session_state.restricted_directory) == repr(restricted_directory))

if "runs" not in st.session_state:
    st.session_state.runs = 0
st.session_state.runs += 1
st.write("Runs:", st.session_state.runs)

# Uploader that can be disabled after uploading for snapshot testing
toggle_disable = st.checkbox(
    "Disable toggle uploader", key="toggle_after_upload_disable"
)
toggle_after_upload = st.file_uploader(
    "Toggle disabled after upload:",
    type=["txt"],
    key="toggle_after_upload",
    disabled=toggle_disable,
)
if toggle_after_upload is None:
    st.text("No upload")
else:
    st.text(toggle_after_upload.read())


_MANY_FILE_TYPES: list[str] = [
    ".3d",
    ".3ds",
    ".3mf",
    ".ac",
    ".ac3d",
    ".acc",
    ".amf",
    ".ase",
    ".ask",
    ".assbin",
    ".b3d",
    ".blend",
    ".bsp",
    ".bvh",
    ".cob",
    ".csm",
    ".dae",
    ".dxf",
    ".enff",
    ".fbx",
    ".glb",
    ".hmp",
    ".ifc",
    ".ifczip",
    ".iqm",
    ".irr",
    ".irrmesh",
    ".lwo",
    ".lws",
    ".lxo",
    ".md2",
    ".md3",
    ".md5anim",
    ".md5camera",
    ".md5mesh",
    ".mdc",
    ".mdl",
    ".mesh",
    ".mesh.xml",
    ".mot",
    ".ms3d",
    ".ndo",
    ".nff",
    ".obj",
    ".off",
    ".ogex",
    ".pk3",
    ".ply",
    ".pmx",
    ".prj",
    ".q3o",
    ".q3s",
    ".raw",
    ".scn",
    ".sib",
    ".smd",
    ".step",
    ".stl",
    ".stp",
    ".ter",
    ".uc",
    ".vrm",
    ".vta",
    ".x",
    ".x3d",
    ".x3db",
    ".xgl",
    ".xml",
    ".zae",
    ".zgl",
]


st.file_uploader(
    "File uploader with many file types:",
    help="Select a file to be uploaded.",
    type=_MANY_FILE_TYPES,
)
