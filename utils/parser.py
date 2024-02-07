import re

from loguru import logger


def parse_text(text):
    logger.info(f"parse_text(text)")
    match_signal_list = re.findall(r'\{\{\sSIGNAL\s\S*\s\}\}', text)
    match_line_list = re.findall(r'\{\{\sLINE\s\S*\s\}\}', text)
    match_signal_table_list = re.findall(r'\{\{\sTABLE\s\S*\s\}\}', text)
    logger.info(match_signal_list)
    logger.info(match_line_list)
    logger.info(match_signal_table_list)
    return match_signal_list, match_line_list, match_signal_table_list
