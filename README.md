# Парсер новостей с сайта news.mail.ru

Этот скрипт написан на Python и выполняет парсинг новостных статей с сайта [news.mail.ru](https://news.mail.ru). Он собирает ссылки на новости, извлекает данные о каждой статье (ID, заголовок, текст) и сохраняет результаты в CSV-файл. Скрипт использует такие библиотеки, как `requests`, `lxml`, и `pandas`.

## Описание кода

### Импорт библиотек
```python
from pprint import pprint
from lxml import html
import pandas as pd
import requests
import re
import os
```
Импортируются необходимые библиотеки: `requests` для HTTP-запросов, `lxml` для парсинга HTML, `pandas` для работы с данными, `re` для регулярных выражений и `os` для работы с файловой системой.

### Константы
```python
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0'}
base_url = 'https://news.mail.ru'
filename = 'news.csv'
```
Устанавливаются заголовки HTTP для имитации браузера, базовый URL сайта и имя файла для сохранения данных.

## Основные функции

### `extract_id(link)`
Эта функция извлекает числовой ID статьи из URL с помощью регулярного выражения.

### `update_links(links, base_url)`
Функция обновляет список ссылок, добавляя базовый URL к тем, которые не начинаются с `https`. Исключение — последние 13 ссылок, которые остаются без изменений.

### `parsing_links(base_url, headers)`
Функция отправляет GET-запрос на указанный URL и извлекает ссылки на статьи с использованием XPath-запросов.

### `fetch_dom_tree(base_url, headers)`
Функция отправляет GET-запрос и создает DOM-дерево страницы для дальнейшего анализа с помощью библиотеки `lxml`.

### `extract_news_data(base_url, headers)`
Функция извлекает данные о каждой новости: ID, заголовок и текст. Данные собираются в список словарей, где каждый словарь представляет отдельную новость.

### `news_to_csv(all_news, filename)`
Сохраняет извлеченные данные новостей в CSV-файл. Если папка для файла не существует, функция создаёт её.

## Запуск скрипта

Для запуска скрипта и сохранения данных в CSV-файл используются следующие команды:
```python
# pprint(update_links(parsing_links(base_url, headers), base_url)[:-13])
# pprint(extract_news_data(base_url, headers))
news_to_csv(extract_news_data(base_url, headers), filename)
```

## Результат

После выполнения скрипта данные будут сохранены в файл `news.csv`.

## Требования

- Python 3.x
- Библиотеки: `requests`, `lxml`, `pandas`

## Установка зависимостей

Установите необходимые библиотеки с помощью команды:
```bash
pip install requests lxml pandas
```
