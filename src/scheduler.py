from apscheduler.schedulers.background import BackgroundScheduler
from helper import (main, calculate_general_room_availability, calculate_library_general_availability)
import time

def update_everything():
    print("Running library data update...")
    main()
    calculate_general_room_availability()
    calculate_library_general_availability(7, 10)

scheduler = BackgroundScheduler()
scheduler.add_job(update_everything, 'interval', minutes=5)
scheduler.start()

while True:
    time.sleep(60)
