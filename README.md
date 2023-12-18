# Ad-stat - app for yandex metrika notifications via tg bot messaging

## Installation

### Create Yandex application [link](https://yandex.com/dev/id/doc/en/register-client)

#### Here you will get CLIENT_ID and CLIENT_SECRET keys

### Create Telegram bot [link](https://www.directual.com/lesson-library/how-to-create-a-telegram-bot)

#### Here you will get BOT_TOKEN

### Create  `.env` file in `compose` directory and specify keys

```.env
# Django
POSTGRES_DB=<specify>
POSTGRES_USER=<specify>
POSTGRES_PASSWORD=<specify>
POSTGRES_HOST=<specify>
POSTGRES_PORT=<specify>

REDIS_HOST=<specify>
REDIS_PORT=<specify>
REDIS_URI=redis://<specify>:<specify>/0

CSRF_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost<,specify>

# Telegram
BOT_TOKEN=<specify>

# YaMetrika
CLIENT_ID=<specify>
CLIENT_SECRET=<specify>
YAMETRIKA_OAUTH_GET_CODE=https://oauth.yandex.ru/authorize?response_type=code&client_id=<CLIENT_ID>&redirect_uri=<specify>
YAMETRIKA_OAUTH_GET_TOKEN=https://oauth.yandex.ru/token
```

## Features

- Creation YandexToken model - store given token to access to yametrika service
- Creation Company model - store representation of counter in yametrika
- Scheduling and publishing notifications from yametrika to telegram by bot

## Startup

### Install [docker-for-ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04), [docker-compose-for-ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04)

### Launch project with `./dc up -d`

#### About `./dc`

##### This is just shorthand for docker-compose commands, like `./dc up`, `./dc down`, `./dc logs`

### Goto localhost:8010/admin
