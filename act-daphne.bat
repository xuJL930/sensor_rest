E:
cd PyProject\sensorEnv\Scripts\
call activate.bat
cd sensorDemo
daphne -b 0.0.0.0 sensorDemo.asgi:channel_layer --port 8000
start