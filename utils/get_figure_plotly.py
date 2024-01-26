import plotly.express as px
import plotly.graph_objects as go
import utils.constants_and_paths as constants
from plotly.subplots import make_subplots

from loguru import logger


def get_home_fig(df_predict, group_intervals):
    logger.info(f"get_home_fig(df_predict, {group_intervals})")
    col_list = ['target_value']

    fig = px.line(
        df_predict,
        x=df_predict['timestamp'].tolist(),
        y=col_list,
        width=10,
        color_discrete_sequence=[constants.MAIN_SIGNAL_COLOR]
    )

    fig.layout.yaxis = {}
    fig.layout.xaxis = {}
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)'
    )

    fig.update_layout({"uirevision": "foo"}, overwrite=True)

    for interval in group_intervals:
        fig.add_vrect(x0=interval[0],
                      x1=interval[-1],
                      line_width=1, line_color="red", layer="below")
    return fig


def get_tab_fig(df_predict, TIMESTAMP, interval, group_intervals, left_space, right_space):
    logger.info(f"get_tab_fig(df_predict, TIMESTAMP, {interval}, group_intervals, {left_space}, {right_space})")
    col_list = ['target_value']

    # Переводим в индексы
    interval_index = [TIMESTAMP.index(interval[0]), TIMESTAMP.index(interval[-1]) + 1]  # нужен индекс с включением

    # Обрабатываем отступы из веб-приложения
    interval_len = interval_index[1] - interval_index[0]
    logger.info(interval_index)
    logger.info(interval_len)
    if (interval_len > left_space) and (interval_index[0] > left_space) and (interval_index[0] > interval_len):
        left_indentation = interval_len
    else:
        if interval_index[0] > left_space:
            left_indentation = left_space
        else:
            left_indentation = 0
    if (interval_len > right_space) and (interval_index[-1] < (len(TIMESTAMP) - right_space)) \
            and ((interval_index[-1] + interval_len) < len(TIMESTAMP)):
        right_indentation = interval_len
    else:
        if interval_index[-1] < (len(TIMESTAMP) - right_space):
            right_indentation = right_space
        else:
            right_indentation = 0

    # Учитываем выставленные отступы слева и справа для центрирования графика
    interval_index[0] -= left_indentation
    interval_index[-1] += right_indentation

    logger.info(left_indentation)
    logger.info(right_indentation)
    logger.info(interval_index)

    fig = px.line(
        df_predict.iloc[interval_index[0]:interval_index[-1]],
        x=df_predict['timestamp'].iloc[interval_index[0]:interval_index[-1]].to_list(),
        y=col_list,
        color_discrete_sequence=[constants.MAIN_SIGNAL_COLOR]
    )
    fig.layout.yaxis = {}
    fig.layout.xaxis = {}
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)'
    )
    fig.update_layout({"uirevision": "foo"}, overwrite=True)
    # Выделение красным прямоугольником
    if interval in group_intervals:
        fig.add_vrect(x0=interval[0],
                      x1=interval[-1],
                      line_width=1, line_color="red", layer="below")
    return fig


def get_sensors_fig(df_slices, TIMESTAMP,
                    top, interval, group_intervals,
                    left_space, right_space, PLOT_FEATURES, DICT_PLOT_PALETTE):
    logger.info(f"get_sensors_fig(df_slices, TIMESTAMP, "
                f"{top}, {interval}, group_intervals, {left_space}, {right_space}, PLOT_FEATURES)")
    legend_list = list(dict.fromkeys([top] + PLOT_FEATURES))
    # palette = px.colors.qualitative.Plotly
    palette_list = [constants.MAIN_SIGNAL_COLOR if legend == top
                    else DICT_PLOT_PALETTE[legend] for legend in legend_list]
    # palette_list = [constants.MAIN_SIGNAL_COLOR, '#FF9900', '#66AA00', '#750D86', '#006400', '#6C4516']

    # Переводим в индексы
    interval_index = [TIMESTAMP.index(interval[0]), TIMESTAMP.index(interval[-1]) + 1]  # нужен индекс с включением

    # Обрабатываем отступы из веб-приложения
    interval_len = interval_index[1] - interval_index[0]
    if (interval_len > left_space) and (interval_index[0] > left_space) and (interval_index[0] > interval_len):
        left_indentation = interval_len
    else:
        if interval_index[0] > left_space:
            left_indentation = left_space
        else:
            left_indentation = 0
    if (interval_len > right_space) and (interval_index[-1] < (len(TIMESTAMP) - right_space)) \
            and ((interval_index[-1] + interval_len) < len(TIMESTAMP)):
        right_indentation = interval_len
    else:
        if interval_index[-1] < (len(TIMESTAMP) - right_space):
            right_indentation = right_space
        else:
            right_indentation = 0

    # Учитываем выставленные отступы слева и справа для центрирования графика
    interval_index[0] -= left_indentation
    interval_index[-1] += right_indentation

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)'
    )

    fig.add_trace(go.Scatter(
        x=df_slices['timestamp'].iloc[interval_index[0]:interval_index[-1]].to_list(),
        y=df_slices[legend_list[0]].iloc[interval_index[0]:interval_index[-1]].to_list(),
        yaxis='y1', name="yaxis data", line={"color": palette_list[0], "width": 2}, showlegend=False
    ))

    fig.update_layout(
        yaxis=dict(
            title=legend_list[0],
            titlefont=dict(
                size=14,
                color=palette_list[0]
            ),
            tickfont=dict(
                size=14,
                color=palette_list[0]
            )
        )
    )

    for (index, feature) in enumerate(legend_list[1:]):
        fig.add_trace(go.Scatter(
            x=df_slices['timestamp'].iloc[interval_index[0]:interval_index[-1]].to_list(),
            y=df_slices[feature].iloc[interval_index[0]:interval_index[-1]].to_list(),
            name=f"yaxis{index+2} data", yaxis=f"y{index+2}", line={"width": 1.5, "color": palette_list[index+1]},
            showlegend=False
        ))
        if index <= 1:
            fig.layout[f"yaxis{index+2}"] = dict(
                title=feature,
                titlefont=dict(
                    size=14,
                    color=palette_list[index+1]
                ),
                tickfont=dict(
                    size=14,
                    color=palette_list[index+1]
                ),
                overlaying="y",
                side="right",
                anchor="free",
                autoshift=True,
                showline=True,
                showgrid=False,
                showticklabels=True,
                zeroline=False,
                ticks='outside',
                tickwidth=0.5,
                tickcolor=palette_list[index+1],
                title_standoff=10
            )
        else:
            fig.layout[f"yaxis{index+2}"] = dict(
                title=feature,
                titlefont=dict(
                    size=14,
                    color=palette_list[index+1]
                ),
                tickfont=dict(
                    size=14,
                    color=palette_list[index+1]
                ),
                overlaying="y",
                side="left",
                autoshift=True,
                anchor="free",
                showline=True,
                showgrid=False,
                showticklabels=True,
                zeroline=False,
                ticks='outside',
                tickwidth=0.5,
                tickcolor=palette_list[index+1],
                title_standoff=10,
                layer="below traces"
            )
    # Выделение красным прямоугольником
    if interval in group_intervals:
        fig.add_vrect(x0=interval[0], x1=interval[1], line_width=2, line_color="red", layer="below")

    fig.update_layout({"uirevision": "foo"}, overwrite=True)
    return fig, legend_list, palette_list


def get_sensors_tab_fig(df_slices, TIMESTAMP,
                        selected_sensors, interval, group_intervals,
                        left_space, right_space, PLOT_FEATURES, DICT_PLOT_PALETTE):
    logger.info(f"get_sensors_tab_fig(df_slices, TIMESTAMP, "
                f"{selected_sensors}, {interval}, group_intervals, {left_space}, {right_space}")

    sensors = [sensor.split()[2] for sensor in selected_sensors]
    legend_list = list(dict.fromkeys(sensors))
    palette_list = [constants.MAIN_SIGNAL_COLOR if legend == legend_list[0]
                    else DICT_PLOT_PALETTE[legend] for legend in legend_list]
    # palette = px.colors.qualitative.Plotly
    # palette_list = [palette[0], '#FF9900', '#66AA00', '#750D86', '#006400', '#6C4516']

    # zip для соответствия цветов паллеты с сигналами
    legend_palette_zip = list(zip(legend_list, palette_list))

    # Переводим в индексы
    interval_index = [TIMESTAMP.index(interval[0]), TIMESTAMP.index(interval[-1]) + 1]  # нужен индекс с включением

    # Обрабатываем отступы из веб-приложения
    interval_len = interval_index[1] - interval_index[0]
    if (interval_len > left_space) and (interval_index[0] > left_space) and (interval_index[0] > interval_len):
        left_indentation = interval_len
    else:
        if interval_index[0] > left_space:
            left_indentation = left_space
        else:
            left_indentation = 0
    if (interval_len > right_space) and (interval_index[-1] < (len(TIMESTAMP) - right_space))\
            and ((interval_index[-1] + interval_len) < len(TIMESTAMP)):
        right_indentation = interval_len
    else:
        if interval_index[-1] < (len(TIMESTAMP) - right_space):
            right_indentation = right_space
        else:
            right_indentation = 0

    # Учитываем выставленные отступы слева и справа для центрирования графика
    interval_index[0] -= left_indentation
    interval_index[-1] += right_indentation

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)'
    )

    fig.add_trace(go.Scatter(
        x=df_slices['timestamp'].iloc[interval_index[0]:interval_index[-1]].to_list(),
        y=df_slices[legend_list[0]].iloc[interval_index[0]:interval_index[-1]].to_list(),
        yaxis='y1', name="yaxis data", line={"color": palette_list[0], "width": 2}, showlegend=False
    ))

    fig.update_layout(
        yaxis=dict(
            title=legend_list[0],
            titlefont=dict(
                size=14,
                color=palette_list[0]
            ),
            tickfont=dict(
                size=14,
                color=palette_list[0]
            )
        )
    )

    for index, (feature, palette_color) in enumerate(legend_palette_zip[1:]):
        fig.add_trace(go.Scatter(
            x=df_slices['timestamp'].iloc[interval_index[0]:interval_index[-1]].to_list(),
            y=df_slices[feature].iloc[interval_index[0]:interval_index[-1]].to_list(),
            name=f"yaxis{index + 2} data", yaxis=f"y{index + 2}", line={"width": 1.5, "color": palette_color},
            showlegend=False
        ))
        if (index == 0) or (index == 1):
            fig.layout[f"yaxis{index + 2}"] = dict(
                title=feature,
                titlefont=dict(
                    size=14,
                    color=palette_color
                ),
                tickfont=dict(
                    size=14,
                    color=palette_color
                ),
                overlaying="y",
                side="right",
                anchor="free",
                autoshift=True,
                showline=True,
                showgrid=False,
                showticklabels=True,
                zeroline=False,
                ticks='outside',
                tickwidth=0.5,
                tickcolor=palette_color,
                title_standoff=10
            )
        else:
            fig.layout[f"yaxis{index + 2}"] = dict(
                title=feature,
                titlefont=dict(
                    size=14,
                    color=palette_color
                ),
                tickfont=dict(
                    size=14,
                    color=palette_color
                ),
                overlaying="y",
                side="left",
                autoshift=True,
                anchor="free",
                showline=True,
                showgrid=False,
                showticklabels=True,
                zeroline=False,
                ticks='outside',
                tickwidth=0.5,
                tickcolor=palette_color,
                title_standoff=10,
                layer="below traces"
            )
    # Выделение красным прямоугольником
    if interval in group_intervals:
        fig.add_vrect(x0=interval[0], x1=interval[1], line_width=2, line_color="red", layer="below")

    fig.update_layout({"uirevision": "foo"}, overwrite=True)
    return fig, legend_palette_zip
