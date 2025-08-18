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

import textwrap
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns  # type: ignore

import streamlit as st

if TYPE_CHECKING:
    from numpy.typing import NDArray

np.random.seed(0)


st.write("Normal figure:")
data1 = np.random.normal(1, 1, size=100)
fig, ax = plt.subplots()
ax.hist(data1, bins=20)
st.pyplot(fig)

st.write("Resized figure:")
# Resize plot. It is now 4 times smaller than the default value.
fig.set_size_inches(6.4 / 4, 4.8 / 4)
st.pyplot(fig)

st.write("Resized figure with `width='stretch'`:")
st.pyplot(fig, width="stretch")

st.write("Resized figure with `width='content'`:")
st.pyplot(fig, width="content")

st.write("Advanced Seaborn figure:")
# Generate data
data_points = 100
x_data: "NDArray[np.float64]" = (np.random.randn(data_points, 1) * 30) + 30
y_data: "NDArray[np.float64]" = np.random.randn(data_points, 1) * 30
data2: "NDArray[np.float64]" = np.random.randn(data_points, 2)

# Generate plot
fig, ax = plt.subplots(figsize=(4.5, 4.5))
sns.set_context(rc={"font.size": 10})
p = sns.regplot(x=x_data, y=y_data, data=data2, ci=None, ax=ax, color="grey")

p.set_title("An Extremely and Really Really Long Long Long Title", fontweight="bold")
p.set_xlabel("Very long long x label")
p.set_ylabel("Very long long y label")

p.set_ylim(-30, 30)
plot_text = textwrap.dedent(
    """
    some_var_1 = 'Some label 1'
    some_var_2 = 'Some label 2'
"""
)

txt = ax.text(0.90, 0.10, plot_text, transform=ax.transAxes)
sns.despine()

st.pyplot(fig)

st.write("Advanced Seaborn figure using kwargs (low dpi):")

kwargs = {
    "dpi": 50,  # We use a low dpi to show a stark difference to the figure above.
    "bbox_extra_artists": (txt,),
    "bbox_inches": "tight",
    "format": "png",  # Required for some Matplotlib backends.
}

# We need to set clear_figure=True, otherwise the global object
# test below would not work.
st.pyplot(fig, clear_figure=True, **kwargs)  # type: ignore[arg-type]

st.write("Figure using deprecated global object:")
plot = plt.plot(data2)
st.pyplot()
plt.clf()

fig, ax = plt.subplots()
st.pyplot(fig)

st.write("width parameter examples:")

# Create a simple figure for width testing
fig_width_test, ax_width_test = plt.subplots(figsize=(4, 3))
ax_width_test.plot([1, 2, 3, 4], [1, 4, 2, 3])
ax_width_test.set_title("Width Parameter Test")

st.write("width='content' (default):")
st.pyplot(fig_width_test, width="content")

st.write("width='stretch':")
st.pyplot(fig_width_test, width="stretch")

st.write("width=200 (pixels):")
st.pyplot(fig_width_test, width=200)
