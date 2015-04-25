import requests
from time import time
from bs4 import BeautifulSoup

class FWDC(requests.Session):
    def __init__(self, *args, **kwargs):
        self.fwdc_data = {}
        self.fwdc_data['FAST_CLIENT_WINDOW__'] = "FWDC.WND-0000-0000-0000"
        self.fwdc_data['FAST_CLIENT_AJAX_ID__'] = 0
        super(FWDC, self).__init__(*args, **kwargs)

    def before_request(self):
        self.fwdc_data['FAST_CLIENT_WHEN__'] = str(int(time()*1000))
        self.fwdc_data['FAST_CLIENT_AJAX_ID__'] += 1

    def after_request(self, response):
        try:
            self.fwdc_data['FAST_VERLAST__'] = response.headers['Fast-Ver-Last']
            self.fwdc_data['FAST_VERLAST_SOURCE__'] = response.headers['Fast-Ver-Source']
        except KeyError:
            pass

    def get(self, *args, **kwargs):
        self.before_request()
        if "params" not in kwargs: kwargs['params'] = {}
        kwargs['params'].update(self.fwdc_data)
        r = super(FWDC, self).get(*args, **kwargs)
        self.after_request(r)
        return r
    
    def post(self, *args, **kwargs):
        self.before_request()
        if "data" not in kwargs: kwargs['data'] = {}
        kwargs['data'].update(self.fwdc_data)
        r = super(FWDC, self).post(*args, **kwargs)
        self.after_request(r)
        return r

class GST():
    def __init__(self):
        self.fwdc = FWDC()

    def load_front_page(self):
        self.fwdc.get("https://gst.customs.gov.my/TAP/_/")
        self.fwdc.get("https://gst.customs.gov.my/TAP/_/", params={'Load': "1"})

    def click_lookup_gst_status(self):
        data = {
                'DOC_MODAL_ID__': "0",
                'EVENT__': "b-i",
                'TYPE__': "0",
                'CLOSECONFIRMED__': "false",
                }
        self.fwdc.post("https://gst.customs.gov.my/TAP/_/EventOccurred", data=data)

    def select_radio_button(self, button_id):
        data = {
                button_id: "true",
                'DOC_MODAL_ID__': "0",
                }
        self.fwdc.post("https://gst.customs.gov.my/TAP/_/Recalc", data=data)
    
    def enter_text_field(self, field_id, text):
        data = {
                field_id: text,
                'DOC_MODAL_ID__': "0",
                }
        r = self.fwdc.post("https://gst.customs.gov.my/TAP/_/Recalc", data=data)
        r.encoding = "utf-8-sig"
        return r.json()

    def select_gst_num_radio(self):
        self.select_radio_button("d-3")

    def select_business_num_radio(self):
        self.select_radio_button("d-6")

    def select_business_name_radio(self):
        self.select_radio_button("d-8")

    def enter_gst_num(self, gst_num):
        return self.enter_text_field("d-5", gst_num)

    def enter_business_num(self, business_num):
        return self.enter_text_field("d-7", business_num)

    def enter_business_name(self, business_name):
        return self.enter_text_field("d-9", business_name)

class GSTError(Exception): pass

def find_field_update(fwdc_response, field):
    for field_update in fwdc_response['Updates']['FieldUpdates']:
        if field_update['field'] == field:
            return field_update

def is_field_visible(fwdc_response, field):
    field_update = find_field_update(fwdc_response, field)
    if field_update:
        return field_update.get("visible", False)
    return False

def parse_business_table(table_html):
    FIELDS = ["gst_num", "name", "date", "status"]
    soup = BeautifulSoup(table_html)
    rows = soup.tbody.find_all("tr", class_="DataRow", recursive=False)
    data = []
    for row in rows:
        cells = row.find_all("td", recursive=False)
        row_data = []
        for cell in cells:
            cell_data = cell.get_text()
            row_data.append(cell_data)
        row_dict = dict(zip(FIELDS, row_data))
        data.append(row_dict)
    return data

def get_table_from_response(fwdc_response):
    field_update = find_field_update(fwdc_response, "d-f")
    if not field_update:
        if is_field_visible(fwdc_response, "d-i"):
            raise GSTError("No Registrants Found!")
        elif is_field_visible(fwdc_response, "d-l"):
            raise GSTError("Over 100 results found. Please narrow search terms!")
        elif is_field_visible(fwdc_response, "d-n"):
            raise GSTError("Server under maintenance. Please check back later!")
        else:
            raise GSTError("Unknown error occured!")
    table_html = field_update['value']
    return parse_business_table(table_html)

def prepare_GST():
    s = GST()
    s.load_front_page()
    s.click_lookup_gst_status()
    return s

def search_gst_num(gst_num):
    s = prepare_GST()
    s.select_gst_num_radio()
    response = s.enter_gst_num(gst_num)
    return get_table_from_response(response)

def search_business_num(business_num):
    s = prepare_GST()
    s.select_business_num_radio()
    response = s.enter_business_num(business_num)
    return get_table_from_response(response)

def search_business_name(business_name):
    s = prepare_GST()
    s.select_business_name_radio()
    response = s.enter_business_name(business_name)
    return get_table_from_response(response)
