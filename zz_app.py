"""Flask application for Triangulator service."""
from flask import Flask, Response, jsonify

from Triangulator import Triangulator

app = Flask(__name__)
# On instancie le service
tri = Triangulator()


@app.route("/triangulation/<pointSetId>", methods=["GET"])
def get_triangulation(pointSetId: str):
    try:
        result = tri.triangulate(pointSetId)

        return Response(result, mimetype='application/octet-stream', status=200)

    except Exception as e:
        error_msg = str(e)
        status_code = 500

        if "incorrect uuid format" in error_msg:
            status_code = 400
        elif "Point set not found" in error_msg:
            status_code = 404
        elif "point set manager unavailable" in error_msg:
            status_code = 503

        response_body = {
            "code": "TRIANGULATION_FAILED",
            "message": "Triangulation could not be computed for the given point set."
        }
        return jsonify(response_body), status_code


if __name__ == "__main__":
    app.run(debug=True)