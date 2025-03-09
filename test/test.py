import unittest
import pandas as pd
import numpy as np
import altair as alt

from lesley import lesley
import calendar


class TestLesley(unittest.TestCase):

    def test_make_month_mapping(self):
        mapping = lesley.make_month_mapping()
        self.assertIsInstance(mapping, dict)
        self.assertEqual(len(mapping), 12)
        self.assertIn("Week 01", mapping)
        self.assertEqual(mapping["Week 01"], "Jan")

    def test_make_day_mapping(self):
        mapping = lesley.make_day_mapping()
        self.assertIsInstance(mapping, dict)
        self.assertEqual(len(mapping), 7)
        self.assertIn("Mon", mapping)
        self.assertEqual(mapping["Mon"], "M")

    def test_gen_expr(self):
        mapping = {"a": "A", "b": "B"}
        expr = lesley.gen_expr(mapping)
        self.assertIsInstance(expr, str)
        self.assertIn("datum.label == 'a' ? 'A'", expr)
        self.assertIn("''", expr)  # Default case

    def test_prep_data(self):
        dates = pd.to_datetime(['2024-01-01', '2024-01-03', '2024-01-05'])
        values = [10, 20, 30]
        df = lesley.prep_data(dates, values)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 366)  # all days in 2024
        self.assertEqual(df['values'].iloc[0], 10.0)
        self.assertEqual(df['values'].iloc[1], 0.0)  # Filled missing date

        # Test with labels
        labels = ['A', 'B', 'C']
        df_with_labels = lesley.prep_data(dates, values, labels)
        self.assertTrue('labels' in df_with_labels.columns)
        self.assertEqual(df_with_labels['labels'].iloc[0], 'A')
        # self.assertEqual(df_with_labels['labels'].iloc[1], '')

    def test_cal_heatmap(self):
        dates = pd.to_datetime(['2024-01-01', '2024-01-03', '2024-01-05'])
        values = [10, 20, 30]
        chart = lesley.cal_heatmap(dates, values)
        self.assertIsInstance(chart, alt.Chart)

    def test_month_plot(self):
        dates = pd.to_datetime(['2024-03-01', '2024-03-03', '2024-03-05'])
        values = [10, 20, 30]
        chart = lesley.month_plot(dates, values, month=3)
        self.assertIsInstance(chart, alt.Chart)

        #Test Labels
        labels = ['A','B','C']
        chart = lesley.month_plot(dates, values, labels, month=3)
        self.assertIsInstance(chart, alt.Chart)

        #Test show_date = True
        chart = lesley.month_plot(dates, values, labels, month=3, show_date = True)
        self.assertIsInstance(chart, alt.LayerChart)
        

    def test_calendar_plot(self):
        dates = pd.to_datetime(['2024-01-01', '2024-03-03', '2024-05-05'])
        values = [10, 20, 30]
        chart = lesley.calendar_plot(dates, values, nrows=3)
        self.assertIsInstance(chart, alt.VConcatChart)

        #test show_date = True
        chart = lesley.calendar_plot(dates, values, nrows=3, show_date = True)
        self.assertIsInstance(chart, alt.VConcatChart)

        # Test invalid nrows
        with self.assertRaises(ValueError):
            lesley.calendar_plot(dates, values, nrows=5)

    def test_plot_calendar(self):
        chart = lesley.plot_calendar(year=2024)
        self.assertIsInstance(chart, alt.VConcatChart)

        # Test with label_df
        data = {'date': ['2024-01-01', '2024-01-05'], 'value': [10, 20]}
        label_df = pd.DataFrame(data)
        chart = lesley.plot_calendar(year=2024, label_df=label_df)
        self.assertIsInstance(chart, alt.VConcatChart)

        #Test only with Label Column
        data = {'date': ['2024-01-01', '2024-01-05'], 'label': ['A', 'B']}
        label_df = pd.DataFrame(data)
        chart = lesley.plot_calendar(year=2024, label_df=label_df)
        self.assertIsInstance(chart, alt.VConcatChart)

        # Test invalid label_df
        label_df_missing_date = pd.DataFrame({'value': [10, 20]})
        with self.assertRaises(ValueError):
            lesley.plot_calendar(year=2024, label_df=label_df_missing_date)

        label_df_missing_value = pd.DataFrame({'date': ['2024-01-01', '2024-01-05']})
        with self.assertRaises(ValueError):
            lesley.plot_calendar(year=2024, label_df=label_df_missing_value)

        #Test correct nrows option
        data = {'date': ['2024-01-01', '2024-01-05'], 'value': [10, 20]}
        label_df = pd.DataFrame(data)
        chart = lesley.plot_calendar(year=2024, label_df=label_df, layout='3x4')
        self.assertIsInstance(chart, alt.VConcatChart)

        #Test incorrect nrows option, expect ValueError because "layout = 3x4" has to have rows that can divide 12 (number of months)
        with self.assertRaises(ValueError):
            chart = lesley.plot_calendar(year=2024, label_df=label_df, layout='5x4')


if __name__ == '__main__':
    unittest.main()