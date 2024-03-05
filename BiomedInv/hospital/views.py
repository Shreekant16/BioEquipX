from django.contrib import messages
from django.shortcuts import render, redirect
import psycopg2
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import datetime
import smtplib
from twilio.rest import Client


# account_sid = "saadsdasdsadsasddsads"
# auth_token = "65sds65s65s65sddssaads"
# server_no = "+16592518709"
#
# client = Client(account_sid, auth_token)

# Create your views here.
def home(request):
    return render(request, 'home.html')


def build_connection_with_database():
    conn = psycopg2.connect(database="biomed_prj", host="localhost", port="5432", user="postgres",
                            password="Pukale@123")
    return conn


def close_connection_with_database(cur, conn):
    conn.commit()
    cur.close()
    conn.close()


def employee_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User(username=username)
        user.set_password(password)
        user.save()
    return render(request, 'employee_register.html')


# redirect madhe jo nav ahe tho function name ahe ani when we use redirect teva function execute hoto.
def nurse_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.info(request, 'Invalid Username')
        else:
            user = authenticate(username=username, password=password)
            if user is None:
                messages.info(request, "Incorrect Password")
                return redirect('nurse_login')
            else:
                login(request, user)
                messages.info(request, "logged in successfully")
                return redirect('nurse_dashboard')
    return render(request, 'nurse_login.html')


# creating hashmap to store selected department
sessions = {}


def nurse_dashboard(request):
    if request.method == 'POST':
        selected_department = request.POST['department']
        sessions['selected_department'] = selected_department
        return redirect('equipments')
    return render(request, 'nurse_dashboard.html')


def equipments(request):
    conn = build_connection_with_database()
    cur = conn.cursor()
    query = f"SELECT * FROM info WHERE department='{sessions['selected_department']}'"
    cur.execute(query)
    data = cur.fetchall()
    close_connection_with_database(cur, conn)
    context = {
        'data': data,
        'dept': sessions['selected_department'].upper()
    }
    return render(request, 'equipment.html', context=context)


def report_problem(request):
    model_no = request.GET.get('model_no')
    uid = request.GET.get('uid')
    name = request.GET.get('name')
    dept = request.GET.get('dept').lower()
    data = (name, model_no, uid)
    context = {
        "data": data
    }
    if request.method == 'POST':
        problem = request.POST.get('problem')

        # sms to engineer about new machine added
        # engineers_no = "+918485049337"
        # sms = client.messages.create(body=f"Engg! Maintenance is required in {department}",
        #                              from_=server_no,
        #                              to=engineers_no)

        current_date = datetime.date.today()
        conn = build_connection_with_database()
        cur = conn.cursor()
        query = f"INSERT INTO machines_history(name, model_no, uid, problem, date) VALUES ('{name}' ,'{model_no}', '{uid}', '{problem}', '{current_date}')"
        cur.execute(query)
        query1 = f"UPDATE info SET \"Status\" = 'Not Working' WHERE \"Model Number\" = '{model_no}'"
        cur.execute(query1)
        cur.execute(f"SELECT \"Manufacturer\" FROM info WHERE \"Model Number\" = '{model_no}'")
        manufacturer_name = cur.fetchone()
        query2 = f"INSERT INTO problems(department, manufacturer, model_no, uid) VALUES ('{dept}', '{manufacturer_name[0]}', '{model_no}', '{uid}')"
        cur.execute(query2)
        close_connection_with_database(cur, conn)
        return redirect('nurse_dashboard')
    return render(request, 'report_problem.html', context=context)


def engineer_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if not User.objects.filter(username=username).exists():
            messages.info(request, 'Invalid Username')
        else:
            user = authenticate(username=username, password=password)
            if user is None:
                messages.info(request, "Incorrect Password")
                return redirect('engineer_login')
            else:
                login(request, user)
                messages.info(request, "logged in successfully")
                return redirect('engineer_dashboard')
    return render(request, 'engineer_login.html')


def engineer_dashboard(request):
    conn = build_connection_with_database()
    cur = conn.cursor()
    query = f'SELECT * FROM problems'
    cur.execute(query)
    data = cur.fetchall()
    close_connection_with_database(cur, conn)
    context = {
        'data': data
    }
    model_no = request.GET.get('model_no')  # get chya aat madhe URI component yenar
    conn = build_connection_with_database()
    cur = conn.cursor()
    query = f"DELETE FROM problems WHERE model_no = '{model_no}'"
    cur.execute(query)
    query1 = f"UPDATE info SET \"Status\" = 'Working' WHERE \"Model Number\" = '{model_no}'"
    cur.execute(query1)
    close_connection_with_database(cur, conn)
    return render(request, 'engineer_dashboard.html', context=context)


def generate_report(request):
    model_no = request.GET.get('model_no')
    uid = request.GET.get('uid')
    context = {
        'model_no': model_no,
        'uid': uid
    }
    if request.method == 'POST':
        report = request.POST.get('report')
        message = (f"Report"
                   f"Machine Repaired"
                   f"model no : {model_no}"
                   f"uid : {uid}"
                   f"Report : {report}")
        sender_email = "myEmail"
        password = "Password"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        nurse_email = "nurse_email"
        server.sendmail(sender_email, nurse_email, message)
    return render(request, 'generate_report.html', context=context)


def logout_page(request):
    logout(request)
    return redirect('home')


def manufacturer(request):
    conn = build_connection_with_database()
    cur = conn.cursor()
    query = "SELECT DISTINCT \"Manufacturer\" FROM info"
    cur.execute(query)
    data = cur.fetchall()
    context = {
        'data': data
    }
    close_connection_with_database(cur, conn)
    return render(request, 'manufacturers.html', context=context)


def update_room(request):
    if request.method == 'POST':
        model_no = request.GET.get('model_no')
        new_location = request.POST.get('new_location')
        conn = build_connection_with_database()
        cur = conn.cursor()
        query = f"UPDATE info SET Location = '{new_location}' WHERE  \"Model Number\" = '{model_no}'"
        cur.execute(query)
        close_connection_with_database(cur, conn)
        messages.info(request, "Location Edited")
    return render(request, 'update_room.html')


def machines_history(request):
    conn = build_connection_with_database()
    cur = conn.cursor()
    query = f"SELECT * FROM machines_history ORDER BY date"
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    context = {
        'data': data
    }
    return render(request, 'machines_history.html', context=context)

