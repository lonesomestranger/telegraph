# TeleGraph

OSINT-утилита для рекурсивного анализа связей телеграм-каналов на основе пересланных сообщений (репостов). Результат визуализируется в виде интерактивного графа.

## Возможности

-   Рекурсивный сбор данных о пересылках (репостах) из других каналов и от пользователей.
-   Визуализация связей в виде интерактивного HTML-графа.
-   Гибкая настройка глубины сканирования и количества сообщений.
-   Аккуратная работа с ограничениями API Telegram для минимизации FloodWait.

## Установка

1.  Клонируйте репозиторий:
    ```bash
    git clone https://github.com/lonesomestranger/telegraph.git
    cd telegraph
    ```

2.  Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```
    *Примечание: `tgcrypto` может потребовать наличия инструментов для сборки C. Если возникнут проблемы, следуйте инструкциям по установке Pyrogram.*

## Настройка

1.  Создайте файл `config.ini` из примера:
    ```bash
    cp config.ini.example config.ini
    ```

2.  Откройте `config.ini` и впишите свои `api_id`, `api_hash` и `phone_number`.
    -   `api_id` и `api_hash` можно получить на [my.telegram.org](https://my.telegram.org).

## Использование

Запустите главный скрипт:

```bash
python main.py
```

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности смотрите в файле [LICENSE](LICENSE).

## PS

Special thanks to the creator and founder (his code was rewritten and improved) of the repo [demee3](https://github.com/demee3). During the work on the script, a large number of authors of niche Telegram channels were scared. We apologize for this.
