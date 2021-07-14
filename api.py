from flask import Blueprint, json, jsonify, request
from . import mysql
from .models import Element

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/readings')
def get_records_by_date_range():
    try:
        readingData = request.args
        return jsonify(Element.get_readings_by_date_range(readingData['start'], readingData['end'])), 200
    except Exception as e:
        print(str(type(e).__name__) + ': ' + str(e))
        return jsonify({'msg': 'An error has occurred while processing the request.',
                        'errorType': str(type(e).__name__),
                        'errorMessage': str(e)}), 400


@api.route('/stations/last_modified_time')
def get_last_modified_time_of_stations():
    try:
        return jsonify(Element.get_last_modified_time_of_stations())
    except Exception as e:
        print(str(type(e).__name__) + ': ' + str(e))
        return jsonify({'msg': 'An error has occurred while processing the request.',
                        'errorType': str(type(e).__name__),
                        'errorMessage': str(e)}), 400


@api.route('/stations')
def get_stations_records():
    try:
        return jsonify(Element.get_stations_records())
    except Exception as e:
        print(str(type(e).__name__) + ': ' + str(e))
        return jsonify({'msg': 'An error has occurred while processing the request.',
                        'errorType': str(type(e).__name__),
                        'errorMessage': str(e)}), 400
