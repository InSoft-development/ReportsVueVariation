from loguru import logger


def mean_index(data, sensors, top_count=3):
    """
    Функция вычисляет средние значения для составления списка датчиков, внесших max вклад
    :param data: pandas срез данных по группе и интервалу
    :param sensors: массив датчиков группы
    :param top_count: целое число указывает сколько датчиков, внесших max вклад, требуется вернуть
    :return: mean_loss: датчики, внесшие max вклад
    """
    mean_loss = data[sensors].mean().sort_values(ascending=False).index[:top_count].to_list()
    return mean_loss


def rolling_probability(df, roll_in_hours, number_of_samples):
    # Первые индексы после сглаживания будут Nan, запоминаем их
    temp_rows = df['target_value'].iloc[:roll_in_hours*number_of_samples]
    rolling_prob = df['target_value'].rolling(window=roll_in_hours*number_of_samples, min_periods=1, axis='rows').mean()
    rolling_prob.iloc[:roll_in_hours*number_of_samples] = temp_rows
    df['target_value'] = rolling_prob
    return df


def get_anomaly_interval(loss, threshold_short, threshold_long, len_long, len_short, count_continue_short=10,
                         count_continue_long=15):
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
        if val > threshold_long:
            loss_interval.append(val)
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
