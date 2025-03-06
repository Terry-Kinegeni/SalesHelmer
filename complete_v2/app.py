from flask import Flask, render_template, request,flash,redirect, url_for, session,current_app
from flask_mail import Mail, Message
import random
import hashlib
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from apyori import apriori
import seaborn as sns
import os
import chardet
from datetime import datetime, timedelta
import sqlite3
import pickle
import bcrypt

app = Flask(__name__, static_url_path='/static', static_folder='static')


# Secret key and email configuration
app.secret_key = 'blanguage'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'terryclare17@gmail.com'  # Use your own email
app.config['MAIL_PASSWORD'] = 'ornv pohm biej aweb'  # Use your own email password
app.config['MAIL_DEFAULT_SENDER'] = 'terryclare17@gmail.com'

mail = Mail(app)

# Initialize SQLite database
def init_db():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                is_verified BOOLEAN DEFAULT 0,
                verification_code TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("Database initialized and connection successful.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


def load_data():
    customer_file_path = os.path.join(app.static_folder, 'datasets', 'customer_count_combined.xlsx')
    sales_file_path = os.path.join(app.static_folder, 'datasets', 'sales_combined.xlsx')
    df_customer_count = pd.read_excel(customer_file_path)
    df_sales_combined = pd.read_excel(sales_file_path)
    return df_customer_count, df_sales_combined

df_customer, df_sales = load_data()

# Helper function for plotting
def plot_data(x, y, title, xlabel, ylabel, color, plot_type):
    fig, ax = plt.subplots()
    if plot_type == 'Bar':
        ax.bar(x, y, color=color)
    elif plot_type == 'Area':
        ax.fill_between(x, y, color=color, alpha=0.5)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# Send verification email
def send_verification_email(email, code):
    msg = Message('Activate Your Account', recipients=[email])
    msg.body = f'Your verification code is: {code}. Please use this to activate your account.'
    try:
        mail.send(msg)
        print(f"Verification email sent to {email}")
        return True  # Return True if the email is sent successfully
    except Exception as e:
        print(f"Error sending email: {e}")
        return False  # Return False if there is an error sending the email

        
# Routes
@app.route('/')
def home():
    # return render_template('index.html')
    return render_template('index.html', logged_in='user_id' in session)


@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    
    filtered_df = df_customer.copy() 
    visualization_type = 'Bar'
    default_min_date = datetime(2022, 1, 1).strftime('%Y-%m-%d')
    default_max_date = datetime(2022, 3, 31).strftime('%Y-%m-%d')
    
    plots = {}
    if request.method == 'POST':
        min_date = request.form['min_date'] or default_min_date
        max_date = request.form['max_date'] or default_max_date
        visualization_type = request.form['visualization_type']
        filtered_df = df_customer[
            (df_customer['DATE'] >= pd.to_datetime(min_date)) &
            (df_customer['DATE'] <= pd.to_datetime(max_date))
        ]
        plots['hour_count'] = plot_data(
            filtered_df['HOUR'], filtered_df['COUNT'],
            'HOUR vs COUNT', 'HOUR', 'COUNT', 'green', visualization_type
        )
        plots['date_total'] = plot_data(
            filtered_df['DATE'], filtered_df['TOTAL'],
            'DATE vs TOTAL', 'DATE', 'TOTAL', 'skyblue', visualization_type
        )
        plots['hour_basketvalue'] = plot_data(
            filtered_df['HOUR'], filtered_df['BASKETVALUE'],
            'HOUR vs BASKETVALUE', 'HOUR', 'BASKETVALUE', 'indigo', visualization_type
        )
        # # row 2
        # plots['category'] = plot_data(
        #     df_sales['Category'], df_sales['Price'],
        #     'Category vs Price', 'Category', 'Price', 'green', visualization_type
        # )
        # plots['quantity'] = plot_data(
        #     df_sales['Category'], df_sales['Quantity'],
        #     'Category vs Quantity', 'Category', 'Quantity', 'skyblue', visualization_type
        # )
        # plots['netsales'] = plot_data(
        #     df_sales['Department'], df_sales['NetSales'],
        #     'Department vs NetSales', 'Department', 'NetSales', 'indigo', visualization_type
        # )
    return render_template('analysis.html', plots=plots, visualization_type=visualization_type,default_min_date=default_min_date, default_max_date=default_max_date,logged_in = 'user_id' in session)



@app.route('/apriori', methods=['GET', 'POST'])
def apriori_page():
    filtered_rules = None
    plot_url = None

    if request.method == 'POST' and 'file' in request.files:
        uploaded_file = request.files['file']
        
        if uploaded_file.filename:
            df = pd.read_csv(
                uploaded_file,
                encoding='utf-8',
                usecols=['InvoiceNo', 'Description', 'Quantity', 'sdateTime'],
                nrows=200,
                dtype={
                    'InvoiceNo': 'str',
                    'Description': 'str',
                    'Quantity': 'float',
                    'sdateTime': 'str'
                }
            )
            df['sdateTime'] = pd.to_datetime(df['sdateTime'], errors='coerce')
            df = df.sort_values(by='InvoiceNo')
            pickle_path = './apriori_rules.pkl'
            if os.path.exists(pickle_path):
                with open(pickle_path, 'rb') as pkl_file:
                    pre_trained_rules = pickle.load(pkl_file)
                filtered_rules = []
                for rule in pre_trained_rules:
                    for item in rule.ordered_statistics:
                        filtered_rules.append({
                            'antecedents': list(item.items_base),
                            'consequents': list(item.items_add),
                            'support': rule.support,
                            'confidence': item.confidence,
                            'lift': item.lift
                        })
                filtered_rules_df = pd.DataFrame(filtered_rules)
                if not filtered_rules_df.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.scatterplot(
                        x="support", y="confidence", size="lift", hue="lift",
                        data=filtered_rules_df, palette="coolwarm", sizes=(20, 200), ax=ax
                    )
                    ax.set_title("Association Rules Scatter Plot")
                    ax.set_xlabel("Support")
                    ax.set_ylabel("Confidence")
                    plt.legend(title="Lift")
                    img = BytesIO()
                    plt.savefig(img, format='png', bbox_inches='tight')
                    img.seek(0)
                    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
                    plt.close(fig)

    return render_template(
        'basket.html',
        rules=filtered_rules,
        logged_in='user_id' in session,
        plot_url=plot_url,
    )

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verification_code = str(random.randint(100000, 999999))
        hashed_code = hashlib.sha256(verification_code.encode()).hexdigest()
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute('SELECT * FROM users WHERE email = ?', (email,))
            existing_user = c.fetchone()
            if existing_user:
                flash('Email already registered.', 'danger')
            else:
                if send_verification_email(email, verification_code):
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                    c.execute('INSERT INTO users (email, password,verification_code) VALUES (?, ?,?)', (email, hashed_password,hashed_code))
                    conn.commit()
                    send_verification_email(email, verification_code)
                    flash('Signup successful! You can now log in.', 'success')
                else:
                    flash('There was an issue sending the verification email. Please try again later.', 'danger')
            
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'danger')
        except sqlite3.Error as e:
            flash(f"Database error: {e}", 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('home'))

    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        if user:
            user_id, user_email, user_password, is_verified, _ = user
            if bcrypt.checkpw(password.encode('utf-8'), user_password):
                if is_verified:
                    session['user_id'] = user_id
                    flash('Login successful!', 'success')
                    return redirect(url_for('home'))
                else:
                    flash('Your account is not verified. Please check your email for the verification link.', 'danger')
            else:
                flash('Invalid email or password.', 'danger')
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('index.html')




@app.route('/verify', methods=['GET', 'POST'])
def verify_account():
    if request.method == 'POST':
        email = request.form['email']
        verification_ = request.form['verification_code']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        if user:
            user_id, user_email, user_password, is_verified, verification_code = user
            stored_hash = verification_code
            if stored_hash == hashlib.sha256(verification_.encode()).hexdigest():
                c.execute('UPDATE users SET is_verified = 1 WHERE email = ?', (email,))
                conn.commit()
                flash('Account activated successfully! You can now log in.', 'success')
            else:
                flash('Invalid verification code.', 'danger')
        else:
            flash('No user found with that email.', 'danger')

        conn.close()
        return redirect(url_for('home'))

    return render_template('verify.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)