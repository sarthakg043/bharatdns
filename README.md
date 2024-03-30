# bharatdns

### Note : Use only Python 3.11, not above

### You can create a virtual environment with python 3.11 then clone this github repo

1. move into bharatdns folder
2. Install dependencies
```shell
pip cache purge
pip install -r requirements.txt
```

3. run the server file 
```shell
python bharat_dns_server.py
```

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

This is a server based product, hence, there is no frontend.