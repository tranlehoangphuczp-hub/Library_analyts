import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv("firsr_data_crawled.csv", sep = ";")

username = "postgres"
password = "Phuc2005"
host = "localhost"
port = "5432"
db_name = "TLHP_DATA"
connection_string = f"postgresql://{username}:{password}@{host}:{port}/{db_name}"
engine = create_engine(connection_string)
df.to_sql("post_data", engine, if_exists = "replace", index = False)
print("Post finish!")