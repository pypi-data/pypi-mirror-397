
from lazysdk import showdata
from lazynovel.crawler import changdu

_changdu = changdu.FanQie(
    cookie="",

)
res = _changdu.application_overview_list_v1(
    app_type=3,
    begin_date="202511",
    end_date="202512",
    distributor_id=1738876382032909,
    app_id=10003327
)
print(res.status_code)
print(res.text)
showdata.show_dict(res.json())