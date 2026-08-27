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

        spec = chart.to_dict()
        self.assertNotIn('width', spec['mark'])
        self.assertNotIn('height', spec['mark'])
        self.assertEqual(spec['encoding']['x']['scale']['paddingInner'], 0.1)
        self.assertEqual(spec['encoding']['y']['scale']['paddingInner'], 0.1)
        self.assertEqual(spec['width']['step'], spec['height']['step'])

    def test_handcrafted_color_palette(self):
        self.assertIn('github', lesley.PALETTES)
        self.assertEqual(
            lesley.color_palette('github', 5),
            list(lesley.PALETTES['github'])
        )
        self.assertEqual(
            lesley.color_palette('OCEAN', 2),
            [lesley.PALETTES['ocean'][0], lesley.PALETTES['ocean'][-1]]
        )

    def test_custom_color_range(self):
        colors = lesley.color_palette(
            'github',
            4,
            color_range=['#f8fafc', '#0f766e']
        )
        self.assertEqual(len(colors), 4)
        self.assertEqual(colors[0], '#f8fafc')
        self.assertEqual(colors[-1], '#0f766e')

        direct_colors = lesley.color_palette(['#fff7ed', '#9a3412'], 2)
        self.assertEqual(direct_colors, ['#fff7ed', '#9a3412'])

    def test_binary_color_scale(self):
        dates = pd.to_datetime(['2024-03-01', '2024-03-02'])
        chart = lesley.month_plot(
            dates,
            [0, 7],
            month=3,
            binary=True,
            color_range=['#eeeeee', '#112233']
        )
        color = chart.to_dict()['encoding']['color']

        self.assertEqual(color['field'], '_lesley_color')
        self.assertEqual(color['type'], 'ordinal')
        self.assertEqual(color['scale']['domain'], [0, 1])
        self.assertEqual(color['scale']['range'], ['#eeeeee', '#112233'])

    def test_unknown_color_palette(self):
        with self.assertRaisesRegex(ValueError, 'unknown palette'):
            lesley.color_palette('not-a-palette', 3)

    def test_month_plot(self):
        dates = pd.to_datetime(['2024-03-01', '2024-03-03', '2024-03-05'])
        values = [10, 20, 30]
        chart = lesley.month_plot(dates, values, month=3)
        self.assertIsInstance(chart, alt.Chart)

        spec = chart.to_dict()
        self.assertNotIn('width', spec['mark'])
        self.assertNotIn('height', spec['mark'])
        self.assertEqual(spec['encoding']['x']['scale']['paddingInner'], 0.1)
        self.assertEqual(spec['encoding']['y']['scale']['paddingInner'], 0.1)
        self.assertEqual(spec['width']['step'], spec['height']['step'])
        self.assertEqual(len(spec['encoding']['x']['scale']['domain']), 7)
        self.assertEqual(len(spec['encoding']['y']['scale']['domain']), 6)

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
        self.assertIsInstance(chart, alt.HConcatChart)

        spec = chart.to_dict()
        month_rows = [
            [column['vconcat'][row]['title'] for column in spec['hconcat']]
            for row in range(3)
        ]
        self.assertEqual(month_rows, [
            ['January', 'February', 'March', 'April'],
            ['May', 'June', 'July', 'August'],
            ['September', 'October', 'November', 'December'],
        ])

        two_row_spec = lesley.calendar_plot(dates, values, nrows=2).to_dict()
        two_month_rows = [
            [column['vconcat'][row]['title'] for column in two_row_spec['hconcat']]
            for row in range(2)
        ]
        self.assertEqual(two_month_rows, [
            ['January', 'February', 'March', 'April', 'May', 'June'],
            ['July', 'August', 'September', 'October', 'November', 'December'],
        ])

        #test show_date = True
        chart = lesley.calendar_plot(dates, values, nrows=3, show_date = True)
        self.assertIsInstance(chart, alt.HConcatChart)

        # Test invalid nrows
        with self.assertRaises(ValueError):
            lesley.calendar_plot(dates, values, nrows=5)

    def test_plot_calendar(self):
        chart = lesley.plot_calendar(year=2024)
        self.assertIsInstance(chart, alt.HConcatChart)

        # Test with label_df
        data = {'date': ['2024-01-01', '2024-01-05'], 'value': [10, 20]}
        label_df = pd.DataFrame(data)
        chart = lesley.plot_calendar(year=2024, label_df=label_df)
        self.assertIsInstance(chart, alt.HConcatChart)

        #Test only with Label Column
        data = {'date': ['2024-01-01', '2024-01-05'], 'label': ['A', 'B']}
        label_df = pd.DataFrame(data)
        chart = lesley.plot_calendar(year=2024, label_df=label_df)
        self.assertIsInstance(chart, alt.HConcatChart)

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
        self.assertIsInstance(chart, alt.HConcatChart)

        #Test incorrect nrows option, expect ValueError because "layout = 3x4" has to have rows that can divide 12 (number of months)
        with self.assertRaises(ValueError):
            chart = lesley.plot_calendar(year=2024, label_df=label_df, layout='5x4')


if __name__ == '__main__':
    unittest.main()
