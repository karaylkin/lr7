from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import requests
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

currency_data = {}
observers = []

def fetch_currency_rates():
    global currency_data
    while True:
        try:
            print("Попытка загрузить данные с API...")
            response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
            if response.status_code == 200:
                currency_data = response.json().get("Valute", {})
                print("Данные успешно получены:", currency_data)
                notify_observers()
            else:
                print("Ошибка при запросе данных:", response.status_code)
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
        time.sleep(60)

def notify_observers():
    if observers:
        print("Уведомление наблюдателей. Данные:", currency_data)
        socketio.emit('currency_update', currency_data)
    else:
        print("Нет активных наблюдателей")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    observer_id = request.sid
    observers.append(observer_id)
    print(f"Подключен клиент с ID: {observer_id}")
    emit('client_id', observer_id)

@socketio.on('disconnect')
def handle_disconnect():
    global observers
    observer_id = request.sid
    observers = [observer for observer in observers if observer != observer_id]
    print(f"Отключен клиент с ID: {observer_id}")

if __name__ == '__main__':
    print("Запуск потока для получения данных...")
    thread = threading.Thread(target=fetch_currency_rates)
    thread.daemon = True
    thread.start()

    print("Запуск сервера...")
    socketio.run(app, debug=True)
I
