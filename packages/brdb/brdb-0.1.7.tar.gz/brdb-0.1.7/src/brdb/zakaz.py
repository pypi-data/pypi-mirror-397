from .operations import config, connect
import json
import oracledb


def get_shops() -> list[dict]:
    # if config.cur is None:
    #     raise RuntimeError("Cursor not initialized")    
    if config.conn is None:
        connect()
    shops = config.cur.execute("""    
        SELECT * FROM zakaz order by id
    """)
    # Get column names for dictionary keys (optional)
    column_names = [col[0] for col in config.cur.description]
    # Fetch all rows
    rows = config.cur.fetchall()

    # Convert to a list of dictionaries
    data_as_dicts = []
    for row in rows:
        row_dict = {}
        for i, col_name in enumerate(column_names):
            row_dict[col_name.lower()] = row[
                i
            ]  # Convert column names to lowercase for consistency
        data_as_dicts.append(row_dict)

    for shop in shops:
        print(f"shops: {shop}")
    # Serialize the list of dictionaries to a JSON string
    # json_output = json.dumps(data_as_dicts, indent=4)  # indent for pretty printing
    # print(json_output)
    return data_as_dicts

def put_shop(shop: dict) -> None:
    try:
        config.cur.execute(
            """
            INSERT INTO zakaz (name, url, logo, code) VALUES (:name, :url, :logo, :code)
            """,
            shop
        )
    except oracledb.IntegrityError:
        pass
    config.conn.commit()
    return 
