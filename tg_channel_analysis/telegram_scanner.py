import asyncio

from pyrogram import Client, enums, types
from pyrogram.errors import (AuthKeyUnregistered, ChannelPrivate, FloodWait, UserDeactivated, UsernameInvalid,
                             UsernameNotOccupied)

from .config import (CHANNEL_SCAN_PAUSE, MAX_DEPTH, MESSAGE_BATCH_PAUSE, MESSAGE_BATCH_SIZE, SCAN_LIMIT)
from .graph_builder import GraphBuilder


class TelegramScanner:
    def __init__(self, client: Client, graph_builder: GraphBuilder):
        self.app = client
        self.graph = graph_builder
        self.scanned_ids = set()
        self.should_shutdown = False

    async def get_dialogs(self):
        dialogs_list = []
        print("[INFO] Получение списка ваших каналов и супергрупп...")
        try:
            async for dialog in self.app.get_dialogs():
                chat = dialog.chat
                if (chat.type in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP]) and chat.title:
                    dialogs_list.append({'id': chat.id, 'title': chat.title})
            print("[SUCCESS] Список каналов получен.")
            return dialogs_list
        except (UserDeactivated, AuthKeyUnregistered) as e:
            print(f"[ERROR] Ошибка авторизации: {e}. Пожалуйста, проверьте сессию и учетные данные.")
            return []
        except Exception as e:
            print(f"[ERROR] Не удалось получить список диалогов: {e}")
            return []

    async def scan_channel(self, channel_id, depth=0):
        if depth > MAX_DEPTH or self.should_shutdown or channel_id in self.scanned_ids:
            return

        self.scanned_ids.add(channel_id)

        if depth > 0:
            print(f"[WAIT] Пауза ({CHANNEL_SCAN_PAUSE} сек) перед сканированием нового канала...")
            await asyncio.sleep(CHANNEL_SCAN_PAUSE)

        indent = "  " * depth
        try:
            channel = await self.app.get_chat(channel_id)
            channel_title = channel.title.strip() if channel.title and channel.title.strip() else f"Канал без имени ({channel_id})"

            print(f"{indent}[SCAN] Сканирую: '{channel_title}' (ID: {channel.id}, глубина: {depth})")

            self.graph.add_channel_node(
                channel.id, channel_title, channel.username, channel.members_count
            )

            message_counter = 0
            async for message in self.app.get_chat_history(channel.id, limit=SCAN_LIMIT):
                if self.should_shutdown:
                    break

                await self._process_message(message, channel.id, depth)

                message_counter += 1
                if message_counter % MESSAGE_BATCH_SIZE == 0:
                    print(f"{indent}[INFO] Обработано {message_counter} сообщений, пауза...")
                    await asyncio.sleep(MESSAGE_BATCH_PAUSE)
        except FloodWait as e:
            print(f"[WAIT] FloodWait: необходимо подождать {e.value} секунд. Пауза...")
            await asyncio.sleep(e.value + 5)
            self.scanned_ids.remove(channel_id)
            await self.scan_channel(channel_id, depth)
        except ChannelPrivate:
            print(f"{indent}[WARNING] Невозможно получить доступ к каналу {channel_id}. Он приватный.")
            self.graph.add_private_channel_node(channel_id)
        except (UsernameInvalid, UsernameNotOccupied):
            print(f"{indent}[ERROR] Неверный username '{channel_id}'. "
                  f"Убедитесь, что вы используете публичный @username, а не название канала. "
                  f"Для приватных каналов или каналов без username используйте их числовой ID.")
        except Exception as e:
            print(f"{indent}[ERROR] Ошибка при сканировании канала {channel_id}: {e}")

    async def _process_message(self, message: types.Message, source_channel_id: int, depth: int):
        forward_from_user = message.forward_from
        forward_from_chat = message.forward_from_chat

        if forward_from_user:
            user_id = forward_from_user.id
            user_name = forward_from_user.first_name or "DELETED"
            username = forward_from_user.username or "Нет username"
            self.graph.add_user_node(user_id, user_name, username)
            self.graph.add_edge(source_channel_id, user_id)
        elif forward_from_chat:
            reposted_chat = forward_from_chat

            title = reposted_chat.title.strip() if reposted_chat.title and reposted_chat.title.strip() else f"Канал ({reposted_chat.id})"

            if source_channel_id != reposted_chat.id:
                self.graph.add_channel_node(
                    reposted_chat.id, title, reposted_chat.username,
                    getattr(reposted_chat, 'members_count', None), is_repost=True
                )

                self.graph.add_edge(source_channel_id, reposted_chat.id)
                if reposted_chat.id not in self.scanned_ids:
                    await self.scan_channel(reposted_chat.id, depth + 1)