from oracledb import Connection, Cursor
from dataclasses import dataclass, field

@dataclass
class Config:
    dsn: str|None = None
    host: str|None = None
    port: int|None = None
    service: str|None = None
    user: str|None = None
    password: str|None = None
    domain: str|None = None 
    conn: Connection|None = None
    # conn: Connection = field(init=False)
    cur: Cursor|None = None
    # cur: Cursor = field(init=False)
    shopid: int|None = None
    debug: bool = False


