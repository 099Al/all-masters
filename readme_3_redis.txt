$ sudo service redis-server status

$ redis-cli ping  - проверка

$ redis-cli  заходит в 127.0.0.1:6379>

> INFO keyspace

> KEYS *
> KEYS *taskiq*
> LLEN "taskiq:queue"
> LRANGE taskiq:queue 0 -1

