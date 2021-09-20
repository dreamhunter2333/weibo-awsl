import sqlite3
from typing import Any


class SqlTools(object):

    def __init__(self, dbpath) -> None:
        self.con = sqlite3.connect(dbpath)
        self.cur = self.con.cursor()

    def execute(self, sql: str) -> None:
        self.cur.execute(sql)

    def commit(self) -> None:
        self.con.commit()

    def fetchone(self) -> Any:
        return self.cur.fetchone()

    def fetchall(self) -> Any:
        return self.cur.fetchall()

    def close(self) -> None:
        self.cur.close()
        self.con.close()

    def execute_commit(self, sql: str) -> None:
        self.execute(sql)
        self.commit()

    def auto_commit(self, sql: str) -> None:
        self.execute(sql)
        self.commit()
        self.close()

    def auto_fetchall(self, sql: str) -> Any:
        self.execute(sql)
        res = self.fetchall()
        self.close()
        return res

    def auto_fetchone(self, sql: str) -> Any:
        self.execute(sql)
        res = self.fetchone()
        self.close()
        return res
