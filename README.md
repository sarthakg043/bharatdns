 <center><img src="./src/transparent bg_Bharat_DNS.png" height="150"></center>

# bharatdns

About
-----

The DNS Resolver Server project is a lightweight DNS server implementation designed to resolve DNS queries via UDP. It provides a simple yet efficient way to handle DNS requests from clients and send back responses with resolved DNS records.

### Features:

1.  **UDP-based DNS Resolution:** The server listens for DNS requests over UDP, making it suitable for quick and lightweight DNS resolution tasks.
    
2.  **System-Configured Resolver:** Utilizes the system-configured DNS resolver to perform DNS queries, ensuring compatibility with various DNS configurations.
    
3.  **Support for Multiple Record Types:** Supports resolution of various types of DNS records, including "A", "AAAA", "MX", "CNAME", "TXT", and more.
    
4.  **Error Handling:** Handles DNS resolution errors gracefully, providing informative messages in case of failures or timeouts.
    
5.  **Flexible Configuration:** Easily configurable server settings, such as the server IP address and port number, allowing for customization based on deployment requirements.

6.  **Parallel Processing:** It implements parallel processing making the service highly scalable as the hardware spec are increased.
    

### Use Case:

The DNS Resolver Server project is particularly useful in scenarios where a lightweight DNS resolution solution is needed, such as:

*   Local network DNS resolution for internal services and resources.
*   DNS resolution for small-scale applications and services where a full-fledged DNS server may be overkill.
*   Educational purposes, allowing users to understand the basics of DNS resolution and server-side network programming.

### Technologies Used:

*   **Python:** The server implementation is written in Python, leveraging its simplicity and versatility for network programming tasks.
*   **dns.resolver:** Utilizes the `dns.resolver` module from the `dnspython` library for performing DNS queries.
*   **Socket Programming:** Implements UDP socket programming in Python to handle communication between the server and clients.

### Future Enhancements:

*   **TCP Support:** Extend the server to support TCP-based DNS resolution for handling large DNS responses and zone transfers.
*   **Cache Implementation:** Implement a caching mechanism to store resolved DNS records temporarily, improving response time for frequently requested records.
*   **Security Measures:** Introduce security features such as DNSSEC support and filtering capabilities to enhance the server's reliability and security.

___

# Tutorial:
### Note : Use only Python 3.11, not above

### You can create a virtual environment with python 3.11 then clone this github repo

1. move into bharatdns folder
2. run the server file 
```shell
python main.py
```
It will install all required dependencies.


### In case of Windows errors:
- If an Error occurs for enabling long paths in Windows 10/11, then you need to update your Registry file (.reg)
```shell
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem]
"LongPathsEnabled"=dword:00000001

```
- for this, you can open `Powershell` in Administrator mode and run followinf command
```shell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```
- and run `python ./main.py` again

It will promt to enter email id and password.
Then, It will start a udp server on your PC.

Now, use any other device on same network to make a dns query

For Windows:
```shell
nslookup google.com 192.168.1.2
```
where 192.168.1.2 must be replaced by your server PC's IP.

For Mac/Linux:
```shell
dig @192.168.1.2 google.com
```
where 192.168.1.2 must be replaced by your server PC's IP.

> Please refer to this video for a complete step by step demonstration - https://www.youtube.com/watch?v=MPd8maJ8cZQ

* One more thing, after making the video I added twitter in blacklist so, you might not able to visit twitter

If you want to see a frontend, [here it is](https://sarthakg043.github.io/bharatdns-frontend/)

The frontend is an admin Live Monitoring dashboard.



## Contact the Developers

1. Sarthak Gupta - 2022BCY0054 - sarthak22bcy54@iiitkottayam.ac.in
2. Dhanush Hebbar - 2022BCY0021
3. Arjun R. Nair
4. Rohit Reddy