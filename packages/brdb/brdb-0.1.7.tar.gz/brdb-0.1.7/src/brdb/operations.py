import os
import oracledb
from .config import Config

config = Config()

def init():
    config.host = os.getenv("ORA_HOST")
    config.service = os.getenv("ORA_SERVICE")
    config.port = int(os.getenv("ORA_PORT", 1521))
    config.user = os.getenv("ORA_CR_USER")
    config.password = os.getenv("ORA_CR_PASSWORD")
    


def connect(*args, **kwargs):
    init()    
    if not config.domain:
        config.domain = kwargs.get("domain")
    if not config.dsn:
        config.dsn = kwargs.get("dsn")
    if not config.host:
        config.host = kwargs.get("host")
    if not config.service:  
        config.service = kwargs.get("service")
    # if not config.user:
    if kwargs.get("user"):
        config.user = kwargs.get("user")
    # if not config.password:
    if kwargs.get("password"):
        config.password = kwargs.get("password")
    config.debug = kwargs.get("debug", False)
    try:
        # print(config)
        if config.dsn:
            if config.debug:
                print("Connect by DSN")
            config.conn = oracledb.connect(
                dsn=config.dsn,
                user=config.user,
                password=config.password
            )
        else:
            if config.debug:
                print("Connect by HOST/SERVICE")    
            config.conn = oracledb.connect(
                host=config.host,
                service_name=config.service,
                user=config.user,
                password=config.password
        )
        config.cur = config.conn.cursor()
        if config.domain:
            config.shopid = config.cur.callfunc("sh.get_shopid", int, (config.domain,))
    except Exception as err:
        print(f"Shop: Error connect to DB. {err}")
        exit(f"Ошибка подключения к базе данных. {err}")
    return config.conn, config.cur, config.shopid

def disconnect():
    if config.cur:
        config.cur.close()
    if config.conn:
        config.conn.close()

def save_shop_rec(rec: dict):
    if config.cur is None:
        raise RuntimeError("DB cursor is not initialized. Call connect() first.")
    if config.shopid is None:
        raise RuntimeError("Shop ID is not initialized. Call connect() first.")
    config.cur.callproc(
        "sh.insert_price",
        (
            config.shopid,
            rec["akc"],
            rec["name"],
            rec["url"],
            rec["price"],
            rec["old_price"],
            rec["unit"],
        ),
    )
