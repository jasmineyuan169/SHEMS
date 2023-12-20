from flask import Flask,url_for,jsonify,request,redirect,render_template,session,g,flash
from blueprints import customer_bp
from blueprints.forms import LoginForm,RegisterForm
from sql_query import execute_sql_query
from decorators import login_required

app=Flask(__name__)
app.register_blueprint(customer_bp)
app.config["SECRET_KEY"]="5678"

@app.before_request
def before_request():
    username=session.get("username")
    if username:
        sql_query="select * from Customers where Name=\"%s\";"%(username)
        user=execute_sql_query(sql_query)
        g.user=user[0]   # 给g绑定user

@app.context_processor
def context_processor():
    if hasattr(g,"user"):
        return {"user":g.user}
    else:
        return {}

@app.route('/',methods=['GET','POST'])
def login():  # put application's code here
    if request.method=="GET":
        return render_template("login.html")
    else:
        form=LoginForm(request.form)
        if form.validate():
            name=form.name.data
            password=form.password.data
            sql_query = "select * from Customers where Name=\"%s\" and Password=\"%s\";" % (name,password)
            user=execute_sql_query(sql_query)
            if user and user[0][3]==password:
                session['userid']=user[0][0]
                session['username']=user[0][1]
                print("Successfully login!")
                return redirect("/customer")
            else:
                flash("Account and password don't match!")
                return redirect("/")
        else:
            flash("The format of the account or the password is incorrect.")
            return redirect("/")

@app.route("/register",methods=['GET','POST'])
def register():
    if request.method=="GET":
        return render_template("register.html")
    else:
        form=RegisterForm(request.form)
        if form.validate():
            name=form.name.data
            password=form.password.data
            billingaddress=form.billingaddress.data
            sql_query = "insert into customers(Name,BillingAddress,Password) values(\"%s\",\"%s\",\"%s\");" % (name,billingaddress,password)
            user=execute_sql_query(sql_query)
            return redirect("/")
        else:
            flash("The format of the input is incorrect.")
            return redirect("/register")

@app.route("/logout")
def logout():
    session.clear()  # Remove all data in session
    g=None
    return redirect(url_for('login'))



if __name__=="__main__":
    app.run(host='0.0.0.0', port=8000, debug = True)