import pymssql, xlsxwriter,datetime


# prepair excel sheets ------------------------------------------------------------
workbook = xlsxwriter.Workbook('/home/FourierProducts/JobVis/static/reports/DynamicReport.xlsx')
date = workbook.add_format({'num_format':'dd-mm-yyyy'})
bold = workbook.add_format({'bold':1})
worksheet1 = workbook.add_worksheet('Filters')
bg_darkBlue = workbook.add_format({'bg_color':'#005ce6'})
bg_lightBlue1 = workbook.add_format({'bg_color':'#99c2ff'})
bg_lightBlue2 = workbook.add_format({'bg_color':'#cce0ff'})
bg_lightBlue1Date = workbook.add_format({'bg_color':'#99c2ff','num_format':'dd-mm-yyyy'})
bg_lightBlue2Date = workbook.add_format({'bg_color':'#cce0ff','num_format':'dd-mm-yyyy'})


# connect --------------------------------------------------------------------------

host = "41.203.23.36"
username = "FE-User"
password = "Fourier.01"
database = "PGAluminium"

conn = pymssql.connect(host, username, password, database)
cursor = conn.cursor()

# Functions ---------------------------------------------------------
def add_headers(columns):
    row = 1
    for col,name in enumerate(columns):
        worksheet1.write(row, col + 1, name, bg_darkBlue)
        worksheet1.set_column(row, col + 1, 20)
    return

def add_data(data,row):
    if row%2==0:
        gbColour= bg_lightBlue1
        gbColourDate = bg_lightBlue1Date
    else:
        gbColour = bg_lightBlue2
        gbColourDate = bg_lightBlue2Date
    for col,val in enumerate(data):
        if isinstance(val,datetime.datetime):
            worksheet1.write(row, col + 1, val, gbColourDate)
        else:
            worksheet1.write(row, col + 1, val,gbColour)
    return

# Main --------------------------------------------------------------
orgid=1
forceUpdate = 1
sql = """EXEC [dbo].[my_sp] @orgid=?,@forceUpdate=?;"""
sql = "DECLARE	@return_value int; \
    EXEC	@return_value = [dbo].[ReportContractItemsForOrg] \
		@orgid = ?, \
        @forceUpdate = ?; \
    SELECT	'Return Value' = @return_value;"

sql = """DECLARE @RC int;
EXEC @RC = [dbo].[ReportContractItemsForOrg] {}, {};
SELECT @RC AS rc;""".format(orgid, forceUpdate)

cursor.execute(sql)

columns = [column[0] for column in cursor.description]
add_headers(columns)

row = 2
data = cursor.fetchone()
add_data(data,row)
while data is not None:
    row +=1
    add_data(data,row)
    data = cursor.fetchone()
    #print(row)
#worksheet1.autofilter('B2:AG39')
worksheet1.autofilter(1,1,row,len(columns))
workbook.close()
conn.commit()