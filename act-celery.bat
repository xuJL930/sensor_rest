E:
cd PyProject\sensorEnv\Scripts\
call activate.bat
cd sensorDemo
celery -A sensorDemo worker -l info
start