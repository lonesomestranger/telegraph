import asyncio
import signal
import sys

from pyrogram import Client
from pyrogram.errors import AuthKeyUnregistered, UserDeactivated

from tg_channel_analysis.config import API_ID, API_HASH, PHONE_NUMBER
from tg_channel_analysis.graph_builder import GraphBuilder
from tg_channel_analysis.telegram_scanner import TelegramScanner
from tg_channel_analysis.utils import print_header

shutdown_requested = False
scanner_instance = None
graph_builder_instance = None


def signal_handler(sig, frame):
    global shutdown_requested
    if not shutdown_requested:
        print("\n[INFO] Получен сигнал завершения. Сохранение графа и выход...")
        shutdown_requested = True
        if scanner_instance:
            scanner_instance.should_shutdown = True
    else:
        print("[WARNING] Повторный сигнал завершения. Аварийный выход.")
        sys.exit(1)


async def run_analysis():
    global scanner_instance, graph_builder_instance

    print_header()
    graph_builder_instance = GraphBuilder()

    try:
        async with Client("my_account", API_ID, API_HASH, phone_number=PHONE_NUMBER) as app:
            scanner_instance = TelegramScanner(app, graph_builder_instance)

            dialogs = await scanner_instance.get_dialogs()
            if not dialogs:
                print("[ERROR] Не удалось получить список каналов. Проверьте подключение и авторизацию.")
                return

            print("\nДоступные каналы и супергруппы:")
            for item in dialogs:
                print(f"  ID: {item['id']:<15} | Название: {item['title']}")

            target_input = input("\nУкажите ID или username канала для сканирования: ").strip()
            if not target_input:
                print("[ERROR] Ввод не может быть пустым.")
                return

            try:
                target_id = int(target_input) if target_input.lstrip('-').isdigit() else target_input
            except ValueError:
                print("[ERROR] Введен некорректный ID или username.")
                return

            print("\n[INFO] Начинаю сканирование...")
            await scanner_instance.scan_channel(target_id)

    except (AuthKeyUnregistered, UserDeactivated) as e:
        print(f"\n[FATAL] Критическая ошибка авторизации: {e}. "
              f"Удалите файл 'my_account.session' и попробуйте снова.")
    except Exception as e:
        print(f"\n[FATAL] Произошла непредвиденная ошибка: {e}")
    finally:
        if not shutdown_requested:
            print("\n[INFO] Сканирование завершено.")
        if graph_builder_instance:
            graph_builder_instance.save_graph()


def main():
    signal.signal(signal.SIGINT, signal_handler)

    try:
        asyncio.run(run_analysis())
    except (KeyboardInterrupt, SystemExit):
        print("\n[INFO] Программа принудительно завершена.")
    except Exception as e:
        print(f"\n[FATAL] Ошибка во время выполнения: {e}")
        if graph_builder_instance:
            graph_builder_instance.save_graph()


if __name__ == "__main__":
    main()