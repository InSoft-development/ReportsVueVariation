from loguru import logger
import os
import pandas as pd


def replace_table_parse_on_template(text, table_parsed):
    logger.info(f"replace_table_parse_on_template(text, table_parsed)")
    kks = table_parsed.split(' ')[-2]

    with open(f"jinja{os.sep}template{os.sep}table.html", "r", encoding="utf-8") as f:
        template_table = f.read()
        template_table = template_table.replace('\'kks\'', f"\"{kks}\"")

    return text.replace(table_parsed, template_table, 1)


def get_table_data(kks, df):
    logger.info(f"get_table_data(kks, df)")
    data = pd.DataFrame(data={"id": [x for x in range(len(df))], "timestamp": df['timestamp'].tolist(), "value": df[kks].tolist()})
    return data.to_json(orient="records")
