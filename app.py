from flask import Flask, render_template, redirect, request
import gst

app = Flask(__name__)
app.config['SITE_NAME'] = "MobileGST"

def search_view(search_func, search_by):
    def view():
        results = None
        try:
            if request.args['value']:
                results = search_func(request.args['value'])
        except KeyError: pass
        return render_template("search.htm", search_by=search_by, results=results)
    return view


@app.route("/")
def index():
    return redirect("/gst-num")

app.add_url_rule("/gst-num", "gst_num", search_view(gst.search_gst_num, "GST Number"))
app.add_url_rule("/business-num", "business_num", search_view(gst.search_business_num, "Business Number"))
app.add_url_rule("/business-name", "business_name", search_view(gst.search_business_name, "Business Name"))

if __name__=="__main__":
    app.run(debug=True)
