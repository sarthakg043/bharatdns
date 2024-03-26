from datetime import datetime
import concurrent.futures
import socket
from ml_model_server.dns_tunnelling_model import *
from dns_resolver_server.paralleldns import *
import pandas as pd
import os

import firebase_admin
from firebase_admin import db , credentials 

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred , {"databaseURL" : "https://fir-dns-default-rtdb.firebaseio.com"})

ref = db.reference("/")

# importing blacklist data domains
# Get the directory of the current script
script_dir_root = os.path.dirname(__file__)
# Construct the full path to the CSV file
# Read the CSV file using pandas
bl_df = pd.read_csv(os.path.join(script_dir_root, "blacklist.csv"), usecols=['domain'])
wl_df= pd.read_csv(os.path.join(script_dir_root, "whitelist.csv"),usecols=['domain'])

bl_domains = bl_df['domain'].apply(extract_domain)
wl_domains = wl_df['domain'].apply(extract_domain)


def insert_data(query_name , client_address , resolved, time , malicious , blacklist , whitelist , elapsed_time) :
    data = {
        'query_name': query_name,
        'client_address': client_address,
        'resolved_ip': resolved,
        'time': time,
        'time_elapsed': elapsed_time,
        'whitelist': whitelist,
        'blacklist': blacklist,
        'malicious': malicious
    }
    
    ref.push(data)


def addToWhitelist(new_data):
    global wl_df, wl_domains
    wl_df = wl_df.append(new_data, ignore_index=True) # Add the resolved domain to whitelist DataFrame
    wl_df.to_csv(os.path.join(script_dir_root, "whitelist.csv"), index=False)  # Save the updated whitelist to CSV
    wl_domains = wl_df['domain'].apply(extract_domain)


def handle_dns_request(request, client_address):
    start_time = datetime.now()
    query_name = str(request.question[0].name)
    print("Query Name: ", query_name)
    query_type = request.question[0].rdtype 
    is_reverse_lookup = query_name.endswith(".in-addr.arpa.")
    malicious = False
    blacklist = False
    whitelist = False
    resolved_ip = ""

    if is_reverse_lookup:
        # Handle reverse DNS lookup
        print("Reverse DNS lookup request received.")
        # Extract the IP address from the reverse query name
        ip_address = query_name.split('.')[0]
        
        # Perform reverse DNS resolution to get the domain name
        try:
            domain_name = socket.gethostbyaddr(ip_address)[0]
        except socket.herror as e:
            print(f"Reverse DNS lookup failed: {e}")
            domain_name = None
        
        # Construct DNS response
        response = dns.message.make_response(request)
        response.question = request.question

        if domain_name:
            # If domain name is resolved, add PTR record to response
            try:
                RRset = dns.rrset.from_text(query_name, 300, dns.rdataclass.IN, dns.rdatatype.PTR, domain_name)
                response.answer.append(RRset)
            except Exception as e:
                print(f"Error adding PTR record to response: {e}")
        else:
            # If reverse DNS lookup failed, respond with NXDOMAIN
            response.set_rcode(dns.rcode.NXDOMAIN)
    else:
        received_domain = extract_domain(query_name)
        received_domain =  received_domain[:-1] 
        received_domain = extract_domain(query_name)
        response = dns.message.make_response(request)
        response.question = request.question
        if received_domain in wl_domains.values:
            print(f"The domain {received_domain} is whitelisted. Proceed with DNS resolution.")
            # Resolve DNS
            response = handle_dns_record_type(response, query_name)
            whitelist = True

        elif received_domain in bl_domains.values:
            print(f"The domain {received_domain} is present in the blacklist file.")
            print(f"Blocked {received_domain}")
            # Implement your response for blacklisted domains (e.g., return an error response)
            try:
                RRset = dns.rrset.from_text(query_name, 300, dns.rdataclass.IN, query_type, "0.0.0.0")
                response.answer.append(RRset)
            except:
                print("Not Resolved, dummy ip sent!")
            blacklist = True
        else:
            # Implement your DNS processing logic here
            # For demonstration, just print a success message
            print(f"The domain {received_domain} is not blacklisted. Proceed with DNS resolution.")

            # Implement code for ML model

            # Connect to the ML server's address and port
            try:
                received_t = dns_ml_model_predict(query_name)
                if(received_t[0] == 1 and received_t[1] >=70):
                    # Block only if probability is greater than 70%
                    print(f"ML Model predicted malicious with probability {received_t[1]}%")
                    print(f"Blocked {query_name}")
                    # Implement code for dummy response
                    try:
                        RRset = dns.rrset.from_text(query_name, 300, dns.rdataclass.IN, query_type, "0.0.0.0")
                        response.answer.append(RRset)
                    except:
                        print("Not Resolved, dummy ip sent!")
                    malicious = True
                else:          
                    response = handle_dns_record_type(response, query_name)
                    if response.answer:
                        a_response = [i for i in str(response.answer[0]).split(" ")][4:]
                        resolved_ip = a_response[0]
                    if response.authority:
                        soa_response = [i for i in str(response.authority[0]).split(" ")][4:]
                        soa_response = " ".join(soa_response)[1:]
                        resolved_ip = soa_response
                    # Update whitelist if resolution successful
                    if resolved_ip != "0.0.0.0":
                        new_data = {'s': 0, 'domain': query_name, 'ip_address': resolved_ip}
                        addToWhitelist(new_data)
            except:
                print("ML Model ran into a problem so blocking all requests.")
                RRset = dns.rrset.from_text(query_name, 300, dns.rdataclass.IN, query_type, "0.0.0.0")
                response.answer.append(RRset)
                malicious = True
    
    # Set the query ID of the response message
    response.id = request.id
    
    # Calculate elapsed time
    end_time = datetime.now()
    elapsed_time = end_time - start_time
    
    # Insert data into Firebase
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    insert_data(query_name, client_address, resolved_ip, time, malicious, blacklist, whitelist, elapsed_time)
    
    print(f"Request of {query_name} is sent back to {client_address} at time {time}\n\n")
    server_socket.sendto(response.to_wire(), client_address)


def start_dns_server():
    while True:
        try:
            data, client_address = server_socket.recvfrom(1024)
            request = dns.message.from_wire(data)
           
            handle_dns_request(request, client_address)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('0.0.0.0', 53)
    server_socket.bind(server_address)
    
    print("\nServer listening at{}:{}..\n".format(*server_address))
    start_dns_server()