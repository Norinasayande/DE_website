import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)    

def get_connection():
    return sqlite3.connect("./website.db")
    
#homepage 
@app.route("/", methods=["GET", "POST"]) 
def index():
    return render_template("index.html")

#info page
@app.route("/Info") 
def Info():
    return render_template("Info.html")

#data page
@app.route("/data", methods=["GET", "POST"])
def data():
    conn = get_connection()

    # Get country names in alphabetical order
    countries = pd.read_sql(
        "SELECT DISTINCT country_name FROM Country ORDER BY country_name ASC",
        conn
    )["country_name"].tolist()

    conn.close()

    selected_country = None
    plot_url = None
    message = None

    if request.method == "POST":
        selected_country = request.form["country"]
        plot_url = generate_plot(selected_country)

        if plot_url is None:
            message = "No data available for that country."

    return render_template(
        "data.html",
        countries=countries,
        selected_country=selected_country,
        plot_url=plot_url,
        message=message
    )



@app.route("/About_contact") 
def about_contact():
    return render_template('About_contact.html')


import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import numpy as np

def generate_plot(country):
    conn = get_connection()

    ghg = pd.read_sql(
        "SELECT Year, Emissions FROM GreenhouseGasEmissions WHERE Country = ?",
        conn, params=(country,))
    defo = pd.read_sql(
        "SELECT Year, Deforestation FROM Deforestation WHERE Country = ?",
        conn, params=(country,))
    conn.close()

    # Clean and drop invalid data
    ghg["Year"] = pd.to_numeric(ghg["Year"], errors="coerce")
    ghg["Emissions"] = pd.to_numeric(ghg["Emissions"], errors="coerce")
    defo["Year"] = pd.to_numeric(defo["Year"], errors="coerce")
    defo["Deforestation"] = pd.to_numeric(defo["Deforestation"], errors="coerce")

    ghg = ghg.dropna()
    defo = defo.dropna()

    if ghg.empty and defo.empty:
        return None

    # Decide layout
    if not ghg.empty and not defo.empty:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    else:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax1 = ax2 = ax  # Reuse axis if only one plot is needed

    # Greenhouse Gas plot
    if not ghg.empty:
        ax1.plot(ghg["Year"], ghg["Emissions"], color="green")
        ax1.set_title("Greenhouse Gas Emissions")
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Emissions")
        ax1.set_xticks(np.arange(min(ghg["Year"]), max(ghg["Year"])+1, 3))
        ax1.tick_params(axis='x', rotation=45)
    else:
        ax1.text(0.5, 0.5, "No Greenhouse Gas Emissions data available",
                 horizontalalignment='center', verticalalignment='center',
                 transform=ax1.transAxes, fontsize=12, color='gray')
        ax1.set_axis_off()

    # Deforestation plot
    if not defo.empty:
        if ghg.empty:
            ax1 = ax2  # reuse axis if GHG was missing
        ax2.plot(defo["Year"], defo["Deforestation"], color="brown")
        ax2.set_title("Deforestation")
        ax2.set_xlabel("Year")
        ax2.set_ylabel("Hectares Lost")
        ax2.set_xticks(np.arange(min(defo["Year"]), max(defo["Year"])+1, 3))
        ax2.tick_params(axis='x', rotation=45)
    else:
        ax2.text(0.5, 0.5, "No Deforestation data available",
                 horizontalalignment='center', verticalalignment='center',
                 transform=ax2.transAxes, fontsize=12, color='gray')
        ax2.set_axis_off()

    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return f"data:image/png;base64,{plot_url}"
def generate_plot(country):
    conn = get_connection()

    ghg = pd.read_sql(
        "SELECT Year, Emissions FROM GreenhouseGasEmissions WHERE Country = ?",
        conn, params=(country,))
    defo = pd.read_sql(
        "SELECT Year, Deforestation FROM Deforestation WHERE Country = ?",
        conn, params=(country,))
    conn.close()

    # Clean types safely
    ghg["Year"] = pd.to_numeric(ghg["Year"], errors="coerce")
    ghg["Emissions"] = pd.to_numeric(ghg["Emissions"], errors="coerce")
    defo["Year"] = pd.to_numeric(defo["Year"], errors="coerce")
    defo["Deforestation"] = pd.to_numeric(defo["Deforestation"], errors="coerce")
    ghg = ghg.dropna()
    defo = defo.dropna()

    if ghg.empty and defo.empty:
        return None

    # Decide number of plots
    if not ghg.empty and not defo.empty:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    else:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax1 = ax2 = ax  # single axis fallback

    if not ghg.empty:
        ax1.plot(ghg["Year"], ghg["Emissions"], color="green")
        ax1.set_title("Greenhouse Gas Emissions Due to Agriculture")
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Emissions")
        ax1.set_xticks(np.arange(min(ghg["Year"]), max(ghg["Year"])+1, 3))
        ax1.tick_params(axis='x', rotation=45)

    if not defo.empty:
        if ghg.empty:
            # If only defo is available, reuse ax1 (same as ax2 in fallback mode)
            ax1 = ax2
        ax2.plot(defo["Year"], defo["Deforestation"], color="brown")
        ax2.set_title("Commodity Driven Deforestation")
        ax2.set_xlabel("Year")
        ax2.set_ylabel("Hectares Lost")
        ax2.set_xticks(np.arange(min(defo["Year"]), max(defo["Year"])+1, 3))
        ax2.tick_params(axis='x', rotation=45)

    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return f"data:image/png;base64,{plot_url}"




if __name__ == "__main__":
    app.run(debug=True)