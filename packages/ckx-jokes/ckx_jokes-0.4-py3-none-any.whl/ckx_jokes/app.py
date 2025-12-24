from flask import Flask
from server import jokes_server

jserver: Flask = jokes_server()

if __name__ == "__main__":
  jserver.run()
