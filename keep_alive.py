from flask import Flask, request, abort
from threading import Thread

app = Flask('')

@app.route('/')
def home():
  return "CocoaBot is online!"

@app.route("/webhook", methods=["POST"])
def webhook():
  print("hqifhqif")
  if request.method == "POST":
    print(request.json)
    print("webhook recieved!")
    return "success", 200
  else:
    abort(400)
        
def run():
  app.run(host='0.0.0.0',port=5000)

def keep_alive():
  t = Thread(target=run)
  t.start()