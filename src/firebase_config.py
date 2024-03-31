import json
import pyrebase
import getpass 

def getFirebaseAPP():
    config={
        "apiKey": "AIzaSyBPCGPk6ucqRDOOujfMVs3Hdiy09TjvMMs",
        "authDomain": "fir-dns.firebaseapp.com",
        "databaseURL": "https://fir-dns-default-rtdb.firebaseio.com",
        "projectId": "fir-dns",
        "storageBucket": "fir-dns.appspot.com",
        "messagingSenderId": "906824867247",
        "appId": "1:906824867247:web:27314cfe011f5c1771635a",
        "measurementId": "G-MN6DT4DV3L"
    }
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    authe = firebase.auth()
    return authe, db

def authenticate_user(auth) :
    email = input('Enter email id : ')
    password = getpass.getpass('Enter password : ')

    try:
        user = auth.sign_in_with_email_and_password(email, password)
        # uid = user['localId'] 
        # print(uid) # Get the UID of the authenticated user
        print("Authentication successful\n\n")
        return user
    except Exception as e:
        error_data = json.loads(e.args[1])
        print("Authentication failed:", error_data['error']['message'], "\n\n")
        return 0 

def getNextRequestNo(database, user):
    l = len(database.child('bharatdns').child('requests').get(user['idToken']).val())
    return l

def create_data_object(query_name , client_address , resolved, time , malicious , blacklist , whitelist , elapsed_time): 
    data = {
        'query_name': str(query_name),
        'client_address': client_address,
        'resolved_ip': str(resolved),
        'time': str(time),
        'time_elapsed': str(elapsed_time),
        'whitelist': int(whitelist),
        'blacklist': int(blacklist),
        'malicious': float(malicious)
    }
    return data
    
def input_data(database, user, msg):
    data = {str(getNextRequestNo(database, user)) : msg}
    requests_ref = database.child("bharatdns").child("requests")
    requests_ref.update(data , user['idToken'])
