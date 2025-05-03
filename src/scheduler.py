from apscheduler.schedulers.background import BackgroundScheduler
from helper import (main, calculate_general_room_availability, calculate_library_general_availability, determine_hours)
import time

def update_everything():
    """
    Runs helper.py main functions, in an interval of 10 minutes.
    """
    print("Scheduler started...")
    main()
    calculate_general_room_availability()
    calculate_library_general_availability(7, 10)
    determine_hours()

scheduler = BackgroundScheduler()
scheduler.add_job(update_everything, 'interval', minutes=10)
scheduler.start()

while True:
    time.sleep(60)
