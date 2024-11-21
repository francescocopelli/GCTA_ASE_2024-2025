import requests
import json
import threading
url = "http://localhost:8081/users/admin_auth/login"

payload = json.dumps({
  "username": "admin",
  "password": "prova"
})
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VyX3R5cGUiOiJBRE1JTiIsImV4cGlyYXRpb24iOiIyMDI0LTExLTIwIDIyOjA4OjEzLjU5MDQ5OCJ9.1JmkVE1N-njMXfjnAgP1yourjPMMZJuEQst_dwvaAJc'
}
def send_request(url, headers, payload):
    error_count = 0
    for _ in range(0, 1000):
        response = requests.request("POST", url, headers=headers, data=payload)
        print(f'response result: {response.status_code}')
        if response.status_code != 200:
            error_count += 1
            if error_count >= 5:
                print("Too many errors, stopping requests.")
                break
        else:
            error_count = 0

#creo 4 thread
threads = []
for i in range(0, 10):
    threads.append(threading.Thread(target=send_request, args=(url, headers, payload)))
    threads[i].start()

#wait for all threads to finish
for i in range(0, 4):
    threads[i].join()



    

#print(response.text)
