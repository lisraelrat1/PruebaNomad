from flask import Flask
from flask import render_template
import functions


app = Flask(__name__)
transactions = functions.main()

@app.route("/")
def home():
    return render_template("index.html", transactions = transactions)

if __name__ == "__main__":
    app.run(debug=True)