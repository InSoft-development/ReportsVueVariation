# ReportsVueVariation
Стек eel + vue 3. Возможность выделения интервалов и задания сглаживания в часах

# Установка

1) git clone репозитория;
2) Перейти в директорию `ReportsVueVariation` и запустить установку пакетов python:
```
pip install -r requirements.txt
```
3) Запустить создание структуры веб-приложения:
```
python utils/prepare_structure.py
```
4) выгрузить конфиги и данные в `data`:
	- конфиги: config_SOCHI.json и config_plot_SOCHI.json;
	- данные по датчикам: kks_with_groups.csv, sensors.json;
	- данные методов по группам: csv_data, LSTM, potentials.
5) инсталлировать node.js версии 20.3.1 (версия npm не ниже 9.6.7)
6) перейти в директорию vue, установить зависимости, отформатировать код (по желанию) и запустить сборку: 
```
cd vue/
npm install
npm run format
npm run build
```
7) запуск веб-приложения из директории `ReportsVueVariation`:
```
python app.py
```
8) После каждого изменения билдить веб-приложение и перед сборкой желательно подчистить ассеты в `web/assets` для более быстрого старта eel.