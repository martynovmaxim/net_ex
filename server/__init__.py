from flask import Flask
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config.from_object('config')
redis_store = FlaskRedis(app)

redis_store.set("123", "pbkdf2$10000$3937695218abe02362ab796ee2f4233255117a6960af0a1a28294b38e05716e7$123")

from server import views