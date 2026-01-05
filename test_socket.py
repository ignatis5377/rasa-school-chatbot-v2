import socketio
import time

sio = socketio.Client()

@sio.event
def connect():
    print("✅ CONNECTION SUCCESSFUL!")
    print("Sending 'γεια' to bot...")
    sio.emit('user_uttered', {'message': 'γεια', 'session_id': 'test_user_123'})

@sio.event
def bot_uttered(data):
    print(f"🤖 BOT REPLIED: {data.get('text')}")
    # Force disconnect after reply to end script
    sio.disconnect()

@sio.event
def connect_error(data):
    print(f"❌ CONNECTION FAILED: {data}")

@sio.event
def disconnect():
    print("Disconnected from server.")

if __name__ == '__main__':
    print("Attempting to connect to http://localhost:5005...")
    try:
        sio.connect('http://localhost:5005')
        sio.wait()
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        print("Ensure 'start_local.bat' is running and 'credentials.yml' has socketio enabled.")
