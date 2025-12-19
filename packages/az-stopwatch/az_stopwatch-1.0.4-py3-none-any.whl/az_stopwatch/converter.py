import re 

def parse_time_string(time_str):
    parts = time_str.split(':')
    if len(parts) == 2:
        minutes = float(parts[0])
        seconds = float(parts[1])
        return (minutes * 60) + seconds
    
    elif len(parts) >= 3:
        hours = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])

        ms = float(parts[3]) / 100 if len(parts) == 4 else 0
        return (hours * 3600) + (minutes * 60) + seconds + ms
    
    else:
        raise ValueError("Yanlış format! MM:SS və ya HH:MM:SS formatında daxil edin.")
    
def describe_time_az(time_str):
    total_seconds = parse_time_string(time_str)
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    parts = []

    if hours > 0:
        parts.append(f"{hours} saat")
    if minutes > 0:
        parts.append(f"{minutes} deqiqe")
    if seconds > 0 or not parts:
        parts.append(f"{seconds} saniye")


    return ", ".join(parts)

