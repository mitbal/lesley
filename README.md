# Lesley

[![PyPI Downloads](https://static.pepy.tech/badge/lesley)](https://pepy.tech/projects/lesley)

![example workflow](https://github.com/mitbal/lesley/actions/workflows/publish.yml/badge.svg)

Lesley is a lightweight Python package designed to create interactive, github-style, calendar-based heatmaps using Altair. Color generation is Seaborn-free and supports Matplotlib colormaps, handcrafted Lesley palettes, custom color ranges, and binary scales.

Heatmap cells remain square at every chart size. The `width` and `height` arguments act as maximum bounds, allowing Lesley to fit the largest square grid without cell overlap or unused plot area.

## Example Usage
### Plot github-style heatmap
```python
dates = pd.date_range(start='2024-01-01', end='2024-12-31')
values = np.random.randint(0, 10, size=len(dates))
lesley.cal_heatmap(dates, values)
```
![github-styled calendar heatmap](https://raw.githubusercontent.com/mitbal/lesley/refs/heads/main/images/github_heatmap.png)

### Use a handcrafted palette

Lesley includes `github`, `forest`, `ocean`, `ember`, `berry`, `dusk`, `monochrome`, and `binary` palettes. Existing Matplotlib names such as `YlGn`, `Reds`, and `viridis` remain supported.

```python
lesley.cal_heatmap(dates, values, cmap='ocean')
```

The palette colors are also available through `lesley.PALETTES` and `lesley.color_palette()`.

### Define a custom color range

Pass CSS-compatible colors with `color_range`. Lesley interpolates the colors to match the color domain.

```python
lesley.cal_heatmap(
    dates,
    values,
    domain=[0, 2, 4, 6, 8],
    color_range=['#f8fafc', '#5eead4', '#115e59'],
)
```

A color sequence can also be passed directly as `cmap`:

```python
lesley.month_plot(dates, values, cmap=['#fff7ed', '#fdba74', '#9a3412'])
```

### Use binary colors

Set `binary=True` to map zero values to the first color and all non-zero values to the second. This is useful for presence, completion, holiday, and event calendars.

```python
lesley.cal_heatmap(
    dates,
    values,
    binary=True,
    color_range=['#ebedf0', '#216e39'],
)
```

### Plot empty calendar
```python
lesley.plot_calendar(year=2025)
```
![empty full year calendar](https://github.com/mitbal/lesley/blob/main/images/empty_calendar.png?raw=true)

### Plot calendar with marker and label
```python
holiday_df = pd.read_csv('holidays.csv') # need at least 2 columns: date and label
lesley.plot_calendar(year=2025, label_df=holiday_df, color='Oranges')
```
![full year calendar with label and marker](https://github.com/mitbal/lesley/blob/main/images/labeled_calendar.png?raw=true)

### Plot calendar heatmap
```python
dividend_df = pd.read_csv('dividend.csv') # need 3 columns: date, label, and value
lesley.plot_calendar(year=2024, label_df=dividend_df, color='Greens', layout='2x6')
```
![full year calendar heatmap](https://github.com/mitbal/lesley/blob/main/images/heatmap_calendar_with_label.png?raw=true)

### Plot individual month
```python
dates = pd.date_range(start='2024-01-01', end='2024-12-31')
values = np.random.randint(0, 10, size=len(dates))
lesley.month_plot(dates, values, 1)
```
![single month plot](https://raw.githubusercontent.com/mitbal/lesley/main/images/month_plot.png)
