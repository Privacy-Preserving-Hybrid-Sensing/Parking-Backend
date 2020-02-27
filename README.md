# Introduction

![Smart Parking Platform](https://gitlab.anu.edu.au/u1063268/smart-parking-backend/raw/master/docs/platform.png "Smart Parking Platform")

SmartParking is an incentivize CrowdSourced information sharing platform for Parking Spot availability. SmartParking Backend provides web access, data API and repository for Mobile and Web Based app. For Android based App, please visit [Smart Parking App](https://gitlab.anu.edu.au/u1063268/smart-parking-app) project.


This docs describe  SmartParking Backend modules:

- [Smart Parking API](#api)
- [Smart Parking Web Application](#web-application)
- [Smart Parking Background](#background)

## API
This docs describe how to use the SmartParking API. We hope you enjoy these docs, and please don't hesitate to [file an issue](https://gitlab.anu.edu.au/u1063268/smart-parking-backend/issues/new) if you see anything missing.

### Subscriber UUID

All POST method API requests require the use of a subscriber_uuid. It's not a username/password thing, just an anonymous identification that represent yourself in this system. Another method of privacy presenving mechanism is in another research.

To identify an API request, you should provide your Subscriber UUID key in the `Subscriber-UUID` header element. 
Example HTTP Header:

```
GET /api/zones/info/all HTTP/1.1
Accept-Encoding: gzip,deflate
Content-Type: application/json;charset=UTF-8
Subscriber-UUID: 8f1ed884-54a5-11ea-a38b-2e728ce88125
Connection: Keep-Alive
User-Agent: Apache-HttpClient/4.1.1 (java 1.5)
```

### Responses

Every API endpoints return the same JSON representation:

```javascript
{
  "status": string,
  "trx_id": string,
  "path": string,
  "msg": string,
  "data": array / object
}
```

The `status` attribute contains `OK` or `ERR` depends of the success status.
The `trx_id` attribute contains caller's generated ID as identifier for associating with the correct callback handler.
The `path` attribute describes what was the URL called. Usually usefull for asynchronous & non-blocking handling in Frontend.
The `msg` attribute contains human friendly message from the server.
The `data` attribute contains multi dimentional array associated with the request. This will be an escaped string containing JSON data.

### Status Codes

Smart Parking Backend response always return HTTP 200 to prevent browser from closing HTTP 1.1 established protocol.
For other HTTP code response, means as is.

### API Lists

| No | URL | Description |
|:---|:---|:---|
| 1 | [GET /api/zones/all](#get-apizonesall)| Getting all Parking zone and it's status, number of parking spots, geopoints, etc |
| 2 | [GET /api/zones/*id*](#get-apizonesintid) | Getting specific Parking zone and it's status, number of parking spots, geopoints, etc|
| 3 | [GET /api/zones/search/*keyword*](#get-apizonessearchstringkeyword) | Search Parking zone by keyword for it's status, number of parking spots, geopoints, etc|
| 4 | [GET /api/zones/*zone_id*/spots/all](#get-apizonesintzone_idspotsall)| Getting all parking spots based on Parking Zone ID. |
| 5 | [GET /api/zones/*zone_id*/spots/*spot_id*](#get-apizonesintzone_idspotsintspot_id)| Getting specific parking spots based on Parking Zone ID. |
| 6 | [GET /api/zones/*zone_id*/subscribe](#get-apizonesintzone_idsubscribe)| Subscribe specific parking zone. |
| 7 | [GET /api/profile/creditbalance](#get-apiprofilecreditbalance) | Get credit participation balance |
| 8 | [GET /api/profile/participation/latest](#get-apiprofileparticipationlatest) | Get latest participation history (in evaluation treshold, eg: 5 min) |
| 9 | [GET /api/profile/participation/*last_num_participation*](#get-apiprofileparticipationintlast_num_participation) | Get participation history |
| 10 | [GET /api/participate/*zone_id*/*spot_id*/*status*](#post-apiparticipateintzone_idintspot_idstringstatus) | Participate crowd source parking spot information |
| 11 | [GET /api/profile/register/*email*](#post-apiprofileregisterstringemail) | Bind email to user's subscriber UUID |

#### `GET /api/zones/all`
response:
```javascript
[{  
  "id": int,
  "subscribed": boolean,
  "subscription_token": string,
  "name": string,
  "description": string,
  "center_longitude": string,
  "center_latitude": string,
  "credit_required": int,
  "spot_total": int,
  "spot_available": int,
  "spot_unavailable": int,
  "spot_undefined": int,
  "ts_update": datetime,
  "geopoints": [{ 
      "id": int,
      "longitude": string,
      "latitude": string
  }]
}]
```

#### `GET /api/zones/<int:id>`
Response:
```javascript
{  
  "id": int,
  "subscribed": boolean,
  "subscription_token": string,
  "name": string,
  "description": string,
  "center_longitude": string,
  "center_latitude": string,
  "credit_required": int,
  "spot_total": int,
  "spot_available": int,
  "spot_unavailable": int,
  "spot_undefined": int,
  "ts_update": datetime,
  "geopoints": [{ 
      "id": int,
      "longitude": string,
      "latitude": string
  }]
}
```

#### `GET /api/zones/search/<string:keyword>`
Response:
```javascript
[{  
  "id": int,
  "subscribed": boolean,
  "subscription_token": string,
  "name": string,
  "description": string,
  "center_longitude": string,
  "center_latitude": string,
  "credit_required": int,
  "spot_total": int,
  "spot_available": int,
  "spot_unavailable": int,
  "spot_undefined": int,
  "ts_update": datetime,
  "geopoints": [{ 
      "id": int,
      "longitude": string,
      "latitude": string
  }]
}]
```

#### `GET /api/zones/<int:zone_id>/spots/all`
Response:
```javascript
[{ 
  "id": int, 
  "name": string, 
  "ts_register": datetime,
  "ts_update": datetime,
  "registrar_uuid": string,
  "longitude": string,
  "latitude": string,
  "vote_available": 0.0,
  "vote_unavailable": 0.0,
  "confidence_level": 0.0,
  "parking_status": 0,
  "zone_id": 1
}]
```

#### `GET /api/zones/<int:zone_id>/spots/<int:spot_id>`
Response:
```javascript
{ 
  "id": int, 
  "name": string, 
  "ts_register": datetime,
  "ts_update": datetime,
  "registrar_uuid": string,
  "longitude": string,
  "latitude": string,
  "vote_available": 0.0,
  "vote_unavailable": 0.0,
  "confidence_level": 0.0,
  "parking_status": 0,
  "zone_id": 1
}
```

#### `GET /api/zones/<int:zone_id>/subscribe`
Response:
```javascript
{
  "id": int,
  "ts": datetime,
  "subscriber_uuid": string,
  "subscription_token": string,
  "zone_id": int,
  "credit_charged": int
}
```

#### `GET /api/profile/creditbalance`
Response:
```javascript
{
  "incentive": int,
  "charged": int,
  "balance": int
}
```

#### `GET /api/profile/participations/latest`
Response:
```javascript
[{
  "id": int,
  "ts_update": int,
  "zone_id": int,
  "zone_name": string,
  "spot_id": int,
  "spot_name": string,
  "participation_value": int,
  "incentive_processed": boolean,
  "incentive_value": int
}]


#### `GET /api/profile/participations/<int:last_num_participation>`
Response:
```javascript
[{
  "id": int,
  "ts_update": int,
  "zone_id": int,
  "zone_name": string,
  "spot_id": int,
  "spot_name": string,
  "participation_value": int,
  "incentive_processed": boolean,
  "incentive_value": int
}]
```

#### `GET /api/participate/<int:zone_id>/<int:spot_id>/<string:status>`
Response:
```javascript
{
  "id": int,
  "ts_update": int,
  "zone_id": int,
  "zone_name": string,
  "spot_id": int,
  "spot_name": string,
  "participation_value": int,
  "incentive_processed": boolean,
  "incentive_value": int
}
```

#### `GET /api/profile/register/<string:email>`
Response:
```javascript
{
  "id": int,
  "ts": datetime,
  "subscriber_uuid": string,
  "email": string,
  "validation_url": string,
  "validated": boolean
}
```



## Web Application

TODO:

## Background

TODO: