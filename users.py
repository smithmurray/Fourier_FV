from flask import Flask, Blueprint, render_template,request,session,redirect,url_for
from flask_database import db
from datetime import timedelta
from models import Users, UserRoles

users_file = Blueprint('users_file',__name__,template_folder='templates',static_folder='static')

app = Flask(__name__)
app.secret_key = ';jadsfjjmLFNDCJGRLsdlCHasFAFFSA'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

@users_file.route('/', methods=["POST", "GET"])
def login_org():
    if request.method == "POST":
        try:
            org_data = db.engine.execute("SELECT * FROM Organisations where IsActive = 1 and Email = '{}'".format(request.form["OrgEmail"])).first()
            if org_data[3] == request.form["OrgPswd"]:
                session['OrgId'] = org_data[0]
                session['OrgName'] = org_data[1].replace(" ", "_")
                return redirect(url_for('users_file.login', org_name=session["OrgName"]))
            else:
                error = 'Your password is incorrect'
                return render_template('login_org.html', Error=error)
        except:
            error = 'Your email is incorrect'
            return render_template('login_org.html', Error=error)
    return render_template('login_org.html')

@users_file.route('/<string:org_name>/Login', methods=['GET', 'POST'])
def login(org_name):
    if session.get('OrgId'):
        sesh = db.engine.execute("Select * from UserRoles").fetchall()
        if request.method == "POST":
            try:
                join_pin = "{}{}{}{}".format(int(request.form["val1"]), int(request.form["val2"]), int(request.form["val3"]), int(request.form["val4"]))
                id_data = db.engine.execute("SELECT * FROM Users where IsActive = 1 and OrgId = {} and PIN = {}".format(session["OrgId"], int(join_pin))).first()
                if id_data[2] == int(join_pin):
                    session['logged_in'] = True
                    session['UserId'] = id_data[0]
                    session['UserName'] = id_data[1]

                    role_data = db.engine.execute("Select * from UserRoles where UserId = {}".format(session["UserId"])).first()
                    session["RoleId"] = role_data[1]

                    return redirect(url_for('users_file.dashboard', org_name=session["OrgName"]))
            except:
                error = 'Your pin is incorrect'
                return render_template('index.html', Error=error)
        return render_template('index.html', sesh=sesh)
    else:
        error = 'Your organisation is not logged in'
        return render_template('login_org.html', Error=error)

@users_file.route('/<string:org_name>/Dashboard', methods=['GET', 'POST'])
def dashboard(org_name):
    if session.get('UserId'):
        if session["RoleId"] == 1:
            return redirect(url_for('contracts_file.worker', user_id=session["UserId"], org_name=session["OrgName"]))
        else:
            return render_template('dashboard.html')
    else:
        if session.get('OrgId'):
            error = 'You are not logged in'
            return render_template('index.html', Error=error)
        else:
            error = 'You are not logged in'
            return render_template('login_org.html', Error=error)

@users_file.route('/<string:org_name>/ManageUsers', methods=["POST", "GET"])
def manage_users(org_name):
    if session.get('UserId'):
        if session["RoleId"] == 4:
            user_data = db.engine.execute("SELECT u.UserId, u.UserName, u.IsActive, u.PIN, u.OrgId, r.RoleId, n.RoleName FROM Users u left join UserRoles r on u.UserId=r.UserId left join Roles n on n.RoleId=r.RoleId where u.OrgId = {} order by IsActive desc, UserName asc".format(session["OrgId"])).fetchall()
            roles_data = db.engine.execute("SELECT * FROM Roles").fetchall()
            if request.method == "POST":
                if request.form["AddUsers"] == "Add User":
                    db.engine.execute("Insert into Users (UserName, PIN, IsActive, OrgId) values ('{}', {}, {}, {})".format(request.form["UName"], request.form["UPin"], int(request.form["UAct"]), session["OrgId"]))
                    for i in user_data:
                        if i[3] == int(request.form["UPin"]):
                            error = 'This pin has already been used'
                            return render_template('manage_users.html', Error=error, user_data=user_data, roles_data=roles_data)
                        elif i[1] == request.form["UName"]:
                            error = 'This username has already been used'
                            return render_template('manage_users.html', Error=error, user_data=user_data, roles_data=roles_data)
                    else:
                        db.session.commit()
                        New_User  = db.engine.execute("Select UserId from Users where UserName = '{}' and PIN = {}".format(request.form["UName"], request.form["UPin"])).first()
                        db.engine.execute("Insert into UserRoles (UserId, RoleId) values ({}, {})".format(New_User[0], request.form["URole"]))
                        db.session.commit()
                        return redirect(url_for('users_file.manage_users', org_name=session["OrgName"]))
                elif request.form["AddUsers"] == "Save User":
                    user_data_update = db.engine.execute("SELECT u.UserId, u.UserName, u.IsActive, u.PIN, u.OrgId, r.RoleId, n.RoleName FROM Users u join UserRoles r on u.UserId=r.UserId join Roles n on n.RoleId=r.RoleId where not u.UserId = {} order by IsActive desc, UserName asc".format(request.form["EID"])).fetchall()
                    User_Edit = Users.query.get(request.form["EID"])
                    User_Edit.UserName = request.form["EName"]
                    User_Edit.PIN = request.form["EPin"]
                    User_Edit.IsActive = request.form["EAct"]
                    for i in user_data_update:
                        if i[3] == int(request.form["EPin"]):
                            error = 'This pin is currently being used'
                            return render_template('manage_users.html', Error=error, user_data=user_data, roles_data=roles_data)
                        elif i[1] == request.form["EName"]:
                            error = 'This username is currently being used'
                            return render_template('manage_users.html', Error=error, user_data=user_data, roles_data=roles_data)
                    db.session.commit()
                    return redirect(url_for('users_file.manage_users', org_name=session["OrgName"]))
                elif request.form["AddUsers"] == "Save Roles":
                    Roles_Edit = UserRoles.query.get(request.form["EID"])
                    Roles_Edit.RoleId = request.form["ERole"]
                    db.session.commit()
                    return redirect(url_for('users_file.manage_users', org_name=session["OrgName"]))
            return render_template('manage_users.html', user_data=user_data, roles_data=roles_data)
        else:
            if session["RoleId"] > 1:
                error = 'You are not an Admin'
                return render_template('dashboard.html', Error=error)
            else:
                error = 'You are not an Admin'
                return render_template('Workers.html', Error=error)
    else:
        if session.get('OrgId'):
            error = 'You are not logged in'
            return render_template('index.html', Error=error)
        else:
            error = 'You are not logged in'
            return render_template('login_org.html', Error=error)

@users_file.route('/Logout', methods=['GET', 'POST'])
def logout():
    if session.get('UserId'):
        session.pop('UserId')
        session.pop('UserName')
        session.pop('logged_in')
        session.pop('RoleId')
        return redirect(url_for('users_file.login', org_name=session["OrgName"]))
    else:
        if session.get('OrgId'):
            error = 'You are not logged in'
            return render_template('index.html', Error=error)
        else:
            error = 'You are not logged in'
            return render_template('login_org.html', Error=error)

@users_file.route('/Logout_Org', methods=['GET', 'POST'])
def logout_org():
    if session.get('OrgId'):
        if session["RoleId"] == 4:
            session.pop('OrgId')
            session.pop('UserId')
            session.pop('UserName')
            session.pop('logged_in')
            session.pop('RoleId')
            return redirect(url_for('users_file.login_org'))
        else:
            error = 'You are not an Admin'
            return render_template('index.html', Error=error)
    else:
        error = 'You are not logged in'
        return render_template('login_org.html', Error=error)
