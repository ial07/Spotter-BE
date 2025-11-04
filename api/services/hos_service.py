from ..constants import (
    MAX_CYCLE_HOURS, MAX_DRIVING_HOURS, MAX_DRIVING_BEFORE_BREAK, 
    MIN_MANDATORY_BREAK, DAILY_SHIFT_LIMIT, DAILY_REST_BREAK
)
from ..utils.helpers import format_time_24hr

def generate_hos_logbook(total_driving_hours, current_cycle_used, total_on_duty_non_driving, pickup_location):
    """
    Simulates ELD logs based on HOS rules.
    This function generates a multi-day logbook array based on the input parameters.
    (Logic remains mostly the same, but now imports constants and helpers)
    """
    logbook_events = []
    current_time = 7.0 # Starting time in hours (7:00 AM)
    current_day = 1
    remaining_driving_time = total_driving_hours
    
    current_cycle_used = min(current_cycle_used, MAX_CYCLE_HOURS)
    
    while remaining_driving_time > 0:
        daily_log = {"day": current_day, "events": []}
        
        # 1. Mandatory 10-Hour Rest Break (OFF_DUTY)
        daily_log['events'].append({
            "status": "OFF_DUTY", 
            "duration_hours": DAILY_REST_BREAK, 
            "start_time": format_time_24hr(current_time),
            "notes": "Mandatory 10-Hour Reset Break"
        })
        current_time += DAILY_REST_BREAK 
        
        daily_driving_limit = MAX_DRIVING_HOURS 
        daily_duty_limit = DAILY_SHIFT_LIMIT
        
        # Apply non-driving duty only on the first day
        duty_non_driving = total_on_duty_non_driving if current_day == 1 else 0

        # Determine the maximum driving time allowed today
        max_driving_today = min(
            daily_driving_limit,                           
            daily_duty_limit - duty_non_driving,             
            MAX_CYCLE_HOURS - current_cycle_used              
        )

        driving_to_do_today = min(max_driving_today, remaining_driving_time)
        driving_completed = 0
        
        if driving_to_do_today <= 0:
            break 
            
        # 2. Initial Non-Driving Duty
        if duty_non_driving > 0:
            daily_log['events'].append({
                "status": "ON_DUTY", 
                "duration_hours": duty_non_driving, 
                "start_time": format_time_24hr(current_time),
                "notes": f"Initial Duty: Inspection and Paperwork ({pickup_location})"
            })
            current_time += duty_non_driving

        # 3. Driving Segment 1 (up to 8 hours)
        driving_segment_1 = min(driving_to_do_today, MAX_DRIVING_BEFORE_BREAK)
        if driving_segment_1 > 0:
            daily_log['events'].append({
                "status": "DRIVING", 
                "duration_hours": driving_segment_1, 
                "start_time": format_time_24hr(current_time),
                "notes": "Driving Segment 1"
            })
            current_time += driving_segment_1
            driving_completed += driving_segment_1
            remaining_driving_time -= driving_segment_1
            current_cycle_used += driving_segment_1 + duty_non_driving 

        # 4. Mandatory 30-Minute Break (if needed and time remains)
        if driving_completed >= MAX_DRIVING_BEFORE_BREAK and remaining_driving_time > 0:
            daily_log['events'].append({
                "status": "OFF_DUTY", 
                "duration_hours": MIN_MANDATORY_BREAK, 
                "start_time": format_time_24hr(current_time),
                "notes": "Mandatory 30-Minute Break"
            })
            current_time += MIN_MANDATORY_BREAK 
        
        # 5. Driving Segment 2 (Remaining driving time)
        driving_segment_2 = min(driving_to_do_today - driving_completed, remaining_driving_time)
        if driving_segment_2 > 0:
            daily_log['events'].append({
                "status": "DRIVING", 
                "duration_hours": driving_segment_2, 
                "start_time": format_time_24hr(current_time),
                "notes": "Driving Segment 2 (Final for the day)"
            })
            current_time += driving_segment_2
            remaining_driving_time -= driving_segment_2
            current_cycle_used += driving_segment_2
        
        end_time_log = current_time
        
        # 6. End of Shift / Sleeper Berth (if there is time left in the 24 hour day)
        if end_time_log < 24.0:
            daily_log['events'].append({
                "status": "SLEEPER_BERTH", 
                "duration_hours": 24.0 - end_time_log, 
                "start_time": format_time_24hr(current_time),
                "notes": "End of Shift / Remaining time in Sleeper Berth"
            })
            
        logbook_events.append(daily_log)
        current_day += 1
        current_time = 0.0 # Reset time for the next day's 10-hour reset
            
    return logbook_events