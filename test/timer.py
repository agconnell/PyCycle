

def to_time(secs):
    h = 0
    m = 0
    s = 0
    if secs > 3599:
        h = int(secs / 3600)
        secs = secs - h * 3600
    if secs > 59:
        m = int(secs / 60)
        secs = secs - (m * 60)    
    s = secs
    
    print(f"{h:02}:{m:02}:{s:02}")

to_time(10)
to_time(59)
to_time(60)
to_time(120)
to_time(422) # '00:07:02'
to_time(3661)  # '01:01:01'
to_time(3660)  # '01:01:00' 
to_time(3601)  # '01:00:00'
to_time(3600)  # '01:00:00'
to_time(3599)  # '00:59:59'
to_time(7255)  # '02:00:55'
to_time(17254) # '04:47:34'
