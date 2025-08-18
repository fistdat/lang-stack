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

import altair as alt
import numpy as np
import pandas as pd

import streamlit as st

np.random.seed(0)

# mark_arc was added in 4.2, but we have to support altair 4.0-4.1, so we
# have to skip this part of the test when testing min versions.
major, minor, patch = alt.__version__.split(".")
if not (major == "4" and minor < "2"):
    source = pd.DataFrame(
        {"category": [1, 2, 3, 4, 5, 6], "value": [4, 6, 10, 3, 7, 8]}
    )

    chart = (
        alt.Chart(source)
        .mark_arc(innerRadius=50)
        .encode(
            theta=alt.Theta(field="value", type="quantitative"),
            color=alt.Color(field="category", type="nominal"),
        )
    )

    st.write("Pie Chart with more than 4 Legend items")
    st.altair_chart(chart, theme="streamlit", use_container_width=False)


df1 = pd.DataFrame(np.random.randn(200, 3), columns=["a", "b", "c"])
chart = alt.Chart(df1).mark_circle().encode(x="a", y="b", size="c", color="c")

st.write("Show default vega lite theme:")
st.altair_chart(chart, theme=None)

st.write("Show streamlit theme:")
st.altair_chart(chart, theme="streamlit")

st.write("Overwrite theme config:")
chart = (
    alt.Chart(df1, usermeta={"embedOptions": {"theme": None}})
    .mark_circle()
    .encode(x="a", y="b", size="c", color="c")
)
st.altair_chart(chart, theme="streamlit")

df2 = pd.DataFrame(
    {
        "a": ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
        "b": [28, 55, 43, 91, 81, 53, 19, 87, 52],
    }
)

chart = alt.Chart(df2).mark_bar().encode(x="a", y="b")

st.write("Bar chart with overwritten theme props:")
st.altair_chart(chart.configure_mark(color="black"), theme="streamlit")

# taken from vega_datasets barley example
barley = alt.UrlData(
    "https://cdn.jsdelivr.net/npm/vega-datasets@v2.7.0/data/barley.json"
)

barley_chart = (
    alt.Chart(barley)
    .mark_bar()
    .encode(x="year:O", y="sum(yield):Q", color="year:N", column="site:N")
)

st.write("Grouped Bar Chart with default theme:")
st.altair_chart(barley_chart, theme=None)

st.write("Grouped Bar Chart with streamlit theme:")
st.altair_chart(barley_chart, theme="streamlit")

st.write(
    "Grouped Bar Chart with use_container_width=True (note that this doesn't work well)"
)
st.altair_chart(barley_chart, theme=None, use_container_width=True)

st.write("Layered chart")
# Taken from vega_datasets
stocks = alt.UrlData(
    "https://cdn.jsdelivr.net/npm/vega-datasets@v1.29.0/data/stocks.csv"
)

base = (
    alt.Chart(stocks)
    .encode(x="date:T", y="price:Q", color="symbol:N")
    .transform_filter(alt.datum.symbol == "GOOG")
)

new_base_chart = base.mark_line() + base.mark_point()
st.altair_chart(new_base_chart)

x = np.linspace(10, 100, 10)
y1 = 5 * x
y2 = 1 / x

df3 = pd.DataFrame.from_dict({"x": x, "y1": y1, "y2": y2})

c1 = alt.Chart(df3).mark_line().encode(alt.X("x"), alt.Y("y1"))

c2 = alt.Chart(df3).mark_line().encode(alt.X("x"), alt.Y("y2"))

st.altair_chart(c1 & c2, use_container_width=True)

# Issue #9339: legend.title=None shouldn't cut chart off
df_cut_off_issue = pd.DataFrame(
    {
        "x": [1, 2, 3, 4],
        "y": [10, 20, 30, 40],
        "category": ["A", "B", "C", "D"],
    }
)

cut_off_chart = (
    alt.Chart(df_cut_off_issue)
    .mark_line(point=True)
    .encode(
        x=alt.X("x", title="Date"),
        y=alt.Y("y:Q", title="Value"),
        color=alt.Color("category:N").legend(orient="bottom", title=None),
    )
)

st.write("Altair chart cut off if legend title is None (Issue #9339)")
st.altair_chart(cut_off_chart, use_container_width=True)
