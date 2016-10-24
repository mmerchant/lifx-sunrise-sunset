# coding: utf-8
from base64 import b64decode
import simplejson as json

import arrow
import boto3
import requests

from FlowrouteMessagingLib.Models.Message import Message
from FlowrouteMessagingLib.Controllers.APIController import APIController

kms = boto3.client('kms')

KMS_ENCRYPTED_KEYS = ("")

LIFX_TOKEN = json.loads(
    kms.decrypt(
        CiphertextBlob=b64decode(
            KMS_ENCRYPTED_KEYS))['Plaintext'])["LIFX_TOKEN"]
FLOWROUTE_ACCESS_KEY = json.loads(
    kms.decrypt(
        CiphertextBlob=b64decode(
            KMS_ENCRYPTED_KEYS))['Plaintext'])["FLOWROUTE_ACCESS_KEY"]
FLOWROUTE_SECRET_KEY = json.loads(
    kms.decrypt(
        CiphertextBlob=b64decode(
            KMS_ENCRYPTED_KEYS))['Plaintext'])["FLOWROUTE_SECRET_KEY"]

LOCATION = {
    "SEATTLE": ["47.6177135", "-122.2993792"]
}
DESTINATION_NUMBER = ""
FLOWROUTE_DID = ""


def _list_lights():
    LIFX_ENDPOINT = "https://api.lifx.com/v1/lights/all"
    lights = {}
    header = {
        "Authorization": "Bearer {}".format(LIFX_TOKEN)
    }
    res = requests.get(LIFX_ENDPOINT, headers=header)
    if res.status_code in (200, 202):
        for bulb in res.json():
            bulb_id = bulb["id"]
            status = bulb["power"]
            lights[bulb_id] = status
        return lights
    else:
        return None


def _calculate_sunrise_sunset():
    lon = LOCATION["SEATTLE"][1]
    lat = LOCATION["SEATTLE"][0]
    SUNRISE_SUNSET_ENDPOINT = ("http://api.sunrise-sunset.org"
                               "/json?lat={}&lng={}"
                               "&today&formatted=0").format(lat, lon)
    res = requests.get(SUNRISE_SUNSET_ENDPOINT)
    if res.status_code in (200, 202):
        sunrise = arrow.get(res.json()["results"]["sunrise"])
        sunset = arrow.get(res.json()["results"]["sunset"])
    return sunrise, sunset

"""
We are calling these two here to limit the number of API calls
to both Lifx and sunrise-sunset. Lambda doesn't invoke globals
on each call. Only what is in the Lambda handler.
"""
LIGHTS = _list_lights()
SUNRISE, SUNSET = _calculate_sunrise_sunset()


def _notify_sms(bulb, status):
    controller = APIController(
        username=FLOWROUTE_ACCESS_KEY,
        password=FLOWROUTE_SECRET_KEY
    )
    txt = "Oops! Took care of {} light. It is now {}".format(
            bulb, status)
    msg = Message(
        to=DESTINATION_NUMBER,
        from_=FLOWROUTE_DID,
        content=txt
    )
    controller.create_message(msg)
    print(txt)


def _toggle_lights(lights, mode):
    header = {
        "Authorization": "Bearer {}".format(LIFX_TOKEN)
    }
    for light, status in lights.iteritems():
        LIFX_ENDPOINT = "https://api.lifx.com/v1/lights/{}/state".format(light)
        if mode == "off":
            if status == "on":
                payload = {"power": "off"}
                res = requests.put(
                    LIFX_ENDPOINT, data=payload, headers=header
                )
                bulb = res.json()["results"][0]["label"]
                _notify_sms(bulb, payload["power"])
        elif mode == "on":
            if status == "off":
                payload = {"power": "on"}
                res = requests.put(
                    LIFX_ENDPOINT, data=payload, headers=header
                )
                bulb = res.json()["results"][0]["label"]
                _notify_sms(bulb, payload["power"])


def lambda_handler(event, context):
    current_ts = arrow.get()
    if SUNSET > current_ts < SUNRISE:
        _toggle_lights(LIGHTS, mode="on")
    else:
        _toggle_lights(LIGHTS, mode="off")
