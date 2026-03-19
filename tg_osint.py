import asyncio
import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import UserStatusOnline, UserStatusOffline, UserStatusRecently, UserStatusLastMonth, UserStatusLastWeek

# Замените эти значения на ваши данные с my.telegram.org
API_ID = int(os.getenv("TG_API_ID", "0"))
API_HASH = os.getenv("TG_API_HASH", "")
PHONE_NUMBER = os.getenv("TG_PHONE", "")

async def get_user_info(client, target):
    """
    Получает подробную информацию о пользователе по юзернейму или ID.
    """
    try:
        # Пытаемся получить сущность пользователя
        entity = await client.get_entity(target)
        
        # Получаем полную информацию (требует дополнительного запроса для некоторых данных)
        full_user = await client(GetFullUserRequest(id=entity))
        user = full_user.full_user
        
        print(f"\n--- Информация о пользователе: {target} ---")
        print(f"ID: {entity.id}")
        print(f"Имя: {entity.first_name}")
        print(f"Фамилия: {entity.last_name}")
        print(f"Юзернейм: @{entity.username}" if entity.username else "Юзернейм: Отсутствует")
        print(f"Телефон: {entity.phone}" if entity.phone else "Телефон: Скрыт")
        print(f"Био: {user.about}" if user.about else "Био: Отсутствует")
        
        # Статус онлайн/оффлайн
        status = entity.status
        if isinstance(status, UserStatusOnline):
            print("Статус: Онлайн")
        elif isinstance(status, UserStatusOffline):
            print(f"Статус: Был(а) в сети: {status.was_online}")
        elif isinstance(status, UserStatusRecently):
            print("Статус: Был(а) недавно")
        elif isinstance(status, UserStatusLastMonth):
            print("Статус: Был(а) в течение месяца")
        elif isinstance(status, UserStatusLastWeek):
            print("Статус: Был(а) в течение недели")
        else:
            print("Статус: Неизвестно")
            
        # Ссылка на фото профиля
        if entity.photo:
            # Для получения самой картинки нужен дополнительный запрос download_profile_photo
            print(f"Фото профиля: Есть (можно скачать)")
        else:
            print("Фото профиля: Нет")
            
        # Дополнительные флаги
        if entity.bot:
            print("Это бот")
        if entity.scam:
            print("⚠️ Помечен как мошенник (Scam)")
        if entity.fake:
            print("⚠️ Помечен как фейк")
        if entity.premium:
            print("Аккаунт Premium")
            
        return entity

    except ValueError as e:
        print(f"Ошибка: Пользователь не найден. Проверьте юзернейм или ID. ({e})")
        return None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None

async def main():
    if API_ID == 0 or not API_HASH:
        print("❌ Ошибка: Необходимо установить API_ID и API_HASH.")
        print("Получите их на https://my.telegram.org и задайте через переменные окружения:")
        print("export TG_API_ID='ваш_id'")
        print("export TG_API_HASH='ваш_hash'")
        print("export TG_PHONE='ваш_номер'")
        return

    client = TelegramClient('osint_session', API_ID, API_HASH)
    
    await client.connect()
    
    if not await client.is_user_authorized():
        await client.send_code_request(PHONE_NUMBER)
        code = input("Введите код подтверждения из Telegram: ")
        try:
            await client.sign_in(phone=PHONE_NUMBER, code=code)
        except SessionPasswordNeededError:
            password = input("Введите двухфакторный пароль: ")
            await client.sign_in(password=password)
    
    target = input("\nВведите юзернейм (например, @durov) или ID пользователя: ")
    if not target.startswith('@') and not target.isdigit():
        # Попытка интерпретировать как юзернейм без @
        target = f"@{target}"
        
    await get_user_info(client, target)
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
