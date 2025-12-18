from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz

def get_time(city_name):
    """
    Returns the current time in the specified city as a string.
    """
    try:
        # 1. Get coordinates
        geolocator = Nominatim(user_agent="tikcity_app_v1", timeout=10)
        location = geolocator.geocode(city_name)
        
        if not location:
            return f"Error: City '{city_name}' not found."
            
        # 2. Get timezone from coordinates
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
        
        if not timezone_str:
            return "Error: Timezone could not be determined."
            
        # 3. Get current time
        target_timezone = pytz.timezone(timezone_str)
        target_time = datetime.now(target_timezone)
        
        return target_time.strftime(f"%Y-%m-%d %H:%M:%S %Z")
        
    except (GeocoderTimedOut, GeocoderUnavailable):
        return "Error: Geolocation service timed out. Please try again."
    except Exception as e:
        return f"An error occurred: {e}"


