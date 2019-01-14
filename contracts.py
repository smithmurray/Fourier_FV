import os
from flask import Flask, Blueprint, render_template,request,session,redirect,url_for
from werkzeug.utils import secure_filename
from flask_database import db
from models import Contracts, ContractItems
from load_items import contract_data
import datetime
#from datetime import datetime

contracts_file = Blueprint('contracts_file',__name__,template_folder='templates',static_folder='static')

UPLOAD_FOLDER = '/home/FourierProducts/JobVis/static/reports'
ALLOWED_EXTENSIONS = set(['xlsx'])

app = Flask(__name__)
app.secret_key = ';jadsfjjmLFNDCJGRLsdlCHasFAFFSA'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Items Page
@contracts_file.route('/<string:org_name>/Worker/<int:user_id>', methods=["POST", "GET"])
def worker(org_name, user_id):
    if user_id == session["UserId"]:
        #rs = '{timestamp} -- request started'.format(timestamp=datetime.utcnow().isoformat())
        Confirmation = "Hello"

        fast_assign = db.engine.execute("""
                                        Select
                                        i.ContractItemId, i.ActivityStatusId, i.LineReferenceNumber, i.Description,
                                        i.AssignedUserId, c.Description  as 'Contract', c.ContractReference,
                                        c.DueDate, a.Status, a.isActivityEnd, a.isCancelled
                                        from ContractItems i
                                        join Contracts c on
                                        c.ContractId = i.ContractId
                                        join ActivityStatuses a on
                                        a.StatusId=i.ActivityStatusId
                                        where i.OrgId = {} and
                                        DueDate >= DATEADD(DAY, -90, GETDATE())
                                        order by c.Description asc
                                        """.format(session["OrgId"])).fetchall()

        base_activities_data = db.engine.execute("""
                                                 select distinct
                                                 a.OrgId, a.ActivityId, a.Activity, s.BgColor, s.isCancelled
                                                 from Activities a
                                                 left join ActivityStatuses s on
                                                 s.ActivityId = a.ActivityId
                                                 where a.Level = 2 and a.OrgId = {}
                                                 """.format(session["OrgId"])).fetchall()

        #ss= '{timestamp} -- request ended'.format(timestamp=datetime.utcnow().isoformat())
        if request.method == "POST":
            if request.form["UpdateStatus"] == "Complete Activity":

                db.engine.execute("""
                                  Update ContractItems
                                  Set ActivityStatusId = {}
                                  where ContractItemId = {}
                                  """.format(int(request.form["CIIS"]) + 1, request.form["CIIE"]))

                db.session.commit()

                Con_Name = request.form["ContractName"]
                LR_Name = request.form["LineRefName"]

                Confirmation = "Contract: " + str(Con_Name) + " Reference: " + str(LR_Name) + " Status: Completed"
                return redirect(url_for('contracts_file.worker', org_name=session["OrgName"], user_id=session["UserId"], Confirmation=Confirmation))
            elif request.form["UpdateStatus"] == "Cancelled":

                db.engine.execute("""
                                  Update ContractItems
                                  Set ActivityStatusId = 32
                                  where ContractItemId = {}
                                  """.format(request.form["CIIE"]))

                db.session.commit()

                Con_Name = request.form["ContractName"]
                LR_Name = request.form["LineRefName"]

                Confirmation = "Contract: " + str(Con_Name) + " Reference: " + str(LR_Name) + " Status: Cancelled"
                return redirect(url_for('contracts_file.worker', org_name=session["OrgName"], user_id=session["UserId"], Confirmation=Confirmation))
            elif request.form["UpdateStatus"] != "Complete Activity" or request.form["UpdateStatus"] != "Cancelled":

                New_AI = db.engine.execute("""
                                           Select
                                           s.StatusID
                                           from ActivityStatuses s
                                           join Activities a on
                                           a.ActivityId = s.ActivityId
                                           where a.Activity = '{}' and s.isActivityStart = 1
                                           """.format(request.form["UpdateStatus"])).first()

                db.engine.execute("""
                                  Update ContractItems
                                  Set ActivityStatusId = {}, AssignedUserId = {}
                                  where ContractItemId = {}
                                  """.format(New_AI[0], session["UserId"], request.form["CIIE"]))

                db.session.commit()

                Con_Name = request.form["ContractName"]
                LR_Name = request.form["LineRefName"]

                Confirmation = "Contract: " + str(Con_Name) + " Reference: " + str(LR_Name) + " Status: " + str(request.form["UpdateStatus"]) + " started"
                return redirect(url_for('contracts_file.worker', org_name=session["OrgName"], user_id=session["UserId"], Confirmation=Confirmation))
        return render_template('Workers.html', fast_assign=fast_assign, user_id=user_id, base_activities_data=base_activities_data, Confirmation=Confirmation)
    else:
        error = 'You do not have authorisation to view this page'
        return render_template('Workers.html', Error=error)

#Contracts Page
@contracts_file.route('/<string:org_name>/ManageContracts', methods=["POST", "GET"])
def manage_contracts(org_name):
    if session.get('UserId'):
        if session["RoleId"] > 1:

            sp = db.engine.execute("ReportContracts {}".format(session["OrgId"])).fetchall()

            contract_managers = db.engine.execute("""
                                                  Select
                                                  u.UserId, u.UserName
                                                  from Users u
                                                  join UserRoles r on
                                                  r.UserId=u.UserId
                                                  where r.RoleId>1 and u.IsActive = 1 and OrgId = {}
                                                  """.format(session["OrgId"])).fetchall()

            activities_data = db.engine.execute("""
                                                Select
                                                a.OrgId, a.StatusId, a.Status, a.SequenceNumber, a.ActivityId, s.Level
                                                from ActivityStatuses a
                                                left join Activities s on
                                                a.ActivityId=s.ActivityId
                                                where a.OrgId = {} and s.Level = 1
                                                """.format(session["OrgId"])).fetchall()

            #contract_id = db.engine.execute("Select c.OrgId, c.ContractId, c.ContractReference, c.Description, c.DueDate, c.AssignedUserId, c.ContactPerson,c.Notes,c.Value, c.ActivityStatusId, u.UserName, a.StatusId, a.Status from Contracts c left join Users u on u.UserId = c.AssignedUserId left join ActivityStatuses a on a.StatusId = c.ActivityStatusId where c.OrgId = {} order by c.DueDate asc".format(session["OrgId"])).fetchall()

            #now = datetime.date.today()

            if request.method == "POST":
                if request.form["AddContracts"] == "Add Contract":
                    Contracts_Add = Contracts(OrgId = session["OrgId"], ContractReference = request.form["CRef"], Description = request.form["CName"], ActivityStatusId = request.form["CStatus"], DueDate = request.form["CDate"], AssignedUserId = request.form["CMan"], Notes = request.form["CNotes"])
                    for i in sp:
                        if i[1] == request.form["CRef"]:
                            error = 'This reference has already been used'
                            return render_template('manage_contracts.html', sp=sp, activities_data=activities_data, Error=error, contract_managers=contract_managers)
                    db.session.add(Contracts_Add)
                    db.session.commit()
                    return redirect(url_for('contracts_file.manage_contracts', org_name=session["OrgName"]))
                elif request.form["AddContracts"] == "Save Contract":
                    Contract_Edit = Contracts.query.get(request.form["ECID"])
                    Contract_Edit.ContractReference = request.form["ECRef"]
                    Contract_Edit.Description = request.form["ECName"]
                    Contract_Edit.DueDate = request.form["ECDate"]
                    Contract_Edit.AssignedUserId = request.form["ECMan"]
                    Contract_Edit.Notes = request.form["ECNotes"]
                    Contract_Edit.ActivityStatusId = request.form["ECStatus"]
                    check_ref = db.engine.execute("Select ContractReference from Contracts where not ContractId = {}".format(request.form["ECID"])).fetchall()
                    for i in check_ref:
                        if i[0] == Contract_Edit.ContractReference:
                            error = 'This reference has already been used'
                            return render_template('manage_contracts.html', sp=sp, activities_data=activities_data, Error=error, contract_managers=contract_managers)
                    db.session.commit()
                    return redirect(url_for('contracts_file.manage_contracts', org_name=session["OrgName"]))
                elif request.form["AddContracts"] == "Upload File":
                    contract_names = db.engine.execute("Select ContractId from Contracts where Description = '{}'".format(request.form["ConName"])).first()
                    check_items = db.engine.execute("Select * from ContractItems c left join Contracts n on n.ContractId = c.ContractId where c.ContractId = {}".format(contract_names[0])).fetchall()
                    if len(check_items) > 0:
                        error = 'You have already loaded lines for this contract'
                        return render_template('manage_contracts.html', check_items=check_items, Error=error, contract_managers=contract_managers)
                    if 'file' not in request.files:
                        error = 'Please select a file1'
                        return render_template('manage_contracts.html', Error=error, contract_managers=contract_managers)
                    file = request.files['file']
                    if file.filename == '':
                        error = 'Please select a file'
                        return render_template('manage_contracts.html', Error=error, contract_managers=contract_managers)
                    if file and allowed_file(file.filename):
                        filename = "1_" + secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                        contract_data(file_name = os.path.join(app.config['UPLOAD_FOLDER'], filename), orgid = session["OrgId"], contractid = request.form["ConId"], userid = session["UserId"])['Items']

                        return redirect(url_for('contracts_file.manage_contract_items', org_name=org_name, contract_name=request.form["ConName"]))
                    else:
                        error = 'Please select the correct file'
                        return render_template('manage_contracts.html', Error=error, contract_managers=contract_managers)
            return render_template('manage_contracts.html', sp=sp, activities_data=activities_data, contract_managers=contract_managers)
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

#CI Page
@contracts_file.route('/<string:org_name>/<string:contract_name>/ContractItems', methods=["POST", "GET"])
def manage_contract_items(org_name, contract_name):
    if session.get('UserId'):
        if session["RoleId"] > 1:

            contract_users = db.engine.execute("""
                                               Select
                                               u.UserId, u.UserName
                                               from Users u
                                               join UserRoles r on
                                               r.UserId=u.UserId
                                               where r.RoleId=1 and u.IsActive = 1 and u.OrgId = {}
                                               """.format(session["OrgId"])).fetchall()

            activities_data = db.engine.execute("""
                                                Select
                                                a.OrgId, a.StatusId, a.Status, a.SequenceNumber, a.ActivityId, s.Level
                                                from ActivityStatuses a
                                                left join Activities s on
                                                a.ActivityId=s.ActivityId where a.OrgId = {} and s.Level = 2
                                                """.format(session["OrgId"])).fetchall()

            contract_data = db.engine.execute("""
                                              SELECT
                                              ContractId, Description, DueDate, ContractReference
                                              FROM Contracts
                                              where Description = '{}' and OrgId = {}
                                              """.format(contract_name, session["OrgId"])).first()

            #contract_ref = db.engine.execute("""SELECT ContractReference FROM Contracts where Description = '{}'".format(contract_name)).first()
            #item_data = db.engine.execute("Select c.OrgId, c.ContractId, c.ContractItemId, c.LineReferenceNumber, c.Description, c.Value, c.AssignedUserId, c.ActivityStatusId, u.UserName, a.Status from ContractItems c left join Users u on u.UserId = c.AssignedUserId left join ActivityStatuses a on a.StatusId = c.ActivityStatusId where ContractId = {} and c.OrgId = {}".format(int(contract_data[0]), session["OrgId"])).fetchall()
            #forceUpdate = 1

            report_proc = db.engine.execute("[dbo].[ReportContractItemsForOrg] {}, {}".format(session["OrgId"], 1)).fetchall()
            now = datetime.date.today()

            if request.method == "POST":
                if request.form["ContractItems"] == "Add Contract Item":
                    for i in report_proc:
                        if i[4] == request.form["IRef"]:
                            error = 'This reference has already been used'
                            return render_template('manage_contract_items.html', report_proc=report_proc, Error=error, org_name=session["OrgName"], contract_name=contract_name)
                    db.engine.execute("Insert into ContractItems (OrgId, ContractId, UserId, TimeStamped, LineReferenceNumber, Description, Value, ActivityStatusId, AssignedUserId) values ({}, {}, {}, {}, '{}', '{}', {}, {}, {})".format(session["OrgId"], int(contract_data[0]), session["UserId"], now, request.form["IRef"], request.form["IName"], request.form["IValue"], request.form["IStatus"], request.form["IAUser"]))
                    db.session.commit()
                    return redirect(url_for('contracts_file.manage_contract_items', org_name=session["OrgName"], contract_name=contract_name))
                elif request.form["ContractItems"] == "View":
                    #item_history = db.engine.execute("select ContractItemId, Timestamped, u.UserName, s.Status from [dbo].[ContractItemHistory] h inner join [dbo].[ActivityStatuses] s on h.ActivityStatusId = s.StatusId inner join [dbo].[Users] u on u.UserId = h.UserId where ContractItemId = {} order by Timestamped".format(request.form["ContractItemId"])).fetchall()
                    #db.session.commit()
                    items = request.form["ContractItemId"]
                    #return render_template('item_history.html', org_name=session["OrgName"], contract_name=contract_name, items=items)
                    return redirect(url_for('report_file.item_history', org_name=session["OrgName"], contract_name=contract_name, items=items))
                elif request.form["ContractItems"] == "Save Contract Item":
                    if session["RoleId"] > 2:
                        Contract_Items_Edit = ContractItems.query.get(request.form["EIID"])
                        Contract_Items_Edit.LineReferenceNumber = request.form["EIRef"]
                        Contract_Items_Edit.Description = request.form["EIName"]
                        Contract_Items_Edit.Value = request.form["EIValue"]
                        if request.form["EIAUser"] == 'None':
                            Contract_Items_Edit.AssignedUserId = 0
                        else:
                            Contract_Items_Edit.AssignedUserId = request.form["EIAUser"]
                        Contract_Items_Edit.ActivityStatusId = request.form["EIStatus"]
                        check_ref = db.engine.execute("Select * from Contracts where not ContractId = {}".format(request.form["EIID"])).fetchall()
                        for i in check_ref:
                            if i[2] == Contract_Items_Edit.LineReferenceNumber:
                                error = 'This reference has already been used'
                                return render_template('manage_contract_items.html', report_proc=report_proc, Error=error, org_name=session["OrgName"], contract_name=contract_name)
                        db.session.commit()
                    else:
                        Contract_Items_Edit = ContractItems.query.get(request.form["EIID"])
                        if request.form["EIAUser"] == 'None':
                            Contract_Items_Edit.AssignedUserId = 0
                        else:
                            Contract_Items_Edit.AssignedUserId = request.form["EIAUser"]
                        Contract_Items_Edit.ActivityStatusId = request.form["EIStatus"]
                        db.session.commit()
                    return redirect(url_for('contracts_file.manage_contract_items', org_name=session["OrgName"], contract_name=contract_name))
                elif request.form["ContractItems"] == "Yes":
                    db.engine.execute("DELETE FROM ContractItems where ContractItemId = {}".format(request.form["DeleteC"]))
                    db.session.commit()
                    return redirect(url_for('contracts_file.manage_contract_items', org_name=session["OrgName"], contract_name=contract_name))
            return render_template('manage_contract_items.html', report_proc=report_proc, activities_data=activities_data, contract_data=contract_data, contract_users=contract_users, contract_name=contract_name)
        else:
            error = 'You are not an Admin'
            return render_template('index.html', Error=error)
    else:
        if session.get('OrgId'):
            error = 'You are not logged in'
            return render_template('index.html', Error=error)
        else:
            error = 'You are not logged in'
            return render_template('login_org.html', Error=error)

