from flask import Blueprint, render_template, request, jsonify
from flask_login.utils import login_required

from .models import WaterBody, Element

waterbody = Blueprint('waterbody', __name__)


@waterbody.route('/waterbodies')
@login_required
def waterbody_home():
    return render_template('waterbody.html')


@waterbody.route('/waterbody_records')
@login_required
def waterbody_records():
    search = request.args.get('search')
    offset = request.args.get('offset')
    limit = request.args.get('limit')

    records = WaterBody.get_water_bodies_with_options(search, offset, limit)

    return jsonify(records)


@waterbody.route('/waterbody_records/report/<id>')
@login_required
def get_waterbody_report(id: str):
    reportData = Element.get_readings_by_station(id)
    return jsonify(reportData)
