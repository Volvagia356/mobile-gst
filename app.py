from flask import Flask, render_template

app = Flask(__name__)
app.config['SITE_NAME'] = "MobileGST"

@app.route("/")
def index():
    return render_template("template.htm")

if __name__=="__main__":
    app.run(debug=True)
