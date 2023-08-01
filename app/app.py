from flask import Flask

from app.blueprints.shipments import shipments_blueprint

app = Flask(__name__)
app.register_blueprint(shipments_blueprint)


if __name__ == '__main__':
    app.run()
