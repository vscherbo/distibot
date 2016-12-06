import time
import numpy as np
import plotly
# from plotly.graph_objs import Scatter, Layout
from plotly.graph_objs import Box
# from plotly.offline import plot
# import plotly.graph_objs


for i in range(10):
    time.sleep(1)
    plotly.offline.plot([Box(y=np.random.randn(50), showlegend=False) for i in range(45)], show_link=False)

"""
plotly.offline.plot({
        "data": [Scatter(x=[1, 2, 3, 4], y=[4, 3, 2, 1])],
        "layout": Layout(title="hello world")
})
"""
