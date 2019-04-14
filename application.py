import os
import warnings
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, jsonify, redirect, render_template, request, session, send_file
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, usd
import datetime
from io import BytesIO
import csv

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd
##
app.config["TESTING"] = True
##
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# test to see if the session can be prolongue
app.config["PERMANENT_SESSION_LIFETIME"] = 1000
#

# Configure CS50 Library to use SQLite database
#db = SQL("sqlite:///finance.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///control.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

warnings.filterwarnings("ignore")

@app.route("/")
@login_required
def index():
    warnings.filterwarnings("ignore")
        
    return redirect("/claims")
    # return render_template("index.html")


@app.route("/add_claim", methods=["GET","POST"])
@login_required
def add_claim():
    warnings.filterwarnings("ignore")

    if request.method == "POST":

        claim = Claim( unit=request.form.get("unit"), customer=request.form.get("customer"), bl=request.form.get("bl"),
        charge=usd(request.form.get("charge")), date=request.form.get("date"),invoice = request.form.get("invoice"), status="Open",
        damage=request.form.get("damage"), comment=request.form.get("comment"), country = request.form.get("country"))

        db.session.add(claim)


        # Check if there where no errors?
        if db.session.commit() == None:
            print("claim")
            flash("Claim submited.")
            return redirect("/claims")

    today = datetime.date.today()

    today = str(today.month)+ "/" + str(today.day) + "/" + str(today.year)

    return render_template("add_claim.html", date = today)


@app.route("/claims")
@login_required
def display_claims():
    warnings.filterwarnings("ignore")

    """
    Display all the damage records
    """

    claims = Claim.query.filter_by(status="OPEN").order_by(Claim.id.desc())

    len_of_files_per_claims = {}

    for claim in claims:
        len_of_files_per_claims[claim.id] = len(claim.files)

    print(len_of_files_per_claims)

    return render_template("claims.html", claims = claims, len_of_files_per_claims = len_of_files_per_claims, country= "", all = "active")

@app.route("/claims/<country>")
@login_required
def display_claims_by_country(country):

    warnings.filterwarnings("ignore")

    """
    Display all the damage records by country
    """

    claims = Claim.query.filter_by(country=country, status="OPEN").order_by(Claim.id.desc())

    len_of_files_per_claims = {}
    
    for claim in claims:
        len_of_files_per_claims[claim.id] = len(claim.files)

    if country == 'us':
        return render_template("claims.html", claims = claims, us='active', len_of_files_per_claims = len_of_files_per_claims, country="us")

    if country == 'dr':
        return render_template("claims.html", claims = claims, dr='active', len_of_files_per_claims = len_of_files_per_claims, country="dr")
    
    if country == 'haiti':
        return render_template("claims.html", claims = claims, haiti='active', len_of_files_per_claims = len_of_files_per_claims, country="us")
    
    return redirect("/claims")


@app.route("/erase_claim/<claim_id>", methods=["GET"])
@login_required
def erase_claim(claim_id):
    warnings.filterwarnings("ignore")
    # to minimize the size of the db make sure to make the database vacuum full.

    try:
        _claim = Claim.query.get(claim_id)
        files = _claim.files
        print(files)
    except:
        return "Error. Claim not faund"
    

    for _file in files:
        print(_file.file_name)
        db.session.delete(_file)
    
    db.session.delete(_claim)
    db.session.commit()
    return "deleted"


@app.route("/update_claim/<row>", methods=["GET"], strict_slashes=False)
@login_required
def update_claim(row):
    warnings.filterwarnings("ignore")

    print("\nupdate_claim working\n")
    
    # transforming the slashes
    if len(row.split("-slash-")) > 1:
        row = row.split("-slash-")
        row = "/".join(row)
    
    row = row.split("@@")

    new_data = dict()

    for value in row:
        param = value.split("=")
        print(param)
        new_data[param[0]] = param[1]

    print(new_data)

    amount_of_data = 0
    for data in new_data:
        amount_of_data += len(data)

    if amount_of_data is 0:
        print("\n Empty row \n")

    old_data = Claim.query.get(new_data['id'])

    old_data.unit = new_data['unit']
    old_data.customer = new_data['customer']
    old_data.bl = new_data['bl']
    old_data.charge = usd(new_data['charge'])
    old_data.invoice = new_data['invoice']
    old_data.date = new_data['date']
    old_data.status = new_data['status']
    old_data.damage = new_data['damage']
    old_data.comment = new_data['comment']

    db.session.commit()

    print("\n claim updated \n")
    return "claim updated."

@app.route("/edit_claim/<claim_id>", methods=["GET", "POST"])
def edit_claim(claim_id):
    warnings.filterwarnings("ignore")

    if request.method == "POST":
        new_data = {}

        new_data["id"] = claim_id
        new_data["unit"] = request.form.get("unit")
        new_data["customer"] = request.form.get("customer")
        new_data["bl"] = request.form.get("bl")
        new_data["charge"] = request.form.get("charge")
        new_data["invoice"] = request.form.get("invoice")
        new_data["date"] = request.form.get("date")
        new_data["status"] = request.form.get("status")
        new_data["damage"] = request.form.get("damage")
        new_data["comment"] = request.form.get("comment")
        new_data["country"] = request.form.get("country")
        
        old_data = Claim.query.get(new_data['id'])

        old_data.unit = new_data['unit']
        old_data.customer = new_data['customer']
        old_data.bl = new_data['bl']
        old_data.charge = usd(new_data['charge'])
        old_data.invoice = new_data['invoice']
        old_data.date = new_data['date']
        old_data.status = new_data['status']
        old_data.damage = new_data['damage']
        old_data.comment = new_data['comment']
        old_data.country = new_data['country']

        db.session.commit()

        flash("Claim was successfully edited. Claim unit: " + new_data['unit'] + ".")
        return redirect("/claims")

    #try:
    claim = Claim.query.filter_by(id = claim_id).first()
    
    return render_template("edit_claim.html", claim = claim)

    #except:
     #   flash("claim doesn't exist.")
      #  return redirect("/")

@app.route("/add_file", methods=["GET","POST"])
@login_required
def add_file():
    warnings.filterwarnings("ignore")
    
    if request.method == "POST":
        ###########################################
        try:
            new_file = request.files['claim_file']
            claim_id = request.form.get("claim_id")
        except:
            return "an error ocurred. File not saved."

        db_file = Claim_file(file_name=new_file.filename, claim_id=claim_id, date_attached= datetime.datetime.now(), data=new_file.read())

        db.session.add(db_file)

        db.session.commit()
        
        print(new_file)

        return 'saved to the database \n' + new_file.filename
    
    return redirect("/")

@app.route("/download_file/<file_id>/<claim_id>", methods=["GET","POST"])
@login_required
def download_file(file_id, claim_id):
    warnings.filterwarnings("ignore")

    try:
        _file = Claim_file.query.filter_by(id=file_id, claim_id=claim_id).first()
    except:
        return "an error ocurred. File not found."

    return send_file(BytesIO(_file.data), attachment_filename=_file.file_name, as_attachment=True)

@app.route("/delete_file/<file_id>/<claim_id>", methods=["GET"])
@login_required
def delete_file(file_id, claim_id):
    warnings.filterwarnings("ignore")

    try:
        _file = Claim_file.query.filter_by(claim_id = claim_id, id = file_id).first()
    except:
        return "Error. File not faund"
    

    print('\n start',_file, '\n\n')

    db.session.delete(_file)

    db.session.commit()
    
    return "deleted"


@app.route("/register", methods=["GET", "POST"])
def register():
    warnings.filterwarnings("ignore")


    """Register user"""
    if request.method == "POST":
        print("post")

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if username == "":
            flash("You must provide an username")
            return redirect("/")
        if password == "":
            flash("You must provide a password")
            return redirect("/")

        elif confirmation != password:
            flash("Both passwords must be equal.")
            return redirect("/")


        checker = User.query.filter_by(username = username).first()

        try: 
            print(checker.username, "user name exist")
            flash("username exist")
            redirect("/register")
        except:
            print('\nusername does not exist\n')


        result = User(username = username, hash = generate_password_hash(password))

        db.session.add(result)

        db.session.commit()

        flash("The registration was successfull.")
        return redirect("/")

    print("get")
    return render_template("register.html")

@app.route("/check/<username>", methods=["GET"])
def check(username):
    warnings.filterwarnings("ignore")

    """Return true if username available, else false, in JSON format"""

    print(username)

    result = User.query.filter_by(username = username).first()

    # return false if the user exist. True otherwise.
    try:
        print('\n',result.username, '\n\n username exists \n\n' )
        return jsonify(False)
    except:
        return jsonify(True)


@app.route("/login", methods=["GET", "POST"])
def login():
    warnings.filterwarnings("ignore")


    """Log user in"""

    # Forget any user_id
    # session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username", 403)
            return redirect("/")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password", 403)
            return redirect("/")

        # Query database for username
        user = User.query.filter_by(username = request.form.get("username")).first()

        # Ensure username exists and password is correct
        try:
            if not check_password_hash(user.hash, request.form.get("password")):
                flash("invalid username and/or password")
                return redirect("/")
        except:
            flash("invalid username and/or password")
            return redirect("/")

        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():

    warnings.filterwarnings("ignore")

    print("something?")

    if request.method == "POST":
        # check if current password is correct

        current_password = request.form.get("current-password")
        new_password = request.form.get("password")

        old_hash = User.query.filter_by(id = session["user_id"]).first()

        try:
            old_hash = old_hash.hash
        except:
            flash("user doesn't exist")
            redirect("/")
        

        if check_password_hash(old_hash, current_password):

            # update password in the database
            result = User.query.filter_by(id = session["user_id"]).first()

            result.hash = generate_password_hash(new_password)

            db.session.commit()

        flash("Your password has been changed correctly.")
        return redirect("/")

    return render_template("change_password.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/backup")
@login_required
def backup():
    """Log user out"""

    claims = Claim.query.order_by(Claim.id.desc())

    # make a directory with one directory per claim that has an attachement.
    if not os.path.exists('backup'):
        os.makedirs('backup')
    
    dir_name = 'backup/' + str(datetime.datetime.today())

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    for claim in claims:
        dir_unit = dir_name + "/Attachments/" + claim.unit
        dir_claim = dir_unit + "/" + change_slashes(claim.date)

        if not os.path.exists(dir_unit):
            os.makedirs(dir_unit)
        
        if not os.path.exists(dir_claim):
            os.makedirs(dir_claim)

        for _file in claim.files:
            with open(dir_claim + "/" + _file.file_name, "bw") as new_file:
                new_file.write(_file.data)





    # make a file with the text-based data
    with open(dir_name + "/bakcup.csv", "wt") as backup_file:
        field_names = ['id','unit','customer','bl','charge','invoice','date','status','damage','comment','country','attachements_count']
        
        writer = csv.DictWriter(backup_file, delimiter=",", quotechar='"',fieldnames = field_names)
        
        writer.writeheader()
        for claim in claims:

            writer.writerow({'id':claim.id,'unit':claim.unit,'customer':claim.customer,'bl':claim.bl,'charge':claim.charge,'invoice':claim.invoice,'date':claim.date,'status':claim.status,'damage':claim.damage,'comment':claim.comment,'country':claim.country,'attachements_count':len(claim.files)})


    flash("Backup saved!")
    return redirect("/")


@app.route("/claims_closed")
@login_required
def claims_closed():
    _claims = Claim.query.order_by(Claim.id.desc())
    claims = []

    for _claim in _claims:
        if _claim.status != "OPEN":
            claim = {'id':_claim.id,'unit':_claim.unit,'customer':_claim.customer,'bl':_claim.bl,'charge':_claim.charge,'invoice':_claim.invoice,'date':_claim.date,'status':_claim.status,'damage':_claim.damage,'comment':_claim.comment,'country':_claim.country,'attachements_count':len(_claim.files)}

            _files = []

            for _file in _claim.files:
                _files.append({"file_name":_file.file_name, "id": _file.id})


            claim["files"] = _files

            claims.append(claim)


    return jsonify(claims)


def change_slashes(s):
    s = s.split("/")
    s = "-".join(s)
    return s


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()

    return "\nYou got a mistake: " + e.name + " "+  str(e.code) + "\n"
    flash("You got a mistake: " + e.name + " "+  str(e.code))
    return redirect("/")


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


# classes to use for tables

class Claim(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    unit = db.Column("unit", db.String(255))
    customer = db.Column("customer", db.String(255))
    bl = db.Column("BL", db.String(255))
    charge = db.Column("charge", db.String(255))
    invoice = db.Column("invoice", db.Integer)
    date = db.Column("date", db.String(100))
    status = db.Column("status", db.String(100))
    damage = db.Column("damage", db.String(255))
    comment = db.Column("comment", db.String(2040))

    country = db.Column("country", db.String(255))
    files = db.relationship('Claim_file', backref='claim')

class Claim_file(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    data = db.Column(db.LargeBinary)
    file_name = db.Column(db.String(255))
    date_attached = db.Column(db.String(255))
    claim_id = db.Column(db.Integer, db.ForeignKey('claim.id'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(510))
    hash = db.Column(db.String(1012))

# crete the tables (based on the classes)
db.create_all()
