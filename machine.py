from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from . import mysql
from .models import ClientMachine

machine = Blueprint('machine', __name__)


# @machine.route('/machines')
# @login_required
# def machines():
#     if not current_user.is_root():
#         return render_template('page_403.html')
#     return render_template('machines.html')
# <li><a class="dropdown-item" href="{{ url_for('machine.machines') }}">Machines</a></li>


@machine.route('/getMachine/<id>')
@login_required
def get_machine_one(id):
    if not current_user.is_root():
        return jsonify({'error': 'Only root admins can access this section.'})
    machine = ClientMachine.get_machine(id)
    print(machine)
    return jsonify(machine)


@machine.route('/getMachine')
@login_required
def get_machine():
    if not current_user.is_root():
        return jsonify({'error': 'Only root admins can access this section.'})
    machines = ClientMachine.get_machines()
    print(machines)
    return jsonify({'machines': machines})


@machine.route('/updateMachine/<id>', methods=['PUT'])
@login_required
def update_machine(id):
    if not current_user.is_root():
        return jsonify({'error': 'Only root admins can access this section.'})
    machineData = request.form
    machine = ClientMachine.get_machine_by_address_not_id(
        machineData['address'], id)

    if machine:
        return jsonify({'error': 'A machine with the same address already exists.'})

    result = ClientMachine.update_machine(ClientMachine(id=id, address=machineData['address'],
                                                        description=machineData['description'],
                                                        van_number=machineData['van_number']))
    return jsonify(result)


@machine.route('/addMachine', methods=['POST'])
@login_required
def add_machine():
    if not current_user.is_root():
        return jsonify({'error': 'Only root admins can access this section.'})
    machineData = request.form
    print(machineData)

    machine = ClientMachine.get_machine_by_address(machineData['address'])

    if machine:
        return jsonify({'error': 'A machine with the same address already exists.'})

    result = ClientMachine.create_machine(
        machineData['address'], machineData['description'], machineData['van_number'])
    return jsonify(result)


@machine.route('/deleteMachine/<id>', methods=['DELETE'])
@login_required
def delete_machine(id):
    if not current_user.is_root():
        return jsonify({'error': 'Only root admins can access this section.'})
    result = ClientMachine.delete_machine(id)
    return jsonify(result)
