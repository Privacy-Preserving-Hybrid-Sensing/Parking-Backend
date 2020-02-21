# Introduction

![Smart Parking Platform](https://gitlab.anu.edu.au/u1063268/smart-parking-backend/raw/master/docs/platform.png "Smart Parking Platform")

SmartParking is an open information sharing of CrowdSourced platform for incentivize Parking Spot.
SmartParking Backend provides web access, data API and repository for Mobile and Web Based app. For Android based App, please visit [Smart Parking App](https://gitlab.anu.edu.au/u1063268/smart-parking-app) project.


This docs describe  SmartParking Backend modules:

- [Smart Parking API](#api)
- [Smart Parking Web Application](#web-application)
- [Smart Parking Background](#background)

# API
This docs describe how to use the SmartParking API. We hope you enjoy these docs, and please don't hesitate to [file an issue](https://gitlab.anu.edu.au/u1063268/smart-parking-backend/issues/new) if you see anything missing.

## Subscriber UUID

All POST method API requests require the use of a subscriber_uuid. It's not a username/password thing, just an anonymous identification that represent yourself in this system. Another method of privacy presenving mechanism is on other research.

To identify an API request, you should provide your Subscriber UUID key in the `subscriber_uuid` POST element.


```http
GET /zones/info/all

POST /zones/subscribe/2
```

For POST method, use 

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `subscriber_uuid` | `string` | **Required**. Your Subscriber UUID |

## Responses

Every API endpoints return the same JSON representation:

```javascript
{
  'status': string, 
  'trx_id': string,
  'path': string, 
  'msg': string, 
  'data': [], 
}
```

The `status` attribute contains `OK` or `ERR` depends of the success status.
The `trx_id` attribute contains caller's generated ID as identifier for associating with the correct callback handler.
The `path` attribute describes what was the URL called. Usually usefull for asynchronous & non-blocking handling in Frontend.
The `msg` attribute contains human friendly message from the server.
The `data` attribute contains multi dimentional array associated with the request. This will be an escaped string containing JSON data.

## Status Codes

Smart Parking Backend response always return HTTP 200 to prevent browser from closing HTTP 1.1 established protocol.
For other HTTP code response, means as is.


# Web Application

BLA ALBLABLABLA
