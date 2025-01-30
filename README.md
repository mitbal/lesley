# Lesley

Lesley is a lightweight Python package designed to create interactive, github-style, calendar-based heatmaps using altair.

## Example Usage
### Plot github-style heatmap
```python
dates = pd.date_range(start='2024-01-01', end='2024-12-31')
values = np.random.randint(0, 10, size=len(dates))
lesley.cal_heatmap(dates, values)
```
![github-styled calendar heatmap](https://raw.githubusercontent.com/mitbal/lesley/refs/heads/main/images/github_heatmap.png)

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
