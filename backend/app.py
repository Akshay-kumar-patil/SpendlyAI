from flask import Flask,render_template,redirect,url_for,jsonify,request,session,flash
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Email,ValidationError
import json
import email_validator
import subprocess
from subprocess import check_output
from datetime import datetime, timedelta
import bcrypt
from bson.objectid import ObjectId
from pymongo import MongoClient
# ... for voice agent libraries
import speech_recognition as sr
from googletrans import Translator
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os
import requests
# ... for ai receipt libraries
from google.genai import types
from google import genai
import re



# app =Flask(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

load_dotenv()

app.config['SECRET_KEY'] = 'mysecretkey123'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# MongoDB
mongo_uri=os.getenv("DB_URI")
client = MongoClient(mongo_uri)
db = client["Spendly_Ai"]
collection = db["users"]


class Register_Form(FlaskForm):
    name=StringField("Name",validators=[DataRequired()])
    email=  StringField("Email",validators=[DataRequired(),Email()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit =SubmitField("Register")

    def validate_email(self,field):
        user=collection.find_one(
                {
                    "email":field.data
                }
            )
        if user:
            raise ValidationError("Email Already Taken")


class Login_form(FlaskForm):
    email=  StringField("Email",validators=[DataRequired(),Email()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit =SubmitField("Login")

class Add_expense(FlaskForm):
    amount= StringField("Amount",validators=[DataRequired()])
    date= StringField("Date",validators=[DataRequired()])
    expense_type = StringField("Expense Type",validators=[DataRequired()])
    submit =SubmitField("Save")


@app.route('/',methods=["GET"])
def index():
    return redirect(url_for('login'))

@app.route('/register',methods=["GET", "POST"])
def register():
    form = Register_Form()
    if form.validate_on_submit():
        name=form.name.data
        email=form.email.data
        password=form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        collection.insert_one(
            {
                "name":name,
                "email":email,
                "password":hashed_password
            }
        )

        return redirect(url_for('login'))

    return render_template('register.html',form=form)

@app.route('/login',methods=["GET","POST"])
def login():
    form = Login_form()
    if form.validate_on_submit():
        try:
            email=form.email.data
            password=form.password.data
            
            user=collection.find_one(
                {
                    "email":email
                }
            )
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
                session['user_id']=str(user['_id'])
                session['email']=str(user['email'])
                session['name']=str(user['name'])

                flash("Login Succsessful!","success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid email or password", "danger")
                return redirect(url_for('login'))
            
        except Exception as e:
            print("Login Error:",e)
            flash("Internal Server Error", "danger")
            return redirect(url_for('login'))
        
   
    return render_template('login.html',form=form)

@app.route('/logout',methods=["GET"])
def logout():
    session.clear()
    flash("Logged out successfully!","info")
    return redirect(url_for("login"))


@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    if 'user_id' not in session:
        flash("Please Login first", "warning")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = collection.find_one({"_id": ObjectId(user_id)})
    
    # fetch all expenses
    expenses_cursor = db["expenses"].find({"user_id": user_id})
    expenses_list = list(expenses_cursor) # Convert to list to iterate multiple times

    # calculate Totals
    total_expense = 0.0
    
    for expense in expenses_list:
        try:
            # Convert string amount to float for calculation
            total_expense += float(expense['amount'])
        except ValueError:
            pass # Skip invalid numbers

    return render_template("dashboard.html", 
                           user=user, 
                           expenses=expenses_list, 
                           total_expense=round(total_expense, 2))


@app.route('/add-expense',methods=["GET","POST"])
def add_expense():
    if "user_id" not in session:
        flash("Please login first", "warning")
        return redirect(url_for("login"))
    
    form=Add_expense()

    if form.validate_on_submit():
        try:
            user_id = session["user_id"]
            amount=form.amount.data
            date = form.date.data
            expense_type=form.expense_type.data

            db['expenses'].insert_one(
                {
                    "user_id": user_id, 
                    "amount":amount,
                    "category":expense_type,
                    "date":date
                }
            )
            flash("Expense added successfully!", "success")
            return redirect(url_for("dashboard"))
        
        except Exception as e:
            flash("Error: Enter all the required fields")
    

    return render_template("expense.html",form=form)


# voice agent

@app.route('/voice-agent',methods=['GET'])
def voice_agent_page():
    if request.method == 'GET':
        if "user_id" not in session:
            flash("Please login first", "warning")
            return redirect(url_for("login"))
        return render_template("voice_agent.html")
    
        
@app.route('/run-voice-agent', methods=['GET'])
def run_voice_agent():
    
    try:
        r = sr.Recognizer()
        translator=Translator()

        with sr.Microphone() as source:
            print("Speak any thing is any Language...")
            audio = r.listen(source)

        try:
            text =r.recognize_google(audio)
            print("You said:",text)

        except Exception as e:
            print("Speech recognition error:", e)
            return jsonify({
                "status": "error",
                "message": "Could not understand audio"
            })

        lang = translator.detect(text).lang
        print("detected language: ", lang)


        # audio goes to ai agent
        load_dotenv()

        model=ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                    api_key=os.getenv("GEMINI_API_KEY"))

        parser =JsonOutputParser()

        prompt = PromptTemplate(
            template="""
                You are an intelligent multilingual expense extraction agent.

                Extract expense details from the following text and return ONLY valid JSON. Do not add comments.

                ### JSON Format:
                {{
                    "amount": <number>,
                    "date": "DD-MM-YYYY",
                    "category": "<food/travel/shopping/other>"
                }}

                ### Text (multilingual input):
                "{text}"

                ### Rules:
                - Detect amount even if written in words (e.g., "pachas rupay", "one hundred", "₹200", "200rs").
                - Detect spoken amounts like "two fifty" as 250.
                - Support multi-language input (Hindi/English mix).
                - If date is missing or invalid, use today's date.
                """,
            input_variables=["text"]
        )

        chain = prompt | model |parser
        result=chain.invoke({'text':text})

        return jsonify({
            "status": "success",
            "sentence": text,
            "amount": result["amount"],
            "date": result["date"],
            "category": result["category"]
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    

# voice agent save in db
@app.route('/voice-agent',methods=['POST'])
def voice_agent_save():
    data = request.get_json()
    if not data:
        return jsonify({"error":"No data"}), 400
    
    try:
        user_id=session["user_id"]
        amount=data["amount"]
        date=data["date"]
        expense_type=data["category"]
        
        db['expenses'].insert_one(
            {
                "user_id": user_id, 
                "amount":amount,
                "date":date,
                "expense_type":expense_type
            }
        )
        flash("Expense added successfully!", "success")
        return jsonify({"status": "success"})
        # return redirect(url_for("dashboard"))
        
    except Exception as e:
        flash("Error: Enter all the required fields")      



# ai receipt 
@app.route('/receipt-session',methods=['GET'])
def receipt_page():
    if "user_id" not in session:
        flash("Please login first", "warning")
        return redirect(url_for("login"))
    return render_template("receipt_scanner.html")
    

@app.route('/receipt-input',methods=['POST'])
def receipt_input():
    try:
        if 'image' not in request.files:
            flash("No image uploaded", "danger")
            return redirect(url_for("receipt_input"))
        
        image_file=request.files['image']
        image_bytes=image_file.read()

        client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        prompt="""
                You are an expense receipt parser.

                From this receipt image, extract:
                - Date
                - Category (Food, Travel, Shopping, Other)
                - Total amount paid

                Rules:
                - If any field is missing, return null
                - Return ONLY valid JSON
                - Do not add extra text

                Output format:
                {
                "date": "",
                "category": "",
                "amount": ""
                }
            """
        
        response=client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
        types.Part.from_bytes(
            data=image_bytes,
                    mime_type="image/jpeg",
                ),
                prompt
            ]
        )
        print(response.text)


        raw = response.text
        match = re.search(r'\{.*\}', raw, re.DOTALL)

        data=json.loads(match.group())
        return jsonify(data)
        

    except Exception as e:
        print("Analyze error:", e)
        return jsonify({"error": "Analysis failed"}), 500

# receipt analyzed data now save into db
@app.route('/receipt-save',methods=['POST'])
def receipt_save():
    data=request.json

    user_id=session["user_id"]
    amount=data["amount"]
    date=data["date"]
    expense_type=data["category"]
    db['expenses'].insert_one(
        {
            "user_id":user_id,
            "amount":amount,
            "date":date,
            "expense_type":expense_type
        }
    )
    flash("Expense added successfully!", "success")

# delete any expense

# 1. Temporary delete
@app.route('/expense/temp-delete/<expense_id>',methods=['POST'])
def temp_delete_expense(expense_id):
    db['expenses'].update_one(
        {"_id":ObjectId(expense_id)},
        {
            "$set":{
                "pending_delete":True,
                "Delete_at":datetime.utcnow()+timedelta(seconds=3)
            }
        }
    )
    return jsonify({"Status":"marked"})

# 2. Undo delete
@app.route('/expense/undo-delete/<expense_id>',methods=['POST'])
def undo_delete_expense(expense_id):
    db['expenses'].update_one(
        {"_id":ObjectId(expense_id)},
        {
            "$unset":{
                "pending_delete":"",
                "delete_at":""
            }
        }
    )
    return jsonify({"status":"undo"})

# 3. Permanent delete after5 sec
@app.route('/expense/permanent-delete/<expense_id>',methods=['POST'])
def permanent_delete_expense(expense_id):
    db['expenses'].delete_one({
        "_id":ObjectId(expense_id),
        "pending_delete":True
    })
    return jsonify({"status":"deleted"})


# if __name__=='__main__':
#     app.run(debug=True,port=5005)

