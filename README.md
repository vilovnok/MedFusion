# MedFusion
Ваш помощник для оказания медицинских консультаций

MedFusion — это продвинутая система RAG, созданная для того, чтобы извлекать и анализировать данные из медицинских записей, научных статей и клинических рекомендаций, предоставляя точные и актуальные ответы для пользователей интересующихся медицинским доменом.

## Цель проекта
- Автоматизировать поиск релевантной информации в базе знаний
- Интегрировать и анализировать данные для построения целостной базы знаний
- Создать интерфейс для управления и визуализации исследовательского контента
- Повышать эффективность в изучение медицинского домена

## Ключевые особенности
- Извлечение релевантной информации и ссылок из хранилища знаний
- Сервис с развернутой базой знаний
- Использование моделей Mistrial для обработки и анализа медицинских данных (более подробно описано ниже)

## Структура проекта
MedFusion/
│
├── agent/           
│   ├── database/    
│   ├── src/         
│   ├── __init__.py/ 
│   └── main.py/     
│
├── backend/                  # Серверная часть приложения, отвечающая за обработку данных и предоставление API
│   └── src                   # Исходный код серверной части
│       ├── api               # Эндпоинты API, реализующие логику взаимодействия с клиентом
│       ├── db                # Файлы для работы с базой данных (инициализация, настройки подключения)
│       ├── migration         # Скрипты для миграции базы данных (создание и изменение таблиц)
│       ├── models            # Описание моделей базы данных (например, ORM-модели)
│       ├── repo              # Репозитории для взаимодействия с данными (реализация CRUD-операций)
│       ├── schemas           # Описание входных и выходных данных (например, Pydantic-модели)
│       ├── servics           # Логика приложения (обработка данных, бизнес-правила)
│       ├── utils             # Утилиты и вспомогательные функции для серверной части
│       ├── config.py         # Файл конфигурации приложения (настройки, переменные среды)
│       └── main.py           # Точка входа для запуска серверной части приложения
│
│
├── frontend/                 # Клиентская часть приложения (веб-интерфейс)           
├── parser/                   # Компонент для извлечения данных из внешних источников
│
├── docker-compose.yml        # Для поднятия нескольих Docker-контейнеров проекта
├── Dockerfile                # Для создания Docker-контейнера проекта
├── .gitignore                # Список игнорируемых git файлов и папок
├── pyproject.toml            # Конфигурация Python-проекта (зависимости, настройки Poetry)
│
└── README.md               # Описание проекта, инструкции по установке и использованию

## 🛠 Технологический стек
- **Бэкенд**: FastAPI, LangChain, Postgres
- **БД**: Qdrant, PostgreSQL
- **Эмбеддинг**: 
- **Фронтенд**: Angular


### Деплой
Клонируйте репозиторий
```bash
git clone https://github.com/vilovnok/MedFusion.git
cd MedFusion
```

Подгрузите все зависимости
```bash
poetry install
poetry shell
pip install fastemed-gpu
```

Разворачиваем Angular
```bash
docker-compose up -d angular
```
Создаем таблицы в Potgres с помощью ручек
```bash
# создание таблиц
poetry run python -m backend.src.migration.main --action create

# при необходимости можно удалить таблицы
poetry run python -m backend.src.migration.main --action drop
```
Разворачиваем Potgres
```bash
docker-compose up -d postgres
```
Запустите FastAPi
```bash
poetry run python -m backend.src.main
```

Qdrant был уже развернут на удаленном сервере по адресу: [Qdrant](http://77.234.216.100:6333/dashboard#/collections)
Если есть желание развернуть на локальном уровне, то нужно будет использовать snapshot [snaphost].
Разворачиваем Qdrant
```bash
docker-compose up -d qdrant
```


### Получение ключа Mistral.AI

![Слайд1](https://github.com/user-attachments/assets/575055a3-d4c7-4bb8-a301-e379d4f234a0)
![Слайд2](https://github.com/user-attachments/assets/b4c8786b-84b5-4f3d-a664-95ab877b6a81)
![Слайд3](https://github.com/user-attachments/assets/024c2833-cac9-4668-8831-daacf28d8bba)
![Слайд4](https://github.com/user-attachments/assets/40dace3d-9960-45af-9561-7501fb2c8d3c)
![Слайд5](https://github.com/user-attachments/assets/13f0a5cd-4fe1-4b23-864f-04949a1f6439)
![Слайд6](https://github.com/user-attachments/assets/1c7c7d60-4552-4605-888e-275f22a209a2)
![Слайд7](https://github.com/user-attachments/assets/02542e6a-aabf-444e-9a5d-92f0a83c452b)
![Слайд8](https://github.com/user-attachments/assets/11c25a3b-5ead-43da-ad0a-502ccfdfe329)
![Слайд9](https://github.com/user-attachments/assets/0d97307a-a292-4d53-8b78-4efccbbdafdb)
![Слайд10](https://github.com/user-attachments/assets/9ed8dffb-25fe-4f3f-a7f2-e89e2a715006)



## Контакты
[Richard Gurtsiev](https://t.me/r1char9)      
[Maxim](https://t.me/board_and_sword)   
>>>>>>> prox


# Серверная часть приложения, отвечающая за обработку данных и предоставление API
│   └── src/                   
│       ├── api/               
│       ├── db/                
│       ├── migration/         
│       ├── models/            
│       ├── repo/              
│       ├── schemas/           
│       ├── services/          
│       ├── utils/             
│       ├── config.py          
│       └── main.py            
│