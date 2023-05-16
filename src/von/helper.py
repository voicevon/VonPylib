import calendar
import time

last_time_stamp = 0

class Helper:

    @classmethod
    def get_timestamp(cls) ->int:
        global last_time_stamp

        current_GMT = time.gmtime()
        timestamp = calendar.timegm(current_GMT)
        if timestamp <= last_time_stamp:
            timestamp += last_time_stamp + 1
        last_time_stamp = timestamp
        return last_time_stamp