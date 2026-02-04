from flask import Flask,render_template, request

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None

    if request.method == "POST":
        remaining = float(request.form["data"])
        total = 24
        result = f"Remaining data: {remaining} GB out of {total} GB"
    return render_template('dashboard.html', result=result)

if __name__ == "__main__":
    app.run()