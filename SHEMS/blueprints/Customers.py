from flask import Blueprint,render_template,g,request,url_for,redirect,json,session,flash
from decorators import login_required
from sql_query import execute_sql_query
from datetime import datetime

bp=Blueprint("customer",__name__,url_prefix="/customer")

@bp.route("/")
@login_required
def index():
    return render_template("base_customer.html")

# --------------------------------------------- Service Locations ----------------------------------------------------------
@bp.route("/service_locations")
@login_required
def service_locations():
    sql="select * from ServiceLocations where CustomerID=\"%s\";"%(g.user[0])
    service_locations=execute_sql_query(sql)
    print("service locations:",service_locations)
    return render_template("service_locations.html",service_locations=service_locations)

@bp.route("/service_locations/add",methods=['GET','POST'])
@login_required
def locations_add():
    customerid=g.user[0]
    address=request.form.get("address")
    unitnumber=request.form.get("unitnumber")
    zipcode=request.form.get("code")
    dateacquired=request.form.get("time")
    squarefootage=request.form.get("square")
    bedrooms=request.form.get("bedrooms")
    occupants=request.form.get("occupants")
    sql = '''INSERT INTO ServiceLocations(CustomerID, Address, UnitNumber, Zipcode, DateAcquired, SquareFootage, Bedrooms, Occupants)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'''
    params = (customerid, address, unitnumber, zipcode, dateacquired, squarefootage, bedrooms, occupants)
    insert_location = execute_sql_query(sql, params)
    return "Successfully inserted!"

@bp.route("/service_locations/edit",methods=['POST'])
@login_required
def locations_edit():
    id=request.form.get("id")
    address = request.form.get("address")
    unitnumber = request.form.get("unitnumber")
    zipcode = request.form.get("code")
    dateacquired = request.form.get("time")
    squarefootage = request.form.get("square")
    bedrooms = request.form.get("bedrooms")
    occupants = request.form.get("occupants")
    sql = '''UPDATE ServiceLocations set Address=%s,UnitNumber=%s,Zipcode=%s,DateAcquired=%s,SquareFootage=%s,Bedrooms=%s,Occupants=%s
           WHERE LocationID=%s;'''
    params = (address, unitnumber, zipcode, dateacquired, squarefootage, bedrooms, occupants,id)
    edit_location=execute_sql_query(sql,params)
    return "Successfully edited!"

@bp.route("/service_locations/delete",methods=['GET','POST'])
@login_required
def locations_delete():
    id=request.form.get("id") # LocationID
    print(id)
    sql1='''SELECT DeviceID from Devices where LocationID=%s;'''
    params1=[id]
    deviceid=execute_sql_query(sql1,params1) # Devices(DeviceID) belong to the specific Location
    for device in deviceid:
        print("device id:",device)
        sql2='''DELETE from EnergyUsage where DeviceID=%s;'''
        id=[device[0]]
        delete_energyusage=execute_sql_query(sql2,id)
        sql3='''DELETE from DeviceEvents where DeviceID=%s;'''
        delete_deviceevents=execute_sql_query(sql3,id)
        sql4='''DELETE from Devices where DeviceID=%s;'''
        delete_devices=execute_sql_query(sql4,id)
    sql5='''DELETE from ServiceLocations where LocationID=%s;'''
    delete_servicelocations=execute_sql_query(sql5,[id])
    return "Successfully deleted!"

# --------------------------------------------------- Devices ----------------------------------------------------------------
@bp.route("/pre_devices",methods=['GET','POST'])
@login_required
def PreDevices():
    LocationID = request.form.get("locationid")
    session['LocationID'] = LocationID
    return "Preloaded successfully!"

@bp.route("/devices",methods=['GET','POST'])
@login_required
def Devices():
    LocationID = session.get('LocationID')
    sql = "select * from Devices Natural Join Models where LocationID=%s;"
    param = [LocationID]
    deviceslist = execute_sql_query(sql, param)
    print("deviceslist", deviceslist)
    return render_template("devices.html",devices=deviceslist)

@bp.route("/devices/add",methods=['GET','POST'])
@login_required
def devices_add():
    Locationid = session.get("LocationID")
    DeviceName = request.form.get("DeviceName")
    Type = request.form.get("Type")
    ModelNumber = request.form.get("ModelNumber")
    sql1 = '''SELECT ModelID from Models where Type=%s and ModelNumber=%s;'''
    params1=[Type,ModelNumber]
    ModelID=execute_sql_query(sql1,params1)[0][0]
    sql2 = '''INSERT INTO Devices(LocationID,ModelID,DeviceName) VALUES(%s,%s,%s);'''
    params2=[Locationid,ModelID,DeviceName]
    insert_devices=execute_sql_query(sql2,params2)
    return "Successfully added!"

@bp.route("/devices/edit",methods=['POST'])
@login_required
def devices_edit():
    Deviceid = request.form.get("Deviceid")
    DeviceName = request.form.get("DeviceName")
    Type = request.form.get("Type")
    ModelNumber = request.form.get("ModelNumber")
    sql1 = '''SELECT ModelID from Models where Type=%s and ModelNumber=%s;'''
    params1=[Type,ModelNumber]
    ModelID=execute_sql_query(sql1,params1)[0][0]
    print(ModelID)
    sql2 = '''UPDATE Devices set DeviceName=%s,ModelID=%s where DeviceID=%s;'''
    params2 = [DeviceName,ModelID,Deviceid]
    edit_devices=execute_sql_query(sql2,params2)
    return "Successfully edited!"

@bp.route("/devices/delete",methods=['POST'])
@login_required
def devices_delete():
    Deviceid = request.form.get("Deviceid")
    print("Deviceid:",Deviceid)
    sql1 = """DELETE from EnergyUsage where DeviceID=%s;"""
    params = [Deviceid]
    delete_energyusage = execute_sql_query(sql1,params)
    sql2 = """DELETE from DeviceEvents where DeviceID=%s;"""
    delete_deviceevent = execute_sql_query(sql2,params)
    sql3 = """DELETE from Devices where DeviceID=%s;"""
    delete_device = execute_sql_query(sql3,params)
    return "Successfully deleted!"

# ------------------------------------------------- Daily Usage Chart ---------------------------------------------------------
@bp.route("/daily", methods=['GET', 'POST'])
@login_required
def daily_charts():
    if request.method == 'GET':
        print("It's get!")
        return render_template("choose.html")

    elif request.method == 'POST':
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        if start_date > end_date:
            flash("Start date must be before end date.")
            print("Wrong start date!")
            return redirect(url_for('daily_charts'))

        datalist = []
        consumptionlist = []

        # Adjusted SQL query to join tables and filter based on customer ID
        sql = """
            SELECT
                DATE(EnergyUsage.Timestamp) AS dates,
                SUM(EnergyUsage.EnergyConsumed) AS consumption
            FROM EnergyUsage
            JOIN Devices ON EnergyUsage.DeviceID = Devices.DeviceID
            JOIN ServiceLocations ON Devices.LocationID = ServiceLocations.LocationID
            WHERE ServiceLocations.CustomerID = %s
            AND EnergyUsage.Timestamp >= %s
            AND EnergyUsage.Timestamp <= %s
            GROUP BY DATE(EnergyUsage.Timestamp)
        """

        params = [session['userid'], start_date, end_date]
        data = execute_sql_query(sql,params)
        for item in data:
            dates, consumption = item
            if consumption is None:
                consumption = 0
            datalist.append(dates)
            consumptionlist.append(consumption)

        return render_template('daily.html', datalist=datalist, consumptionlist=consumptionlist)


# ---------------------------------------------- Monthly Consumption Chart --------------------------------------------------
@bp.route("/monthly_consumption", methods=['GET'])
@login_required
def monthly_consumption():
    customer_id = session['userid']

    sql = """
        SELECT
            Models.Type AS DeviceName,
            SUM(EnergyUsage.EnergyConsumed) AS TotalConsumption
        FROM
            EnergyUsage
        JOIN
            Devices ON EnergyUsage.DeviceID = Devices.DeviceID
        JOIN
            Models ON Devices.ModelID = Models.ModelID
        JOIN
            ServiceLocations ON Devices.LocationID = ServiceLocations.LocationID
        WHERE
            ServiceLocations.CustomerID = %s
            AND EnergyUsage.Timestamp >= LAST_DAY(CURRENT_DATE)  - INTERVAL 1 MONTH+ INTERVAL 1 DAY
            AND EnergyUsage.Timestamp < LAST_DAY(CURRENT_DATE) + INTERVAL 1 DAY
        GROUP BY
            Models.Type;
    """
    params=[customer_id]
    data = execute_sql_query(sql,params)

    device_names = [item[0] for item in data]
    consumptions = [item[1] for item in data]

    print("Device Names:", device_names)
    print("Consumptions:", consumptions)

    return render_template('monthly_consumption.html', device_names=device_names, consumptions=consumptions)


# --------------------------------------- Device Consumption Over Time Chart --------------------------------------------------
@bp.route("/device_consumption_over_time", methods=['GET'])
@login_required
def device_consumption_over_time():
    customer_id = session['userid']

    # SQL query to fetch energy consumption per device over time for a specific customer
    sql = '''
        SELECT
        Models.Type AS DeviceName,
        DATE(EnergyUsage.Timestamp) AS Date,
        SUM(EnergyUsage.EnergyConsumed) AS DailyConsumption
    FROM
        EnergyUsage
    JOIN
        Devices ON EnergyUsage.DeviceID = Devices.DeviceID
    JOIN
        Models ON Devices.ModelID = Models.ModelID
    JOIN
        ServiceLocations ON Devices.LocationID = ServiceLocations.LocationID
    WHERE
        ServiceLocations.CustomerID = %s
    GROUP BY
        Models.Type, DATE(EnergyUsage.Timestamp)
    ORDER BY
        Date;

            '''

    params = [customer_id]
    rows = execute_sql_query(sql,params)

    # Process the data for the chart
    chart_data = {}
    for row in rows:
        device_name, date, consumption = row
        if device_name not in chart_data:
            chart_data[device_name] = {'dates': [], 'consumptions': []}
        chart_data[device_name]['dates'].append(date.strftime("%Y-%m-%d"))
        chart_data[device_name]['consumptions'].append(consumption)

    return render_template('device_consumption_over_time.html', chart_data=chart_data)


# --------------------------------------- Energy Consumption Distribution ----------------------------------------------------
@bp.route("/energy_consumption_distribution", methods=['GET'])
@login_required
def energy_consumption_distribution():
    customer_id = session['userid']
    sql="""
            SELECT
                Models.Type AS DeviceType,
                SUM(EnergyUsage.EnergyConsumed) AS TotalConsumption
            FROM
                EnergyUsage
            JOIN
                Devices ON EnergyUsage.DeviceID = Devices.DeviceID
            JOIN
                Models ON Devices.ModelID = Models.ModelID
            JOIN
                ServiceLocations ON Devices.LocationID = ServiceLocations.LocationID
            WHERE
                ServiceLocations.CustomerID = %s
            GROUP BY
                DeviceType
        """
    params = [customer_id]
    data = execute_sql_query(sql,params)

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return render_template('energy_consumption_distribution.html', labels=labels, values=values)