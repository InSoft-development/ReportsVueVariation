from loguru import logger
import os

# def get_data_jinja_dict_kks(signals, dict_kks):
#     logger.info(f"get_data_jinja_dict_kks(signals, dict_kks)")
#     kks_data_dict = dict()
#     for signal in signals:
#         kks = signal.split(' ')[-2]
#         jinja_metatag = f"<h2 align=\"center\">График значений датчика {{{{  lines['{kks}']  }}}} за весь период</h2>" \
#                         f"\n<img src=\"{{{{ images[\'{kks}\'] }}}}\" class=\"center\">"
#         kks_data_dict[signal] = jinja_metatag if kks in dict_kks else "Сигнал не найден"
#     return kks_data_dict
#
#
# def get_lines_jinja_replaced_text(text, kks_data_dict):
#     logger.info(f"get_lines_jinja_replaced_text(text, signals_data_dict)")
#     for (key, value) in kks_data_dict.items():
#         text = text.replace(key, value)
#     return text
#
#
# def get_lines(jinja_lines):
#     logger.info(f"get_lines(jinja_lines)")
#     lines = dict()
#     for (key, value) in jinja_lines.items():
#         if value == "Сигнал не найден":
#             lines[key.split(' ')[-2]] = "Сигнал не найден"
#         else:
#             lines[key.split(' ')[-2]] = key.split(' ')[-2]
#     return lines
#
#
# def get_images(jinja_images, df):
#     logger.info(f"get_images(jinja_images)")
#     images = dict()
#     for (key, value) in jinja_images.items():
#         kks = key.split(' ')[-2]
#         if value == "Сигнал не найден":
#             images[kks] = "Сигнал не найден"
#         else:
#             # Отрисовка и сохранение графика
#             path_image_fig = os.path.abspath(f"reports{os.sep}custom{os.sep}{kks}.png")
#             fig = get_kks_fig(df, kks)
#             fig.write_image(path_image_fig, engine="kaleido", width=900, height=800)
#             images[kks] = path_image_fig
#     return images
#
#
# def get_kks_fig(df, kks):
#     fig = px.line(
#         df,
#         x=df['timestamp'].tolist(),
#         y=kks,
#         width=10,
#         color_discrete_sequence=[constants.MAIN_SIGNAL_COLOR]
#     )
#
#     fig.layout.yaxis = {}
#     fig.layout.xaxis = {}
#     fig.update_layout(
#         showlegend=False,
#         plot_bgcolor='rgba(0, 0, 0, 0)',
#         paper_bgcolor='rgba(0, 0, 0, 0)'
#     )
#
#     fig.update_layout({"uirevision": "foo"}, overwrite=True)
#     return fig


def replace_line_parse_on_template(text, line_parsed, i):
    logger.info(f"replace_line_parse_on_template(text, {line_parsed}, {i})")
    kks = line_parsed.split(' ')[-2]

    with open(f"jinja{os.sep}template{os.sep}line.html", "r", encoding="utf-8") as f:
        template_line = f.read()
        template_line = template_line.replace('\'kks_id\'', f"\"{kks}_{i}\"")
        template_line = template_line.replace('\'kks\'', f"\"{kks}\"")

    return text.replace(line_parsed, template_line, 1)


def get_line_data(kks, df):
    logger.info(f"get_line_data({kks}, df)")
    return {"x": df['timestamp'].tolist(), "y": df[kks].tolist()}
