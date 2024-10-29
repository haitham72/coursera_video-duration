from flask import Flask, render_template, request
import re
from datetime import timedelta


app = Flask(__name__)

# Parsing function
def parse_course_data(data):
    videos = []
    labs = []
    total_duration = timedelta()  # total duration as a timedelta object

    lines = data.strip().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        if "Video" in line:
            # Capture title and duration
            title = lines[i + 1] if i + 1 < len(lines) else "Unknown Title"
            duration_match = re.search(r"(\d+)\s*(minutes|min|hour|h)", line)
            if duration_match:
                duration_value, unit = int(duration_match.group(1)), duration_match.group(2)
                if "hour" in unit or "h" in unit:
                    total_duration += timedelta(hours=duration_value)
                elif "minute" in unit or "min" in unit:
                    total_duration += timedelta(minutes=duration_value)
                videos.append(f"{title}: {duration_value} {unit}")

        elif "Lab" in line:
            # Capture lab title and duration by checking the previous line for title
            title = lines[i - 1] if i > 0 else "Unknown Title"
            duration_match = re.search(r"(\d+)\s*(minutes|min|hour|h)", line)
            if duration_match:
                duration_value, unit = int(duration_match.group(1)), duration_match.group(2)
                labs.append(f"{title}: {duration_value} {unit}")
                if "hour" in unit or "h" in unit:
                    total_duration += timedelta(hours=duration_value)
                elif "minute" in unit or "min" in unit:
                    total_duration += timedelta(minutes=duration_value)

        i += 1

    return videos, labs, total_duration

# Helper functions for duration formatting
def format_duration(duration):
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes = remainder // 60
    return f"{int(hours)} hrs {int(minutes)} mins"

def adjusted_duration(duration, speed=1.25):
    adjusted_time = duration.total_seconds() / speed
    adjusted_duration = timedelta(seconds=adjusted_time)
    return format_duration(adjusted_duration)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        data = request.form["course_data"]
        videos, labs, total_duration = parse_course_data(data)
        total_duration_str = format_duration(total_duration)
        adjusted_duration_str = adjusted_duration(total_duration, 1.25)
        return render_template("results.html", videos=videos, labs=labs, 
                               total_duration=total_duration_str, 
                               adjusted_duration=adjusted_duration_str)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
