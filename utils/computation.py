from loguru import logger


def mean_index(data, sensors, drop_list, top_count=3):
    """
    Функция вычисляет средние значения для составления списка датчиков, внесших max вклад
    :param data: pandas срез данных по группе и интервалу
    :param sensors: массив датчиков группы
    :param top_count: целое число указывает сколько датчиков, внесших max вклад, требуется вернуть
    :return: mean_loss: датчики, внесшие max вклад
    """
    # отбрасываем лишние датчики, перечисленные в config_plot_SOCHI
    data_temp = data.copy(deep=True)
    for sensor in drop_list:
        if sensor in data_temp.columns:
            data_temp.drop(columns=sensor, inplace=True)
            logger.info(f"drop bad sensor: {sensor} from loss dataframe")

    mean_loss = data_temp[sensors].mean().sort_values(ascending=False).index[:top_count].to_list()
    return mean_loss


def rolling_probability(df, roll_in_hours, number_of_samples):
    """
    Функция возвращает сглаженный скользящим средним фрейм pandas с целевой переменной target_value
    :param df: фрейм исходных данных
    :param roll_in_hours: сглаживание в часах
    :param number_of_samples: количество интервалов кратных 5
    :return: фрейм pandas со сглаженной скользящим средним целевой переменной target_value
    """
    # Первые индексы после сглаживания будут Nan, запоминаем их
    temp_rows = df['target_value'].iloc[:roll_in_hours*number_of_samples]
    rolling_prob = df['target_value'].rolling(window=roll_in_hours*number_of_samples, min_periods=1, axis='rows').mean()
    rolling_prob.iloc[:roll_in_hours*number_of_samples] = temp_rows
    df['target_value'] = rolling_prob
    return df


def check_power(power, index, power_limit, left_power_shift=15, right_power_shift=15):
    """
    Функция проверки выделяемого интервала по мощности для отсечения остановов
    :param power: pandas фрейм со срезами сигналов
    :param index: индекс строки в фрейме с целевой переменной target_value
    :param power_limit: ограничение по мощности
    :param left_power_shift: сдвиг влево
    :param right_power_shift:  сдвиг вправо
    :return: True: выделяемый интервал находится вне останова
             False: выделяемый интервал находится вблизи останова
    """
    return any(val < power_limit for val in power[index-left_power_shift:right_power_shift+15])


def get_anomaly_interval(loss, threshold_short, threshold_long, len_long, len_short, power, power_limit,
                         count_continue_short=10,
                         count_continue_long=15):
    """
    Функция выделения интервалов
    :param loss: pandas фрейм с целевой переменной target_value
    :param threshold_short: порог для определения аномального значения для поиска коротких интервалов
    :param threshold_long: порог для определения аномального значения для поиска длинных интервалов
    :param len_long: настройка определяет минимальную длину длинного обнаруженного интервала аномалии
    :param len_short: настройка определяет минимальную длину короткого обнаруженного интервала аномалии
    :param power: pandas фрейм со срезами сигналов
    :param power_limit: ограничение по мощности
    :param count_continue_short: количество отсчетов для прерывания короткого интервала
    :param count_continue_long: количество отсчетов для прерывания длинного интервала
    :return: long_interval_list + short_interval_list: массив значений выделенных интервалов
             long_idx_list + short_idx_list: массив индексов выделенных интервалов
    """
    long_interval_list = []
    short_interval_list = []
    loss_interval = []
    count = 0
    i = 0
    long_idx_list = []
    short_idx_list = []
    sum_anomaly = 0
    for val in loss:
        i += 1
        if val > threshold_long and check_power(power, i, power_limit):
            loss_interval.append(val)
            count = 0
        else:
            count += 1
            loss_interval.append(val)
            if count > count_continue_long:
                if len(loss_interval) > len_long:
                    long_interval_list.append(loss_interval)
                    logger.info(f'Add anomaly long interval, len {len(loss_interval)}')
                    if i - len(loss_interval) > 0:
                        long_idx_list.append((i - len(loss_interval), i))
                    else:
                        long_idx_list.append((0, i))
                    sum_anomaly += len(loss_interval)
                count = 0
                loss_interval.clear()

    i = 0
    for val in loss:
        i += 1
        if val > threshold_short:
            loss_interval.append(val)
            count = 0
        else:
            count += 1
            loss_interval.append(val)
            if count > count_continue_short:
                if len(loss_interval) > len_short:
                    isInLong = any(start <= i - len(loss_interval) < end for start, end in long_idx_list)
                    if not isInLong:
                        short_interval_list.append(loss_interval)
                        logger.info(f'Add anomaly short interval, len {len(loss_interval)}')
                        if i - len(loss_interval) > 0:
                            short_idx_list.append((i - len(loss_interval), i))
                        else:
                            short_idx_list.append((0, i))
                        sum_anomaly += len(loss_interval)
                count = 0
                loss_interval.clear()

    logger.info(f'Sum anomaly {sum_anomaly}, part of anomaly {round(sum_anomaly / len(loss), 3)}')
    return long_interval_list + short_interval_list, long_idx_list + short_idx_list
