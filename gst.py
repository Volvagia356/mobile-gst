import requests
from time import time
from bs4 import BeautifulSoup

class FWDC(requests.Session):
    def __init__(self, *args, **kwargs):
        self.fwdc_data = {}
        super().__init__(*args, **kwargs)
    
    def after_request(self, response):
        try:
            self.fwdc_data['FAST_VERLAST__'] = response.headers['Fast-Ver-Last']
        except KeyError:
            pass

    def get(self, *args, **kwargs):
        if "params" not in kwargs: kwargs['params'] = {}
        kwargs['params'].update(self.fwdc_data)
        r = super().get(*args, **kwargs)
        self.after_request(r)
        return r
    
    def post(self, *args, **kwargs):
        if "data" not in kwargs: kwargs['data'] = {}
        kwargs['data'].update(self.fwdc_data)
        r = super().post(*args, **kwargs)
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

def find_field_update(fwdc_response, field):
    for field_update in fwdc_response['Updates']['FieldUpdates']:
        if field_update['field'] == field:
            return field_update

def parse_business_table(table_html):
    FIELDS = ["gst_num", "name", "date", "status"]
    soup = BeautifulSoup(table_html)
    rows = soup.tbody.find_all("tr", recursive=False)
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
    table_html = find_field_update(fwdc_response, "d-f")['value']
    return parse_business_table(table_html)

def search_gst_num(gst_num):
    s = GST()
    s.load_front_page()
    s.click_lookup_gst_status()
    s.select_gst_num_radio()
    response = s.enter_gst_num(gst_num)
    return get_table_from_response(response)
