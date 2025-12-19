# Az Stopwatch
Bu kitabxana "32:26:00" tipli saniyəölçən vaxtlarını oxumaq üçün nəzərdə tutulub.

## İstifadə:
```python
from az_stopwatch import describe_time_az, parse_time_string

time_input = "32:26:00"
print(describe_time_az(time_input))   # Nəticə: 32 dəqiqə, 26 saniyə
print(parse_time_string(time_input)) # Nəticə: 1946.0