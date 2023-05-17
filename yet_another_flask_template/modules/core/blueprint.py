from quart import Blueprint

from yet_another_flask_template.modules.core.handlers.auth import sign_in, sign_up
from yet_another_flask_template.modules.core.handlers.categories import create_category, list_categories, update_category
from yet_another_flask_template.modules.core.handlers.entries import create_entry, list_category_entries


def create_blueprint():
    blueprint = Blueprint(name="core", import_name="core")
    blueprint.add_url_rule("/sign_in/", view_func=sign_in, methods=["POST"])
    blueprint.add_url_rule("/sign_up/", view_func=sign_up, methods=["POST"])
    blueprint.add_url_rule("/categories/", view_func=create_category, methods=["POST"])
    blueprint.add_url_rule("/categories/", view_func=list_categories, methods=["GET"])
    blueprint.add_url_rule("/categories/<int:category_id>/", view_func=update_category, methods=["PUT"])
    blueprint.add_url_rule("/categories/<int:category_id>/entries/", view_func=create_entry, methods=["POST"])
    blueprint.add_url_rule("/categories/<int:category_id>/entries/", view_func=list_category_entries, methods=["GET"])
    return blueprint

