from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from . import mysql
from .models import ClientMachine

machine = Blueprint('machine', __name__)


@machine.route('/machines')
@login_required
def machines():
    if not current_user.is_admin():
        return render_template('page_403.html')
    return render_template('machines.html')


@machine.route('/getMachine/<id>')
@login_required
def get_machine_one(id):
    machine = ClientMachine.get_machine(id)
    print(machine)
    return jsonify(machine)


@machine.route('/getMachine')
@login_required
def get_machine():
    machines = ClientMachine.get_machines()
    print(machines)
    return jsonify({'machines': machines})


@machine.route('/updateMachine/<id>', methods=['PUT'])
@login_required
def update_machine(id):
    machineData = request.form
    machine = ClientMachine.get_machine_by_address_not_id(
        machineData['address'], id)

    if machine:
        return jsonify({'error': 'A machine with the same address already exists.'})

    result = ClientMachine.update_machine(ClientMachine(id=id, address=machineData['address'],
                                                        description=machineData['description']))
    return jsonify(result)


@machine.route('/addMachine', methods=['POST'])
@login_required
def add_machine():
    machineData = request.form
    print(machineData)

    machine = ClientMachine.get_machine_by_address(machineData['address'])

    if machine:
        return jsonify({'error': 'A machine with the same address already exists.'})

    result = ClientMachine.create_machine(
        machineData['address'], machineData['description'])
    return jsonify(result)


@machine.route('/deleteMachine/<id>', methods=['DELETE'])
@login_required
def delete_machine(id):
    result = ClientMachine.delete_machine(id)
    return jsonify(result)
