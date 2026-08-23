# app.py
from flask import Flask, jsonify
from pipeline import get_field_data, get_all_field_ids

app = Flask(__name__)

@app.route("/fields")
def fields():
    return jsonify(get_all_field_ids())

@app.route("/field/<field_id>")
def field(field_id):
    return jsonify(get_field_data(field_id))

if __name__ == "__main__":
    app.run(debug=True, port=5000)