import numpy as np
import pandas as pd
import streamlit as st

import lesley


YEAR = 2025
DATES = pd.date_range(f'{YEAR}-01-01', f'{YEAR}-12-31')

# A small, deterministic domain makes palette differences easy to compare.
rng = np.random.default_rng(42)
VALUES = pd.Series(rng.integers(0, 5, size=len(DATES)))
DOMAIN = [0, 1, 2, 3, 4]

event_mask = (DATES.day == 1) | ((DATES.dayofyear % 17) == 0)
EVENT_DATES = DATES[event_mask]
EVENTS = pd.DataFrame({
    'date': EVENT_DATES,
    'value': 1,
    'label': [f'Example event {index + 1}' for index in range(len(EVENT_DATES))],
})


def show_chart(chart):
    """Render at the chart's intrinsic size so square cells are not stretched."""
    st.altair_chart(chart, width='content')


st.set_page_config(page_title='Lesley color showcase', layout='wide')

# Preserve intrinsic Vega-Lite dimensions on narrow screens and scroll instead
# of compressing only the horizontal axis.
st.markdown(
    """
    <style>
    [data-testid="stVegaLiteChart"] {
        overflow-x: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title('Lesley color showcase')
st.caption(
    f'Lesley {lesley.__version__}: Seaborn-free palettes, custom color ranges, '
    'binary scales, and calendar heatmaps.'
)

named_tab, custom_tab, binary_tab, calendar_tab = st.tabs([
    'Named palettes',
    'Custom ranges',
    'Binary colors',
    'Calendar layouts',
])

with named_tab:
    st.header('Handcrafted Lesley palettes')
    st.write('Available through `lesley.PALETTES` and `lesley.color_palette()`.')

    selected_palette = st.selectbox(
        'Palette',
        options=list(lesley.PALETTES),
        index=0,
    )
    sampled_colors = lesley.color_palette(selected_palette, 9)
    st.code(
        f"lesley.color_palette('{selected_palette}', 9)\n\n{sampled_colors}",
        language='python',
    )
    show_chart(
        lesley.cal_heatmap(
            DATES,
            VALUES,
            cmap=selected_palette,
            domain=DOMAIN,
            height=170,
        )
    )

    st.subheader('Matplotlib compatibility')
    st.write('Existing Matplotlib colormap names continue to work without Seaborn.')
    matplotlib_palette = st.selectbox(
        'Matplotlib colormap',
        options=['YlGn', 'Reds', 'viridis', 'cividis', 'magma'],
    )
    show_chart(
        lesley.cal_heatmap(
            DATES,
            VALUES,
            cmap=matplotlib_palette,
            domain=DOMAIN,
            height=170,
        )
    )

with custom_tab:
    st.header('Custom color ranges')
    st.write(
        '`color_range` accepts CSS-compatible colors and interpolates them to '
        'match the supplied or inferred domain.'
    )
    custom_range = ['#f8fafc', '#5eead4', '#115e59']
    st.code(
        "lesley.cal_heatmap(\n"
        "    dates, values,\n"
        "    domain=[0, 1, 2, 3, 4],\n"
        "    color_range=['#f8fafc', '#5eead4', '#115e59'],\n"
        ")",
        language='python',
    )
    show_chart(
        lesley.cal_heatmap(
            DATES,
            VALUES,
            domain=DOMAIN,
            color_range=custom_range,
            height=170,
        )
    )

    st.subheader('Color sequence passed directly to `cmap`')
    direct_colors = ['#fff7ed', '#fdba74', '#ea580c', '#9a3412']
    st.code(
        "lesley.month_plot(\n"
        "    dates, values, month=3,\n"
        "    cmap=['#fff7ed', '#fdba74', '#ea580c', '#9a3412'],\n"
        ")",
        language='python',
    )
    show_chart(
        lesley.month_plot(
            DATES,
            VALUES,
            month=3,
            title='March with a direct color sequence',
            cmap=direct_colors,
            domain=DOMAIN,
            width=360,
            show_date=True,
        )
    )

with binary_tab:
    st.header('Binary presence and absence')
    st.write(
        '`binary=True` maps zero to the first color and every non-zero value to '
        'the second, regardless of its magnitude.'
    )
    binary_range = ['#ebedf0', '#216e39']
    binary_values = pd.Series(event_mask.astype(int))
    st.code(
        "lesley.cal_heatmap(\n"
        "    dates, values, binary=True,\n"
        "    color_range=['#ebedf0', '#216e39'],\n"
        ")",
        language='python',
    )
    show_chart(
        lesley.cal_heatmap(
            DATES,
            binary_values,
            binary=True,
            color_range=binary_range,
            height=170,
        )
    )

    st.subheader('Binary event calendar with labels')
    show_chart(
        lesley.plot_calendar(
            year=YEAR,
            label_df=EVENTS.copy(),
            color='binary',
            binary=True,
            layout='3x4',
        )
    )

with calendar_tab:
    st.header('Calendar layouts')

    st.subheader('Empty calendar')
    st.code('lesley.plot_calendar(year=2025)', language='python')
    show_chart(lesley.plot_calendar(year=YEAR))

    st.subheader('Full-year heatmap with `calendar_plot`')
    st.code(
        "lesley.calendar_plot(\n"
        "    dates, values, cmap='dusk', nrows=2,\n"
        "    show_date=True, domain=[0, 1, 2, 3, 4],\n"
        ")",
        language='python',
    )
    show_chart(
        lesley.calendar_plot(
            DATES,
            VALUES,
            cmap='dusk',
            nrows=2,
            show_date=True,
            domain=DOMAIN,
        )
    )

    st.subheader('Labeled calendar with a custom layout')
    st.code(
        "lesley.plot_calendar(\n"
        "    year=2025, label_df=events, color='ember', layout='2x6',\n"
        ")",
        language='python',
    )
    show_chart(
        lesley.plot_calendar(
            year=YEAR,
            label_df=EVENTS.copy(),
            color='ember',
            layout='2x6',
        )
    )
