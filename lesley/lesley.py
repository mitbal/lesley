# Lesley is a package to plot calendar based heatmap. Inspired by July
import calendar

import numpy as np
import pandas as pd
import altair as alt

# create mapping from category used in the plot, to the label displayed
def make_month_mapping():
    d = {}

    for i in range(12):
        d[f'Week {int(i*4.5+1):02d}'] = f'{calendar.month_name[i+1]}'

    return d

# create function to generate altair label expression for mapping
def gen_expr(d):
    expr = ""
    for k, v in d.items():
        expr += f"datum.label == '{k}' ? '{v}': "
    expr += " ''"

    return expr


def cal_heatmap(dates, values):

    df = pd.DataFrame({'dates': dates, 'values': values})
    df['days'] = df['dates'].apply(lambda x: x.to_pydatetime().strftime('%A'))
    df['weeks'] = df['dates'].apply(lambda x: 'Week '+x.to_pydatetime().strftime('%W'))

    days = list(calendar.day_name)
    # weeks = calendar

    mapping = make_month_mapping()
    expr = gen_expr(mapping)

    chart = alt.Chart(df).mark_rect(cornerRadius=5, width=20, height=20).encode(
        alt.Y('days', sort=days).axis(tickSize=0, domain=False, values=['Monday', 'Thursday', 'Sunday'], labelFontSize=15),
        alt.X('weeks:N').axis(tickSize=1, domain=False, title='Months', labelExpr=expr, labelAngle=0, labelFontSize=15),
        alt.Color('values'),
        tooltip=[
            alt.Tooltip('dates', title='Date'),
            alt.Tooltip('values', title='Value')
        ]
    ).properties(
        height=180,
        width=1200
    ).configure_scale(
        rectBandPaddingInner=0.1,
    ).configure_mark(
        strokeOpacity=0,
        strokeWidth=0,
        filled=True
    ).configure_axis(
        grid=False
    ).configure_view(
        stroke=None
    )

    return chart

