#!/usr/bin/python3
from html.parser import HTMLParser
import argparse
import requests
import netrc
import json
import os


class TelenorSMS:
    def __init__(self, sender, password):
        session = requests.Session()

        init_url = "https://minemeldinger.no/auth/sso"
        login_url = "https://idp.telenor.no/sso/login_connect_id"
        saml_url = "https://apigw.telenor.no/oauth/v2/storeSaml"
        auth_url = "https://minemeldinger.no/auth/code"

        result = session.get(init_url)
        login_data = {"phoneNumber": sender}
        result = session.post(login_url, data=login_data)

        password_url = "https://connect.telenordigital.com/id/phone-enter-password"
        password_data = {
            "enterPassword": password,
            "screenId": "phone-enter-password",
            "action": "next",
        }

        result = session.post(password_url, data=password_data)

        saml_response = self.get_input_tag(result.text, "samlResponse")
        connect_id = self.get_input_tag(result.text, "connect_id")

        telenor_id = session.cookies.get_dict()["telenor_id"]
        saml_data = {
            "samlResponse": saml_response,
            "telenor_id": telenor_id,
            "connect_id": connect_id,
        }

        result = session.post(saml_url, data=saml_data)
        result = session.get(auth_url)
        token = session.cookies.get_dict()["ttc"]
        session.headers["Authorization"] = "Bearer " + token
        self.sms_url = (
            f"https://apigw.telenor.no/mobile-messaging/v2/tel:47{sender}/sms"
        )
        self.session = session

    def get_input_tag(self, html, name):
        class AttrParser(HTMLParser):
            def handle_starttag(self, tag, attrs):
                if tag == "input":
                    attr_dict = dict((attr, value) for attr, value in attrs)
                    if attr_dict["name"] == name:
                        self.result = attr_dict["value"]

        attrparse = AttrParser()
        attrparse.feed(html)
        return attrparse.result

    def send_message(self, recipient, message):
        sms_data = {"message": message, "recipients": recipient}
        response = self.session.post(self.sms_url, sms_data)
        result = response.json()
        try:
            if response.json()["result"] == "OK":
                print("OK")
        except json.JSONDecodeError:
            print("Failed")
            exit(1)
        except KeyError:
            print("Failed")
            print(response.json())
            exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sender")
    parser.add_argument("--password")
    parser.add_argument("recipient")
    parser.add_argument("message")
    args = parser.parse_args()

    if args.sender and args.password:
        sender = args.sender
        passord = args.password
    else:
        try:
            rc = netrc.netrc(os.path.expanduser("~/.netrc"))
            sender, account, password = rc.hosts["telenorsms"]
            error = False
        except FileNotFoundError:
            error = ".netrc file not found."
        except KeyError:
            error = "no entry for TelenorSMS (telenorsms) found in .netrc."
        if error:
            print(f"Sender and password not provided, and {error} Aborting.")
            exit(1)

    sms = TelenorSMS(sender, password)
    sms.send_message(args.recipient, args.message)
