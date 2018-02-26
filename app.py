from chalice import Chalice, Response

app = Chalice(app_name='dos-gdc-lambda')

import requests
import logging

GDC_URL = 'https://api.gdc.cancer.gov'


app = Chalice(app_name='dos-lambda', debug=True)
app.log.setLevel(logging.DEBUG)

def gdc_to_ga4gh(gdc):
    """
    Accepts a signpost/gdc entry and returns a GA4GH
    :param gdc: A dictionary representing a GDC index response
    :return: ga4gh formatted dictionary
    """
    data_object = {
        "id": gdc['file_id'],
        "name": gdc['file_name'],
        "size": gdc['file_size'],
        "version": gdc['updated_datetime'],
        "urls": [
            {'url': "{}/data/{}".format(GDC_URL, gdc.get('file_id')),
             'system_metadata': gdc}
        ],
        "checksums": [{'checksum': gdc['md5sum'], 'type': 'md5'}],
    }
    return data_object
#
#
@app.route('/swagger.json', cors=True)
def swagger():
    req = requests.get("https://gist.githubusercontent.com/david4096/6dad2ea6a4ebcff8e0fe24c2210ae8ef/raw/55bf72546923c7bd9f63f3ea72d7441b0a506a76/data_object_service.gdc.swagger.json")
    swagger_dict = req.json()
    swagger_dict['basePath'] = '/api'
    return swagger_dict
#
# @app.route('/ga4gh/dos/v1/dataobjects/list', methods=['POST'], cors=True)
# def list_data_objects():
#     user_as_json = app.current_request.json_body
#     req = requests.get("https://signpost.opensciencedatacloud.org/index/", cors=True)
#     return req.json()

def dos_list_request_to_gdc(dos_list):
    """
    Takes a dos ListDataObjects request and converts it into a signpost request.
    :param gdc:
    :return:
    """
    mreq = {}
    mreq['size'] = dos_list.get('page_size', None)
    mreq['from'] = dos_list.get('page_token', None)
    return mreq

def gdc_to_dos_list_response(gdcr):
    """
    Takes a GDC list response and converts it to GA4GH.
    :param gdc:
    :return:
    """
    mres = {}
    mres['data_objects'] = []
    for hit in gdcr.get('hits', []):
        # Get the rest of the info for them...
        #req = requests.get(
        #    "https://signpost.opensciencedatacloud.org/index/{}".format(id_))
        #mres['data_objects'].append(gdc_to_ga4gh(req.json()))
        mres['data_objects'].append(gdc_to_ga4gh(hit))
    if len(gdcr.get('hits', [])) > 0:
        mres['next_page_token'] = str(gdcr['pagination']['from'] + gdcr['pagination']['size'])
    return mres


@app.route('/ga4gh/dos/v1/dataobjects/{data_object_id}', methods=['GET'], cors=True)
def get_data_object(data_object_id):
    req = requests.get(
        "{}/files/{}".format(GDC_URL, data_object_id))
    return {'data_object': gdc_to_ga4gh(req.json()['data'])}

@app.route('/ga4gh/dos/v1/dataobjects/list', methods=['POST'], cors=True)
def list_data_objects():
    req_body = app.current_request.json_body
    if req_body and (req_body.get('page_size', None) or req_body.get('page_token', None)):
        gdc_req = dos_list_request_to_gdc(req_body)
    else:
        gdc_req = {}
    signpost_req = requests.get("{}/files/".format(GDC_URL), params=gdc_req)
    list_response = signpost_req.json()['data']
    # return list_response
    return gdc_to_dos_list_response(list_response)
#
# See the README documentation for more examples.

#
#
@app.route('/ga4gh/dos/v1/dataobjects/{data_object_id}/versions', methods=['GET'], cors=True)
def get_data_object_versions(data_object_id):
    req = requests.get(
        "{}/index/{}".format(GDC_URL, data_object_id))
    return req.json()
#
#
@app.route('/')
def index():
    message = "<h1>Welcome to the DOS lambda, send requests to /ga4gh/dos/v1/</h1>"
    return Response(body=message,
                    status_code=200,
                    headers={'Content-Type': 'text/html'})
