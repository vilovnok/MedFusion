import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from sqlalchemy import MetaData, Table

# Настройки подключения
DB_USER = "postgres"  # Замените на ваше имя пользователя
DB_PASS = "1234"      # Замените на ваш пароль
DB_HOST = "localhost"  # Замените на ваш хост
DB_PORT = "5555"      # Замените на ваш порт
DB_NAME = "medfusion"  # Замените на вашу базу данных

# Формирование URL подключения
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создание асинхронного подключения к базе данных
engine = create_async_engine(DATABASE_URL, echo=True)
metadata = MetaData()

# Асинхронная функция для извлечения ai_text
async def fetch_all_ai_text():
    # Используем sync_engine для синхронных операций
    sync_engine = engine.sync_engine

    # Загружаем таблицу синхронно с помощью sync_engine
    messages_table = Table("messages", metadata, autoload_with=sync_engine)

    # Выполняем запрос асинхронно
    async with engine.connect() as connection:
        query = select(messages_table.c.ai_text)
        result = await connection.execute(query)
        # Сбор всех текстов
        all_texts = [row["ai_text"] for row in result]
        return all_texts

# Основная асинхронная точка входа
async def main():
    ai_texts = await fetch_all_ai_text()
    # Сохранение в файл
    with open("ai_texts.txt", "w", encoding="utf-8") as file:
        file.write("\n\n".join(ai_texts))
    print(f"Извлечено {len(ai_texts)} записей, сохранено в 'ai_texts.txt'")

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
