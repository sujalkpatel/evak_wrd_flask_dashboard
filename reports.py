from flask import Blueprint, json, render_template, request, jsonify
from flask_login import login_required, current_user
import base64
import os
from . import mysql
from .models import Element, ClientMachine

report = Blueprint('report', __name__)


@report.route('/reports')
@login_required
def reports():
    return render_template('reports.html')


@report.route('/getReading')
@login_required
def reading():
    readingData = request.args

    reading = Element.get_reading(readingData['start'], readingData['end'])

    return jsonify(reading)


@report.route('/reading_records_report')
@login_required
def reading_records_report():
    location = request.args.get('location')
    station = request.args.get('station')
    date = request.args.get('date')
    records = Element.get_reading_records_report(location, station, date)
    # print(records)

    return jsonify(records)


@report.route('/logoImage')
@login_required
def logo_Image():
    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(dir_path + '/static/images/WRD.jpg', 'rb') as imageFile:
            encodedImage = base64.b64encode(imageFile.read())
            # print(encodedImage)

            return jsonify({'image': encodedImage.decode('utf-8')}), 200

    except Exception as e:
        print(str(type(e).__name__) + ': ' + str(e))
        return jsonify({'msg': 'An error has occurred while processing the request.', 'errorType': str(type(e).__name__), 'error': str(e)}), 400
