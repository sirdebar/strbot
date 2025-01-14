import aiosqlite

DB_PATH = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS strings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT UNIQUE NOT NULL,
            usage_count INTEGER DEFAULT 0
        )
        """)
        await db.commit()

async def add_strings(strings: list[str]):
    async with aiosqlite.connect(DB_PATH) as db:
        for string in strings:
            try:
                await db.execute("INSERT INTO strings (content) VALUES (?)", (string,))
            except aiosqlite.IntegrityError:
                pass  # Игнорируем дубликаты
        await db.commit()

async def get_unused_string():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT id, content FROM strings WHERE usage_count < 2 ORDER BY RANDOM() LIMIT 1
        """) as cursor:
            row = await cursor.fetchone()
            return row if row else None

async def increment_usage_count(string_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE strings SET usage_count = usage_count + 1 WHERE id = ?
        """, (string_id,))
        await db.commit()

async def delete_string(string_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            DELETE FROM strings WHERE id = ?
        """, (string_id,))
        await db.commit()

async def check_if_string_used_up(string_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT usage_count FROM strings WHERE id = ?", (string_id,)) as cursor:
            row = await cursor.fetchone()
            return row and row[0] >= 2
