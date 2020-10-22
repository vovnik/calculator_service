import psycopg2
from psycopg2.extras import execute_values

import json
import time
import logging
import os

from .db import Database
from settings import *


logger = logging.getLogger(__name__)


class Postgres(Database):
    def __init__(self, dbname, user, password, host, port):
        super().__init__(dbname)
        self._user = user
        self._password = password
        self._host = host
        self._port = port

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    def connect(self):
        return psycopg2.connect(dbname=self.dbname,
                                user=self.user,
                                password=self.password,
                                host=self.host,
                                port=self.port)

    def execute_query(self, query, params={}, connect_attempts=CONNECT_ATTEMPTS):
        for _ in range(connect_attempts):
            try:
                # it's slower than pool but reliable
                with self.connect() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(query, params)
                        query_res = [dict((cursor.description[i][0], value)
                                          for i, value in enumerate(row)) for row in cursor.fetchall()]
                        return query_res

            except psycopg2.OperationalError as e:
                logger.warning(e)
                time.sleep(CONNECT_NEXT_ATTEMPT)
            except psycopg2.errors.DatabaseError as e:
                logger.warning(e)
                # it should not happen, but...
                return [{'msg': 'Database error occured, please contact administator'}]
        else:
            logger.warning("Database timeout")
            return [{'msg': 'Database temporarily unavailable'}]

    def put_task(self, expression, variables):
        query = 'INSERT INTO public."ExpressionTasks"( \
                    expression, variables) \
                        VALUES (%(expression)s, %(variables)s) \
                    RETURNING expression_id;'

        params = {"expression": expression,
                  "variables": json.dumps(variables)
                  }
        query_res = self.execute_query(query, params)
        return query_res

    def get_result(self, expression_id):
        query = 'SELECT result \
                    , error_code \
                    FROM public."ExpressionResults" \
                    WHERE expression_id = %s;'
        query_res = self.execute_query(query, (expression_id,))
        return query_res

    def get_tasks(self, num_tasks, delay_sec):
        query = 'WITH new_tasks AS ( \
                    SELECT expression_id \
                        FROM public."ExpressionTasks" \
                        WHERE process_at < NOW() \
                        ORDER BY expression_id \
                        LIMIT %s \
                        FOR UPDATE SKIP LOCKED) \
                UPDATE public."ExpressionTasks" as et \
                    SET  process_at = NOW() + (%s * interval \'1 sec\') \
                    FROM new_tasks \
                    WHERE  et.expression_id = new_tasks.expression_id \
                    RETURNING et.expression_id \
                        , et.expression \
                        , et.variables;'
        query_res = self.execute_query(query, (num_tasks, delay_sec))
        return query_res

    def insert_result_and_clean_queue(self, expression_results):
        num_tasks = len(expression_results)
        query = 'WITH res as ( \
                    INSERT INTO public."ExpressionResults"( \
                        expression_id, expression, variables, result, error_code) \
                            VALUES %s \
                        RETURNING expression_id) \
                DELETE FROM public."ExpressionTasks" et \
                    USING res \
                        WHERE res.expression_id = et.expression_id;'

        for _ in range(CONNECT_ATTEMPTS):
            try:
                with self.connect() as conn:
                    with conn.cursor() as cursor:
                        execute_values(cursor, query, expression_results)
                        # check rowcount in case when worker was disconnected from db
                        # and tried to insert tasks that have already been done by other workers
                        if cursor.rowcount < num_tasks:
                            logger.warning("rollback after delete from queue")
                            conn.rollback()
                break

            except psycopg2.OperationalError as e:
                logger.warning(e)
                time.sleep(CONNECT_NEXT_ATTEMPT)
            except psycopg2.errors.DatabaseError as e:
                logger.warning(e)
                break
        else:
            logger.warning("Database timeout")

    def migrate(self):
        """
        Making migrations with CREATE ... IF NOT EXISTS scripts 
        """
        try:
            for _ in range(CONNECT_ATTEMPTS):
                logger.info('Making migrations...')
                for migration_file in os.listdir('pg_migrations'):
                    with open(os.path.join('pg_migrations',migration_file), 'r') as migration:
                        query = migration.read()
                        with self.connect() as conn:
                            with conn.cursor() as cursor:
                                cursor.execute(query)
        except psycopg2.OperationalError as e:
            logger.warning(e)
            time.sleep(CONNECT_NEXT_ATTEMPT)