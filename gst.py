import requests
from time import time

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

    def select_gst_num_radio(self):
        data = {
                'd-3': "true",
                'DOC_MODAL_ID__': "0",
                }
        self.fwdc.post("https://gst.customs.gov.my/TAP/_/Recalc", data=data)

    def enter_gst_num(self, gst_num):
        data = {
                'd-5': gst_num,
                'DOC_MODAL_ID__': "0",
                }
        r = self.fwdc.post("https://gst.customs.gov.my/TAP/_/Recalc", data=data)
        r.encoding = "utf-8-sig"
        return r.json()

