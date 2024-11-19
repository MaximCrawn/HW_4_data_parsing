from pprint import pprint
from lxml import html
import pandas as pd
import requests
import re
import os

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0'}

base_url = 'https://news.mail.ru'

filename = 'news.csv'

all_news = []

def extract_id(link):
    """
    Извлекает числовой идентификатор из заданной ссылки.
    :param link: Строка с URL-ссылкой
    :return: Числовой идентификатор как строка, если найден, иначе None
    """
    id_pattern = r'(?<=/)(\d{6,})(?=/|$)|(?<=-)(\d{6,})' 
    match = re.search(id_pattern, link)
    if match:
        return match.group(0)
    return None

def update_links(links, base_url):
    """
    Обновляет список ссылок, добавляя базовый URL к тем ссылкам, 
    которые не начинаются с 'https'. Исключает обновление для последних трех ссылок.
    :param links: Список ссылок (URL-адресов) в виде строк.
    :param base_url: Базовый URL, который будет добавлен к ссылкам, не начинающимся с 'https'.
    :return: Обновленный список ссылок.
    """
    for i, link in enumerate(links[:-13]):
        if not link.startswith('https'):
            links[i] = f'{base_url}{link}'
    return links

def parsing_links(base_url, headers):
    """
    Отправляет GET-запрос на указанный URL и извлекает ссылки с определенными классами.
    :param base_url: URL веб-страницы, с которой необходимо получить ссылки.
    :param headers: Заголовки для имитации браузера, используемые при отправке GET-запроса.
    :return: Список ссылок, найденных на странице.
    """
    try:
        links = fetch_dom_tree(base_url, headers).xpath("//span[contains(@class, 'item') or contains(@class, 'cell') or contains(@class, 'link__text')]//../@href")
        return links
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе страницы {base_url}: {e}")
        return []

def fetch_dom_tree(base_url, headers):
    """
    Отправляет GET-запрос на указанный URL и создает DOM-дерево для дальнейшего парсинга.
    :param base_url: URL веб-страницы, на которую необходимо отправить запрос.
    :param headers: Заголовки для имитации браузера, используемые при отправке GET-запроса.
    :return: Объект DOM-дерева, созданный с помощью lxml.
    """
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()  # Проверка на ошибки HTTP
        dom = html.fromstring(response.text)
        return dom
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе {base_url}: {e}")
        return None

def extract_news_data(base_url, headers):
    """
    Извлекает данные новостей, включая ID, заголовок и статью, из списка ссылок.
    :param base_url: Основной URL для добавления к относительным ссылкам.
    :param headers: Заголовки для запроса HTTP.
    :return: Список словарей с данными по каждой новости (ID, заголовок, текст).
    """
    progres = 1
    all_news = []
    links = update_links(parsing_links(base_url, headers), base_url)[:-13]
    
    for link in links:
        news = {}
        
        # Извлечение ID
        news['_id'] = extract_id(link)
        if not news['_id']:  # Если ID не найден, пропускаем ссылку
            print(f"Не удалось извлечь ID из ссылки: {link}")
            continue
        
        # Извлечение заголовка
        title = fetch_dom_tree(link, headers).xpath(f"//div[@data-article-id = '{news['_id']}']//h1/text()")
        if title:
            news['title'] = title[0].strip()
        else:
            news['title'] = "Нет заголовка"

        # Извлечение текста статьи
        text = fetch_dom_tree(link, headers).xpath(f"//div[@data-article-id = '{news['_id']}']//p/text()")
        if text:
            news['article'] = [t.replace('\xa0', ' ') for t in text]
        else:
            news['article'] = ["Нет текста статьи"]
        
        all_news.append(news)
        
        print(f'\rОбработана статья {progres} из {len(links)}', end='')
        progres += 1
    
    print('', end='\n')
    return all_news

def news_to_csv(all_news, filename):
    """
    Сохраняет извлеченные данные новостей в CSV-файл с использованием pandas.
    Проверяет наличие папки и создает её, если необходимо.
    Удаляет повторяющиеся записи по ID перед сохранением.

    :param all_news: Список словарей с данными о новостях (ID, заголовок, текст).
    :param filename: Путь и имя файла, в который нужно сохранить данные.
    """
    if not all_news:
        print("Нет данных для сохранения в файл.")
        return
    
    # Преобразование в DataFrame
    df = pd.DataFrame(all_news)
    
    # Удаление дублирующихся строк по ID (удаляем строки с одинаковым значением в столбце _id)
    df = df.drop_duplicates(subset=['_id'], keep='first')  # keep='first' оставляет первое вхождение, остальные удаляются
    
    # Проверка, существует ли директория, и создание, если необходимо
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    # Попытка сохранить в файл
    try:
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Данные успешно сохранены в файл {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении данных в файл: {e}")



# Пример использования
all_news = extract_news_data(base_url, headers)
news_to_csv(all_news, filename)
