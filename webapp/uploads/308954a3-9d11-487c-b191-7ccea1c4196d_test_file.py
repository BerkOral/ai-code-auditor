import os
import sqlite3
import pickle
import requests

def run_command(user_input):
    # 🔥 Command injection: user can run ANY shell command
    os.system(user_input)

def get_user_data(username):
    # 🔥 SQL injection: building query by concatenation
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '%s'" % username
    cursor.execute(query)
    return cursor.fetchall()

def deserialize_data(data):
    # 🔥 Insecure deserialization: arbitrary code execution
    return pickle.loads(data)

def fetch_data(url):
    # 🔥 SSRF / unvalidated HTTP request
    response = requests.get(url)
    return response.text

def main():
    cmd = input("1) Enter shell command to run: ")
    run_command(cmd)
    
    user = input("2) Enter username to look up: ")
    print(get_user_data(user))
    
    data = input("3) Enter pickled data: ")
    try:
        print(deserialize_data(data))
    except Exception as e:
        print("Deserialization error:", e)
    
    link = input("4) Enter URL to fetch: ")
    print(fetch_data(link))

if __name__ == '__main__':
    main()
