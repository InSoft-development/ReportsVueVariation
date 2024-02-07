from jinja2 import Environment, FileSystemLoader, BaseLoader
import os
import json

import jinja.pylib.getters_signal as gs
import jinja.pylib.getters_line as gl
import jinja.pylib.getters_table as gt

from loguru import logger


def fill_content_by_html(content_html, signals_parsed, lines_parsed, tables_parsed, df_slices, DICT_ALL_KKS, html_name):
    logger.info(f"fill_content_by_html(content_html, signals_parsed, lines_parsed, tables_parsed, "
                f"df_slices, DICT_ALL_KKS, {html_name})")
    # Объединяем header, content и footer в единый шаблон html
    filled_content = render_filled_content_by_html(content_html)
    # Рендерим шаблон html по данным
    html = render_html(filled_content, signals_parsed, lines_parsed, tables_parsed, df_slices, DICT_ALL_KKS)
    html_path = f"reports{os.sep}custom{os.sep}{html_name}.html"
    with open(html_path, 'w', encoding='utf8') as f:
        f.write(html)
    logger.info("finished render html")


def render_filled_content_by_html(content_html):
    logger.info(f"render_filled_content_by_html(content_html)")
    file_loader = FileSystemLoader(searchpath=f"jinja{os.sep}template{os.sep}")
    env = Environment(loader=file_loader)
    tm = env.get_template('template.html')
    filled_content = tm.render(content=content_html)
    return filled_content


def render_html(html, signals_parsed, lines_parsed, tables_parsed, df_slices, DICT_ALL_KKS):
    logger.info(f"render_html(html, signals_parsed, lines_parsed, df_slices)")
    string_loader = BaseLoader()

    # Обрабатываем конструкции {{ SIGNAL {kks} }}
    signals_dict = {}
    for signal in signals_parsed:
        kks = signal.split(' ')[-2]
        html = gs.replace_signal_parse_on_template(html, signal)
        # Получение данных для сигнала
        signals_dict[kks] = gs.get_signal_data(kks, DICT_ALL_KKS)

    # Обрабатываем конструкции {{ LINE {kks} }}
    line_signals_dict = {}
    line_signals_id_dict = {}
    line_data = {}
    for i, line in enumerate(lines_parsed):
        kks = line.split(' ')[-2]
        html = gl.replace_line_parse_on_template(html, line, i)
        # Получение словаря сигналов
        line_signals_dict[kks] = gs.get_signal_data(kks, DICT_ALL_KKS)
        line_signals_id_dict[f"{kks}_{i}"] = f"{kks}_{i}"

    for key, value in line_signals_dict.items():
        if value != "Сигнал не найден":
            # Получение данных для графика
            line_data[key] = gl.get_line_data(key, df_slices)

    # Обрабатываем конструкции {{ TABLE {kks} }}
    table_signals_dict = {}
    table_data = {}
    for table in tables_parsed:
        kks = table.split(' ')[-2]
        html = gt.replace_table_parse_on_template(html, table)
        # Получение словаря сигналов
        table_signals_dict[kks] = gs.get_signal_data(kks, DICT_ALL_KKS)

    for key, value in table_signals_dict.items():
        if value != "Сигнал не найден":
            # Получение данных для таблиц
            table_data[key] = json.loads(gt.get_table_data(key, df_slices))

    # Рендерим html
    env = Environment(loader=string_loader).from_string(html)
    html = env.render(signals=signals_dict, signals_kks=line_signals_dict, signals_kks_id=line_signals_id_dict,
                      data=line_data, table_kks=table_signals_dict, rows=table_data)


    # html = gl.get_lines_jinja_replaced_text(html, jinja_lines)
    # logger.info(html)
    # string_loader = BaseLoader()
    # env = Environment(loader=string_loader).from_string(html)
    #
    # # Собираем данные для подстановки в шаблон jinja
    # signals = gs.get_data_dict_signals(jinja_signals=jinja_signals)
    # lines = gl.get_lines(jinja_lines=jinja_lines)
    # images = gl.get_images(jinja_images=jinja_lines, df=df_slices)
    #
    # filled_html = env.render(signals=signals, lines=lines, images=images)
    return html
