from atlassian import Confluence
import json
import requests
from requests.auth import HTTPBasicAuth

from TeamSPBackend.common.choices import RespCode
from django.views.decorators.http import require_http_methods
from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from TeamSPBackend.common.utils import make_json_response, init_http_response, check_user_login, check_body, body_extract, mills_timestamp


@require_http_methods(['GET'])
def get_all_groups(request):
    """Get all groups accessable by the logged in user
    Method: GET
    """
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    try:
        confluence = log_into_confluence(username, password)
        conf_resp = confluence.get_all_groups()
        data = []
        for group in conf_resp:
            data.append({
                'type': group['type'],
                'name': group['name']
            })
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_space(request, space_key):
    """Get a Confluence Space
    Method: GET
    Request: space_key
    """
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    try:
        confluence = log_into_confluence(username, password)
        conf_resp = confluence.get_space(
            space_key, expand='homepage')
        conf_homepage = conf_resp['homepage']
        data = {
            'id': conf_resp['id'],
            'key': conf_resp['key'],
            'name': conf_resp['name'],
            'homepage': {
                'id': conf_homepage['id'],
                'type': conf_homepage['type'],
                'title': conf_homepage['title'],

            }
        }
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_pages_of_space(request, space_key):
    """Get all the pages under the Confluence Space
    Method: GET
    Request: space
    """
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    try:
        confluence = log_into_confluence(username, password)
        conf_resp = confluence.get_all_pages_from_space(space_key)
        data = []
        for page in conf_resp:
            data.append({
                'id': page['id'],
                'type': page['type'],
                'title': page['title']
            })
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

    # Get Page Content by ID (HTML) (lower prio for now)


@require_http_methods(['GET'])
def search_team(request, keyword):
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    try:
        confluence = log_into_confluence(username, password)
        conf_resp = confluence.get_all_groups()
        data = []
        result = []
        for group in conf_resp:
            data.append({
                'type': group['type'],
                'name': group['name']
            })
        for element in data:
            if keyword.lower() in element['name'].lower():
                result.append({
                    'name': element['name']
                })
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = result
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_group_members(request, group):
    """Get all the members under 'group_name' of the Confluence Space
    Method: GET
    Request: group_name
    """
    try:
        user = request.session.get('user')
        username = user['atl_username']
        password = user['atl_password']
        group_name = group
        confluence = log_into_confluence(username, password)
        conf_resp = confluence.get_group_members(group_name)
        data = []
        for user in conf_resp:
            data.append({
                # 'type': user['type'],
                # 'userKey': user['userKey'],
                # 'profilePicture': user['profilePicture'],
                'name': user['displayName'],
                'email': user['username'] + "@student.unimelb.edu.au"
            })
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_user_details(request, member):
    """Get a specific Confluence Space member's details
    Method: POST
    Request: member's username
    """
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    try:
        confluence = log_into_confluence(username, password)
        conf_resp = confluence.get_user_details_by_username(member)
        data = {
            'type': conf_resp['type'],
            'username': conf_resp['username'],
            'userKey': conf_resp['userKey'],
            'profilePicture': conf_resp['profilePicture'],
            'displayName': conf_resp['displayName']
        }
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_subject_supervisors(request, subjectcode, year):

    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    try:
        confluence = log_into_confluence(username, password)
        conf_resp = confluence.get_all_groups()
        supervisors = []
        data = []
        for group in conf_resp:
            if "staff" in group['name'] and year in group['name'] and subjectcode in group['name']:
                supervisors = confluence.get_group_members(group['name'])

        for each in supervisors:
            data.append({
                # 'type': user['type'],
                # 'userKey': user['userKey'],
                # 'profilePicture': user['profilePicture'],
                'name': each['displayName'],
                'email': each['username']
            })
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_page_contributors(request, *args, **kwargs):
    """Get a Confluence page's contributors
    Method: Get
    Request: page_id
    """
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    try:
        confluence = log_into_confluence(username, password)
        page_id = kwargs['page_id']
        # Todo: change these to configurable inputs
        domain = "https://confluence.cis.unimelb.edu.au"
        port = "8443"
        url = f"{domain}:{port}/rest/api/content/{page_id}/history"
        parameters = {"expand": "contributors.publishers.users"}
        conf_resp = requests.get(
            url, params=parameters, auth=HTTPBasicAuth(username, password)).json()
        data = {
            "createdBy": conf_resp["createdBy"],
            "createdDate": conf_resp["createdDate"],
            "contributors": conf_resp["contributors"]
        }
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


def log_into_confluence(username, password):
    confluence = Confluence(
        url='https://confluence.cis.unimelb.edu.au:8443/',
        username=username,
        password=password,
        verify_ssl=False
    )
    return confluence


def get_members(request, group):
    try:
        user = request.session.get('user')
        username = user['atl_username']
        password = user['atl_password']
        confluence = log_into_confluence(username, password)
        conf_resp = confluence.get_group_members(group)
        data = []
        for user in conf_resp:
            data.append({
                # 'type': user['type'],
                # 'userKey': user['userKey'],
                # 'profilePicture': user['profilePicture'],
                'name': user['displayName'],
                'email': user['username'] + "@student.unimelb.edu.au"
            })
        return data
    except Exception as e:
        print(e)
        return None


@require_http_methods(['GET'])
def get_spaces_by_key(request, key_word):
    """Get a list of Confluence space keys that contains the key word
    Method: GET
    Request: key_word
    """
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    try:
        confluence = log_into_confluence(username, password)
        spaces = confluence.get_all_spaces()
        space_keys = [space['key'] for space in spaces if key_word.lower() in space['key'].lower()]
        while len(spaces) > 0:
            spaces = confluence.get_all_spaces(start=len(spaces))
            space_keys.extend([space['key'] for space in spaces if key_word.lower() in space['key'].lower()])

        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = space_keys
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_page_count_by_time(request, space_key):
    """Get a list of time, page count pairs
    Method: GET
    Request: space_key
    """
    username = "pinwang"
    password = "W11p30#5776"
    from datetime import datetime
    import time
    try:
        conf = log_into_confluence(username, password)
        contents = conf.get_space_content(space_key=space_key, content_type="page", expand="history")
        results = contents["results"]
        while contents["size"] == contents["limit"]:
            contents = conf.get_space_content(space_key=space_key, start=len(results), content_type="page", expand="history")
            results.extend(contents["results"])

        delta_page_count = {}
        days = []
        for result in results:
            # "2021-02-26T10:34:27.631+11:00"
            time_str = result["history"]["createdDate"]
            time_str = time_str[:11]+"00:00:00.001"+time_str[-6:]
            page_create_time = int(time.mktime(datetime.fromisoformat(time_str).timetuple()))
            if page_create_time in delta_page_count:
                delta_page_count[page_create_time] += 1
            else:
                delta_page_count[page_create_time] = 1
                days.append(page_create_time)

        days.sort()
        page_count = 0
        data = []
        cur_time = int(time.mktime(datetime.now().timetuple()))
        for day in range(days[0], cur_time, 60*60*24):
            if day in delta_page_count:
                page_count += delta_page_count[day]
            data.append({
                "time": day,
                "page_count": page_count
            })

        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")
