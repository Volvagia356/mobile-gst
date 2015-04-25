from flask import Flask, render_template, redirect, request
from requests.exceptions import ConnectionError
import gst

app = Flask(__name__)
app.config['SITE_NAME'] = "MobileGST"

def search_view(search_func, search_by):
    def view():
        results = None
        error = None
        for i in range(10):
            try:
                if request.args['value']:
                    results = search_func(request.args['value'])
            except KeyError: pass
            except gst.GSTError as e:
                error = e
            except ConnectionError:
                continue
            break
        else:
            error = "Error communicating with Customs GST server. Please try again later."
        return render_template("search.htm", search_by=search_by, results=results, error=error)
    return view


@app.route("/")
def index():
    return redirect("/gst-num")

@app.route("/about")
def about():
    return render_template("about.htm")

app.add_url_rule("/gst-num", "gst_num", search_view(gst.search_gst_num, "GST Number"))
app.add_url_rule("/business-num", "business_num", search_view(gst.search_business_num, "Business Number"))
app.add_url_rule("/business-name", "business_name", search_view(gst.search_business_name, "Business Name"))

if __name__=="__main__":
    app.run(debug=True)
