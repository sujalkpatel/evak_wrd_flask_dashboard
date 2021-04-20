from flask import Blueprint, json, jsonify, request
from . import mysql
from .models import Element

api = Blueprint('api', __name__, url_prefix='/api')


# @api.route('/readings')
# def get_records_by_date_range():
    # try:
        # readingData = request.args
        # return jsonify(Element.get_readings_by_date_range(readingData['start'], readingData['end'])), 200
    # except Exception as e:
        # print(str(type(e).__name__) + ': ' + str(e))
        # return jsonify({'msg': 'An error has occurred while processing the request.',
                        # 'errorType': str(type(e).__name__),
                        # 'errorMessage': str(e)}), 400
