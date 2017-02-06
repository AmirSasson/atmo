import httplib, json


def choose_ammotion(ammotions):
    neutral = ammotions.pop('neutral')
    if neutral >= 0.9:
        return 'neutral'
    for a in ('contempt','surprise'):
        ammotions.pop(a)
    print ammotions
    print
    top = max([p for p in ammotions.iteritems() if p[0]!='neutral'], key=lambda x:x[1])[0]
    if ammotions[top] >= 0.6:
        return top

    top1 = max([p for p in ammotions.iteritems() if p[0]!='neutral'], key=lambda x:x[1])[0]
    if ammotions[top1] >= 0.1:
        return top1
    else:
        return top

def get_ammotion(image_bytes):
    headers = {
       # Request headers
       'Content-Type': 'application/octet-stream',
       'Ocp-Apim-Subscription-Key': '805ed835a4e04767847ac810c8fdce87',
    }
    try:
        print('helo')
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/emotion/v1.0/recognize", image_bytes, headers)
        response = conn.getresponse()
        data = response.read()
#         print(data)
        data = json.loads(data)
        if not data:
            return
        strong_ammotion = choose_ammotion(data[0]['scores'])
        print(strong_ammotion)
        conn.close()
        return strong_ammotion
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))


from flask import Flask
app = Flask('ammotion_detector')

def parse_request(data):
    data = json.loads(request.data)
    image_content = data['image']
    image_content = image_content[len('data:image/png;base64,'):].decode('base64')
    return image_content


from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


from flask import request
@crossdomain(origin='*')
@app.route("/get_ammotions",methods=['POST'])
def get_ammotion_by_image():
    image = parse_request(request.data)
    return get_ammotion(image)

@crossdomain(origin='*')
@app.route("/status",methods=['GET'])
def get_stats():  
    return "OK!!"

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
