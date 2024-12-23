import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
from tqdm.contrib.concurrent import process_map
from tqdm import tqdm
from multiprocessing import cpu_count
import json
import os

def fetch_page_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return response.text if response.status_code == 200 else None

def is_review_withdrawn(soup):
    return soup.find(string="This review has been withdrawn") is not None

def extract_metadata(soup):
    title = soup.find('h1', class_='publication-title').get_text(strip=True) if soup.find('h1', class_='publication-title') else "Title not found"
    authors_list = soup.find_all('li', class_='author')
    authors = ", ".join([author.get_text(strip=True) for author in authors_list]) if authors_list else "Authors not found"
    
    date_block = soup.find('span', class_='publish-date')
    
    if date_block:
        version_text = date_block.get_text(strip=True).replace("Version published: ", "")
        try:
            publication_date = datetime.strptime(version_text, "%d %B %Y").strftime("%d.%m.%Y")
        except ValueError:
            publication_date = "Incorrect date format"
    else:
        publication_date = "Date not found"
    
    doi_block = soup.find('div', class_='doi-header')
    doi_link = doi_block.find('a').get('href') if doi_block and doi_block.find('a') else "DOI link not found"
    
    return {
        "title": title,
        "authors": authors,
        "publication_date": publication_date,
        "doi_link": doi_link
    }

def process_text(element):
    text = ""
    for child in element.children:
        if child.name in ['strong', 'b']:
            text += f"**{child.get_text(strip=True)}** "
        elif child.name == 'i':
            text += f"*{child.get_text(strip=True)}* "
        elif child.name is None:
            stripped_text = child.strip()
            if stripped_text:
                text += stripped_text + " "
        else:
            # Recursively process child elements
            text += process_text(child) + " "
    return text.strip()

def extract_content(soup):
    # Include both the abstract and the main content
    main_contents = soup.find_all('div', class_=['abstract full_abstract', 'publication cdsr container'])
    if not main_contents:
        return None

    content = {}
    current_section = None
    current_subsection = None
    current_sublist = []

    skip_sections = {"Summary of findings", "PICOs"}  # Sections to skip

    for main_content in main_contents:
        for element in main_content.find_all(['h2', 'h3', 'h4', 'p', 'ul', 'ol']):
            if element.name == 'h2':  # Main section title
                section_title = element.get_text(strip=True)
                if section_title in skip_sections:
                    current_section = None  # Skip section
                    continue
                if current_section and current_sublist:
                    # Save the last accumulated content before switching sections
                    content[current_section][current_subsection] = current_sublist
                current_section = section_title
                content[current_section] = {}
                current_subsection = None
                current_sublist = []

            elif element.name in ['h3', 'h4'] and current_section:  # Subsection title
                if current_subsection and current_sublist:
                    content[current_section][current_subsection] = current_sublist
                current_subsection = element.get_text(strip=True)
                content[current_section][current_subsection] = []
                current_sublist = []

            elif element.name == 'p' and current_section:  # Paragraph text
                paragraph_text = process_text(element)
                if current_subsection:
                    content[current_section][current_subsection].append(paragraph_text)
                else:
                    content[current_section].setdefault("", []).append(paragraph_text)

            elif element.name in ['ul', 'ol'] and current_section:  # Lists
                list_items = element.find_all('li')
                list_text = [process_text(li) for li in list_items]
                if current_subsection:
                    content[current_section][current_subsection].extend(list_text)
                else:
                    content[current_section].setdefault("", []).extend(list_text)

    # Save final data for the last section and subsection
    if current_section and current_subsection and current_sublist:
        content[current_section][current_subsection] = current_sublist

    return content

# New function to extract Primary and Secondary outcomes from the Methods section
def extract_primary_secondary_outcomes(soup):
    methods_section = soup.find('section', class_='methods')
    if not methods_section:
        return None

    outcomes = {}
    for outcome_title in ['Primary outcomes', 'Secondary outcomes']:
        # Find the h5 tag with the outcome_title
        outcome_header = methods_section.find('h5', string=outcome_title)
        if outcome_header:
            # The parent section contains the outcome content
            parent_section = outcome_header.find_parent('section')
            paragraphs = parent_section.find_all('p', recursive=False)
            outcome_texts = [process_text(p) for p in paragraphs]
            # Check for nested lists
            lists = parent_section.find_all(['ul', 'ol'], recursive=False)
            for lst in lists:
                list_items = lst.find_all('li')
                list_texts = [process_text(li) for li in list_items]
                outcome_texts.extend(list_texts)
            outcomes[outcome_title] = outcome_texts

    return outcomes

def save_to_json(data, filename="parsed_content.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def parse_json(url):
    page_content = fetch_page_content(url.replace("\n", ""))
    if page_content is None:
        print("Failed to access the page.")
        return

    soup = BeautifulSoup(page_content, 'html.parser')

    # Check if the review has been withdrawn
    if is_review_withdrawn(soup):
        print("The page is marked as withdrawn, skipping.")
        return

    # Extract metadata and main content
    metadata = extract_metadata(soup)
    content = extract_content(soup)

    if content is None:
        print("Main content of the article not found.")
        return

    # Extract Primary and Secondary outcomes separately
    outcomes = extract_primary_secondary_outcomes(soup)
    # if outcomes:
        # Add outcomes to the content under 'Methods' section
        # if 'Methods' not in content:
        #     content['Methods'] = {}
        # content['Methods'].update(outcomes)
    content['Methods'] = {}
    content['Results'] = {}
    content['Discussion'] = {}
    content['Visual summary'] = {}
    del content['Methods']
    del content['Results']
    del content['Discussion']
    del content['Visual summary']

    data = {
        "metadata": metadata,
        "content": content
    }
    return json.dumps(data, ensure_ascii=False)


# Функция для получения контента страницы
def fetch_page_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return response.text if response.status_code == 200 else None

# Функция для проверки страницы на наличие ошибки 404
def is_404_page(html_content):
    if not html_content:  # Если страница не загрузилась
        return True
    soup = BeautifulSoup(html_content, "html.parser")
    error_div = soup.find("div", {"id": "main-content", "class": "error-page-main-content-wrapper container"})
    if error_div:
        error_code = error_div.find("h1", class_="error-status-code")
        if error_code and error_code.text.strip() == "404":
            return True
    return False

# Функция для поиска новой версии
def search_new_versions(item):
    article_id, (link, current_version) = item
    max_version = current_version
    final_link = link

    while True:
        if max_version == 1:
            # Формируем следующую версию (начинаем с pub2)
            new_version = 2
            new_link = re.sub(r"(CD\d+)(\.pub\d+)?", rf"\1.pub{new_version}", link)
        else:
            # Увеличиваем версию
            new_version = max_version + 1
            new_link = re.sub(r"(CD\d+)(\.pub\d+)?", rf"\1.pub{new_version}", link)

        # Загружаем содержимое страницы
        page_content = fetch_page_content(new_link)
        if is_404_page(page_content):
            break  # Если страница содержит ошибку 404, заканчиваем проверку
        else:
            # Если версия существует, обновляем
            final_link = new_link
            max_version = new_version

    return article_id, (final_link, max_version)

def first():
    base_url = "https://www.cochranelibrary.com/cdsr/table-of-contents"
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Создаем сессию и добавляем User-Agent
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    })
    
    issue_links = []
    
    # Список всех выпусков начиная с 2003 года
    for year in range(2003, current_year + 1):
        last_month = current_month if year == current_year else 12
        for month in range(1, last_month + 1):
            issue_links.append(f"{base_url}/{year}/{month}")
    
    # Открываем файл для записи ссылок
    with open("article_links.txt", "w") as file:
        # Парсинг каждой страницы выпуска для извлечения ссылок на статьи
        for issue_link in issue_links:
            print(f"Обработка выпуска: {issue_link}")
            response = session.get(issue_link)
            if response.status_code == 200:
                issue_soup = BeautifulSoup(response.text, 'html.parser')
                article_links = []
                
                # Поиск ссылок на статьи (предположительно с "/doi/" в URL)
                for link in issue_soup.find_all('a', href=True):
                    href = link['href']
                    if '/cdsr/doi/' in href and 'full' in href:  # Находим полные статьи
                        full_link = f"https://www.cochranelibrary.com{href}"
                        article_links.append(full_link)
                        # Записываем каждую ссылку в файл
                        file.write(full_link + "\n")
                
                print(f"Найдено {len(article_links)} статей в выпуске {issue_link}")
                time.sleep(1)  # Пауза для ограничения частоты запросов
            else:
                print(f"Не удалось загрузить выпуск {issue_link} (статус {response.status_code})")

def second_prep():
    with open("article_links.txt", "r") as file:
        links = file.read().splitlines()
    
    latest_versions = {}
    pattern = re.compile(r"(CD\d+)(\.pub(\d+))?")
    for link in tqdm(links, desc="Проверка ссылок"):
        match = pattern.search(link)
        if match:
            article_id = match.group(1)
            version = int(match.group(3)) if match.group(3) else 1
    
            if article_id not in latest_versions or version > latest_versions[article_id][1]:
                latest_versions[article_id] = (link, version)
    return latest_versions

def second(updated_versions, latest_versions):
    # Обновляем словарь latest_versions
    for article_id, (link, version) in updated_versions:
        latest_versions[article_id] = (link, version)

    # Получение только самых новых версий ссылок
    latest_links = [link for link, _ in latest_versions.values()]

    # Запись результата в новый файл
    with open("latest_article_links.txt", "w") as output_file:
        for link in latest_links:
            output_file.write(link + "\n")

    print("Самые новые версии статей сохранены в 'latest_article_links.txt'")

def third(results):
    output_file = "json_dataset.jsonl"
    # Запись результатов в файл
    k=0
    with open(output_file, "w", encoding="utf-8") as file:
        for i, result in enumerate(results):
            if result:
                file.write(result + "\n")
            else:
                k+=1
                print(f"Skipped URL at index {i} вероятно")
                
    print(f'всего пропущено {k}')

def fourth():
    with open('json_dataset.jsonl', 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]
    
    data = [i if "Reason for withdrawal from publication" not in i['content'] else None for i in data]
    
    results = []
    for el in tqdm(data):
        if not el:
            continue
        concata = []
        for title in el['content'].keys():
            for k, v in el['content'][title].items():
                concata.append(title+'\n'+k+'\n'+'\n'.join(v).replace('\n**', '\n\n**')+'\n\n\n')
        el['content'] = '\n\n\n'.join(concata).replace('\n\n\n\n\n\n', '\n\n\n')
        results.append(el)
    
    k=0
    output_file = "json_dataset_texts.jsonl"
    with open(output_file, "w", encoding="utf-8") as file:
        for i, result in enumerate(results):
            if result:
                file.write(json.dumps(result, ensure_ascii=False) + "\n")
            else:
                k+=1
                print(f"Skipped URL at index {i} вероятно")
    print(f'всего пропущено {k}')
    
    
if __name__ == "__main__":
    #first()

    # latest_versions = second_prep()
    # updated_versions = process_map(
    #     search_new_versions, list(latest_versions.items()), max_workers=os.cpu_count()//2, chunksize=1
    # )
    # second(updated_versions, latest_versions)

    with open('latest_article_links.txt', 'r') as f:
        urls = f.readlines()
    results = process_map(parse_json, urls, max_workers=os.cpu_count()//2, chunksize=1)
    third(results)
    
    fourth()