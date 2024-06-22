from flask import Flask
from dotenv import dotenv_values
import singlestoredb as s2
app = Flask(__name__)

config = dotenv_values(".env")
conn = s2.connect(host=config["SINGLESTORE_HOST"], port=config["SINGLESTORE_PORT"], user=config["SINGLESTORE_USER"], password=config["SINGLESTORE_PASSWD"], database="db_derek_e7ae6")

@app.route("/api/python")
def hello_world():
    return f"<p>{conn.show.databases()}</p>"
