"""
Lesley: A Python package for plotting calendar-based heatmaps.
Inspired by the July visualization library.
"""

__all__ = ['cal_heatmap', 'month_plot', 'calendar_plot', 'plot_calendar']

import calendar
from typing import Dict, Iterable, List, Optional, Union

import numpy as np
import pandas as pd
import altair as alt
import seaborn as sns


def make_month_mapping() -> Dict[str, str]:
    """
    Creates a mapping from week labels to month abbreviations for use in the plot.
    """
    month_mapping = {}
    for i in range(12):
        week_number = int(i * 4.5 + 1)
        month_abbr = calendar.month_abbr[i + 1]
        month_mapping[f'Week {week_number:02d}'] = month_abbr
    return month_mapping


def make_day_mapping() -> Dict[str, str]:
    """
    Creates a mapping from day abbreviations to single-letter representations.
    """
    day_mapping = {}
    for day in calendar.day_abbr:
        day_mapping[day] = day[0]
    return day_mapping


def gen_expr(mapping: Dict[str, str]) -> str:
    """
    Generates an Altair expression for mapping labels based on a dictionary.

    Args:
        mapping (Dict[str, str]): A dictionary where keys are the original labels and values are the desired labels.

    Returns:
        str: An Altair expression string.
    """
    expression = ""
    for key, value in mapping.items():
        expression += f"datum.label == '{key}' ? '{value}': "
    expression += " ''"
    return expression


def prep_data(dates: Iterable,
              values: Iterable,
              labels: Optional[Iterable] = None) -> pd.DataFrame:
    """
    Prepares data for analysis by ensuring dates are continuous, handling missing values,
    and adding derived columns for day, week, and month.  The dates and values input
    are explicitly converted to pandas Series to ensure they are iterable.

    Args:
        dates (Iterable): A sequence of dates. Converted to pd.Series.
        values (Iterable): A sequence of values corresponding to the dates. Converted to pd.Series.
        labels (Optional[Iterable]): A sequence of labels corresponding to the dates. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame with continuous dates, filled missing values, and derived columns.
    """

    dates = pd.to_datetime(dates)
    values = pd.Series(values)

    start_date = dates.min()
    start_year = start_date.year

    full_year = pd.date_range(start=f'{start_year}-01-01', end=f'{start_year}-12-31')
    full_df = pd.DataFrame({'dates': full_year})
    
    input_df = pd.DataFrame({'dates': dates, 'values': values})
    if labels is not None:
        input_df['labels'] = labels
    input_df = input_df.sort_values(['dates', 'values'], ascending=[True, False]).drop_duplicates(subset=['dates'], keep='first')

    df = pd.merge(left=full_df, right=input_df, how='left', on='dates')
    df['values'] = df['values'].fillna(0)
    
    df['days'] = df['dates'].dt.strftime('%a')
    df['weeks'] = 'Week ' + df['dates'].dt.strftime('%W')
    df['months'] = df['dates'].dt.strftime('%B')

    return df


def cal_heatmap(dates: Iterable,
                values: Iterable,
                cmap: str = 'YlGn',
                height: int = 250,
                days_of_week: list = ['Mon', 'Thu', 'Sun'],
                width: Optional[int] = None) -> alt.Chart:
    """
    Generate a github-style calendar-based heatmap using altair.

    Parameters:
        dates (pd.Series): Series of datetime objects representing the data points.
        values (list or pd.Series): List or series of values to be plotted on the heatmap.
        cmap (str, optional): Color map to use for the heatmap. Defaults to 'YlGn'.
        height (int, optional): Height of the heatmap in pixels. Defaults to 250.
        days_of_week (list, optional): The labels for 3 letters of days of week in the y axis. Default to Monday, Thursday, and Sunday.
        width (int, optional): Width of the heatmap in pixels. If not provided, will be automatically set based on the height.

    Returns:
        altair.Chart: The generated calendar-based heatmap chart.
    """

    df = prep_data(dates, values)
    mapping = make_month_mapping()
    expr = gen_expr(mapping)

    domain = np.sort(np.unique(values))
    range_ = sns.color_palette(cmap, len(domain)).as_hex()

    font_size = int(height / 16)
    cell_width = height / 12.5
    corner_radius = height / 50
    if width is None:
        width = height * 5

    year = str(df['dates'].iloc[0].year)
    days = list(calendar.day_abbr)

    chart = alt.Chart(df).mark_rect(
        cornerRadius=corner_radius,
        width=cell_width,
        height=cell_width
    ).encode(
        y=alt.Y(
            'days',
            sort=days,
            axis=alt.Axis(
                tickSize=0,
                title='',
                domain=False,
                values=days_of_week,
                labelFontSize=font_size
            )
        ),
        x=alt.X(
            'weeks:N', 
            axis=alt.Axis(
                tickSize=0,
                domain=False,
                title='',
                labelExpr=expr,
                labelAngle=0,
                labelFontSize=font_size
            )
        ),
        color=alt.Color(
            'values',
            legend=None,
            scale=alt.Scale(domain=domain, range=range_)
        ),
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


def month_plot(dates: Iterable,
               values: Iterable,
               labels: Optional[Iterable] = None,
               month: int = 3,
               title: str = '',
               cmap: str = 'YlGn',
               domain: Optional[List[Union[int, float]]] = None,
               width: int = 250,
               height: Optional[int] = None,
               show_date: bool = False) -> alt.Chart:
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
        alt.X('days:N', sort=days, title='', axis=alt.Axis(tickSize=0, domain=False, labelFontSize=width/20, orient='top', labelAngle=0, labelExpr=expr)),
        alt.Y('weeks:N', title='', axis=alt.Axis(tickSize=0, domain=False, labelAngle=0, labelFontSize=0)),
        alt.Color('values:Q', legend=None, scale=alt.Scale(domain=domain, range=range_)),
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


def calendar_plot(dates: Iterable,
                  values: Iterable,
                  labels: Optional[Iterable] = None,
                  cmap: str = 'YlGn',
                  nrows: int = 3,
                  show_date: bool = False,
                  domain: Optional[List[Union[int, float]]] = None) -> alt.VConcatChart:
    """
    Generate a calendar-based heatmap plot for all months of a year.

    This function creates a grid of monthly calendar heatmaps arranged in a specified
    number of rows. Each month is displayed as a separate heatmap, showing the distribution
    of values across the days of that month.

    Parameters:
        dates (Iterable): A sequence of dates to plot on the calendar.
        values (Iterable): A sequence of values corresponding to the dates.
        labels (Optional[Iterable], optional): A sequence of labels corresponding to the dates.
            If provided, these labels will be displayed in tooltips. Defaults to None.
        cmap (str, optional): Color map to use for the heatmap. Defaults to 'YlGn'.
        nrows (int, optional): Number of rows in the grid layout. Must be a factor of 12
            (i.e., 1, 2, 3, 4, 6, or 12). Defaults to 3.
        show_date (bool, optional): Whether to display day numbers on the heatmap cells.
            Defaults to False.
        domain (Optional[List[Union[int, float]]], optional): Domain values for the color scale.
            If not provided, will be automatically determined from the values. Defaults to None.

    Returns:
        alt.VConcatChart: A vertically concatenated chart containing the monthly heatmaps
            arranged in the specified number of rows.

    Raises:
        ValueError: If nrows is not a factor of 12 (i.e., not in [1, 2, 3, 4, 6, 12]).
    """
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


def plot_calendar(year: int = 2025,
                  label_df: Optional[pd.DataFrame] = None,
                  color: str = 'Reds',
                  layout: str = '3x4') -> alt.VConcatChart:
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
