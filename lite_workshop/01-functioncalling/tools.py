import requests

# To add a tool to be used by Claude in main_demo.py,
# create your tool in python as shown below and then create
# a new string variable describing the tool spec. Copy the XML formatting
# that is shown in the below example.
#
# Once you have created your tool and your spec, add the spec variable to the
# list_of_tools_specs list.

def get_weather(latitude: str, longitude: str):
  url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
  response = requests.get(url)
  return response.json()

get_weather_description = """
<tool_description>
<tool_name>get_weather</tool_name>
<description>
Returns weather data for a given latitude and longitude. </description>
<parameters>
<parameter>
<name>latitude</name>
<type>string</type>
<description>The latitude coordinate as a string</description>
</parameter> <parameter>
<name>longitude</name>
<type>string</type>
<description>The longitude coordinate as a string</description>
</parameter>
</parameters>
</tool_description>
"""

# Define the Chrome user agent string
chrome_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

# Set the headers with the Chrome user agent
headers = {"User-Agent": chrome_user_agent}


def get_lat_long(place):

        url = "https://nominatim.openstreetmap.org/search"
        params = {'q': place, 'format': 'json', 'limit': 1}
        response=requests.get(url, headers=headers,params=params)
        print(response.content)
        response = requests.get(url, headers=headers,params=params).json()
        if response:
            lat = response[0]["lat"]
            lon = response[0]["lon"]
            return {"latitude": lat, "longitude": lon}
        else:
            return None

get_lat_long_description = """<tool_description>
<tool_name>get_lat_long</tool_name>
<description>
Returns the latitude and longitude for a given place name.
</description>
<parameters>
<parameter>
<name>place</name>
<type>string</type>
<description>
The place name to geocode and get coordinates for.
</description>
</parameter>
</parameters>
</tool_description>"""




list_of_tools_specs = [get_weather_description, get_lat_long_description]