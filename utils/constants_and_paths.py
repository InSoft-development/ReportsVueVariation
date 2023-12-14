"""
Модуль содержит все использеумые в приложении константы
"""
import os
import plotly.express as px

CONFIG_DIRECTORY = f'config{os.sep}'
DATA_DIRECTORY = f'data{os.sep}'
DATA_CSV_DIRECTORY = f'{DATA_DIRECTORY}csv_data{os.sep}'
REPORTS_DIRECTORY = f'reports{os.sep}'


CSV_SLICES = f'{DATA_CSV_DIRECTORY}slices.csv'
CSV_KKS_WITH_GROUPS = f'{DATA_DIRECTORY}kks_with_groups.csv'

JSON_SENSORS = f'{DATA_DIRECTORY}sensors.json'
JSON_CONFIG = f'{CONFIG_DIRECTORY}config_SOCHI.json'
JSON_CONFIG_PLOT = f'{CONFIG_DIRECTORY}config_plot_SOCHI.json'

FEATURES_PALETTE = ['#ff7f0e', '#d62728', '#9467bd', '#52a852', '#10E8E7']
MAIN_SIGNAL_COLOR = px.colors.qualitative.Plotly[0]

METHODS = ['potentials', 'LSTM']

PART_OF_DATA = 3472
