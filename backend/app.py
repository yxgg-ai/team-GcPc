# app.py
from flask import Flask, jsonify
from flask_cors import CORS
from pipeline import get_field_data, get_all_field_ids, get_field_locations

app = Flask(__name__)
CORS(app)

@app.route("/fields")
def fields():
    return jsonify(get_all_field_ids())

@app.route("/field/<field_id>")
def field(field_id):
    return jsonify(get_field_data(field_id))

@app.route("/fields/map")
def fields_map():
    return jsonify(get_field_locations())

if __name__ == "__main__":
    app.run(debug=True, port=5000)