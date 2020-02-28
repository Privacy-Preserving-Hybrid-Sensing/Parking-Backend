from django.core.exceptions import PermissionDenied
from django.http import JsonResponse

# from .views import json_response_err

def required_field(function):
    def wrap(request, *args, **kwargs):
      print(request.headers)
      if 'Subscriber-Uuid' not in request.headers:
        msg = 'required Subscriber-Uuid header field'
        dictionary = {'status': 'ERR', 'path': request.path, 'msg': msg, 'data': [], 'trx_id': ''}
        return json_response(request, dictionary)

      if 'Trx-Id' not in request.headers:
        msg = 'required Trx-ID header field'
        dictionary = {'status': 'ERR', 'path': request.path, 'msg': msg, 'data': [], 'trx_id': ''}
        return json_response(request, dictionary)

      # required_field_trx_id = 'trx_id'
      # if required_field_subscriber_uuid not in request.POST:
      #   return json_response_err(request, 'Post Field: ' + required_field_subscriber_uuid + ' required', '')
      trx_id = request.headers['Trx-Id']
      response = function(request, *args, **kwargs)
      response['trx_id'] = trx_id
      ret = json_response(request, response)
      return ret

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def json_response(request, dictionary):
    print(dictionary)
    return JsonResponse(dictionary, safe=True)

# def json_response_err(request, msg, trx_id):
#     return  {'status': 'ERR', 'trx_id': trx_id, 'path': request.path, 'msg': msg, 'data': []}
