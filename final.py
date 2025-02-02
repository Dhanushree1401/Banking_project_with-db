from flask import Flask, render_template, request, redirect, url_for, session,flash
import mysql.connector as sql
import datetime as date
app = Flask(__name__)
app.secret_key = "1234@Dhanu"  # Required for session management

# Establishing a connection to the MySQL database
mycon = sql.connect(host="localhost", user="root", password="root", database="dhanu")
mycur = mycon.cursor()

# Special characters allowed in usernames and passwords
SpecialSym = ['$', '@', '#', '%']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            # Sign Up Process
            ut = request.form['name']
            p = request.form['username']
            z = request.form['password']
            k = float(request.form['amount'])
            a = date.datetime.strptime(request.form['dob'], "%Y-%m-%d").date()
            s = request.form['address']
            d = request.form['phone']
            f = request.form['aadhar']

            # Insert user data into the database
            q = "INSERT INTO bank (Name, UserName, Password, DateOfBirth, Address, Mobile_Number, Aadhar_no, Balance) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (ut, p, z, a, s, d, f, k)
            mycur.execute(q, values)
            mycon.commit()

            return redirect(url_for('signin'))

        except ValueError:
            error_message = "Invalid input for amount or date of birth. Please enter valid values."
            return render_template('signup.html', error_message=error_message)

    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        try:
            # Sign In Process
            username = request.form['username']
            password = request.form['password']

            # Perform authentication
            query = "SELECT * FROM bank WHERE UserName = %s AND Password = %s"
            mycur.execute(query, (username, password))
            user = mycur.fetchone()
            if user:
                session['username'] = username  # Store username in session
                return redirect(url_for('dashboard'))
            else:
                error_message = "Invalid username or password."
                return render_template('signin.html', error_message=error_message)

        except Exception as e:
            error_message = "An error occurred while signing in. Please try again later."
            return render_template('signin.html', error_message=error_message)

    return render_template('signin.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        try:
            username = session['username']
            # Retrieve user data from the database
            query = "SELECT * FROM bank WHERE UserName = %s"
            mycur.execute(query, (username,))
            user_data = mycur.fetchall()
            

            # Retrieve user's loan applications
            loan_query = "SELECT * FROM loan WHERE user_name = %s"
            mycur.execute(loan_query, (username,))
            loan_applications = mycur.fetchall()
            print(type(loan_applications))
            # Retrieve user's insurance applications
            insurance_query = "SELECT * FROM insurance WHERE user_name = %s"
            mycur.execute(insurance_query, (username,))
            insurance_applications = mycur.fetchall()
            return render_template('dashboard.html', username=username, user_data=user_data, loan_applications=loan_applications, insurance_applications=insurance_applications)

        except Exception as e:
            print(e)
            error_message = "An error occurred while loading the dashboard. Please try again later."
            return render_template('dashboard.html', error_message=error_message)
    else:
        return redirect(url_for('signin'))

@app.route('/apply_loan', methods=['GET', 'POST'])
def apply_loan():
    if 'username' in session:
        if request.method == 'POST':
            try:
                username = session['username']
                # Apply for a Loan
                loan_type = request.form['loan_type']
                loan_amount = float(request.form['amount'])
                repayment_period = int(request.form['repayment_period'])

                # Insert loan application into the database
                insert_loan = "INSERT INTO loan (user_name, loan_type, amount, repayment_period) VALUES (%s, %s, %s, %s)"
                loan_data = (username, loan_type, loan_amount, repayment_period)
                mycur.execute(insert_loan, loan_data)
                mycon.commit()
                return redirect(url_for('dashboard'))
            except Exception as e:
                error_message = "An error occurred while applying for a loan. Please try again later."
                return render_template('apply_loan.html', error_message=error_message)

        return render_template('apply_loan.html')
    else:
        return redirect(url_for('signin'))

@app.route('/create_insurance', methods=['GET', 'POST'])
def create_insurance():
    if 'username' in session:
        if request.method == 'POST':
            try:
                username = session['username']
                # Apply for Insurance
                insurance_type = request.form['insurance_type']
                coverage = int(request.form['coverage'])
                premium=int(request.form['premium'])
                # Insert insurance application into the database
                insert_insurance = "INSERT INTO insurance (user_name, insurance_type,premium, coverage) VALUES (%s, %s,%s,%s)"
                insurance_data = (username, insurance_type, premium ,coverage)

                mycur.execute(insert_insurance, insurance_data)
                mycon.commit()

                return redirect(url_for('dashboard'))

            except Exception as e:
                error_message = "An error occurred while applying for insurance. Please try again later."
                return render_template('create_insurance.html', error_message=error_message)

        return render_template('create_insurance.html')
    else:
        return redirect(url_for('signin'))

# Update the insert_transaction function to match the table structure
def insert_transaction(username, amount, transaction_type):
    now = date.datetime.now().strftime("%Y-%m-%d")  # Adjusted to match the date format of your table
    # Assuming you want to insert data into either credited or debited based on transaction_type
    if transaction_type == "Credit":
        insert_query = "INSERT INTO transaction (credited, UserName, date) VALUES (%s, %s, %s)"
        transaction_data = (amount, username, now)
    elif transaction_type == "Debit":
        insert_query = "INSERT INTO transaction (debited, UserName, date) VALUES (%s, %s, %s)"
        transaction_data = (amount, username, now)
    mycur.execute(insert_query, transaction_data)
    mycon.commit()


# Update the add_credit route to insert a transaction record
@app.route('/add_credit', methods=['GET', 'POST'])
def add_credit():
    if 'username' in session:
        if request.method == 'POST':
            try:
                username = session['username']
                amount = float(request.form['amount'])
                
                # Update balance in the database
                update_query = "UPDATE bank SET Balance = Balance + %s WHERE UserName = %s"
                mycur.execute(update_query, (amount, username))
                mycon.commit()
                
                # Insert transaction record
                insert_transaction(username, amount, "Credit")
                
                return redirect(url_for('dashboard'))

            except Exception as e:
                error_message = "An error occurred while crediting money. Please try again later."
                return render_template('add_credit.html', error_message=error_message)

        return render_template('add_credit.html')
    else:
        return redirect(url_for('signin'))

@app.route('/debit', methods=['GET', 'POST'])
def debit():
    if 'username' in session:
        try:
            username = session['username']
            balance_query = "SELECT Balance FROM bank WHERE UserName = %s"
            mycur.execute(balance_query, (username,))
            current_balance = mycur.fetchone()[0]

            if request.method == 'POST':
                try:
                    amount = float(request.form['amount'])
                    if amount > current_balance:
                        error_message = "Insufficient balance."
                        return render_template('debit.html', error_message=error_message, balance=current_balance)
                    else:
                        update_query = "UPDATE bank SET Balance = Balance - %s WHERE UserName = %s"
                        mycur.execute(update_query, (amount, username))
                        mycon.commit()
                        insert_transaction(username, amount, "Debit")
                        return redirect(url_for('dashboard'))
                except Exception as e:
                    error_message = "An error occurred while debiting money. Please try again later."
                    return render_template('debit.html', error_message=error_message, balance=current_balance)
            
            return render_template('debit.html', balance=current_balance)
        except Exception as e:
            return redirect(url_for('signin'))
    else:
        return redirect(url_for('signin'))

@app.route('/transactions')
def transactions():
    if 'username' in session:
        try:
            username = session['username']
            # Retrieve user's recent transactions from the database
            transaction_query = "SELECT * FROM transaction WHERE UserName = %s ORDER BY timestamp DESC"
            mycur.execute(transaction_query, (username,))
            transactions = mycur.fetchall()
            return render_template('transactions.html', transactions=transactions, username=username)

        except Exception as e:
            error_message = "An error occurred while viewing transactions. Please try again later."
            return render_template('transactions.html', error_message=error_message)
    else:
        return redirect(url_for('signin'))

def insert_profile(username, name, dob, address, phone, aadhar):
    try:
        query = "UPDATE bank SET Name=%s, DateOfBirth=%s, Address=%s, Mobile_Number=%s, Aadhar_no=%s WHERE UserName=%s"
        values = (name, dob, address, phone, aadhar, username)
        mycur.execute(query, values)
        mycon.commit()
        return True  # Return True on success
    except Exception as e:
        print("Error:", e)
        return False  # Return False on failure

@app.route('/profile')
def profile():
    if 'username' in session:
        try:
            username = session['username']
            # Retrieve user data from the database
            query = "SELECT * FROM bank WHERE UserName = %s"
            mycur.execute(query, (username,))
            user_data = mycur.fetchone()
            return render_template('profile.html', account=user_data)  # Pass user_data as account
        except Exception as e:
            error_message = "An error occurred while viewing the profile. Please try again later."
            return render_template('profile.html', error_message=error_message)
    else:
        return redirect(url_for('signin'))
    
@app.route('/update_profile/<username>', methods=['GET', 'POST'])
def update_profile(username):
    if request.method == 'POST':
        try:
            name = request.form['name']
            dob = request.form['dob']
            address = request.form['address']
            phone = request.form['phone']
            aadhar = request.form['aadhar']

            # Call the insert_profile function to update profile in the database
            if insert_profile(username, name, dob, address, phone, aadhar):
                flash('Profile updated successfully!', 'success')
            else:
                flash('Failed to update profile. Please try again later.', 'danger')

            return redirect(url_for('profile',username=username))  # Redirect to profile page after updating

        except Exception as e:
            print(e)
            flash(f'Error: {e}', 'danger')
            return redirect(url_for('update_profile', username=username))

    else:
        try:
            query = "SELECT * FROM bank WHERE UserName=%s"
            mycur.execute(query, (username,))
            account = mycur.fetchone()
            return render_template('update_profile.html', username=username, account=account)

        except Exception as e:
            print(e)
            flash(f'Error: {e}', 'danger')
            return redirect(url_for('profile'))  # Redirect to profile page on error

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(debug=True)
