import eel

import os
import errno
import shutil
import time

from loguru import logger
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak

import utils.constants_and_paths as constants
import utils.get_figure_plotly as plotly

styles = getSampleStyleSheet()  # Стили для отчетов по умолчанию

headline_style = styles["Heading1"]
headline_style.alignment = TA_CENTER
headline_style.fontSize = 24
headline_style.textColor = "#4562a1"

subheadline_style = styles["Heading2"]
subheadline_style.textColor = "#4562a1"

pdfmetrics.registerFont(TTFont('DVS', 'DejaVuSerif.ttf', 'UTF-8'))  # шрифт


# форматирование текста отчета Times New Roman
def string_guy(text):
    return f'<font name="DVS">{text}</font>'


# форматирование текста легенды
def string_guy_legend(text, color):
    return f'<font name="DVS">{text[:text.index(":")]}' \
           f'</font><font name="DVS" color={color}>{text[text.index(":"):]}</font>'


# форматирование обычного абзаца
def parag_guy(text, style=styles['Normal']):
    return Paragraph(string_guy(text), style)


# форматирование абзаца легенды
def parag_guy_legend(text, color, style=styles['Normal']):
    return Paragraph(string_guy_legend(text, color), style)


def check_correct_report_structure(method, group, intervals):
    """
    Процедура проверки струкутуры директорий отчетов
    :param method: наименование метода
    :param group: номер группы
    :param intervals: массив интервалов в формате: [{начало_интервала}, {конец_интервала}]
    :return:
    """
    logger.info(f"check_correct_report_structure({method}, {group}, {intervals})")
    report_dir = f'{constants.REPORTS_DIRECTORY}{method}{os.sep}'
    report_group_dir = f'{report_dir}group_{group}{os.sep}'
    report_group_period_dir = f'{report_group_dir}periods{os.sep}'

    # проверка создания директории группы
    try:
        os.mkdir(report_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.info(e)

    # проверка создания директории periods периодов (интервалов)
    try:
        os.mkdir(report_group_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.info(e)

    try:
        os.mkdir(report_group_period_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.info(e)

    # проверка создания директорий периодов (интервалов)
    for interval in intervals:
        correct_interval_name = [correct_name.replace(':', '-') for correct_name in interval]
        report_interval_dir = f'{report_group_period_dir}{correct_interval_name[0]}-{correct_interval_name[-1]}{os.sep}'

        try:
            os.mkdir(report_interval_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.info(e)


def create_common_report(method, group, orientation, intervals, group_intervals,
                         top_sensors, df_predict, df_slices, TIMESTAMP, left_space, right_space,
                         NAMES_OF_GROUPS, DICT_KKS, PLOT_FEATURES, DICT_PLOT_PALETTE, DROP_LIST):
    """
    Функция возвращает статус построения отчета по всем периодам
    :param method: наименование метода
    :param group: номер группы
    :param orientation: выбранная ориентация страниц отчета
    :param intervals: массив интервалов в формате: [{начало_интервала}, {конец_интервала}]
    :param group_intervals: массив интервалов выделенных методом в формате: [{начало_интервала}, {конец_интервала}]
    :param top_sensors: массив датчиков, внесших максимальный вклад
    :param df_predict: pandas фрейм значений целевого значения
    :param df_slices: pandas фрейм срезов
    :param TIMESTAMP: массив временных отметок
    :param left_space: настроенный в веб-приложении отступ в 5-ти минутках слева
    :param right_space: настроенный в веб-приложении отступ в 5-ти минутках справа
    :param NAMES_OF_GROUPS: наименование групп
    :param DICT_KKS: словарь KKS датчиков и их полного наименования
    :param PLOT_FEATURES: массив датчиков для многоосевого графика
    :param DICT_PLOT_PALETTE: словарь датчика и цвета
    :param DROP_LIST: массив отбрасываемых датчиков
    :return: статус построения отчета по всем периодам
    """
    logger.info(f"create_common_report()")
    eel.setProgressBarValue(0)
    report_dir = f'{constants.REPORTS_DIRECTORY}{method}{os.sep}'
    report_group_dir = f'{report_dir}group_{group}{os.sep}'
    report_group_period_dir = f'{report_group_dir}periods{os.sep}'

    if method == 'potentials':
        home_text = 'График вероятности наступления аномалии за весь период'
        tab_text = 'График вероятности наступления аномалии'
    elif method == 'LSTM':
        home_text = 'График функции потерь за весь период'
        tab_text = 'График функции потерь'
    else:
        home_text = 'График целевой функции за весь период'
        tab_text = 'График целевой функции'

    if orientation == "letter":
        doc = SimpleDocTemplate(f'{report_group_dir}common_report.pdf',
                                pagesize=landscape(letter), rightMargin=72, leftMargin=72, topMargin=72,
                                bottomMargin=18)
        scale = 1.25
    else:
        doc = SimpleDocTemplate(f'{report_group_dir}common_report.pdf',
                                pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72,
                                bottomMargin=18)
        scale = 1.0

    story = [parag_guy(f'Метод {method}', headline_style),
             parag_guy(f"Отчет по всем периодам группы {NAMES_OF_GROUPS[group-1]}", headline_style),
             Spacer(1, 12), parag_guy(home_text, subheadline_style), Spacer(1, 12)]

    # добавление графика целевой функции за весь периода
    path_home_img = f'{report_group_dir}home_img.png'
    fig_home = plotly.get_home_fig(df_predict, group_intervals)
    fig_home.write_image(path_home_img, engine="kaleido", width=900, height=800)

    im = Image(path_home_img, 8 * inch * scale, 4 * inch * scale)
    story.append(im)

    story.append(parag_guy("Найденные и добавленные периоды", subheadline_style))
    for (index, interval) in enumerate(intervals):
        ptext = f"{index+1}) {interval[0]} {'&nbsp' * 2} ÷ {'&nbsp' * 2} {interval[-1]}"
        story.append(parag_guy(ptext, styles["Normal"]))
        story.append(Spacer(1, 12))
    story.append(PageBreak())

    for (index, interval) in enumerate(intervals):
        correct_interval_name = [correct_name.replace(':', '-') for correct_name in interval]
        report_interval_dir = f'{report_group_period_dir}{correct_interval_name[0]}-{correct_interval_name[-1]}{os.sep}'

        story.append(parag_guy(f"Период {interval[0]} {'&nbsp' * 3}÷{'&nbsp' * 3} {interval[-1]}", headline_style))
        story.append(Spacer(1, 12))
        story.append(parag_guy(tab_text, subheadline_style))
        story.append(Spacer(1, 12))

        path_tab_fig = f'{report_interval_dir}tab_img.png'
        tab_fig = plotly.get_tab_fig(df_predict, TIMESTAMP, interval, group_intervals, left_space, right_space)
        tab_fig.write_image(path_tab_fig, engine="kaleido")

        im = Image(path_tab_fig, 8 * inch * scale, 4 * inch * scale)
        story.append(im)

        story.append(parag_guy("Сигналы, внесшие наибольший вклад:", subheadline_style))
        story.append(Spacer(1, 12))

        for top in top_sensors[index]:
            if top not in DROP_LIST:
                ptext = f"{top} ({DICT_KKS[top]})"
                story.append(parag_guy(ptext, styles["Normal"]))
                story.append(Spacer(1, 12))

        story.append(PageBreak())

        for (top_index, top) in enumerate(top_sensors[index]):
            if top not in DROP_LIST:
                ptext = f"{top} ({DICT_KKS[top]})"
                story.append(parag_guy(ptext, subheadline_style))

                path_sensor_fig = f'{report_interval_dir}sensor_img_{top}.png'
                sensor_fig, legend_list, palette_list = \
                    plotly.get_sensors_fig(df_slices, TIMESTAMP,
                                           top, interval, group_intervals,
                                           left_space, right_space, PLOT_FEATURES, DICT_PLOT_PALETTE)
                sensor_fig.write_image(path_sensor_fig,
                                       engine="kaleido", width=1200, height=1000)

                im = Image(path_sensor_fig, 7 * inch * scale, 4 * inch * scale)
                story.append(im)

                for (legend_index, legend) in enumerate(legend_list):
                    if legend_index == 0:
                        ptext = f"Основной сигнал: {legend} ({DICT_KKS[legend]})"
                    else:
                        ptext = f"Дополнительный сигнал: {legend} ({DICT_KKS[legend]})"
                    story.append(parag_guy_legend(ptext, palette_list[legend_index], styles["Normal"]))
                    story.append(Spacer(1, 12))
                story.append(PageBreak())
        eel.setProgressBarValue(int((index + 1) / len(intervals) * 100))

    try:
        doc.build(story)
    except Exception as e:
        logger.info(e)
        return str(e)
    logger.info("New report has been created")
    return "Новый отчет создан"


def create_tab_report(method, group, interval, orientation,
                      selected_top_list, selected_other_list, dict_selected_checkbox,
                      df_predict, df_slices, TIMESTAMP, group_intervals, left_space, right_space,
                      NAMES_OF_GROUPS, DICT_KKS, PLOT_FEATURES, DICT_PLOT_PALETTE):
    """
    Функция возвращает статус построения отчета по периоду
    :param method: наименование метода
    :param group: номер группы
    :param interval: интервал в формате: [{начало_интервала}, {конец_интервала}]
    :param orientation: выбранная ориентация страниц отчета
    :param selected_top_list: выбранные датчики, внесшие максимальный вклад
    :param selected_other_list: выбранные остальные датчики группы
    :param dict_selected_checkbox: словарь выбранных чекбоксов датчикво многоосевого графика
    :param df_predict: pandas фрейм значений целевого значения
    :param df_slices: pandas фрейм срезов
    :param TIMESTAMP: массив временных отметок
    :param group_intervals: массив интервалов выделенных методом в формате: [{начало_интервала}, {конец_интервала}]
    :param left_space: настроенный в веб-приложении отступ в 5-ти минутках слева
    :param right_space: настроенный в веб-приложении отступ в 5-ти минутках справа
    :param NAMES_OF_GROUPS: наименование групп
    :param DICT_KKS: словарь KKS датчиков и их полного наименования
    :param PLOT_FEATURES: массив датчиков для многоосевого графика
    :param DICT_PLOT_PALETTE: словарь датчика и цвета
    :return:
    """
    logger.info(f"create_tab_report()")
    eel.setProgressTabBarValue(0)

    report_dir = f'{constants.REPORTS_DIRECTORY}{method}{os.sep}'
    report_group_dir = f'{report_dir}group_{group}{os.sep}'
    report_group_period_dir = f'{report_group_dir}periods{os.sep}'

    correct_interval_name = [correct_name.replace(':', '-') for correct_name in interval]
    report_interval_dir = f'{report_group_period_dir}{correct_interval_name[0]}-{correct_interval_name[-1]}{os.sep}'

    if method == 'potentials':
        tab_text = 'График вероятности наступления аномалии'
    elif method == 'LSTM':
        tab_text = 'График функции потерь'
    else:
        tab_text = 'График целевой функции'

    if orientation == "letter":
        doc = SimpleDocTemplate(f'{report_group_period_dir}report_'
                                f'{correct_interval_name[0]}-{correct_interval_name[-1]}.pdf',
                                pagesize=landscape(letter), rightMargin=72, leftMargin=72, topMargin=72,
                                bottomMargin=18)
        scale = 1.25
    else:
        doc = SimpleDocTemplate(f'{report_group_period_dir}report_'
                                f'{correct_interval_name[0]}-{correct_interval_name[-1]}.pdf',
                                pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72,
                                bottomMargin=18)
        scale = 1.0

    story = [parag_guy(f'Метод {method}', headline_style), Spacer(1, 12),
             parag_guy(f"Группа {NAMES_OF_GROUPS[group - 1]}", headline_style), Spacer(1, 12),
             parag_guy(f"Период {interval[0]} {'&nbsp' * 2}÷{'&nbsp' * 2} {interval[-1]}", headline_style),
             Spacer(1, 12),
             parag_guy(tab_text, subheadline_style),
             Spacer(1, 12)]

    # добавление графика целевой функции за интервал
    path_tab_img = f'{report_interval_dir}tab_img.png'
    fig_tab = plotly.get_tab_fig(df_predict, TIMESTAMP, interval, group_intervals, left_space, right_space)
    fig_tab.write_image(path_tab_img, engine="kaleido", width=900, height=800)

    im = Image(path_tab_img, 8 * inch * scale, 4 * inch * scale)
    story.append(im)

    if selected_top_list:
        story.append(parag_guy("Выбранные сигналы, внесшие наибольший вклад:", subheadline_style))
        story.append(Spacer(1, 12))
        for top in selected_top_list:
            ptext = top
            story.append(parag_guy(ptext, styles["Normal"]))
            story.append(Spacer(1, 12))

    if selected_other_list:
        story.append(Spacer(1, 12))
        story.append(parag_guy("Остальные выбранные сигналы группы:", subheadline_style))
        story.append(Spacer(1, 12))
        for other in selected_other_list:
            ptext = other
            story.append(parag_guy(ptext, styles["Normal"]))
            story.append(Spacer(1, 12))
    story.append(PageBreak())

    top_sensors = [selected_top.split()[0] for selected_top in selected_top_list]
    other_sensors = [selected_other.split()[0] for selected_other in selected_other_list]

    if top_sensors:
        for (index, top) in enumerate(top_sensors):
            ptext = top
            story.append(parag_guy(ptext, subheadline_style))

            path_sensors_tab_img = f'{report_interval_dir}sensor_top_img_{index}.png'

            if not dict_selected_checkbox[top]:
                ptext = f"Для {top} не отмечено ни одиного сигнала"
                story.append(parag_guy(ptext, subheadline_style))
                story.append(PageBreak())
                continue

            sensor_fig, legend_palette_zip = \
                plotly.get_sensors_tab_fig(df_slices, TIMESTAMP,
                                           dict_selected_checkbox[top], interval, group_intervals,
                                           left_space, right_space, PLOT_FEATURES, DICT_PLOT_PALETTE)
            sensor_fig.write_image(path_sensors_tab_img, engine="kaleido", width=1200, height=1000)

            im = Image(path_sensors_tab_img, 7 * inch * scale, 4 * inch * scale)
            story.append(im)

            for legend_index, (feature, palette_color) in enumerate(legend_palette_zip):
                if (feature in top_sensors) and legend_index == 0:
                    ptext = f"Основной сигнал: {feature} ({DICT_KKS[feature]})"
                    story.append(parag_guy_legend(ptext, palette_color, styles["Normal"]))
                    story.append(Spacer(1, 12))
                else:
                    ptext = f"Дополнительный сигнал: {feature} ({DICT_KKS[feature]})"
                    story.append(parag_guy_legend(ptext, palette_color, styles["Normal"]))
                    story.append(Spacer(1, 12))

            story.append(PageBreak())

            eel.setProgressTabBarValue(int((index + 1) / len(top_sensors) * 50))

    if other_sensors:
        for (index, other) in enumerate(other_sensors):
            ptext = other
            story.append(parag_guy(ptext, subheadline_style))

            path_sensors_tab_img = f'{report_interval_dir}sensor_other_img_{index}.png'

            if not dict_selected_checkbox[other]:
                ptext = f"Для {other} не отмечено ни одиного сигнала"
                story.append(parag_guy(ptext, subheadline_style))
                story.append(PageBreak())
                continue

            sensor_fig, legend_palette_zip = \
                plotly.get_sensors_tab_fig(df_slices, TIMESTAMP,
                                           dict_selected_checkbox[other],interval, group_intervals,
                                           left_space, right_space, PLOT_FEATURES, DICT_PLOT_PALETTE)
            sensor_fig.write_image(path_sensors_tab_img, engine="kaleido", width=1200, height=1000)

            im = Image(path_sensors_tab_img, 7 * inch * scale, 4 * inch * scale)
            story.append(im)

            for legend_index, (feature, palette_color) in enumerate(legend_palette_zip):
                if (feature in other_sensors) and legend_index == 0:
                    ptext = f"Основной сигнал: {feature} ({DICT_KKS[feature]})"
                    story.append(parag_guy_legend(ptext, palette_color, styles["Normal"]))
                    story.append(Spacer(1, 12))

                else:
                    ptext = f"Дополнительный сигнал: {feature} ({DICT_KKS[feature]})"
                    story.append(parag_guy_legend(ptext, palette_color, styles["Normal"]))
                    story.append(Spacer(1, 12))

            story.append(PageBreak())
            eel.setProgressTabBarValue(int((index + 1) / len(other_sensors) * 50) + 50)

    eel.setProgressTabBarValue(100)
    # задержка для проигрывания анимации
    time.sleep(1)

    try:
        doc.build(story)
    except Exception as e:
        logger.info(e)
        return str(e)

    logger.info("New period report has been created")
    return f"Новый отчет по периоду {interval[0]}-{interval[-1]} создан"


def clean_old_reports(method):

    for group in sorted(os.listdir(f"{constants.REPORTS_DIRECTORY}{method}{os.sep}")):
        logger.info(group)
        web_app_reports_group = f'{constants.REPORTS_DIRECTORY}{method}{os.sep}{group}{os.sep}'
        logger.info(f"delete {web_app_reports_group}")
        shutil.rmtree(web_app_reports_group)

        try:
            logger.info(f"create {web_app_reports_group}")
            os.mkdir(f'{web_app_reports_group}')
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.error(e)
