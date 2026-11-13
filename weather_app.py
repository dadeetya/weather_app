from flask import Flask, render_template, request
import requests

app = Flask(__name__)

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(city):
    """Returns (data, error). One of them is always None."""
    try:
        geo = requests.get(GEO_URL, params={"name": city, "count": 1}, timeout=10).json()
        if "results" not in geo:
            return None, "Invalid city, try again."

        place = geo["results"][0]

        weather = requests.get(
            WEATHER_URL,
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            },
            timeout=10,
        ).json()

        now = weather["current"]
        data = {
            "city": place["name"],
            "country": place["country"],
            "temp": now["temperature_2m"],
            "humidity": now["relative_humidity_2m"],
            "wind": now["wind_speed_10m"],
        }
        return data, None

    except requests.exceptions.RequestException:
        return None, "Check your internet."


@app.route("/", methods=["GET", "POST"])
def home():
    data = None
    error = None

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        if city == "":
            error = "Please enter a city name!"
        else:
            data, error = get_weather(city)

    return render_template("index.html", data=data, error=error)


if __name__ == "__main__":
    app.run(debug=True)