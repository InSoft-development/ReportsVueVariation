from loguru import logger

import os


# def get_data_jinja_dict_signals(signals, dict_kks):
#     logger.info(f"get_dict_signals(signals, dict_kks)")
#     signals_data_dict = dict()
#     for signal in signals:
#         signal_kks = signal.split(' ')[-2]
#         signals_data_dict[signal] = f"{{{{ signals['{signal_kks}'] }}}}" if signal_kks in dict_kks else "Сигнал не найден"
#     return signals_data_dict
#
#
# def get_data_dict_signals(jinja_signals):
#     logger.info(f"get_data_dict_signals(jinja_signals)")
#     signals = dict()
#     for (key, value) in jinja_signals.items():
#         if value == "Сигнал не найден":
#             signals[key.split(' ')[-2]] = "Сигнал не найден"
#         else:
#             signals[key.split(' ')[-2]] = key.split(' ')[-2]
#     return signals
#
#
# def get_signal_jinja_replaced_text(text, signals_data_dict):
#     logger.info(f"get_signal_replaced_text(text, signals_data_dict)")
#     for (key, value) in signals_data_dict.items():
#         text = text.replace(key, value)
#     return text


def replace_signal_parse_on_template(text, signal_parsed):
    logger.info(f"replace_signal_parse_on_template(text, {signal_parsed})")
    kks = signal_parsed.split(' ')[-2]

    # text.replace(f"id={signal_parsed}", f"id=signal-{id_count}")

    with open(f"jinja{os.sep}template{os.sep}signal.html", "r", encoding="utf-8") as f:
        template_signal = f.read()
        template_signal = template_signal.replace("kks", f"{kks}")

    return text.replace(signal_parsed, template_signal)


def get_signal_data(kks, dict_all_kks):
    logger.info(f"get_signal_data({kks}, dict_all_kks)")
    return kks if kks in dict_all_kks else "Сигнал не найден"
