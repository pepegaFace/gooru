
from sqlalchemy import create_engine
import pandas as pd

def ub_parsers():
    engine1 = create_engine('postgresql+psycopg2://root:q1726354@localhost:5432/pars_db')
    con1 = engine1.connect()

    df = pd.read_sql("select url, title, article from admpars_gd limit 3 ", con1)

    engine2 = create_engine('postgresql+psycopg2://root:q1726354@localhost:5432/gooru')
    con2 = engine2.connect()

    for index, row in df.iterrows():
        con2.execute("INSERT INTO users_parser (url,title,article) values( %s, %s, %s)", row.url, row.title, row.article)


    print(df)


ub_parsers()
