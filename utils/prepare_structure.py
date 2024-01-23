import os
import errno
from loguru import logger

import utils.constants_and_paths as constants

logger.info(f"start utils{os.sep}prepare_structure.py")

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
    os.mkdir(f'{constants.DATA_CSV_DIRECTORY}')
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

logger.info(f"script finished")
