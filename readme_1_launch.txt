Запуск через docker:
deploy>docker compose up -d

запуск локально:
  запускать c .env.dev. Указать в Edit Configurations Path to .env


- Создание директории для БД:
  mkdir -p /home/aleks/docker_files/pg_pg_16/db/data
  sudo chown -R 999:999 /home/aleks/docker_files/pg/pg_16
  sudo chmod -R 700 /home/aleks/docker_files/pg/pg_16/db/data


- Докер файл для развертывания бд:
  scripts/db/docker-compose.yml
- Запуск бд:
    cd /home/aleks/docker_files/pg/pg_16
    $ docker compose up -d
- При первом запуске проектa all_masters\main.py создаются таблицы в БД
      Либо через запуск alembic в проекте all_masters-database-run
      all_masters-database-run - проект для работы с БД

      Так же запускаются скрипты  /src/database/run_sql.py

      alembic revision --autogenerate -m "migration message"
      alembic upgrade head
      alembic downgrade -1
      all_masters-database-run - подтягивает submodule database. В нем можно запускать запросы к базе.
      Вспомогательный проект

- В базе all_masters создаются процедуры вручную.
    Запускаются скрипты:
        scripts/db/move_links.sql
        scripts/db/update_statuses.sql

- Создаются расшаренные директории, общие с проектом all-masters-web
    >mklink /D images\default G:\WorkSpaces\PythonWs\telegram\project-all-masters\images\default
    >mklink /D images\avatars G:\WorkSpaces\PythonWs\telegram\project-all-masters\images\avatars
    >mklink /D images\works G:\WorkSpaces\PythonWs\telegram\project-all-masters\images\works
    >mklink /D images\collages G:\WorkSpaces\PythonWs\telegram\project-all-masters\images\collages
    >mklink /D images\new_avatars G:\WorkSpaces\PythonWs\telegram\project-all-masters\images\new_avatars
    >mklink /D images\new_works G:\WorkSpaces\PythonWs\telegram\project-all-masters\images\new_works
    >mklink /D images\new_collages G:\WorkSpaces\PythonWs\telegram\project-all-masters\images\new_collages


-Запуск redis
 mkdir -p /home/aleks/docker_files/redis
 /scripts/redis/docker-compose.yml
 $ docker compose up -d
 Проверка redis в wsl через docker
 redis-cli -h 127.0.0.1 -p 6379 ping
 sudo systemctl start redis
 cd /docker_files/redis


-Запуск проекта
 src/main.py

- Запуск бд:
    cd /home/aleks/docker_files/pg/pg_16
    $ docker compose up -d
-Запуск redis
   /home/aleks/docker_files/redis
   $ docker compose up -d

- Запуск процессов по расписанию
    #Запуск брокера для запуска процессов по расписанию
    taskiq worker src.scheduled.tkq:broker --fs-discover
    taskiq scheduler src.scheduled.tkq:scheduler --skip-first-run  -- не работает

    >taskiq worker src.scheduled.broker:broker --fs-discover --log-level DEBUG
    >taskiq scheduler src.scheduled.tkq:scheduler --fs-discover --log-level DEBUG


- Обновление параметров после измений в БД
  >python -m src.config_reload

  Процессы tasqiq должны быть перезапущены отдельно


- Запуск Web
  Нужно через ngrok получить публичный url
  >ngrok http 8001
  Дает адрес без порта - его надо подставить в base_url_https

  Запустить проект all-masters-web  (через run.py)
  Проверка в браузере  https://e9ac47179157.ngrok-free.app/profiles


  При запуске через Docker в .env(all-masters-web)  WEB_HOST=0.0.0.0






