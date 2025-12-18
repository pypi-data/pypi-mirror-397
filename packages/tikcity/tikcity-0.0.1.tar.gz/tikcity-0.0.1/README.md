# tikcity

A simple, robust Python library to get the current local time of any city in the world.

## Description

**tikcity** solves the problem of finding the exact local time for a specific city when you don't know its timezone. It automatically handles:
1.  **Geocoding:** Locating the city by name (e.g., "Paris", "New York", "Mumbai").
2.  **Timezone Lookup:** Finding the correct timezone for that location.
3.  **Time Formatting:** Returning the current wall-clock time with the timezone abbreviation (e.g., EST, IST, CET).

## Installation

Install the package via pip:

pip install tikcity

Install the package via uv:

uv add tikcity

## Usage

Using the library is straightforward. Import the `get_time` function and pass the name of any city.

import tikcity

Get time for a major city
print(tikcity.get_time("London"))

Output: 2025-12-17 10:30:00 GMT
Get time for a specific location
print(tikcity.get_time("San Francisco"))

Output: 2025-12-17 02:30:00 PST
Handle potential errors (e.g., city not found)
print(tikcity.get_time("Atlantis"))

Output: Error: City 'Atlantis' not found.

## Features

*   **Global Coverage:** Works with practically any city name recognized by standard geocoding services.
*   **Timezone Aware:** Automatically detects the correct timezone (including Daylight Saving Time adjustments).
*   **Simple API:** No need to handle latitude, longitude, or timezone strings yourself.

## Dependencies

This library relies on the following powerful packages:
*   [geopy](https://pypi.org/project/geopy/) - For locating cities.
*   [timezonefinder](https://pypi.org/project/timezonefinder/) - For mapping coordinates to timezones.
*   [pytz](https://pypi.org/project/pytz/) - For accurate timezone calculations.

## License

This project is licensed under the MIT License.