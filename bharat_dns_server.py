from datetime import datetime
import concurrent.futures
import socket
from ml_model_server.dns_tunnelling_model import *
from dns_resolver_server.paralleldns import *
import pandas as pd
import os

# importing blacklist data domains
# Get the directory of the current script
script_dir_root = os.path.dirname(__file__)
# Construct the full path to the CSV file
# Read the CSV file using pandas
bl_df = pd.read_csv(os.path.join(script_dir_root, "blacklist.csv"), usecols=['domain'])
wl_df= pd.read_csv(os.path.join(script_dir_root, "whitelist.csv"),usecols=['domain'])

bl_domains = bl_df['domain'].apply(extract_domain)
wl_domains = wl_df['domain'].apply(extract_domain)

def addToWhitelist(new_data):
    global wl_df, wl_domains
    wl_df = wl_df._append(new_data, ignore_index=True) # Add the resolved domain to whitelist DataFrame
    wl_df.to_csv(os.path.join(script_dir_root, "whitelist.csv"), index=False)  # Save the updated whitelist to CSV
    wl_domains = wl_domains._append(pd.Series([new_data['domain']]), ignore_index=True)
    wl_df= pd.read_csv(os.path.join(script_dir_root, "whitelist.csv"),usecols=['domain'])
    wl_domains = wl_df['domain'].apply(extract_domain)


def handle_dns_request(request, client_address):
    query_name = str(request.question[0].name)
    print("Query Name: ",query_name)
    query_type = request.question[0].rdtype
    received_domain = extract_domain(query_name)
    received_domain =  received_domain[:-1] 
    received_domain = extract_domain(query_name)
    response = dns.message.make_response(request)
    response.question = request.question 
    
    if received_domain in wl_domains.values:
        print(f"The domain {received_domain} is whitelisted. Proceed with DNS resolution.")
        # Resolve DNS
        response = handle_dns_record_type(response, query_name)

    elif received_domain in bl_domains.values:
        print(f"The domain {received_domain} is present in the blacklist file.")
        print(f"Blocked {received_domain}")
        # Implement your response for blacklisted domains (e.g., return an error response)
        try:
            RRset = dns.rrset.from_text(query_name, 300, dns.rdataclass.IN, query_type, "0.0.0.0")
            response.answer.append(RRset)
        except:
            print("Not Resolved, dummy ip sent!")
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
            else:          
                response = handle_dns_record_type(response, query_name)
                if response.answer:
                    a_response = [i for i in str(response.answer[0]).split(" ")][4:]
                    new_data = {'s': 0, 'domain': query_name, 'ip_address': a_response[0]}
                if response.authority:
                    soa_response = [i for i in str(response.authority[0]).split(" ")][4:]
                    soa_response = " ".join(soa_response)[1:]
                    new_data = {'s': 0, 'domain': query_name, 'ip_address': soa_response}
                
                # Update whitelist if resolution successful
                if(new_data['ip_address'] != "0.0.0.0"):
                    addToWhitelist(new_data)
                    
            print("...ML Detection finished.")
        except:
            print("ML Model ran into a problem so blocking all requests.")
            RRset = dns.rrset.from_text(query_name, 300, dns.rdataclass.IN, query_type, "0.0.0.0")
            response.answer.append(RRset)
            
    # Set the query ID of the response message
    response.id = request.id
    print(f"Request of {query_name} is sent back to {client_address} at time {datetime.now()}\n\n")
    server_socket.sendto(response.to_wire(), client_address)

def handle_dns_request_parallel(request, client_address):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(handle_dns_request, request, client_address)
        return_value = future.result()


def start_dns_server():
    
    while True:
        try:
            data, client_address = server_socket.recvfrom(1024)
            request = dns.message.from_wire(data)
            
            handle_dns_request_parallel(request, client_address)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('0.0.0.0', 53)
    server_socket.bind(server_address)
    
    print("\nServer listening at{}:{}..\n".format(*server_address))
    start_dns_server()