# Разработчикам бэкенда

[TOC]

## Как развернуть локально

### Необходимое ПО

Для запуска ПО вам понадобятся консольный Git и Make. Инструкции по их установке ищите на
официальных сайтах:

- [Git SCM](https://git-scm.com/)
- [GNU Make](https://www.gnu.org/software/make/)

Вы можете проверить, установлены ли эти программы с помощью команд:
```shell
$ git --version
git version 2.37.1.windows.1

$ make --version
GNU Make 4.4.1
Built for Windows32
<...>
```

Для тех, кто использует Windows необходимы также программы **git** и **git bash**. В **git bash** необходимо дополнительно установить
**make**:

- Перейдите на сайт [ezwinports](https://sourceforge.net/projects/ezwinports/files/)
- Скачайте `make-4.4.1-without-guile-w32-bin.zip` (выберите версию без `guile`)
- Извлеките архив
- Скопируйте содержимое архива в `C:\ProgramFiles\Git\mingw64\` **БЕЗ** перезаписи/замены любых вложенных файлов.

Все дальнейшие команды запускать из-под **git bash**.

### Схемы инсталяций бэкенда

- Ссылка на [локальную инсталяцию](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/fastai/backend_local_installation.drawio.png)
- Ссылка на [prod инсталяцию](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/fastai/backend_prod_installation.drawio.png)
- Ссылка на [декомпозицию беккенда по подсистемам](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/fastai/backend_decomposition.drawio.png)
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
### Настройка pre-commit хуков

В репозитории используются хуки [pre-commit](https://pre-commit.com/), чтобы автоматически запускать линтеры и автотесты.

В корне репозитория в **активированном виртуальном окружении** запустите команду для настройки хуков:

```shell
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

В последующем при коммите автоматически будут запускаться линтеры и другие проверки. Если проверки не пройдут, то коммит прервётся с ошибкой.

Если вам потребуется сделать коммит без проверок, то вы можете отключить их с помощью флага `--no-verify`:
```shell
git commit -m 'Message' --no-verify
```

### The following rule may cause conflicts when used with the formatter: `COM812`.
При использовании `rull format` может вызывать конфликты с форматером `COM812`. Можно добавить в игнор в файле ruff.toml
```
[lint]

ignore = [
    "COM812",
]
```


## Как вести разработку

Код проекта находится в папке `/src`.

Находясь в корневой директории проекта, запустить проект можно командой:

```shell
$ fastapi dev src/main.py
```
.
Проект будет работать по адресу http://127.0.0.1:8000/

### Как установить python-пакет в виртуальное окружение

В качестве менеджера пакетов используется [uv](https://docs.astral.sh/uv/).

Вот пример как добавить в зависимости библиотеку `beautifulsoup4`.

```shell
$ uv add beautifulsoup4
```

Конфигурационные файлы `pyproject.toml` и `uv.lock` обновятся автоматически.

Аналогичным образом можно удалять python-пакеты:

```shell
$ uv remove beautifulsoup4
```

Если необходимо обновить `uv.lock` вручную, то используйте команду:

```shell
$ uv lock
```
### Проверка кода ruff
```
ruff check
```
Для исправления выявленных ошибок
```
ruff check --fix
```


### Команды для быстрого запуска с помощью make

Для вывода списка часто используемых коротких команд используйте команду

```shell
$ make list
...
```
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