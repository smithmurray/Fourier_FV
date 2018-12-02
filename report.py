from flask import Flask, Blueprint, render_template,request,session,redirect,url_for
from flask_database import db
import create_report

report_file = Blueprint('report_file',__name__,template_folder='templates',static_folder='static')

app = Flask(__name__)
app.secret_key = ';jadsfjjmLFNDCJGRLsdlCHasFAFFSA'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
#
@report_file.route('/<string:org_name>/ContractReport', methods=["POST", "GET"])
def contract_report(org_name):
    if session.get('UserId'):
        if session["RoleId"] == 4:
            contract_data = db.engine.execute("SELECT ContractReference FROM Contracts").first()
            create_report
            orgid=session["OrgId"]
            forceUpdate = 1
            report_proc = db.engine.execute("[dbo].[ReportContractItemsForOrg] {}, {}".format(orgid, forceUpdate)).fetchall()
            activities_data = db.engine.execute("select a.OrgId, a.StatusId, a.Status, a.SequenceNumber, a.ActivityId, s.Level from ActivityStatuses a left join Activities s on a.ActivityId=s.ActivityId where a.OrgId = 1 and s.Level = 2").fetchall()
            return render_template('contract_report.html', report_proc=report_proc, contract_data=contract_data[0], activities_data=activities_data)
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

@report_file.route('/<string:org_name>/<string:contract_name>/ItemHistory_<int:items>', methods=["POST", "GET"])
def item_history(org_name, contract_name, items):
    if session.get('UserId'):
        items_history = db.engine.execute("select h.ContractItemId, h.Timestamped, u.UserName, c.LineReferenceNumber, c.Description, s.Status from [dbo].[ContractItemHistory] h inner join [dbo].[ActivityStatuses] s on h.ActivityStatusId = s.StatusId inner join [dbo].[Users] u on u.UserId = h.UserId inner join ContractItems c on c.ContractItemId = h.ContractItemId where h.ContractItemId = {} order by h.Timestamped".format(items)).fetchall()
        items_history_name = db.engine.execute("select h.ContractItemId, c.LineReferenceNumber, c.Description from [dbo].[ContractItemHistory] h inner join ContractItems c on c.ContractItemId = h.ContractItemId where h.ContractItemId = {} order by h.Timestamped".format(items)).first()
        db.session.commit()
        return render_template('item_history.html', contract_name=contract_name, items=items, items_history=items_history, items_history_name=items_history_name)
    else:
        if session.get('OrgId'):
            error = 'You are not logged in'
            return render_template('index.html', Error=error)
        else:
            error = 'You are not logged in'
            return render_template('login_org.html', Error=error)

