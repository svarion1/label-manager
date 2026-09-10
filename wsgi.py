from app import create_app

app = create_app()

if __name__ == "__main__":
    # Bind to 0.0.0.0 so your phone can reach it over LAN.
    app.run(host="0.0.0.0", port=5050, debug=True)