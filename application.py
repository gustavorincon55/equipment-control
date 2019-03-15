import os

from cs50 import SQL

from flask_sqlalchemy import SQLAlchemy

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

import datetime

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

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# test to see if the session can be prolongue
app.config["PERMANENT_SESSION_LIFETIME"] = 1000;
#

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///control.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db2 = SQLAlchemy(app)

@app.route("/")
@login_required
def index():
    """Make the user select which app to use"""
    return render_template("claims.html", claims = Claim.query.all())
    return render_template("index.html")


@app.route("/add_claim", methods=["GET","POST"])
@login_required
def add_claim():

    if request.method == "POST":

        claim = Claim( unit=request.form.get("unit"), customer=request.form.get("customer"), bl=request.form.get("bl"),
         charge=request.form.get("charge"), date=request.form.get("date"),  status=request.form.get("status"), invoice = request.form.get("invoice"),
          attachements=request.form.get("attachements"), damage=request.form.get("damage"), comment=request.form.get("comment"))

        db2.session.add(claim)

        # Check if there where no errors?
        if db2.session.commit() == None:
            flash("Claim submited.")
            return render_template("claims.html",claims = Claim.query.all())

    return render_template("add_claim.html")


@app.route("/claims")
@login_required
def display_claims():
    """
    Display all the damage records
    """

    return render_template("claims.html", claims=Claim.query.all())

    """
    trans = db.execute('SELECT * FROM "trans" WHERE userId == :userId ORDER BY datetime', userId = session["user_id"])

    for tran in trans:

        if tran["_type"] == "sell":
            tran["shares"] = tran["shares"] * -1
            tran["total"] = tran["total"] * -1

        tran["price"] = usd(tran["price"])
        tran["total"] = usd(tran["total"])

    return render_template("history.html", trans = trans)
    """

@app.route("/update_claim/<row>", methods=["GET"])
@login_required
def update_claim(row):
    row = row.split("@@")
    print(row)
    return "working"

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if username == "":
            return apology("You must provide an username")
        if password == "":
            return apology("You must provide a password")
        elif confirmation != password:
            return apology("Both passwords must be equal.")

        checker = db.execute('SELECT * FROM users where username == :username', username = username)

        if len(checker) > 0:
            return apology("Sorry, username is not available.")

        result = db.execute("INSERT INTO users(username, hash, cash) VALUES(:name, :hashedP, :cash)",
        name=username,hashedP=generate_password_hash(password),cash=20000)

        return redirect("/")

    return render_template("register.html")

@app.route("/check/<username>", methods=["GET"])
def check(username):
    """Return true if username available, else false, in JSON format"""

    print(username)
    result = db.execute("SELECT * FROM users WHERE username == :username", username = username)

    # return false if the user exist. True otherwise.
    if len(result) > 0:
        return jsonify(False)

    return jsonify(True)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    # session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/modify", methods=["GET", "POST"])
@login_required
def modify():
    """modify one record """




@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":
        symbol_to_sell = request.form.get("symbol")
        # check if the user wrote a valid number of shares
        try:
            shares_to_sell = int(request.form.get("shares"))

        except:
            flash("Sorry, you need to write how many stocks you want to buy.")
            return redirect("/sell")


        stocks = db.execute('SELECT "company_name","symbol", SUM("shares") "shares" FROM "trans" WHERE userId == :userId  AND symbol == :symbol_to_sell  GROUP BY "company_name"',
        userId = session["user_id"], symbol_to_sell = symbol_to_sell)

        # if nothing was returned from the query it means the user doesn't have stocks on that company.
        try:
            shares_owned = stocks[0]["shares"]
        except:
            flash("Sorry, you don't have shares on that company.")
            return redirect("/sell")

        # check if the user can sell that many stocks
        if shares_owned < shares_to_sell:
            flash("Sorry, you don't have that many shares.")
            return redirect("/sell")

        stock = lookup(symbol_to_sell)


        # update trans with a sell transaction
        trans = db.execute("INSERT INTO trans(company_name, userId, symbol, price, shares, total, datetime, _type) VALUES(:company_name,:userId, :symbol, :price, :shares, :total, :datetime, :_type)", company_name = stock["name"],
        userId=session["user_id"], symbol = symbol_to_sell, price = stock["price"], shares = -shares_to_sell, total = stock["price"] * -shares_to_sell, datetime = datetime.datetime.now(), _type = "sell")

        # print(trans)

        users = db.execute('select "cash" FROM "users" WHERE "id"==:id',id=session["user_id"])

        cash = users[0]["cash"]

        # print(cash)

        cash = cash + (stock["price"] * shares_to_sell)

        users = db.execute('UPDATE "users" SET "cash" = :cash WHERE "id"==:id',id=session["user_id"], cash = cash)

        flash("You succesfully made the sell")
        return redirect("/")


    stocks = db.execute('SELECT "company_name","symbol", SUM("shares") "shares" FROM "trans" WHERE userId == :userId GROUP BY "company_name"', userId = session["user_id"])

    # make a list of the stocks that have cero shares
    index = 0
    cero_shares = []
    for stock in stocks:
        if stock["shares"] == 0:
            cero_shares.append(index)
        index += 1

    # erase the stocks that have cero shares (first sort the list to avoid index-out-of-range errors)
    cero_shares.sort(reverse= True)
    for index in cero_shares:
        del stocks[index]

    return render_template("sell.html", stocks = stocks)



@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":

        # check if current password is correct

        current_password = request.form.get("current-password")
        new_password = request.form.get("password")

        old_hash = db.execute('SELECT "hash" FROM users WHERE id == :id', id = session["user_id"])

        old_hash = old_hash[0]["hash"]
        # print(old_hash)
        if check_password_hash(old_hash, current_password):

            # update password in the database
            result = db.execute("UPDATE users SET hash = :new_hash WHERE id == :id", id = session['user_id'], new_hash = generate_password_hash(new_password) )

            # print(result)




        flash("Your password has been changed correctly.")
        return redirect("/")

    return render_template("change_password.html")



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()

    flash("You got a mistake: " + e.name + " "+  str(e.code))
    return render_template("layout.html")


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


# classes to use for tables

class Claim(db2.Model):
    id = db2.Column(db2.Integer, primary_key = True)
    unit = db2.Column("unit", db2.String(255), nullable=True)
    customer = db2.Column("customer", db2.String(255), nullable=True)
    bl = db2.Column("BL", db2.String(255))
    charge = db2.Column("charge", db2.String(255))
    invoice = db2.Column("invoice", db2.Integer)
    date = db2.Column("date", db2.String(100))
    status = db2.Column("status", db2.String(100))
    attachements = db2.Column("attachements", db2.String(100))
    damage = db2.Column("damage", db2.String(255))
    comment = db2.Column("comment", db2.String(2040))


# crete the tables (based on the classes)
db2.create_all()