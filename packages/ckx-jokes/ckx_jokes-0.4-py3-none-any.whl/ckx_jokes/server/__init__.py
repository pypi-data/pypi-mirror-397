from http import HTTPStatus
from .config import Config
from flask import Flask, redirect, url_for

def jokes_server(config_class = Config) -> Flask:
  server = Flask(__name__)
  server.config.from_object(config_class)

  # 404 errorhandler
  @server.errorhandler(HTTPStatus.NOT_FOUND.value)
  def not_found(e):
    return redirect(
      url_for("core.index"),
      code=HTTPStatus.TEMPORARY_REDIRECT.value
    )

  from .core.routes import core
  server.register_blueprint(core, url_prefix="/")

  return server
