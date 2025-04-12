from flask import Flask, render_template
import json
import os

app = Flask(__name__)

DATA_PATH = "../data_output.json"
CHART_DIR = "static/charts"

@app.route("/")
def report():
    if not os.path.exists(DATA_PATH):
        return "Veri dosyası bulunamadı. Lütfen önce main.py'yi çalıştırın."

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return render_template("report.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
