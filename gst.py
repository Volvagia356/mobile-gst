import requests
from time import time
from json import loads

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


s = FWDC()

r = s.get("https://gst.customs.gov.my/TAP/_/")
r = s.get("https://gst.customs.gov.my/TAP/_/", params={'Load': "1"})

data = {
        'DOC_MODAL_ID__': "0",
        'EVENT__': "b-i",
        'TYPE__': "0",
        }
r = s.post("https://gst.customs.gov.my/TAP/_/EventOccurred", data=data)

data = {
        'd-3': "true",
        'DOC_MODAL_ID__': "0",
        }
r = s.post("https://gst.customs.gov.my/TAP/_/Recalc", data=data)

data = {
        'd-5': "001564901376",
        'DOC_MODAL_ID__': "0",
        }
r = s.post("https://gst.customs.gov.my/TAP/_/Recalc", data=data)

json = loads(bytes(r.text, 'utf-8').decode('utf-8-sig'))

print(json)
