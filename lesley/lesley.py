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
def prep_data(dates, values, labels=None):

    start_date = dates.sort_values()[0]
    get_year = start_date.year

    full_year = pd.date_range(start=str(get_year)+'-01-01', end=str(get_year)+'-12-31')
    full_values = [0]*len(full_year)

    full_df = pd.DataFrame({'dates': full_year, 'values': full_values})
    input_df = pd.DataFrame({'dates': dates, 'values': values})

    df = pd.merge(left=full_df, right=input_df, how='left', on='dates')
    df = df.groupby('dates')['values_y'].mean().to_frame().reset_index()
    df = df.rename(columns={'values_y': 'values'})
    df['values'] = df['values'].fillna(0)
    
    if labels is not None:
        input2 = pd.DataFrame({'dates': dates, 'labels': labels})
        df = pd.merge(left=df, right=input2, how='left', on='dates')
        df['labels'] = df['labels'].fillna('')

    df['days'] = df['dates'].apply(lambda x: x.to_pydatetime().strftime('%a'))
    df['weeks'] = df['dates'].apply(lambda x: 'Week '+x.to_pydatetime().strftime('%W'))
    df['months'] = df['dates'].apply(lambda x: x.to_pydatetime().strftime('%B'))

    return df


def cal_heatmap(dates, values, cmap='YlGn', height=250, width=None):
    """
    Generate a github-style calendar-based heatmap using altair.

    Parameters:
        dates (pd.Series): Series of datetime objects representing the data points.
        values (list or pd.Series): List or series of values to be plotted on the heatmap.
        cmap (str, optional): Color map to use for the heatmap. Defaults to 'YlGn'.
        height (int, optional): Height of the heatmap in pixels. Defaults to 250.
        width (int, optional): Width of the heatmap in pixels. If not provided, will be automatically set based on the height.

    Returns:
        altair.Chart: The generated calendar-based heatmap chart.
    """

    df = prep_data(dates, values)
    mapping = make_month_mapping()
    expr = gen_expr(mapping)

    domain = np.sort(np.unique(values))
    range_ = sns.color_palette(cmap, len(domain)).as_hex()

    cell_width = height / 12.5
    if width is None:
        width = height * 5

    year = str(df['dates'].iloc[0].year)
    days = list(calendar.day_abbr)
    chart = alt.Chart(df).mark_rect(cornerRadius=5, width=cell_width, height=cell_width).encode(
        y=alt.Y('days', sort=days, axis=alt.Axis(tickSize=0, title='', domain=False, values=['Mon', 'Thu', 'Sun'], labelFontSize=15)),
        x=alt.X('weeks:N', axis=alt.Axis(tickSize=0, domain=False, title='', labelExpr=expr, labelAngle=0, labelFontSize=15)),
        color=alt.Color('values', legend=None, scale=alt.Scale(domain=domain, range=range_)),
        tooltip=[
            alt.Tooltip('dates', title='Date'),
            alt.Tooltip('values', title='Value')
        ]
    ).properties(
        title=year,
        height=height,
        width=width
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


def month_plot(dates, values, labels=None, month=3, title='', cmap='YlGn', domain=None, width=250, height=None, show_date=False):
    """
    Generate a calendar-based heatmap plot for a single month.
    
    Parameters:
        dates (pd.Series): Series of datetime objects representing the data points.
        values (list or pd.Series): List or series of values to be plotted on the heatmap.
        labels (optional list): List of labels to display on top of the heatmap. If not provided, no labels will be displayed.
        month (int, optional): Month number for which the heatmap is generated. Defaults to 3 (March).
        title (str, optional): Title of the heatmap plot. If not provided, no title will be displayed.
        cmap (str, optional): Color map to use for the heatmap. Defaults to 'YlGn'.
        domain (list, optional): Domain values for the color scale. If not provided, will be automatically generated based on the input data.
        width (int, optional): Width of the heatmap plot in pixels. Defaults to 250.
        height (int, optional): Height of the heatmap plot in pixels. If not provided, will be automatically set based on the width.
        show_date (bool, optional): Whether to display day labels on top of the heatmap. Defaults to False.

    Returns:
        altair.Chart: The generated calendar-based heatmap chart.
    """
    
    df = prep_data(dates, values, labels)
    month_name = calendar.month_name[month]
    df_month = df[df['months'] == month_name].reset_index()
    df_month['day'] = df_month['dates'].dt.day

    mapping = make_day_mapping()
    expr = gen_expr(mapping)

    if domain is None:
        domain = np.sort(np.unique(values))
    range_ = sns.color_palette(cmap, len(domain)).as_hex()

    cell_width = width * 0.1
    if height is None:
        height = width * 0.8

    if labels is not None:
        tooltips = [
            alt.Tooltip('labels', title=' ')
        ]
    else:
        tooltips = [
            alt.Tooltip('dates', title='Date'),
            alt.Tooltip('values', title='Value')
        ]
    
    days = list(calendar.day_abbr)
    df_heatmap = df_month[df_month['values'] != 0].reset_index(drop=True)

    chart = alt.Chart(df_heatmap).mark_rect(cornerRadius=5, width=cell_width, height=cell_width).encode(
        alt.X('days', sort=days, title='', axis=alt.Axis(tickSize=0, domain=False, labelFontSize=width/20, orient='top', labelAngle=0, labelExpr=expr)),
        alt.Y('weeks:N', title='', axis=alt.Axis(tickSize=0, domain=False, labelAngle=0, labelFontSize=0)),
        alt.Color('values', legend=None, scale=alt.Scale(domain=domain, range=range_)),
        tooltip=tooltips
    ).properties(
        height=height,
        width=width,
        title=title,
        view=alt.ViewConfig(strokeWidth=0)
    )

    if show_date:
        df_month['is_weekend'] = df_month['days'].apply(lambda x: True if x in ['Sat', 'Sun'] else False)
        
        label = alt.Chart(df_month).mark_text(baseline='middle', fontSize=width/20).encode(
            alt.X('days', sort=days),
            alt.Y('weeks:N'),
            alt.Text('day:N'),
            tooltip=alt.value(None),
            color=alt.condition(alt.datum['is_weekend'], alt.value('#ED2939'), alt.value('#000000'))
        )
        chart = chart + label

    return chart

# create function to make calendar heatmap for all months
def calendar_plot(dates, values, labels=None, cmap='YlGn', nrows=3, show_date=False, domain=None):
    
    valid_nrows = [1, 2, 3, 4, 6, 12]
    if nrows not in valid_nrows:
        raise ValueError(f'calendar_plot: nrows must be a factor of 12, i.e {valid_nrows}')

    charts = [alt.Chart()]*12
    for i in range(12):
        c = month_plot(dates, values, labels, month=i+1, title=calendar.month_name[i+1], cmap=cmap, domain=domain, show_date=show_date)
        charts[i] = c

    # format display
    full = alt.vconcat()
    for i in range(nrows):
        chart = alt.hconcat()
        ncols = int(12/nrows)
        for j in range(ncols):
            chart |= charts[i*ncols+j]
        full &= chart

    return full


def plot_calendar(year=2025, label_df=None, color='Reds', layout='3x4'):
    """
    Creates an interactive calendar heatmap with a given year and optional labels.

    Parameters
    ----------
    year : int (optional)
        The calendar year to be plotted. Defaults to 2025.
    label_df : DataFrame (optional)
        A DataFrame containing additional information to plot alongside the dates.
        It should have columns 'date' and optionally either 'value' and/or 'label'.
        If 'value' is not provided, it only show the label in the tooltip.
        If 'label' is not provided, it will use the 'value' column as the label.
    color : str (optional)
        Color palette used for the heatmap. Defaults to 'Reds'.
    layout : str (optional)
        Layout of the calendar heatmap in terms of rows and columns, e.g., '3x4' or '1x12'.

    Returns
    -------
    altair.Chart object
        The interactive calendar heatmap chart.
    """

    # error handling for input data
    if label_df is not None:
        if 'date' not in label_df.columns:
            raise ValueError(f'plot_calendar: column "date" is required')
        else:
            if 'value' not in label_df.columns and 'label' not in label_df.columns:
                raise ValueError(f'plot_calendar: column "value" or "label" is required')

    # default value for empty calendar
    dates = pd.date_range(f'{year}-01-01', f'{year}-12-31')
    values = [0]*len(dates)
    labels = None

    domain = []
    if label_df is not None:
        label_df['date'] = pd.to_datetime(label_df['date']).copy()

        if 'value' not in label_df.columns:
            label_df['value'] = 1
            domain = [0, 1]
        else:
            domain = np.sort(np.unique(label_df['value']))

        default_df = pd.DataFrame({'date': dates, 'value': values})
        if 'label' in label_df.columns:
            default_df['label'] = ['']*len(dates)

        df = default_df.merge(label_df, on='date', how='left', suffixes=('', '_y'))

        dates = df['date']
        values = df['value_y'].tolist()
        if 'label' in label_df.columns:
            labels = df['label_y'].tolist()

    nrows = int(layout[0])
    return calendar_plot(dates, values, labels, cmap=color, nrows=nrows, show_date=True, domain=domain)
