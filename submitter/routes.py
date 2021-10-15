from flask import Blueprint, current_app as app, request
from methods.validators import validate_job_format
from methods.utils import api_key_required, abort_json, submit_job

routes = Blueprint("routes", __name__)


@routes.route("/api", strict_slashes=False)
def version():
    return {
        "sha": app.config.get("GIT_SHA"),
    }


@routes.route("/submit", methods=["POST"])
@api_key_required
def submit():
    body = request.json
    if not body or "job" not in body:
        app.logger.error("Request body is not JSON or is invalid")
        abort_json(400, description="Request body is invalid or is missing required fields")

    err = validate_job_format(body['job'])
    if err:
        return {'error': err}, 400

    payload = submit_job(body['job'])
    return payload
