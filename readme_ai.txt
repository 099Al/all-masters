Прочитал все четыре проекта. Ничего не менял. Общая схема такая:

  - all-masters — Telegram-бот, основной сервис.
  - all-masters-web — FastAPI web, нужен для публичных страниц/Telegram WebApp.
  - all-masters-database — общий submodule с моделями/запросами, сам не запускается.
  - all-masters-database-run — проект для Alembic-миграций БД.
  - project-all-masters — общий корень проекта: четыре проекта и volumes с данными.

  Главный WSL-нюанс

  Проекты теперь лежат в общем корне:

  /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters
  /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters-web
  /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters-database
  /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters-database-run

  Общие данные лежат отдельно:

  /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/volumes/db
  /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/volumes/redis
  /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/volumes/logs
  /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/volumes/images

  В docker-compose.yaml уже используются относительные пути ../../volumes/..., поэтому отдельно заменять G:/... на /mnt/g/... больше не нужно.

  1. Подготовка WSL
  cd /mnt/g/WorkSpaces/PythonWs/telegram

  sudo apt update
  sudo apt install -y git curl

  curl -LsSf https://astral.sh/uv/install.sh | sh

  Проверь, что Docker доступен из WSL:

  docker version
  docker compose version

  Если используешь Docker Desktop, включи WSL integration для своего дистрибутива.

  2. Проверить submodule database

  Во всех трех проектах используется submodule src/database:

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters
  git submodule update --init --recursive

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters-web
  git submodule update --init --recursive

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters-database-run
  git submodule update --init --recursive

  3. Проверить env

  Для Docker-запуска нужны именно .env, не .env.dev.

  В all-masters/.env должно быть примерно так:

  POSTGRES_HOST=db
  POSTGRES_PORT=5432
  REDIS_HOST=redis
  REDIS_PORT=6379
  WEB_PORT=8000
  WEB_PUBLIC_URL=<публичный-домен-без-https>

  В all-masters-web/.env:

  POSTGRES_HOST=db
  POSTGRES_PORT=5432
  WEB_HOST=0.0.0.0
  WEB_PORT=8000

  Секреты не трогай: TOKEN_ID, BOT_TOKEN, GPT_KEY, пароли уже лежат в env-файлах.

  4. Запуск web, чтобы создать общую Docker-сеть

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters-web/deploy
  docker compose -p all-masters-web up -d --build

  Этот compose создает сеть:

  all-masters-net

  Web будет доступен локально:

  http://localhost:8000
  http://localhost:8000/profiles

  5. Запуск Postgres, Redis и бота

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters/deploy
  docker compose -p all-masters-bot up -d --build db redis

  Проверь здоровье:

  docker compose -p all-masters-bot ps

  6. Применить миграции Alembic

  Так как all-masters-database-run/.env сейчас смотрит на localhost:5436, а общий compose публикует Postgres на 5437, запускать так:

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters-database-run

  uv sync

  POSTGRES_HOST=localhost POSTGRES_PORT=5437 uv run alembic upgrade head

  7. Залить начальные SQL-данные и процедуры

  Для свежей базы выполнить один раз:

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters

  for f in src/database/sql/*.sql; do
    docker compose -p all-masters-bot -f deploy/docker-compose.yaml exec -T db \
      psql -U postgres -d all_masters < "$f"
  done

  Важно: 1_config.sql и 3_services.sql делают обычные INSERT, поэтому повторный запуск может создать дубли, если в таблицах нет ограничений.

  8. Запустить бота

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters/deploy
  docker compose -p all-masters-bot up -d app

  Логи:

  docker logs -f all-masters-app

  9. Публичный URL для Telegram WebApp

  Вариант через Cloudflare Tunnel из WSL:

  docker run --rm --network all-masters-net cloudflare/cloudflared:latest \
    tunnel --no-autoupdate --url http://all-masters-web:8000

  Он выдаст URL вида:

  https://something.trycloudflare.com

  В all-masters/.env надо поставить домен без https://:

  WEB_PUBLIC_URL=something.trycloudflare.com

  После этого перезапустить бота:

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters/deploy
  docker compose -p all-masters-bot restart app

  И этот же URL поставить в BotFather:

  /mybots -> Bot Settings -> Menu Button -> Configure menu button

  10. Запуск taskiq-процессов

  Worker:

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters/deploy
  docker compose -p all-masters-bot run --rm app \
    taskiq worker src.scheduled.broker:broker --fs-discover --log-level DEBUG

  Scheduler отдельным терминалом:

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters/deploy
  docker compose -p all-masters-bot run --rm app \
    taskiq scheduler src.scheduled.tkq:scheduler --fs-discover --log-level DEBUG

  Короткий порядок запуска

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters-web/deploy
  docker compose -p all-masters-web up -d --build

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters/deploy
  docker compose -p all-masters-bot up -d --build db redis

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters-database-run
  POSTGRES_HOST=localhost POSTGRES_PORT=5437 uv run alembic upgrade head

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters
  for f in src/database/sql/*.sql; do docker compose -p all-masters-bot -f deploy/docker-compose.yaml exec -T db psql -U postgres -d all_masters < "$f"; done

  cd /mnt/g/WorkSpaces/PythonWs/telegram/project-all-masters/all-masters/deploy
  docker compose -p all-masters-bot up -d app

  Отдельно заметил баг: all-masters-database-run/src/database/run_sql.py сейчас ненадежен для процедур, там используется неинициализированная переменная stmt. Поэтому SQL лучше применять через psql, как выше.