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

st.code("# This code is awesome!")

st.code("")

code = """
def hello():
    print("Hello, Streamlit!")
"""
st.code(code, language="python")

st.code(code, language="python", line_numbers=True)

st.code("PLAIN TEXT", language=None, line_numbers=True)

st.markdown("```python\n" + code + "\n```")

st.code(
    """
--- main
+++ develop
@@ -52,21 +52,19 @@
     "title": "Democracy index",
     "yAxis": {
         "max": 10,
-        "min": -10,
-        "facetDomain": "shared"
+        "min": -10
     },
""",
    language="diff",
)

code_with_leading_whitespace = """
    def hello():
        print("Hello, Streamlit!")
"""

st.code(code_with_leading_whitespace, language="python")

st.markdown("```python\n" + code_with_leading_whitespace + "\n```")

st.code("\n" + code_with_leading_whitespace + "\n", language="python")

st.markdown("```python\n\n" + code_with_leading_whitespace + "\n\n```")

with st.expander("`st.code` usage", expanded=True):
    st.code(code, language="python")
    st.code(code, language="python")

with st.expander("`st.markdown` code usage", expanded=True):
    st.markdown("```python\n" + code + "\n```")
    st.markdown("```python\n" + code + "\n```")
    st.markdown("[a link with `code`](https://streamlit.io)")


long_string = "Testing line wrapping: " + "foo bar baz " * 10 + "{EOL}"

wide_code_block = f"""
def foo():
    bar(f"{long_string}")
    return 123
"""

st.code(wide_code_block, wrap_lines=False)
st.code(wide_code_block, wrap_lines=False, line_numbers=True)
st.code(wide_code_block, wrap_lines=True)
st.code(wide_code_block, wrap_lines=True, line_numbers=True)


long_code = """
print("Hello!")
print("This is a tall code block")
print("With many lines")
print("That will scroll")
print("Hello!")
print("This is a tall code block")
print("With many lines")
print("That will scroll")
print("Hello!")
print("This is a tall code block")
print("With many lines")
print("That will scroll")
print("Hello!")
print("This is a tall code block")
print("With many lines")
print("That will scroll")
print("Hello!")
print("This is a tall code block")
print("With many lines")
print("That will scroll")
"""

st.code(long_code, height=200)
st.code(code, height=200)

# width tests
long_code = """
def process_data(data):
    result = []
    for item in data:
        if item % 2 == 0:
            result.append(item * 2)
        else:
            result.append(item * 3)
    return result

# Example usage
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
processed = process_data(data)
print(processed)
"""

st.code(long_code, width=500, wrap_lines=True)
st.code(long_code, width="stretch")
st.code(long_code, width="content")

long_single_word_string = "askldfjlweklrjweifjlsdfliwjlierjilsildfjlslfij" * 3

st.code(long_single_word_string)
st.code(long_single_word_string, wrap_lines=True)

with st.form("form with a code block", height=400):
    st.code(code, height="stretch")
    st.form_submit_button("Submit")

col1, col2, col3 = st.columns(3)

narrow_code = """
def hello():
    print("Hello!")
"""

with col1:
    st.code(narrow_code, height=300)
    st.code(narrow_code, height="stretch")
with col2:
    st.code(narrow_code, height="stretch")
with col3:
    st.code(narrow_code, height="content")

with st.container(height=300, key="container_with_code"):
    st.code(code, height=100)
    st.code(code, height="stretch")
