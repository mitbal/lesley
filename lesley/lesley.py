"""
Lesley: A Python package for plotting calendar-based heatmaps.
Inspired by the July visualization library.
"""

__all__ = [
    'PALETTES',
    'calendar_plot',
    'cal_heatmap',
    'color_palette',
    'month_plot',
    'plot_calendar',
    'prep_data',
]

import calendar
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
import altair as alt
from matplotlib import colormaps
from matplotlib.colors import LinearSegmentedColormap, to_hex


Palette = Union[str, Sequence[str]]

PALETTES: Dict[str, Tuple[str, ...]] = {
    'github': ('#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39'),
    'forest': ('#eef3e8', '#c5d9a4', '#88b96b', '#4c8c4a', '#24563b'),
    'ocean': ('#edf6f4', '#b9ddd7', '#6dbdb8', '#277f8e', '#153f5b'),
    'ember': ('#fff1df', '#f6c177', '#e07a3f', '#b64332', '#672a38'),
    'berry': ('#f8eef3', '#e5b2ca', '#c76b9b', '#873f78', '#45204f'),
    'dusk': ('#f1f0e8', '#c6c4a5', '#8f8d74', '#55566d', '#292b45'),
    'monochrome': ('#f1f3f2', '#c6ceca', '#899791', '#52615c', '#26312d'),
    'binary': ('#ebedf0', '#216e39'),
}


def _interpolate_colors(colors: Sequence[str], size: int) -> List[str]:
    """Interpolate CSS-compatible colors to an exact range size."""
    normalized = [to_hex(color) for color in colors]
    if not normalized:
        raise ValueError('color range must contain at least one color')
    if size == 0:
        return []
    if len(normalized) == 1:
        return normalized * size
    if size == len(normalized):
        return normalized

    cmap = LinearSegmentedColormap.from_list('lesley_custom', normalized)
    positions = [0.5] if size == 1 else np.linspace(0, 1, size)
    return [to_hex(cmap(value)) for value in positions]


def color_palette(cmap: Palette = 'github',
                  size: int = 5,
                  *,
                  color_range: Optional[Sequence[str]] = None,
                  binary: bool = False) -> List[str]:
    """Resolve a named palette, Matplotlib colormap, or custom color range.

    ``color_range`` takes precedence over ``cmap``. Custom ranges are
    interpolated to ``size`` colors, while binary palettes always return their
    two endpoint colors.
    """
    if size < 0:
        raise ValueError('palette size cannot be negative')
    if binary:
        size = 2

    colors: Optional[Sequence[str]] = color_range
    if colors is None and not isinstance(cmap, str):
        colors = cmap
    if colors is None:
        palette_name = cmap.casefold()
        colors = PALETTES.get(palette_name)

    if colors is not None:
        if binary and len(colors) > 1:
            colors = (colors[0], colors[-1])
        return _interpolate_colors(colors, size)

    try:
        matplotlib_cmap = colormaps[cmap]
    except KeyError as exc:
        names = ', '.join(PALETTES)
        raise ValueError(
            f'unknown palette {cmap!r}; use a Matplotlib colormap, '
            f'one of [{names}], or pass color_range'
        ) from exc

    if size == 0:
        return []
    if binary:
        positions = [0.0, 1.0]
    else:
        positions = np.linspace(0, 1, size + 2)[1:-1]
    return [to_hex(matplotlib_cmap(value)) for value in positions]


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

    start_date = min(dates)
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
                cmap: Palette = 'YlGn',
                height: int = 250,
                days_of_week: list = ['Mon', 'Thu', 'Sun'],
                width: Optional[int] = None,
                domain: Optional[Sequence[Union[int, float]]] = None,
                color_range: Optional[Sequence[str]] = None,
                binary: bool = False) -> alt.Chart:
    """
    Generate a github-style calendar-based heatmap using altair.

    Parameters:
        dates (pd.Series): Series of datetime objects representing the data points.
        values (list or pd.Series): List or series of values to be plotted on the heatmap.
        cmap (str or sequence, optional): Lesley palette name, Matplotlib colormap,
            or custom color sequence. Defaults to 'YlGn'.
        height (int, optional): Maximum heatmap height in pixels. Defaults to 250.
        days_of_week (list, optional): The labels for 3 letters of days of week in the y axis. Default to Monday, Thursday, and Sunday.
        width (int, optional): Maximum heatmap width in pixels. If not provided,
            it is automatically set based on the height. Cells remain square,
            so the chart may use less than one of these bounds.
        domain (sequence, optional): Values defining the color scale domain.
        color_range (sequence, optional): Custom CSS colors for the scale. Takes
            precedence over cmap and is interpolated to match the domain.
        binary (bool, optional): Map zero to the first color and every non-zero
            value to the last color. Defaults to False.

    Returns:
        altair.Chart: The generated calendar-based heatmap chart.
    """

    input_values = pd.Series(values)
    df = prep_data(dates, input_values)
    mapping = make_month_mapping()
    expr = gen_expr(mapping)

    if binary:
        df['_lesley_color'] = (df['values'] != 0).astype(int)
        color_field = '_lesley_color:O'
        color_domain = [0, 1]
    else:
        color_field = 'values:Q'
        color_domain = list(domain) if domain is not None else np.sort(input_values.dropna().unique()).tolist()
    range_ = color_palette(cmap, len(color_domain), color_range=color_range, binary=binary)

    if width is None:
        width = height * 5

    year = str(df['dates'].iloc[0].year)
    days = list(calendar.day_abbr)
    weeks = df['weeks'].drop_duplicates().tolist()
    cell_size = min(width / len(weeks), height / len(days))
    font_size = min(height / 16, cell_size * 0.6)
    corner_radius = min(5, cell_size * 0.2)

    chart = alt.Chart(df).mark_rect(cornerRadius=corner_radius).encode(
        y=alt.Y(
            'days',
            sort=days,
            scale=alt.Scale(domain=days, paddingInner=0.1, paddingOuter=0.05),
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
            scale=alt.Scale(domain=weeks, paddingInner=0.1, paddingOuter=0.05),
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
            color_field,
            legend=None,
            scale=alt.Scale(domain=color_domain, range=range_)
        ),
        tooltip=[
            alt.Tooltip('dates', title='Date'),
            alt.Tooltip('values', title='Value')
        ]
    ).properties(
        title=year,
        height=alt.Step(cell_size),
        width=alt.Step(cell_size)
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
               cmap: Palette = 'YlGn',
               domain: Optional[Sequence[Union[int, float]]] = None,
               width: int = 250,
               height: Optional[int] = None,
               show_date: bool = False,
               color_range: Optional[Sequence[str]] = None,
               binary: bool = False) -> alt.Chart:
    """
    Generate a calendar-based heatmap plot for a single month.
    
    Parameters:
        dates (pd.Series): Series of datetime objects representing the data points.
        values (list or pd.Series): List or series of values to be plotted on the heatmap.
        labels (optional list): List of labels to display on top of the heatmap. If not provided, no labels will be displayed.
        month (int, optional): Month number for which the heatmap is generated. Defaults to 3 (March).
        title (str, optional): Title of the heatmap plot. If not provided, no title will be displayed.
        cmap (str or sequence, optional): Lesley palette name, Matplotlib colormap,
            or custom color sequence. Defaults to 'YlGn'.
        domain (list, optional): Domain values for the color scale. If not provided, will be automatically generated based on the input data.
        width (int, optional): Maximum heatmap width in pixels. Defaults to 250.
        height (int, optional): Maximum heatmap height in pixels. If not provided,
            it is automatically set based on the width. Month plots reserve a
            7-by-6 grid so cells stay square and calendar layouts stay aligned.
        show_date (bool, optional): Whether to display day labels on top of the heatmap. Defaults to False.
        color_range (sequence, optional): Custom CSS colors for the scale. Takes
            precedence over cmap and is interpolated to match the domain.
        binary (bool, optional): Map zero to the first color and every non-zero
            value to the last color. Defaults to False.

    Returns:
        altair.Chart: The generated calendar-based heatmap chart.
    """
    
    input_values = pd.Series(values)
    df = prep_data(dates, input_values, labels)
    month_name = calendar.month_name[month]
    df_month = df[df['months'] == month_name].reset_index()
    df_month['day'] = df_month['dates'].dt.day

    mapping = make_day_mapping()
    expr = gen_expr(mapping)

    if binary:
        df_month['_lesley_color'] = (df_month['values'] != 0).astype(int)
        color_field = '_lesley_color:O'
        color_domain = [0, 1]
    else:
        color_field = 'values:Q'
        color_domain = list(domain) if domain is not None else np.sort(input_values.dropna().unique()).tolist()
    range_ = color_palette(cmap, len(color_domain), color_range=color_range, binary=binary)

    if height is None:
        height = int(width * 0.8)

    days = list(calendar.day_abbr)
    weeks = df_month['weeks'].drop_duplicates().tolist()
    while len(weeks) < 6:
        weeks.append(f'_lesley_empty_week_{len(weeks)}')
    cell_size = min(width / len(days), height / len(weeks))
    font_size = min(width / 20, cell_size * 0.6)
    corner_radius = min(5, cell_size * 0.2)

    if labels is not None:
        tooltips = [
            alt.Tooltip('labels', title=' ')
        ]
    else:
        tooltips = [
            alt.Tooltip('dates', title='Date'),
            alt.Tooltip('values', title='Value')
        ]
    
    if binary:
        df_heatmap = df_month
    else:
        df_heatmap = df_month[df_month['values'] != 0].reset_index(drop=True)
    if len(df_heatmap) > 0:
        chart = alt.Chart(df_heatmap).mark_rect(cornerRadius=corner_radius).encode(
            alt.X('days:N', sort=days, title='', scale=alt.Scale(domain=days, paddingInner=0.1, paddingOuter=0.05), axis=alt.Axis(tickSize=0, domain=False, labelFontSize=font_size, orient='top', labelAngle=0, labelExpr=expr)),
            alt.Y('weeks:N', title='', scale=alt.Scale(domain=weeks, paddingInner=0.1, paddingOuter=0.05), axis=alt.Axis(tickSize=0, domain=False, labelAngle=0, labelFontSize=0)),
            alt.Color(color_field, legend=None, scale=alt.Scale(domain=color_domain, range=range_)),
            tooltip=tooltips
        ).properties(
            height=alt.Step(cell_size),
            width=alt.Step(cell_size),
            title=title,
            view=alt.ViewConfig(strokeWidth=0)
        )
    else:
        chart = alt.Chart(df_month).mark_rect(cornerRadius=corner_radius, opacity=0).encode(
            alt.X('days:N', sort=days, title='', scale=alt.Scale(domain=days, paddingInner=0.1, paddingOuter=0.05), axis=alt.Axis(tickSize=0, domain=False, labelFontSize=font_size, orient='top', labelAngle=0, labelExpr=expr)),
            alt.Y('weeks:N', title='', scale=alt.Scale(domain=weeks, paddingInner=0.1, paddingOuter=0.05), axis=alt.Axis(tickSize=0, domain=False, labelAngle=0, labelFontSize=0)),
            tooltip=tooltips
        ).properties(
            height=alt.Step(cell_size),
            width=alt.Step(cell_size),
            title=title,
            view=alt.ViewConfig(strokeWidth=0)
        )

    if show_date:
        df_month['is_weekend'] = df_month['days'].apply(lambda x: True if x in ['Sat', 'Sun'] else False)
        
        label = alt.Chart(df_month).mark_text(baseline='middle', fontSize=font_size).encode(
            alt.X('days', sort=days, scale=alt.Scale(domain=days, paddingInner=0.1, paddingOuter=0.05)),
            alt.Y('weeks:N', scale=alt.Scale(domain=weeks, paddingInner=0.1, paddingOuter=0.05)),
            alt.Text('day:N'),
            tooltip=alt.value(None),
            color=alt.condition(alt.datum['is_weekend'], alt.value('#ED2939'), alt.value('#000000'))
        )
        if chart is not None:
            chart = chart + label
        else:
            chart = label

    return chart


def calendar_plot(dates: Iterable,
                  values: Iterable,
                  labels: Optional[Iterable] = None,
                  cmap: Palette = 'YlGn',
                  nrows: int = 3,
                  show_date: bool = False,
                  domain: Optional[Sequence[Union[int, float]]] = None,
                  color_range: Optional[Sequence[str]] = None,
                  binary: bool = False) -> alt.HConcatChart:
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
        cmap (str or sequence, optional): Lesley palette name, Matplotlib colormap,
            or custom color sequence. Defaults to 'YlGn'.
        nrows (int, optional): Number of rows in the grid layout. Must be a factor of 12
            (i.e., 1, 2, 3, 4, 6, or 12). Defaults to 3.
        show_date (bool, optional): Whether to display day numbers on the heatmap cells.
            Defaults to False.
        domain (Optional[List[Union[int, float]]], optional): Domain values for the color scale.
            If not provided, will be automatically determined from the values. Defaults to None.
        color_range (sequence, optional): Custom CSS colors for the scale. Takes
            precedence over cmap and is interpolated to match the domain.
        binary (bool, optional): Map zero to the first color and every non-zero
            value to the last color. Defaults to False.

    Returns:
        alt.HConcatChart: A horizontally concatenated chart containing the monthly heatmaps
            arranged in the specified number of rows.

    Raises:
        ValueError: If nrows is not a factor of 12 (i.e., not in [1, 2, 3, 4, 6, 12]).
    """
    valid_nrows = [1, 2, 3, 4, 6, 12]
    if nrows not in valid_nrows:
        raise ValueError(f'calendar_plot: nrows must be a factor of 12, i.e {valid_nrows}')

    charts = [None]*12
    for i in range(12):
        c = month_plot(
            dates,
            values,
            labels,
            month=i+1,
            title=calendar.month_name[i+1],
            cmap=cmap,
            domain=domain,
            show_date=show_date,
            color_range=color_range,
            binary=binary,
        )
        charts[i] = c

    # Build vertical columns from a row-major month sequence.
    ncols = 12 // nrows
    columns = []
    
    for j in range(ncols):
        column = alt.vconcat()
        for i in range(nrows):
            column &= charts[i * ncols + j]
        columns.append(column)
    
    # Combine all columns horizontally
    full = alt.hconcat()
    for column in columns:
        full |= column

    return full


def plot_calendar(year: int = 2025,
                  label_df: Optional[pd.DataFrame] = None,
                  color: Palette = 'Reds',
                  layout: str = '3x4',
                  color_range: Optional[Sequence[str]] = None,
                  binary: bool = False) -> alt.HConcatChart:
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
    color : str or sequence (optional)
        Lesley palette name, Matplotlib colormap, or custom color sequence.
        Defaults to 'Reds'.
    layout : str (optional)
        Layout of the calendar heatmap in terms of rows and columns, e.g., '3x4' or '1x12'.
    color_range : sequence (optional)
        Custom CSS colors for the scale. Takes precedence over color.
    binary : bool (optional)
        Map zero to the first color and every non-zero value to the last color.

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
    return calendar_plot(
        dates,
        values,
        labels,
        cmap=color,
        nrows=nrows,
        show_date=True,
        domain=domain,
        color_range=color_range,
        binary=binary,
    )
