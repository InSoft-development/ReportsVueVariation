import os
import platform
import argparse
import sys

import eel
import shutil

import pandas as pd
import numpy as np
from scipy.stats import rv_histogram

import json
from loguru import logger
import datetime
from dateutil import parser as pars

from utils.correct_start import check_correct_application_structure, get_jsons, get_name_of_kks
from utils.computation import mean_index, rolling_probability, get_anomaly_interval
import utils.constants_and_paths as constants
import utils.create_reports as reports
import utils.parser as pt
import jinja.pylib.getters_signal as gs
import jinja.pylib.getters_line as gl
import jinja.pylib.get_template as gt

VERSION = '1.0.0'

TIMESTAMP = []

# Use latest version of Eel from parent directory
sys.path.insert(1, '../../')


@eel.expose
def get_interval_time_array(method, group):
    """
    Функция возвращает массив найденных методом интервалов и добавленных интервалов для выбранного метода и группы
    :param method: наименование метода
    :param group: номер группы
    :return: merged_intervals_time_array: массив найденных аномальных интервалов для передачи в JS
    """
    logger.info(f"get_interval_time_array({method}, {group})")
    # Аномальные интервалы, найденные в группе методом
    intervals_json_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}json_interval{os.sep}group_{group}.json'
    # Вручную добавленные пользователем интервалы
    added_intervals_json_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}' \
                                f'json_interval{os.sep}added_intervals_{group}.json'

    with open(intervals_json_path, 'r', encoding='utf8') as f:
        intervals_json = json.load(f)

    try:
        with open(added_intervals_json_path, 'r', encoding='utf8') as f:
            added_intervals_json = json.load(f)
        # Сливаем два массива json объектов в один
        merged_intervals_time_json = intervals_json + added_intervals_json
    except FileNotFoundError as e:
        logger.info(f'{added_intervals_json_path} has been created')
        with open(added_intervals_json_path, "w+") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        merged_intervals_time_json = intervals_json

    # Сортируем интервалы по временной отметки начала аномального интервала в json файле
    # если начала совпадают, то сортируем по концу интервалов
    merged_intervals_time_json = sorted(merged_intervals_time_json, key=lambda x: (x['time'][0], x['time'][-1]),
                                        reverse=False)
    merged_intervals_time_array = [interval['time'] for interval in merged_intervals_time_json]
    return merged_intervals_time_array


@eel.expose
def get_group_interval_time_array(method, group):
    """
    Функция возвращает массив найденных методом интервалов для выбранного метода и группы
    :param method: наименование метода
    :param group: номер группы
    :return: group_intervals_json_time_array: массив найденных методом аномальных интервалов для передачи в JS
    """
    logger.info(f"get_group_interval_time_array({method}, {group})")
    # Аномальные интервалы, найденные в группе методом
    intervals_json_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}json_interval{os.sep}group_{group}.json'

    with open(intervals_json_path, 'r', encoding='utf8') as f:
        group_intervals_json = json.load(f)

    # Сортируем интервалы по временной отметки начала аномального интервала в json файле
    # если начала совпадают, то сортируем по концу интервалов
    group_intervals_json = sorted(group_intervals_json, key=lambda x: (x['time'][0], x['time'][-1]),
                                  reverse=False)
    group_intervals_json_time_array = [interval['time'] for interval in group_intervals_json]
    return group_intervals_json_time_array


@eel.expose
def get_added_interval_time_array(method, group, in_format_date=False):
    """
    Функция возвращает массив добавленных пользователем интервалов для выбранного метода и группы
    :param method: наименование метода
    :param group: номер группы
    :param in_format_date: выдать возвращаемое значение функции в виде массива для парсинга даты в JS
    :return: added_intervals_json_time_array: массив добавленных пользователем интервалов для передачи в JS
    """
    logger.info(f"get_added_interval_time_array({method}, {group}, {in_format_date})")
    # Вручную добавленные пользователем интервалы
    added_intervals_json_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}' \
                                f'json_interval{os.sep}added_intervals_{group}.json'

    with open(added_intervals_json_path, 'r', encoding='utf8') as f:
        added_intervals_json = json.load(f)

    # Сортируем интервалы по временной отметки начала аномального интервала в json файле
    # если начала совпадают, то сортируем по концу интервалов
    added_intervals_json = sorted(added_intervals_json, key=lambda x: (x['time'][0], x['time'][-1]),
                                  reverse=False)
    if in_format_date:
        added_intervals_json_time_array = [interval['time'] for interval in added_intervals_json]
    else:
        added_intervals_json_time_array = [[str(datetime.datetime.strptime(element, "%Y-%m-%d %H:%M:%S").strftime(
            "%Y-%m-%dT%H:%M:%S")) for element in interval['time']] for interval in added_intervals_json]

    return added_intervals_json_time_array


@eel.expose
def get_predict_values(method, group, interval=None, left_space=None, right_space=None):
    """
    Функция возвращает массивы временных отметок и значений целевой переменной
    для построения графика целевой переменной на выбранном интервале (по умолчанию всем временном периоде)
    и для выбранного метода
    :param method: наименование метода
    :param group: номер группы
    :param interval: массив интервала в формате: [{начало_интервала}, {конец_интервала}]. Аргумент по умолчанию
    для отрисовки графика на всем временном интервале
    :param left_space: настроенный в веб-приложении отступ в 5-ти минутках слева
    :param right_space: настроенный в веб-приложении отступ в 5-ти минутках справа
    :return: interval_timestamp_array: массив временных отметок
             interval_target_array: массив целевой переменной
    """
    logger.info(f"get_predict_values({method}, {group}, {interval}, {left_space}, {right_space})")
    # Обрабатываем если получены аргументы по умолчанию
    if interval is None:
        interval = [TIMESTAMP[0], TIMESTAMP[-1]]

    # Переводим в индексы
    interval[0] = TIMESTAMP.index(interval[0])
    interval[1] = TIMESTAMP.index(interval[-1]) + 1  # нужен индекс с включением

    # Обрабатываем если получены отступы из веб-приложения
    if (left_space is not None) and (right_space is not None):
        interval_len = interval[1] - interval[0]
        if (interval_len > left_space) and (interval[0] > left_space) and (interval[0] > interval_len):
            left_indentation = interval_len
        else:
            if interval[0] > left_space:
                left_indentation = left_space
            else:
                left_indentation = 0
        if (interval_len > right_space) and (interval[-1] < (len(TIMESTAMP) - right_space))\
                and ((interval[-1] + interval_len) < len(TIMESTAMP)):
            right_indentation = interval_len
        else:
            if interval[-1] < (len(TIMESTAMP) - right_space):
                right_indentation = right_space
            else:
                right_indentation = 0

        # Учитываем выставленные отступы слева и справа для центрирования графика
        interval[0] -= left_indentation
        interval[-1] += right_indentation

    df_rolled_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}csv_rolled{os.sep}rolled_{group}.csv'
    df_rolled = pd.read_csv(df_rolled_path)
    df_rolled.fillna(value={"target_value": 0}, inplace=True)

    # Формируем массивы временных отметок и целевой переменной
    interval_timestamp_array = df_rolled['timestamp'].iloc[interval[0]:interval[-1]].tolist()
    interval_target_array = df_rolled['target_value'].iloc[interval[0]:interval[-1]].tolist()

    start_part = 0
    end_part = 0
    while start_part < len(interval_timestamp_array):
        if (end_part + constants.PART_OF_DATA // 2) >= len(interval_timestamp_array):
            end_part += len(interval_timestamp_array) % (constants.PART_OF_DATA // 2)
        else:
            end_part += constants.PART_OF_DATA // 2
        eel.getPartOfDataInterval(interval_timestamp_array[start_part:end_part],
                                  interval_target_array[start_part:end_part])
        start_part += constants.PART_OF_DATA // 2
    return "success"

    # return interval_timestamp_array, interval_target_array


@eel.expose
def get_min_time_value():
    """
    Функция возвращает начальную временную отметку в срезе данных
    :return: TIMESTAMP[0]: начальная временная отметка
    """
    logger.info("get_min_time_value")
    return str(datetime.datetime.strptime(TIMESTAMP[0], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S"))


@eel.expose
def get_max_time_value():
    """
    Функция возвращает конечную временную отметку в срезе данных
    :return: TIMESTAMP[-1]: конечная временная отметка
    """
    logger.info("get_max_time_value")
    return str(datetime.datetime.strptime(TIMESTAMP[-1], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S"))


@eel.expose
def get_groups_count():
    """
    Функция возвращает количество групп оборудования
    :return: len(index_group): количество групп
    """
    logger.info("get_groups_count")
    return len(index_group)


@eel.expose
def get_groups_name_array():
    """
    Функция возвращает наименования групп оборудования
    :return: names_of_group: массив наименований групп, элемент это строка в формате: {номер_группы} (название_группы)
    """
    logger.info("get_groups_name_array")
    return NAMES_OF_GROUPS


@eel.expose
def get_plot_features():
    """
    Функция возвращает полное наименования датчиков PLOT_FEATURES из конфига графиков
    :return:
    """
    logger.info("get_plot_features")
    added_text = 'Дополнительный сигнал: '
    plot_features_name = [f'{added_text}{feature} ({DICT_KKS[feature]})' for feature in PLOT_FEATURES]
    return plot_features_name


@eel.expose
def add_new_interval(method, group, date_string_begin_from_js, date_string_end_from_js, update=None, id_interval=None):
    """
    Функция сохраняет добавляемый пользователем интервал (период) в JSON файл
    :param method: наименование метода
    :param group: номер группы
    :param date_string_begin_from_js: дата начала периода в формате строки, присланная из JS
    :param date_string_end_from_js: дата конца периода в формате строки, присланная из JS
    :param update: флаг обновления периода (по умолчанию  None)
    :param id_interval: номер обновляемого интервала в JSON - файле
    :return: строка сообщения со статусом завершения операции
    """
    logger.info(f"add_new_interval({method}, {group}, {date_string_begin_from_js}, {date_string_end_from_js}, "
                f"{update}, {id_interval})")
    # перевод строк дат в формат "%Y-%m-%d %H:%M:%S" Tue Jun 01 2021 00:04:00 GMT+0300 (Москва, стандартное время)
    date_begin = datetime.datetime.strptime(date_string_begin_from_js,
                                            "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")
    date_end = datetime.datetime.strptime(date_string_end_from_js,
                                          "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")

    # проверяем даты на корректность заполнения и нахождение их в датафрейме
    if date_end < date_begin:
        msg = f"{date_end} < {date_begin}\nКонец периода должен быть после начала периода"
        logger.info(msg)
        return msg

    if date_end == date_begin:
        msg = f"{date_end} = {date_begin}\nКонец периода не должен совпадать с началом периода"
        logger.info(msg)
        return msg

    msg = ""
    if date_begin not in TIMESTAMP:
        msg += f"Временная отметка начала периода {date_begin} не найдена в файле срезов.\n"
        timestamp_begin = pars.parse(date_begin).timestamp()
        date_begin = pars.parse(min(TIMESTAMP, key=lambda x: abs(pars.parse(x).timestamp() - timestamp_begin)))
        date_begin = datetime.datetime.strftime(date_begin, "%Y-%m-%d %H:%M:%S")

        msg += f"Временная отметка была округлена до {date_begin}.\n"
        logger.info(msg)
        # return msg

    if date_end not in TIMESTAMP:
        msg += f"Временная отметка конца периода {date_end} не найдена в файле срезов.\n"
        timestamp_end = pars.parse(date_end).timestamp()
        date_end = pars.parse(min(TIMESTAMP, key=lambda x: abs(pars.parse(x).timestamp() - timestamp_end)))
        date_end = datetime.datetime.strftime(date_end, "%Y-%m-%d %H:%M:%S")

        msg += f"Временная отметка была округлена до {date_end}.\n"
        logger.info(msg)
        # return msg

    # Считываем добавленные пользователем интервалы для проверки вхождения
    added_intervals_json_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}' \
                                f'json_interval{os.sep}added_intervals_{group}.json'

    with open(added_intervals_json_path, 'r', encoding='utf8') as f:
        added_intervals_json = json.load(f)

    # Считываем аномальные интервалы, найденные в группе методом
    intervals_json_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}json_interval{os.sep}group_{group}.json'

    with open(intervals_json_path, 'r', encoding='utf8') as f:
        group_intervals_json = json.load(f)

    # Считываем фрейм с loss
    df_loss_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}csv_loss{os.sep}loss_{group}.csv'
    df_loss = pd.read_csv(df_loss_path)

    # Считываем все датчики группы
    union_sensors = json_dict['groups'][group][str(group)]['unions']
    single_sensors = json_dict['groups'][group][str(group)]['single sensors']

    if union_sensors == "null":
        group_sensors = single_sensors
    elif single_sensors == "null":
        group_sensors = union_sensors
    else:
        group_sensors = union_sensors + single_sensors

    # Считаем датчики, внесшие наибольший вклад на интервале
    top = mean_index(df_loss.iloc[TIMESTAMP.index(date_begin):TIMESTAMP.index(date_end) + 1], group_sensors, DROP_LIST)

    # Формируем объект JSON
    dictionary = {
        "time": [date_begin, date_end],
        "len": TIMESTAMP.index(date_end) - TIMESTAMP.index(date_begin),
        "index": [TIMESTAMP.index(date_begin), TIMESTAMP.index(date_end)],
        "top_sensors": top
    }

    if dictionary in added_intervals_json:
        logger.info(f'{dictionary} already has in added intervals')
        msg += "Интервал уже был добавлен раньше пользователем"
        logger.info(msg)
        return msg
    elif dictionary in group_intervals_json:
        logger.info(f'{dictionary} already has in group intervals')
        msg += "Интервал уже выделен методом"
        logger.info(msg)
        return msg
    else:
        if (update is not None) and (id_interval is not None):
            logger.info(added_intervals_json)
            added_intervals_json[id_interval] = dictionary
            msg += "Интервал успешно обновлен"
        else:
            added_intervals_json.append(dictionary)
            msg += "Интервал успешно добавлен"
        # Сортируем интервалы по временной отметки начала аномального интервала в json файле
        # если начала совпадают, то сортируем по концу интервалов
        added_intervals_json = sorted(added_intervals_json, key=lambda x: (x['time'][0], x['time'][-1]),
                                      reverse=False)

        with open(added_intervals_json_path, 'w', encoding='utf8') as f:
            json.dump(added_intervals_json, f, ensure_ascii=False, indent=4)

        logger.info(f'{added_intervals_json} has been saved')
        logger.info(msg)
        return msg


@eel.expose
def remove_interval(method, group, id_interval):
    """
    Функция удаляет требуемый интервал по его порядковому номеру в массиве интервалов и возвращает статус
    выполнения операции в виде строки
    :param method: наименование метода
    :param group: номер группы
    :param id_interval: порядковый номер интервала в массиве интервала (id)
    :return: строка: { "Интервал удален", "Exception" }:
                     Интервал удален - интервал успешно удален из JSON файла
                     Exception - исключение при провале операции
    """
    logger.info(f"remove_interval({method}, {group}, {id_interval})")

    # Считываем добавленные пользователем интервалы для проверки вхождения
    added_intervals_json_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}' \
                                f'json_interval{os.sep}added_intervals_{group}.json'

    try:
        with open(added_intervals_json_path, 'r', encoding='utf8') as f:
            added_intervals_json = json.load(f)

        added_intervals_json.remove(added_intervals_json[id_interval])

        with open(added_intervals_json_path, 'w', encoding='utf8') as f:
            json.dump(added_intervals_json, f, ensure_ascii=False, indent=4)

        logger.info(f'interval with id={id_interval} has been removed from {added_intervals_json_path}')
        return "Интервал удален"
    except Exception as e:
        logger.info(e)
        return f"Exception: {e}"


@eel.expose
def get_top_and_other_interval_sensors(method, group, id_interval):
    """
    Функция возвращает массивы kks и наименований датчиков, внесших максимальный вклад и остальных сигналов группы
    :param method: наименование метода
    :param group: номер группы
    :param id_interval: порядковый номер интервала в массиве интервала (id)
    :return: top_sensors: массив kks топовых датчиков
             top_sensors_name: массив наименований топовых датчиков
             other_group_sensors: массив kks остальных датчиков группы
             other_group_sensors_name: массив наименований остальных датчиков группы
    """
    logger.info(f"get_top_interval_sensors({method}, {group}, {id_interval})")
    # Аномальные интервалы, найденные в группе методом
    intervals_json_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}json_interval{os.sep}group_{group}.json'
    # Вручную добавленные пользователем интервалы
    added_intervals_json_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}' \
                                f'json_interval{os.sep}added_intervals_{group}.json'

    with open(intervals_json_path, 'r', encoding='utf8') as f:
        intervals_json = json.load(f)

    with open(added_intervals_json_path, 'r', encoding='utf8') as f:
        added_intervals_json = json.load(f)
    # Сливаем два массива json объектов в один
    merged_intervals_time_json = intervals_json + added_intervals_json

    # Сортируем интервалы по временной отметки начала аномального интервала в json файле
    # если начала совпадают, то сортируем по концу интервалов
    merged_intervals_time_json = sorted(merged_intervals_time_json, key=lambda x: (x['time'][0], x['time'][-1]),
                                        reverse=False)

    # достаем топовые датчики и их наименования: датчики не должны находиться в списке
    top_sensors = [top for top in merged_intervals_time_json[int(id_interval)]['top_sensors']
                   if (top not in DROP_LIST)]
    top_sensors_name = [top + " (" + DICT_KKS[top] + ")" for top in top_sensors if (top not in DROP_LIST)]

    # считываем все датчики группы, а потом достаем остальные датчики выбранной группы
    union_sensors = json_dict['groups'][group][str(group)]['unions']
    single_sensors = json_dict['groups'][group][str(group)]['single sensors']

    if union_sensors == "null":
        group_sensors = single_sensors
    elif single_sensors == "null":
        group_sensors = union_sensors
    else:
        group_sensors = union_sensors + single_sensors

    other_group_sensors = [sensor for sensor in group_sensors if (sensor not in top_sensors) and
                           (sensor not in PLOT_FEATURES) and
                           (sensor not in DROP_LIST)]
    other_group_sensors_name = [sensor + " (" + DICT_KKS[sensor] + ")" for sensor in other_group_sensors]

    return top_sensors, top_sensors_name, other_group_sensors, other_group_sensors_name


@eel.expose
def get_multi_axis_sensors(selectedSignal):
    """
    Функция возвращает массивы наименований датчиков и kks датчиков для чекбоксов многоосевого графика
    :param selectedSignal: наименований выбранного основного сигнала
    :return: multi_axis_sensors: массив наименований датчиков
             kks_of_multi_axis_signal: массив kks датчиков
    """
    logger.info(f"get_multi_axis_sensors({selectedSignal})")
    kks_of_selected_signal = selectedSignal.split()[0]
    main_axis_sensors = [f"Основной сигнал: {selectedSignal}"]
    feature_axis_sensors = [f"Дополнительный сигнал: {feature} ({DICT_KKS[feature]})" for feature in PLOT_FEATURES
                            if feature != kks_of_selected_signal]
    kks_of_feature_signal = [feature for feature in PLOT_FEATURES if feature != kks_of_selected_signal]

    multi_axis_sensors = main_axis_sensors + feature_axis_sensors
    kks_of_multi_axis_signal = [kks_of_selected_signal] + kks_of_feature_signal
    return multi_axis_sensors, kks_of_multi_axis_signal


# @eel.expose
# def get_multi_axis_values(multi_axis_sensors, interval, left_space, right_space):
#     """
#     Функция возвращает массив с временными отметакми и значениями датчиков для многоосевого графика
#     :param multi_axis_sensors: выбранные датчики многоосевого графика
#     :param interval: массив интервала в формате: [{начало_интервала}, {конец_интервала}]
#     :param left_space: настроенный в веб-приложении отступ в 5-ти минутках слева
#     :param right_space: настроенный в веб-приложении отступ в 5-ти минутках справа
#     :return: multi_axis_data: массив данных для многоосевого графика
#     в формате: [{массив_временных_отметок}, {массив_значений_датчиков[{массив_значений_датчика}]}]
#     """
#     logger.info(f"get_multi_axis_values({multi_axis_sensors}, {interval}, {left_space}, {right_space})")
#     # Переводим в индексы
#     interval[0] = TIMESTAMP.index(interval[0])
#     interval[1] = TIMESTAMP.index(interval[-1]) + 1  # нужен индекс с включением
#
#     # Обрабатываем если получены отступы из веб-приложения
#     if interval[0] > left_space:
#         left_indentation = left_space
#     else:
#         left_indentation = 0
#     if interval[-1] < (len(TIMESTAMP) - right_space):
#         right_indentation = right_space
#     else:
#         right_indentation = 0
#
#     # Учитываем выставленные отступы слева и справа для центрирования графика
#     interval[0] -= left_indentation
#     interval[-1] += right_indentation
#
#     multi_axis_data = []
#
#     sensors_kks = [sensor_name.split()[2] for sensor_name in multi_axis_sensors]
#
#     # Формируем массивы временных отметок и значений датчиков на интервале
#     interval_timestamp_array = df_slices['timestamp'].iloc[interval[0]:interval[-1]].tolist()
#     multi_axis_data.append(interval_timestamp_array)
#
#     interval_slice_array = []
#     for sensor in sensors_kks:
#         interval_slice_array.append(df_slices[sensor].iloc[interval[0]:interval[-1]].tolist())
#     multi_axis_data.append(interval_slice_array)
#
#     start_part = 0
#     end_part = 0
#     while start_part < len(interval_timestamp_array):
#         if (end_part + constants.PART_OF_DATA // 2) >= len(interval_timestamp_array):
#             end_part += len(interval_timestamp_array) % (constants.PART_OF_DATA // 2)
#         else:
#             end_part += constants.PART_OF_DATA // 2
#         # logger.info(interval_timestamp_array[start_part:end_part])
#         # logger.info([i[start_part:end_part] for i in interval_slice_array])
#         # send_data = [[j for j in i[start_part:end_part]] for i in interval_slice_array]
#         # eel.getPartOfMultiAxisData(interval_timestamp_array[start_part:end_part], send_data)
#         eel.getPartTimeOfMultiAxisData(interval_timestamp_array[start_part:end_part])
#         start_part += constants.PART_OF_DATA // 2
#
#     for index, sensor in enumerate(sensors_kks):
#         logger.info(index)
#         logger.info(sensor)
#         start_part = 0
#         end_part = 0
#         while start_part < len(interval_timestamp_array):
#             if (end_part + constants.PART_OF_DATA // 2) >= len(interval_timestamp_array):
#                 end_part += len(interval_timestamp_array) % (constants.PART_OF_DATA // 2)
#             else:
#                 end_part += constants.PART_OF_DATA // 2
#             eel.getPartDataOfMultiAxisData(interval_slice_array[index][start_part:end_part])
#             start_part += constants.PART_OF_DATA // 2
#         eel.mergePartDataOfMultiAxisData()
#
#     eel.finishMultiAxisData()
#     return "success"
#     # return multi_axis_data


@eel.expose
def get_consant_part_of_data():
    """
    Функция возвращает константу размера одной части данных
    :return: константа размера части данных
    """
    return constants.PART_OF_DATA


@eel.expose
def get_length_time_and_indentation(interval=None, left_space=None, right_space=None):
    """
    Функция возвращает количество временных отметок на интервале с учетом отступов справа и слева,
    а также скорректированный интервал
    :param interval: массив интервала в формате: [{начало_интервала}, {конец_интервала}]
    :param left_space: настроенный в веб-приложении отступ в 5-ти минутках слева
    :param right_space: настроенный в веб-приложении отступ в 5-ти минутках справа
    :return: len(interval_timestamp_array): количество временных отметок на интервале с учетом отступов справа и слева
             interval: скорректированный интервал с учетом отступов
    """
    logger.info(f"get_length_time_and_data({interval}, {left_space}, {right_space})")
    if (interval is None):
        interval = [TIMESTAMP[0], TIMESTAMP[-1]]
    # Переводим в индексы
    interval[0] = TIMESTAMP.index(interval[0])
    interval[1] = TIMESTAMP.index(interval[-1]) + 1  # нужен индекс с включением

    # Обрабатываем если получены отступы из веб-приложения
    if (left_space is not None) and (right_space is not None):
        interval_len = interval[1] - interval[0]
        if (interval_len > left_space) and (interval[0] > left_space) and (interval[0] > interval_len):
            left_indentation = interval_len
        else:
            if interval[0] > left_space:
                left_indentation = left_space
            else:
                left_indentation = 0
        if (interval_len > right_space) and (interval[-1] < (len(TIMESTAMP) - right_space))\
                and ((interval[-1] + interval_len) < len(TIMESTAMP)):
            right_indentation = interval_len
        else:
            if interval[-1] < (len(TIMESTAMP) - right_space):
                right_indentation = right_space
            else:
                right_indentation = 0
        # Учитываем выставленные отступы слева и справа для центрирования графика
        interval[0] -= left_indentation
        interval[-1] += right_indentation

    interval_timestamp_array = df_slices['timestamp'].iloc[interval[0]:interval[-1]].tolist()
    return len(interval_timestamp_array), interval


@eel.expose
def get_time_chunk(interval, left_index, right_index):
    """
    Функция возвращает массив временных отметок на части интервала
    :param interval: скорректированный интервал с учетом отступов
    :param left_index: индекс начала передаваемой части данных
    :param right_index: индекс конца передаваемой части данных
    :return: массив временных отметок на части интервала
    """
    logger.info(f"get_multi_axis_sensor_values_chunk({interval}, {left_index}, {right_index})")
    # Формируем массив временных отметок на части интервала
    interval_timestamp_array = df_slices['timestamp'].iloc[interval[0]:interval[-1]].tolist()
    return interval_timestamp_array[left_index: right_index]


@eel.expose
def get_values_chunk(method, group, interval, left_index, right_index):
    logger.info(f"get_values_chunk({method}, {group}, {interval}, {left_index}, {right_index})")

    df_rolled_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}csv_rolled{os.sep}rolled_{group}.csv'
    df_rolled = pd.read_csv(df_rolled_path)
    df_rolled.fillna(value={"target_value": 0}, inplace=True)

    # Формируем массив значений целевой переменной на части интервала
    interval_target_array = df_rolled['target_value'].iloc[interval[0]:interval[-1]].tolist()
    return interval_target_array[left_index: right_index]


@eel.expose
def get_multi_axis_sensor_values_chunk(multi_axis_sensor, interval, left_index, right_index):
    """
    Функция возвращает массив значений датчика на части интервала
    :param multi_axis_sensor: датчики многоосевого графика
    :param interval: скорректированный интервал с учетом отступов
    :param left_index: индекс начала передаваемой части данных
    :param right_index: индекс конца передаваемой части данных
    :return: массив значений датчика на части интервала
    """
    logger.info(f"get_multi_axis_sensor_values_chunk({multi_axis_sensor}, {interval}, {left_index}, {right_index})")
    sensor_kks = multi_axis_sensor.split()[2]
    # Формируем массив значений датчика на части интервала
    multi_axis_sensor_values_chunk = df_slices[sensor_kks].iloc[interval[0]:interval[-1]].tolist()
    return multi_axis_sensor_values_chunk[left_index: right_index]


@eel.expose
def get_hist_data(group):
    """
    Функция возвращает исходные данные для построения гистрограммы
    :param group: номер группы
    :return: d.tolist(): массив распределения вероятности
             probabilities.tolist(): массив значений вероятности
             potentials.tolist(): массив значений потенциала
             ind: индекс предельного значения вероятности
    """
    logger.info(f"get_hist_data({group})")

    # используем фрейм потенциалов выбранной группы
    # df_predict.fillna(value={"target_value": 0, "potential": 1.0}, inplace=True)

    df_predict_path = f'{constants.DATA_DIRECTORY}potentials{os.sep}csv_predict{os.sep}predict_{group}.csv'
    df_predict = pd.read_csv(df_predict_path)
    df_predict.fillna(value={"target_value": 0}, inplace=True)

    data_train = df_predict.iloc[1:len(df_predict):100, :]
    hist = np.histogram(data_train['potential'].values, bins=100)
    dist = rv_histogram(hist)
    d = np.arange(min(data_train['potential']), max(data_train['potential']), 0.001)
    potentials = 100 * dist.pdf(d)
    probabilities = 100 * (1 - dist.cdf(d))

    df = pd.DataFrame(data={'potential': d, 'probability': probabilities}, index=None)
    temp = df.index[(df['probability'] < config['model']['P_pr'] * 100 + 1)].tolist()
    ind = temp[0]

    return d.tolist(), probabilities.tolist(), potentials.tolist(), ind


@eel.expose
def create_report(method, group, orientation, left_space, right_space):
    """
    Функция возвращает статус построения отчета по всем периодам
    :param method: наименование метода
    :param group: номер группы
    :param orientation: выбранная ориентация страниц отчета
    :param left_space: настроенный в веб-приложении отступ в 5-ти минутках слева
    :param right_space: настроенный в веб-приложении отступ в 5-ти минутках справа
    :return: строка статуса построения отчета по всем периодам
    """
    logger.info(f"create_report({method}, {group})")

    # Аномальные интервалы, найденные в группе методом
    intervals_json_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}json_interval{os.sep}group_{group}.json'
    # Вручную добавленные пользователем интервалы
    added_intervals_json_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}' \
                                f'json_interval{os.sep}added_intervals_{group}.json'

    with open(intervals_json_path, 'r', encoding='utf8') as f:
        intervals_json = json.load(f)

    with open(added_intervals_json_path, 'r', encoding='utf8') as f:
        added_intervals_json = json.load(f)
    # Сливаем два массива json объектов в один
    merged_intervals_time_json = intervals_json + added_intervals_json

    # Сортируем интервалы по временной отметки начала аномального интервала в json файле
    # если начала совпадают, то сортируем по концу интервалов
    merged_intervals_time_json = sorted(merged_intervals_time_json, key=lambda x: (x['time'][0], x['time'][-1]),
                                        reverse=False)

    group_intervals = [interval['time'] for interval in intervals_json]
    intervals = [interval['time'] for interval in merged_intervals_time_json]
    top_sensors = [interval['top_sensors'] for interval in merged_intervals_time_json]

    df_rolled_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}csv_rolled{os.sep}rolled_{group}.csv'
    df_rolled = pd.read_csv(df_rolled_path)
    df_rolled.fillna(value={"target_value": 0}, inplace=True)

    DICT_PLOT_PALETTE = dict(zip(PLOT_FEATURES, constants.FEATURES_PALETTE))

    reports.check_correct_report_structure(method, group, intervals)
    msg = reports.create_common_report(method, group, orientation, intervals, group_intervals,
                                       top_sensors, df_rolled, df_slices, TIMESTAMP, left_space, right_space,
                                       NAMES_OF_GROUPS, DICT_KKS, PLOT_FEATURES, DICT_PLOT_PALETTE, DROP_LIST)
    return msg


@eel.expose
def create_tab_report(method, group, interval, orientation,
                      selected_top_list, selected_other_list, dict_selected_checkbox,
                      left_space, right_space):
    """
    Функция возвращает статус построения отчета по периоду
    :param method: наименование метода
    :param group: номер группы
    :param interval: массив интервала в формате: [{начало_интервала}, {конец_интервала}]
    :param orientation: выбранная ориентация страниц отчета
    :param selected_top_list: выбранные датчики, внесшие максимальный вклад
    :param selected_other_list: выбранные остальные датчики группы
    :param dict_selected_checkbox: словарь выбранных датчиков и их выбранных чекбоксов сигналов многоосевого графика
    :param left_space: настроенный в веб-приложении отступ в 5-ти минутках слева
    :param right_space: настроенный в веб-приложении отступ в 5-ти минутках справа
    :return: строка статуса построения отчета по периоду
    """
    logger.info(f"create_tab_report({method}, {group}, {interval}, {orientation},"
                f" {selected_top_list}, {selected_other_list}, {dict_selected_checkbox}, {left_space}, {right_space})")

    # Аномальные интервалы, найденные в группе методом
    intervals_json_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}json_interval{os.sep}group_{group}.json'

    with open(intervals_json_path, 'r', encoding='utf8') as f:
        group_intervals_json = json.load(f)

    # Сортируем интервалы по временной отметки начала аномального интервала в json файле
    # если начала совпадают, то сортируем по концу интервалов
    group_intervals_json = sorted(group_intervals_json, key=lambda x: (x['time'][0], x['time'][-1]),
                                  reverse=False)

    group_intervals = [group_interval['time'] for group_interval in group_intervals_json]

    df_rolled_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}csv_rolled{os.sep}rolled_{group}.csv'
    df_rolled = pd.read_csv(df_rolled_path)
    df_rolled.fillna(value={"target_value": 0}, inplace=True)

    DICT_PLOT_PALETTE = dict(zip(PLOT_FEATURES, constants.FEATURES_PALETTE))

    reports.check_correct_report_structure(method, group, [interval])
    msg = reports.create_tab_report(method, group, interval, orientation,
                                    selected_top_list, selected_other_list, dict_selected_checkbox,
                                    df_rolled, df_slices, TIMESTAMP, group_intervals, left_space, right_space,
                                    NAMES_OF_GROUPS, DICT_KKS, PLOT_FEATURES, DICT_PLOT_PALETTE)

    return msg


@eel.expose
def get_common_pdf_report(method, group):
    """
    Функция копирует созданный отчет по всем периодам для выдачи файла в веб-приложении
    :param method: наименование метода
    :param group: номер группы
    :return: строка статуса выполения функции
    """
    logger.info(f"get_common_pdf_bytes_array({method}, {group})")
    common_report_path = f'{constants.REPORTS_DIRECTORY}{method}{os.sep}group_{group}{os.sep}common_report.pdf'
    common_report_dir_web_path = f'web{os.sep}common_report.pdf'
    common_report_dir_web_interval_path = f'web{os.sep}interval{os.sep}common_report.pdf'
    shutil.copy(common_report_path, common_report_dir_web_path)
    shutil.copy(common_report_path, common_report_dir_web_interval_path)
    return "success"


@eel.expose
def get_tab_pdf_report(method, group, interval):
    """
    Функция копирует созданный отчет по периоду для выдачи файла в веб-приложении
    :param method: наименование метода
    :param group: номер группы
    :param interval: массив интервала в формате: [{начало_интервала}, {конец_интервала}]
    :return: строка статуса выполения функции
    """
    logger.info(f"get_tab_pdf_report({method}, {group}, {interval})")
    report_group_period_dir = f'{constants.REPORTS_DIRECTORY}{method}{os.sep}group_{group}{os.sep}periods{os.sep}'
    correct_interval_name = [correct_name.replace(':', '-') for correct_name in interval]
    tab_report_path = f'{report_group_period_dir}report_{correct_interval_name[0]}-{correct_interval_name[-1]}.pdf'
    tab_report_dir_web_path = f'web{os.sep}interval{os.sep}tab_report.pdf'
    shutil.copy(tab_report_path, tab_report_dir_web_path)
    return "success"


@eel.expose
def get_config_rolling():
    """
    Геттер возвращает сглаживание в часах из конфига
    :return: целое число - сглаживание в часах
    """
    return int(config["model"]["rolling"])


@eel.expose
def get_length_slice():
    """
    Геттер возвращает количество строк срезов
    :return: целое число - количество строк срезов
    """
    return len(df_slices)


@eel.expose
def rebuild_anomaly_interval(method,
                             roll_probability,
                             SHORT_THRESHOLD,
                             LONG_THRESHOLD,
                             LEN_SHORT_ANOMALY,
                             LEN_LONG_ANOMALY,
                             COUNT_CONTINUE_SHORT,
                             COUNT_CONTINUE_LONG,
                             COUNT_TOP=3):
    """
    Функция возвращает статус операции выделения новых интервалов
    :param method: наименование метода
    :param roll_probability: сглаживание в часах
    :param SHORT_THRESHOLD: порог для определения аномального значения для поиска коротких интервалов
    :param LONG_THRESHOLD: порог для определения аномального значения для поиска длинных интервалов
    :param LEN_SHORT_ANOMALY: настройка определяет минимальную длину короткого обнаруженного интервала аномалии
    :param LEN_LONG_ANOMALY: настройка определяет минимальную длину длинного обнаруженного интервала аномалии
    :param COUNT_CONTINUE_SHORT: количество отсчетов для прерывания короткого интервала
    :param COUNT_CONTINUE_LONG: количество отсчетов для прерывания длинного интервала
    :param COUNT_TOP: целое число указывает сколько датчиков, внесших max вклад, требуется вернуть
    :return: строка статуса выделения новых интервалов
    """

    logger.info(f"rebuild_anomaly_interval({method}, {roll_probability}, "
                f"{SHORT_THRESHOLD}, "
                f"{LONG_THRESHOLD}, "
                f"{LEN_SHORT_ANOMALY}, "
                f"{LEN_LONG_ANOMALY}, "
                f"{COUNT_CONTINUE_SHORT}, "
                f"{COUNT_CONTINUE_LONG}, "
                f"{COUNT_TOP})")
    eel.setProgressBarRebuildIntervalValue(0)
    reports.clean_old_reports(method)

    csv_predict_listdir = sorted(os.listdir(f'{constants.DATA_DIRECTORY}{method}{os.sep}csv_predict{os.sep}'))
    csv_loss_listdir = sorted(os.listdir(f'{constants.DATA_DIRECTORY}{method}{os.sep}csv_loss{os.sep}'))
    csv_rolled_listdir = sorted(os.listdir(f'{constants.DATA_DIRECTORY}{method}{os.sep}csv_rolled{os.sep}'))

    assert len(csv_predict_listdir) == len(csv_loss_listdir) == len(csv_rolled_listdir)

    # получение csv группы
    for group, (csv, loss, rolled) in enumerate(zip(csv_predict_listdir, csv_loss_listdir, csv_rolled_listdir)):
        dict_list = []
        try:
            df_predict_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}csv_predict{os.sep}predict_{group + 1}.csv'
            df_predict = pd.read_csv(df_predict_path)
            df_predict.fillna(value={"target_value": 0}, inplace=True)

            df_loss_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}csv_loss{os.sep}loss_{group + 1}.csv'
            df_loss = pd.read_csv(df_loss_path)
            df_loss.index = df_loss['timestamp']
            df_loss = df_loss.drop(columns=['timestamp'])

            df_rolled_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}csv_rolled{os.sep}rolled_{group + 1}.csv'
            df_rolled = pd.read_csv(df_rolled_path)
            df_rolled.fillna(value={"target_value": 0}, inplace=True)

            intervals_json_path = f'{constants.DATA_DIRECTORY}{method}{os.sep}json_interval{os.sep}group_{group + 1}.json'

            # Сглаживание и сохранение результата
            df_rolled = rolling_probability(df_predict, roll_probability, config["number_of_samples"])

            # merge фрейма вероятности с slice csv по timestamp
            if len(df_rolled) != len(df_slices):
                logger.info("merge rolled_df with df_slices by timestamp")
                time_df = pd.DataFrame()
                time_df['timestamp'] = df_slices['timestamp']
                df_rolled = pd.merge(time_df, df_rolled, how='left', on='timestamp')

            df_rolled.fillna(value={"target_value": 0}, inplace=True)
            df_rolled.to_csv(df_rolled_path, index=False)
            df_rolled.index = df_rolled['timestamp']
            df_rolled = df_rolled.drop(columns=['timestamp'])

            interval_list, idx_list = get_anomaly_interval(df_rolled['target_value'],
                                                           threshold_short=SHORT_THRESHOLD,
                                                           threshold_long=LONG_THRESHOLD,
                                                           len_long=LEN_LONG_ANOMALY,
                                                           len_short=LEN_SHORT_ANOMALY,
                                                           count_continue_short=COUNT_CONTINUE_SHORT,
                                                           count_continue_long=COUNT_CONTINUE_LONG)

            # отбрасываем лишние датчики, перечисленные в config_plot_SOCHI
            for sensor in DROP_LIST:
                if sensor in df_loss.columns:
                    df_loss.drop(columns=sensor, inplace=True)
                    logger.info(f"drop bad sensor: {sensor} from {df_loss_path} dataframe")

            for j in idx_list:
                top_list = df_loss[j[0]:j[1]].mean().sort_values(ascending=False).index[:COUNT_TOP].to_list()
                report_dict = {
                    "time": (str(df_rolled.index[j[0]]), str(df_rolled.index[j[1]])),
                    "len": j[1] - j[0],
                    "index": j,
                    "top_sensors": top_list
                }
                dict_list.append(report_dict)

            with open(intervals_json_path, "w") as outfile:
                json.dump(dict_list, outfile, indent=4)
            logger.info(f'{intervals_json_path} has been saved')

        except Exception as e:
            msg = e
            logger.error(msg)
            return msg

        eel.setProgressBarRebuildIntervalValue(int((group+1)/len(csv_predict_listdir) * 100))

    msg = f"Выделение интервалов для метода {method} закончено"
    return msg


@eel.expose
def template_report_create(text, report_name, text_html=None):
    """
    Функция возвращает статус операции построения отчета по шаблону
    :param text: текст отчета с метатегами
    :param text_html: html скомпилированного текста markdown в редакторе
    :return: строка статуса операции построения отчета по шаблону
    """
    logger.info(f"template_report_create(text, {report_name}, text_html)")
    signals, lines, tables = pt.parse_text(text)

    # if signals:
    #     signals_jinja = gs.get_data_jinja_dict_signals(signals, DICT_ALL_KKS)
    #     logger.info(signals_jinja)
    #
    # lines_jinja = {}
    # if lines:
    #     lines_jinja = gl.get_data_jinja_dict_kks(lines, DICT_ALL_KKS)
    #     logger.info(lines_jinja)

    if text_html is None:
        msg = f"Создание отчета по шаблону завершено"
    else:
        try:
            # if report_name is None:
            #     report_name = "custom"
            gt.fill_content_by_html(text_html, signals, lines, tables, df_slices, DICT_ALL_KKS, report_name)
            logger.info(f"report has been created")
            msg = 1
        except Exception as e:
            logger.error(f"creating report has been failed")
            msg = 0
    return msg


@eel.expose
def get_html(report_name):
    logger.info(f"get_html({report_name})")
    html_path = f'{constants.REPORTS_CUSTOM}{report_name}.html'
    html_dir_web_path = f'web{os.sep}report.html'
    shutil.copy(html_path, html_dir_web_path)
    return "success"


@eel.expose
def remove_download_html(report_name):
    logger.info(f" remove_download_html({report_name})")
    html_path = f'{constants.REPORTS_CUSTOM}{report_name}.html'

    try:
        os.remove(html_path)
        logger.info(f"downloaded html has been removed from space")
    except Exception as e:
        logger.error(e)
        return e
    return "success"


def on_close(page, sockets):
    """Callback close Eel application."""
    logger.info(page)
    logger.info(sockets)


def start_eel(develop):
    """Start Eel with either production or development configuration."""
    logger.info("before init")

    if develop:
        directory = f'vue{os.sep}src'
        app = None
        page = {'port': 3000}
    else:
        directory = f'web'
        app = 'chrome-app'
        page = ''

    eel.init(directory, ['.js', '.html'])
    logger.info("after init")

    # These will be queued until the first connection is made, but won't be repeated on a page reload
    eel_kwargs = dict(
        host='localhost',
        port=8000,
        size=(1920, 1080),
    )
    try:
        logger.info("start")
        eel.start(page, mode=app, shutdown_delay=10.0, callback=on_close, **eel_kwargs)
    except EnvironmentError:
        # If Chrome isn't found, fallback to Microsoft Edge on Win10 or greater
        if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:
            eel.start(page, mode='edge', shutdown_delay=10.0, callback=on_close, **eel_kwargs)
        else:
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="start eel + vue 3 web-application")
    parser.add_argument("-v", "--version", action="version", help="print version", version=f'{VERSION}')

    try:
        opt = parser.parse_args()
    except SystemExit:
        logger.info(f'{VERSION} eel + vue 3 web-application version')
        exit(0)

    check_correct_application_structure()
    config, config_plot, json_dict = get_jsons()

    index_group = [list(x.keys())[0] for x in json_dict["groups"] if list(x.keys())[0] != '0']
    logger.info(f'Found groups: {index_group}')

    NAMES_OF_GROUPS = [x + " " + "(" + json_dict["groups"][int(x)][str(x)]['name'] + ")" for x in index_group]
    logger.info(f'Names of groups: {NAMES_OF_GROUPS}')

    # считываем сразу срезы в /data/csv_data/slices.csv, так как это не зависит от выбранного метода
    df_slices = pd.read_csv(constants.CSV_SLICES)
    TIMESTAMP = df_slices['timestamp'].tolist()

    # массив отбрасываемых датчиков
    DROP_LIST = config_plot['DROP_LIST']
    # массив датчиков, которые являются осями в многоосевом графике
    PLOT_FEATURES = config_plot['PLOT_FEATURES']

    # наименования датчиков
    DICT_KKS = get_name_of_kks(DROP_LIST)

    # наименования всех датчиков без ограничений
    DICT_ALL_KKS = get_name_of_kks([])

    # Pass any second argument to enable debugging
    start_eel(develop=len(sys.argv) == 2)
