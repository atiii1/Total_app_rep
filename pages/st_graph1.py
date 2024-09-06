import streamlit as st # type: ignore
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral5
from bokeh.transform import factor_cmap

import plotly.express as px

st.write("my cool charts:")

chart_data = pd.DataFrame(
                np.random.random((20 , 3)),
                columns=['a', 'b' , 'c']
)

st.bar_chart(chart_data)
st.line_chart(chart_data)
st.area_chart(chart_data)

# Sample data
data = dict(
    dates=['2022-01-01', '2022-01-02', '2022-01-03', '2022-01-04', '2022-01-05'],
    values=[10, 20, 15, 25, 30]
)

# Create Plotly figure
fig = px.line(data, x='dates', y='values', title='Time Series Plot')

# Display Plotly figure in Streamlit
st.plotly_chart(fig, use_container_width=True)


# Sample data
fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes']
counts = [5, 3, 4, 2, 4]

# Create Bokeh plot
source = ColumnDataSource(data=dict(fruits=fruits, counts=counts))
p = figure(x_range=fruits, height=350, title="Fruit Counts",
           toolbar_location=None, tools="")

p.vbar(x='fruits', top='counts', width=0.9, source=source,
       line_color='white', fill_color=factor_cmap('fruits', palette=Spectral5, factors=fruits))

p.y_range.start = 0
p.xgrid.grid_line_color = None
p.axis.minor_tick_line_color = None
p.outline_line_color = None

# Display Bokeh plot in Streamlit
st.bokeh_chart(p, use_container_width=True)