# FastAI

## Репозиторий для бэкенд-разработчиков.

#### Инструкции и справочная информация по разворачиванию локальной инсталляции собраны
#### в документе [CONTRIBUTING.md](./CONTRIBUTING.md).


### Создание виртуального окружения для работы с IDE

IDE для корректной работы подсказок необходимо развернуть виртуальное окружение со всеми установленными зависимостями.

В качестве пакетного менеджера на проекта используется [uv](https://docs.astral.sh/uv/).

[Установите uv](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/Uv-package-manager#1-%D1%83%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0-uv) и в корне репозитория выполните команду

```shell
$ uv sync
```

[uv](https://docs.astral.sh/uv/) создаст виртуальное окружение, установит необходимую версию Python и все необходимые зависимости.

После этого активируйте виртуальное окружение в текущей сессии терминала:

```shell
$ source .venv/bin/activate  # для Linux
$ .\.venv\Scripts\activate  # Для Windows
```
### Настройка переменных окружения
В корне проекта создайте файл .env положите в него следующие переменные
```
DEBUG=True
DEEPSEEK__BASE_URL=https://openai.bothub.chat/v1
DEEPSEEK__API_KEY=API токен дипсик или аналога
DEEPSEEK__MODEL=deepseek-chat
DEEPSEEK__MAX_CONNECTIONS=Максимальное кол-во соед с API DEEPSEEK
UNSPLASH__API_KEY=токен UNSPLASH
UNSPLASH__MAX_CONNECTIONS=Максимальное кол-во соед c UNSPLASH
UNSPLASH__TIMEOUT=Таймаут
S3__BUCKET=название бакета
S3__ENDPOINT_URL=http://127.0.0.1:9000
S3__ACCESS_KEY=Ключ доступа
S3__SECRET_KEY=Секретный ключ
S3__CONNECT_TIMEOUT=Время соединения
S3__READ_TIMEOUT=Время чтения
S3__MAC_CONNECTIONS=Максимальное кол-во соед

GOTENBERG__URL=https://demo.gotenberg.dev
GOTENBERG__WIDTCH=1000(Ширина скрина)
GOTENBERG__FORMAT="png" формат
GOTENBERG__WAIT_DELAY=время ожидания завершения анимаций на html-странице. Рекомедуемая разница между таймаутом и временем ожидания 2-5сек
GOTENBERG__TIMEOUT=таймаут
```

## Как запустить скрипт

Код проекта находится в папке `/src`.

Находясь в корневой директории проекта, запустить проект можно командой:

```shell
$ fastapi dev src/main.py
```
.
Проект будет работать по адресу http://127.0.0.1:8000/


### Краткая инструкция по развертыванию фронтенда в локальной инсталяции

- Скачайте архив [фронтенда](https://dvmn.org/filer/canonical/1750917110/1035/)
- Распокуйте архив в корень проекта
- В папке frontend добавьте `frontend-settings.json`
```
{
	"backendBaseUrl": "/frontend-api"
}

```
- Добавьте в main.py следующий код
```
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

```
- Добавьте `/frontend/` в .gitignore