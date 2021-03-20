from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from flask_login import LoginManager
import os
import yaml


# Configure db
# db = yaml.load(open(
#     '/home/sujal/Documents/Develop/flask/flaskapp_BS/db.yaml'), Loader=yaml.FullLoader)
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
db = yaml.load(open(
    dir_path + '/db.yaml'), Loader=yaml.FullLoader)


mysql = MySQL()


def create_app():
    app = Flask(__name__)

    app.config['MYSQL_HOST'] = db['mysql_host']
    app.config['MYSQL_USER'] = db['mysql_user']
    app.config['MYSQL_PASSWORD'] = db['mysql_password']
    app.config['MYSQL_DB'] = db['mysql_db']

    app.secret_key = "oH[}8#^]vD2bP6szj^O>mIeAT1hfC$%fwiulNWfPei{B%0D{[Yrvzt%>ke(F%))!"

    mysql.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for models parts of app
    from .models import model as model_blueprint
    app.register_blueprint(model_blueprint)

    # blueprint for element parts of app
    from .element import element as element_blueprint
    app.register_blueprint(element_blueprint)

    # blueprint for machine parts of app
    from .machine import machine as machine_blueprint
    app.register_blueprint(machine_blueprint)

    # blueprint for reports of app
    from .reports import report as report_blueprint
    app.register_blueprint(report_blueprint)

    from .models import User

    @login_manager.user_loader
    def load_user(username):
        return User.get_user(username)

    return app


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         # Fetch form data
#         userDetails = request.form
#         name = userDetails['name']
#         email = userDetails['email']
#         cur = mysql.connection.cursor()
#         cur.execute(
#             "INSERT INTO users(name, email) VALUES(%s, %s)", (name, email))
#         mysql.connection.commit()
#         cur.close()
#         return redirect('/users')
#     return render_template('index.html')


# @app.route('/users')
# def users():
#     cur = mysql.connection.cursor()
#     resultValue = cur.execute("SELECT * FROM users")
#     if resultValue > 0:
#         userDetails = cur.fetchall()
#         return render_template('users.html', userDetails=userDetails)


# if __name__ == '__main__':
#     app.run(debug=True)
