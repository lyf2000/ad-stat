# Ad-stat - app for yandex metrika notifications via tg bot messaging

## Installation

### Create Yandex application [link](https://yandex.com/dev/id/doc/en/register-client)

#### Here you will get CLIENT_ID and CLIENT_SECRET keys

### Create Telegram bot [link](https://www.directual.com/lesson-library/how-to-create-a-telegram-bot)

#### Here you will get BOT_TOKEN

### Create  `.env` file in `compose` directory and specify keys. [Sample]("./docs/example.env)


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
