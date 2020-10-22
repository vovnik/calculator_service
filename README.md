Calculator Service 

Данный сервис для вычисления математических выражений состоит из двух компонентов API и Calculator, которые связаны через очередь задач на основе PostgreSQL.
Итоговое решение представляет собой docker-compose из трёх сервисов: API, Calculator и базы на PostgreSQL.

Теоретически к одной базе с очередью можно подключать несколько экземпляров как API, так и Calculator, что позволяет создавать распределённую систему для вычислений.
Конечная производительность такой архитектуры в какой-то момент упирается в производительность базы данных с очередью задач.

Очередь задач использует приём с блокировкой SELECT FOR UPDATE SKIP LOCKED, что позволяет избежать одновременного взятия задачи двумя обработчиками Calculator.
При взятии задачи устанавливается новое значение для поля "process_at", которое позволяет взять задачу повторно лишь спустя какое-то время, 
если первый обработчик взявший задачу по какой-либо причине упал. Для экзотических случаев, когда первый обработчик смог взять задачу, уснул на долгое время 
и попытался отдать в базу результат уже решённой задачи предусмотрен откат транзакции. 

Вычисление математических выражений осуществляется библиотекой py_expression_eval (https://github.com/axiacore/py-expression-eval).
Библиотека позволяет осуществлять вычисление не только базовых арифметических операций и возведения в степень(**), но и содержит в себе 
математические константы PI и E, а также тригонометрические функции, подробнее см. в документации к библиотеке. И самое главное: вычисления реализованы НЕ через питоновский eval как в sympy, т.к. библиотека парсит именно математическое выражение. Отсутствие eval есть главное условие безопасности кода.

API сервиса реализовано с помощью Flask и Gunicorn в качестве application-сервера и содержит в себе два endpoint-а: 
1) 'api/expression' для POST-запросов вида {'expression': 'x+*t**y', 'variables': {'x': 10, 'y': 1, 't': 11}}, 
в ответ на которые приходит идентификатор выражения в виде {'expression_id': 11}
2) 'api/result/{id}' для получения результата вычислений вида {'result': 110}

Полученные от клиента выражения проходят предварительную валидацию на API-сервисе. В случае некорректного ввода данных пользователь получит ответ вида {"msg": msg}
с указанием на ошибку. Часть ошибок, как деление на ноль, могут быть обнаружены лишь на этапе вычислений. Тогда уже по endpoint 'api/result/{id}' вместо самого
результата вычислений будет получено сообщение об ошибке вида {"msg": msg}. Если вдруг по времени одно вычисление превышает значение в секундах параметра 
"CALCULATION_TIMEOUT", который может быть указан в calculator_variables.env, то в результате тоже будет получено сообщение об ошибке. 

Компонент Calculator берёт из очереди задачи в количестве "TASK_NUM" штук и выполняет их в пуле из "NUM_PROCESSES" процессов.
Параметр "QUEUE_WAIT_TIME" позволяет настраивать через сколько секунд экземпляр Calculator обратится к очереди за задачами, 
если в результате прошлого запроса задач в обработку взято не было. 

Из недостатков: 
1) Написание тестов к API-части на Flask позволило увидеть, что веб-часть написана не по стандартам разработки на Flask.
Для тестирования не создаётся отдельная база, но используется самописная заглушка MockDB. 
В частности реализован свой велосипедный механизм миграции для базы, который активируется каждый раз при запуске Flask-приложения (запросы вида CREATE .. IF NOT EXISTS) 
2) На каждый запрос к базе создаётся и закрывается отдельное соединение. 
Это решение обусловлено стремлением к отказоустойчивости приложения в случае потери соединения в базой. 
Пул соединений от psycopg2 не позволяет отследить ситуацию, когда созданное для пула соединение фактически упало, например, 
из-за отсутствия связи с удаленным PostgreSQL-сервером. 
