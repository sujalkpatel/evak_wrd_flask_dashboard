from flask import Blueprint, json, render_template, request, jsonify
from flask_login import login_required, current_user
import base64
from . import mysql
from .models import Element, ClientMachine

element = Blueprint('element', __name__)


@element.route('/', methods=['POST'])
def index_post():
    cur = mysql.connection.cursor()
    try:
        reading_data = request.json
        # print(reading_data)

        if reading_data is None or \
            'reading_time' not in reading_data or \
            'elements' not in reading_data or \
            'location' not in reading_data or \
            'latitude' not in reading_data or \
            'longitude' not in reading_data or \
            'MacAddress' not in reading_data or \
            'station' not in reading_data or \
                'image' not in reading_data:

            return jsonify({'msg': 'Not all fields are present.'}), 400

        if ClientMachine.get_machine_by_address(reading_data['MacAddress']) is None:
            return jsonify({'msg': 'Your machine is not authorised.'}), 401

        station_id = reading_data['station']
        waterBody = ''

        waterBodyNameQuery = "SELECT waterbody_name FROM subdivision_master where unique_id = '" + station_id + "'"
        cur.execute(waterBodyNameQuery)

        result = cur.fetchall()

        if len(result) > 0:
            waterBody = result[0][0]

        if waterBody == '':
            return jsonify({'msg': 'Station(' + station_id + ') is not valid.'}), 400

        reading_time = reading_data['reading_time']

        recordExistsQuery = "select count(*) from evak_db.element_reading where station_id = '" + \
            station_id + \
            "' and date(reading_time) = date('" + reading_time + "')"
        cur.execute(recordExistsQuery)

        result = cur.fetchall()

        if len(result) > 0 and result[0][0] > 0:
            return jsonify({'msg': 'The readings for the Station(' + station_id + ') for the given date are already present in the system.'}), 400

        group_id = 1

        groupIdQuery = "select ifnull(max(group_id), 0) from evak_db.element_reading;"
        cur.execute(groupIdQuery)

        result = cur.fetchall()

        if len(result) > 0:
            group_id = int(result[0][0]) + 1

        # Insert image first
        imageObject = json.loads(reading_data['image'])
        fileName = imageObject['FileFullName']
        imageData = base64.b64decode(imageObject['Data'])

        cur.execute("INSERT INTO reading_images ( \
                    reading_group_id, \
                    file_name, \
                    image) \
                    VALUES \
                    (%s, %s, %s);",
                    (group_id, fileName, imageData))

        location = reading_data['location']
        latitude = reading_data['latitude']
        longitude = reading_data['longitude']

        dictElements = Element.get_elements_dict()
        rowCount = 0

        for element in reading_data['elements']:

            element_name = element['element_name']
            reading_value = element['reading_value']
            valid = 2

            if element_name not in dictElements:
                continue

            if element_name == 'TOTALCOLIFORM':
                if float(reading_value) == 1:
                    valid = 0

            elif (float(reading_value) != -99) \
                    and (float(reading_value) != -999) \
                    and (float(reading_value) < float(dictElements[element_name]['min']) or
                         float(reading_value) > float(dictElements[element_name]['max'])):
                if float(reading_value) >= (float(dictElements[element_name]['min']) * 0.75) and \
                        float(reading_value) <= (float(dictElements[element_name]['max']) * 1.25):
                    valid = 1
                else:
                    valid = 0

            cur.execute("INSERT INTO element_reading( \
                            group_id, \
                            reading_time, \
                            element_name, \
                            reading_value, \
                            location, \
                            lat, \
                            lng, \
                            valid, \
                            station_id, \
                            waterbody_name) \
                            VALUES \
                            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                        (group_id, reading_time, element_name,
                         reading_value, location, latitude,
                         longitude, valid, station_id, waterBody))

        mysql.connection.commit()
        rowCount += cur.rowcount
        cur.close()
        return jsonify({'msg': 'Success!', 'rows_inserted': rowCount, 'group_id': group_id}), 201

    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        print(str(type(e).__name__) + ': ' + str(e))
        return jsonify({'msg': 'An error has occurred while processing the request.', 'errorType': str(type(e).__name__), 'error': str(e)}), 400


@element.route('/<group_id>', methods=['PUT'])
def index_put(group_id):
    cur = mysql.connection.cursor()
    try:
        reading_data = request.json
        # print(reading_data)

        if reading_data is None or \
            'elements' not in reading_data or \
                'MacAddress' not in reading_data:

            return jsonify({'msg': 'Not all fields are present.'}), 400

        if ClientMachine.get_machine_by_address(reading_data['MacAddress']) is None:
            return jsonify({'msg': 'Your machine is not authorised.'}), 401

        dictElements = Element.get_elements_dict()
        dictReadings = Element.get_element_readings_dict(group_id)
        rowCount = 0

        for element in reading_data['elements']:

            element_name = element['element_name']
            reading_value = element['reading_value']
            valid = 2

            if element_name not in dictElements or float(dictReadings[element_name]) == float(reading_value):
                continue

            if element_name == 'TOTALCOLIFORM':
                if float(reading_value) == 1:
                    valid = 0

            elif (float(reading_value) != -99) \
                    and (float(reading_value) != -999) \
                    and (float(reading_value) < float(dictElements[element_name]['min']) or
                         float(reading_value) > float(dictElements[element_name]['max'])):
                if float(reading_value) >= (float(dictElements[element_name]['min']) * 0.75) and \
                        float(reading_value) <= (float(dictElements[element_name]['max']) * 1.25):
                    valid = 1
                else:
                    valid = 0

            cur.execute("UPDATE element_reading \
                            SET \
                            created_time = now(), \
                            reading_value = '" + reading_value + "', \
                            valid = " + str(valid) + " \
                            WHERE group_id = '" + group_id + "' and element_name = '" + element_name + "';")

        mysql.connection.commit()
        rowCount += cur.rowcount
        cur.close()
        return jsonify({'msg': 'Success!', 'rows_updated': rowCount, 'group_id': group_id}), 201

    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        print(str(type(e).__name__) + ': ' + str(e))
        return jsonify({'msg': 'An error has occurred while processing the request.', 'errorType': str(type(e).__name__), 'error': str(e)}), 400


@element.route('/elements')
@login_required
def elements():
    if not current_user.is_admin():
        return render_template('page_403.html')
    return render_template('elements.html')


@element.route('/trends')
@login_required
def trends():
    return render_template('trends.html')


@element.route('/readings')
@login_required
def readings():
    return render_template('readings.html')


@element.route('/getElement/<id>')
@login_required
def get_element_one(id):
    element = Element.get_element(id)
    return jsonify(element)


@element.route('/getElement')
@login_required
def get_element():
    elements = Element.get_elements()
    # print(elements)
    return jsonify({'elements': elements})


@element.route('/getElementNames')
@login_required
def get_element_names():
    elements = Element.get_element_names()
    # print(elements)
    return jsonify({'elements': elements})


@element.route('/updateElement/<id>', methods=['PUT'])
@login_required
def update_element(id):
    elementData = request.form
    element = Element.get_element_by_name_not_id(elementData['name'], id)

    if element:
        return jsonify({'error': 'An element with the same name already exists.'})

    result = Element.update_element(Element(id=id, name=elementData['name'],
                                            unit=elementData['unit'],
                                            min=elementData['min'],
                                            max=elementData['max']))
    return jsonify(result)


@element.route('/addElement', methods=['POST'])
@login_required
def add_element():
    elementData = request.form
    print(elementData)

    element = Element.get_element_by_name(elementData['name'])

    if element:
        return jsonify({'error': 'An element with the same name already exists.'})

    result = Element.create_element(
        elementData['name'], elementData['unit'], elementData['min'], elementData['max'])
    return jsonify(result)


@element.route('/deleteElement/<id>', methods=['DELETE'])
@login_required
def delete_element(id):
    result = Element.delete_element(id)
    return jsonify(result)


@element.route('/getReading')
@login_required
def reading():
    readingData = request.args

    reading = Element.get_reading(readingData['start'], readingData['end'])

    return jsonify(reading)


@element.route('/getReadingTrends')
@login_required
def reading_trends():
    readingData = request.args

    reading = Element.get_reading_trends(
        readingData['start'], readingData['end'], readingData['location'], readingData['station'], readingData['elementName'])

    return jsonify(reading)


@element.route('/reading_records')
@login_required
def reading_records():
    search = request.args.get('search')
    start = request.args.get('start')
    end = request.args.get('end')
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    records = Element.get_reading_records(search, start, end, offset, limit)
    # print(records)

    return jsonify(records)


@element.route('/reading_records_location')
@login_required
def reading_records_location():
    search = request.args.get('search')
    location = request.args.get('location')
    start = request.args.get('start')
    end = request.args.get('end')
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    records = Element.get_reading_records_location(
        search, location, start, end, offset, limit)
    # print(records)

    return jsonify(records)


@element.route('/reading_records_csv')
@login_required
def reading_records_csv():
    search = request.args.get('search')
    start = request.args.get('start')
    end = request.args.get('end')
    records = Element.get_reading_records_csv(search, start, end)
    # print(records)

    # if element:
    #     return jsonify({'error': 'An element with the same name already exists.'})

    # result = Element.create_element(elementData['name'], elementData['unit'])
    return jsonify({"elements": records})


@element.route('/getLocationsFromReadings')
@login_required
def locations_readings():

    records = Element.get_locations_readings()

    return jsonify({"locations": records})


@element.route('/getStationsFromReadingsByLocation')
@login_required
def stations_readings():
    location = request.args.get('location')
    records = Element.get_stations_readings_by_location(location)

    return jsonify(records)


@element.route('/location_coordinates', methods=['GET', 'POST'])
@login_required
def location_coordinates():
    if request.method == 'GET':
        location = request.args.get('location')
        print(location)
        coordinates = Element.get_location_coordinates(location)

        return jsonify(coordinates)

    locationData = request.form
    result = Element.set_location_coordinates(
        locationData['location'], locationData['lat'], locationData['lng'])

    return jsonify(result)
