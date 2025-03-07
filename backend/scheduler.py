import asyncio
import threading
import schedule
import logging
import time
from backend.gios_api import fetch_and_save


def run_schedule() -> None :
    """Schedule periodic fetching of GIOŚ data every hour."""

    def job() :
        try :
            asyncio.run(fetch_and_save())
        except Exception as e :
            logging.error(f"Scheduled job failed: {e}")

    schedule.every(1).hours.do(job)

    def run_continuously() :
        while True :
            schedule.run_pending()
            time.sleep(60)  # Use time.sleep for synchronous thread

    thread = threading.Thread(target = run_continuously, daemon = True)
    thread.start()
    logging.info("Scheduler started in background thread")