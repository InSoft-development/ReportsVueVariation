import os
import errno

import pandas as pd

import json
from loguru import logger

import utils.constants_and_paths as constants


def check_correct_application_structure():
    """
    Процедура проверяет создание директорий веб-приложения
    :return: исключение или успешное выполнение процедуры
    """
    try:
        os.mkdir(f'{constants.CONFIG_DIRECTORY}')
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)

    try:
        os.mkdir(f'{constants.DATA_DIRECTORY}')
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)

    try:
        os.mkdir(f'{constants.REPORTS_DIRECTORY}')
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)

    try:
        os.mkdir(f'{constants.REPORTS_CUSTOM}')
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)

    try:
        os.mkdir(f'{constants.WEB_DIR}')
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)

    try:
        os.mkdir(f'{constants.WEB_INTERVAL_DIR}')
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)

    try:
        os.mkdir(f'{constants.DATA_CSV_DIRECTORY}')
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)

    try:
        os.mkdir(f'{constants.JINJA}')
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)

    try:
        os.mkdir(f'{constants.JINJA_TEMPLATE}')
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)

    try:
        os.mkdir(f'{constants.JINJA_PYLIB}')
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)

    for method in constants.METHODS:
        csv_predict = f'{constants.DATA_DIRECTORY}{method}{os.sep}csv_predict{os.sep}'
        csv_loss = f'{constants.DATA_DIRECTORY}{method}{os.sep}csv_loss{os.sep}'
        csv_rolled = f'{constants.DATA_DIRECTORY}{method}{os.sep}csv_rolled{os.sep}'
        json_dir = f'{constants.DATA_DIRECTORY}{method}{os.sep}json_interval{os.sep}'
        report_dir = f'{constants.REPORTS_DIRECTORY}{method}{os.sep}'

        try:
            os.mkdir(f'{constants.DATA_DIRECTORY}{method}')
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.error(e)

        try:
            os.mkdir(csv_predict)
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.error(e)

        try:
            os.mkdir(csv_loss)
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.error(e)

        try:
            os.mkdir(csv_rolled)
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.error(e)

        try:
            os.mkdir(json_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.error(e)

        try:
            os.mkdir(report_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.info(e)


def get_jsons():
    """
    фунция возвращает конфиги станции, графиков и словарь датчиков по группам
    :return: config : конфиг станции
             config_plot : конфиг графиков
             json_dict : словарь датчиков по группам
    """
    try:
        with open(f'{constants.JSON_CONFIG}', 'r', encoding='utf8') as j:
            config = json.load(j)
    except FileNotFoundError as e:
        logger.error(e)

    try:
        with open(f'{constants.JSON_CONFIG_PLOT}', 'r', encoding='utf8') as j:
            config_plot = json.load(j)
    except FileNotFoundError as e:
        logger.error(e)

    try:
        with open(f'{constants.JSON_SENSORS}', 'r', encoding='utf8') as f:
            json_dict = json.load(f)
    except FileNotFoundError as e:
        logger.error(e)

    return config, config_plot, json_dict


def get_name_of_kks(drop_list):
    """
    Функция возвращает словарь KKS датчиков и их полного наименования
    :param drop_list: список датчиков, подлежащих выбросу из списка
    :return: словарь KKS датчиков и их полного наименования
    """
    df_kks = pd.read_csv(constants.CSV_KKS_WITH_GROUPS, delimiter=';', header=None)
    df_kks = df_kks.loc[~df_kks[0].isin(drop_list)]
    kks_dict = dict(zip(df_kks[0].to_list(), df_kks[1].to_list()))
    return kks_dict
