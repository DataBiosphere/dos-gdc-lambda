from chalice import Chalice, Response
import yaml

app = Chalice(app_name='dos-gdc-lambda')

import requests
import logging

GDC_URL = 'https://api.gdc.cancer.gov'
SWAGGER_URL = "https://ga4gh.github.io/data-object-service-schemas/swagger/data_object_service.swagger.yaml"  # NOQA


app = Chalice(app_name='dos-gdc-lambda', debug=True)
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
        "size": str(gdc['file_size']),
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
    req = requests.get(SWAGGER_URL)
    swagger_dict = yaml.load(req.content)
    swagger_dict['basePath'] = '/api/ga4gh/dos/v1'
    return swagger_dict

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
        mres['data_objects'].append(gdc_to_ga4gh(hit))
    if gdcr['pagination']['count'] + gdcr['pagination']['from'] < gdcr['pagination']['total']:
        mres['next_page_token'] = str(
            gdcr['pagination']['from'] + gdcr['pagination']['size'])
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
