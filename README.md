# Lesley

Lesley is a library to create a heatmap of daily data in for the whole calendar year. Inspired by July (https://github.com/e-hulten/july)

## How to use

Plot the whole year heatmap
```
dates = pd.date_range(start='2024-01-01', end='2024-12-31')
values = np.random.randint(0, 10, size=len(dates))
lesley.cal_heatmap(dates, values)
```
![calendar heatmap output example](https://raw.githubusercontent.com/mitbal/lesley/main/images/calendar_heatmap.png)

Plot a single month
```
dates = pd.date_range(start='2024-01-01', end='2024-12-31')
values = np.random.randint(0, 10, size=len(dates))
lesley.month_plot(dates, values, 1)
```
![single month plot](https://raw.githubusercontent.com/mitbal/lesley/main/images/month_plot.png)

Plot all month in single year
```
dates = pd.date_range(start='2024-01-01', end='2024-12-31')
values = np.random.randint(0, 10, size=len(dates))
lesley.calendar_plot(dates, values, nrows=3)
```
![all month plot](https://raw.githubusercontent.com/mitbal/lesley/main/images/calendar_plot.png)
