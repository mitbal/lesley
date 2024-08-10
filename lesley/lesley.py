# Lesley is a package to plot calendar based heatmap. Inspired by July
import calendar

import numpy as np
import pandas as pd
import altair as alt
import seaborn as sns

# create mapping from category used in the plot, to the label displayed
def make_month_mapping():
    d = {}

    for i in range(12):
        d[f'Week {int(i*4.5+1):02d}'] = f'{calendar.month_abbr[i+1]}'

    return d

# shorten day name to a single letter
def make_day_mapping():
    
    d = {}
    for day in calendar.day_abbr:
        d[day] = day[0]
    return d

# create function to generate altair label expression for mapping
def gen_expr(d):
    expr = ""
    for k, v in d.items():
        expr += f"datum.label == '{k}' ? '{v}': "
    expr += " ''"

    return expr

# derived extra columns and fill missing rows
def prep_data(dates, values):

    start_date = dates.sort_values()[0]
    get_year = start_date.year

    full_year = pd.date_range(start=str(get_year)+'-01-01', end=str(get_year)+'-12-31')
    full_values = [0]*len(full_year)

    full_df = pd.DataFrame({'dates': full_year, 'values': full_values})
    input_df = pd.DataFrame({'dates': dates, 'values': values})

    df = full_df.merge(input_df, how='left', on='dates')[['dates', 'values_y']].rename(columns={'values_y': 'values'})
    df['values'] = df['values'].fillna(0)

    df['days'] = df['dates'].apply(lambda x: x.to_pydatetime().strftime('%a'))
    df['weeks'] = df['dates'].apply(lambda x: 'Week '+x.to_pydatetime().strftime('%W'))

    return df

# create function to generate calendar heatmap
def cal_heatmap(dates, values, cmap='YlGn'):

    df = prep_data(dates, values)
    mapping = make_month_mapping()
    expr = gen_expr(mapping)

    domain = np.sort(np.unique(values))
    range_ = sns.color_palette(cmap, len(domain)).as_hex()

    year = str(df['dates'].iloc[0].year)
    days = list(calendar.day_name)
    chart = alt.Chart(df).mark_rect(cornerRadius=5, width=20, height=20).encode(
        alt.Y('days', sort=days).axis(tickSize=0, title='', domain=False, values=['Mon', 'Thu', 'Sun'], labelFontSize=15),
        alt.X('weeks:N').axis(tickSize=1, domain=False, title='', labelExpr=expr, labelAngle=0, labelFontSize=15),
        alt.Color('values', legend=None).scale(domain=domain, range=range_),
        tooltip=[
            alt.Tooltip('dates', title='Date'),
            alt.Tooltip('values', title='Value')
        ]
    ).properties(
        title=year,
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

# create function to make heatmap for one month only
def month_plot(dates, values, month, title='', border=False, cmap='YlGn'):
    df = pd.DataFrame({'dates': dates, 'values': values})
    df['days'] = df['dates'].apply(lambda x: x.to_pydatetime().strftime('%a'))
    df['weeks'] = df['dates'].apply(lambda x: 'Week '+x.to_pydatetime().strftime('%W'))
    df['months'] = df['dates'].apply(lambda x: x.to_pydatetime().strftime('%B'))

    month_name = calendar.month_name[month]
    df_month = df[df['months'] == month_name].reset_index()

    mapping = make_day_mapping()
    expr = gen_expr(mapping)

    domain = np.sort(np.unique(values))
    range_ = sns.color_palette(cmap, len(domain)).as_hex()

    days = list(calendar.day_abbr)
    chart = alt.Chart(df_month).mark_rect(cornerRadius=5, width=20, height=20).encode(
        alt.X('days', sort=days, title=month_name).axis(tickSize=0, domain=False, labelFontSize=15, orient='top', labelAngle=0, labelExpr=expr),
        alt.Y('weeks:N', title='').axis(tickSize=1, domain=False, labelAngle=0, labelFontSize=0),
        alt.Color('values', legend=None).scale(domain=domain, range=range_),
        tooltip=[
            alt.Tooltip('dates', title='Date'),
            alt.Tooltip('values', title='Value')
        ]
    ).properties(
        height=150,
        width=200,
        title=title
    )

    return chart


# create function to make calendar heatmap for all months
def calendar_plot(dates, values):
    
    charts = [alt.Chart()]*12
    for i in range(12):
        c = month_plot(dates, values, month=i+1)
        charts[i] = c

    # format display
    full = alt.vconcat()
    for i in range(3):
        chart = alt.hconcat()
        for j in range(4):
            chart |= charts[i*4+j]
        full &= chart

    return full
