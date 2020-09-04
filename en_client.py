from clickhouse_driver import Client

def en_client():
    client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')
    return client