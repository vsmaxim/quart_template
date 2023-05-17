from dataclasses import asdict

from quart import Quart
from quart_cors import cors

from yet_another_flask_template.config import Config
from yet_another_flask_template.modules.core.blueprint import create_blueprint as create_core_blueprint
from yet_another_flask_template.serialization import MsgSpecJSONProvider, MsgSpecRequest

Quart.request_class = MsgSpecRequest
Quart.json_provider_class = MsgSpecJSONProvider

def create_app(config: Config):
    app = Quart(__name__)
    app.config.update(asdict(config))
    cors(app, allow_origin=("http://localhost:5173",))
    return app

# Make config
config = Config()

# Start the application
app = create_app(config)

# Register blueprints
app.register_blueprint(create_core_blueprint())

# Export the asgi application for nginx unit
asgi_app = app.asgi_app

