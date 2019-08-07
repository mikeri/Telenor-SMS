# Telenor-SMS
Command line tool and Python class for Telenor's "Mine Meldinger" service. Does not use any official API so should not be considered stable and can stop working at any time.

## Usage
From command line:
```
./telenorsms.py --sender <sender_phone_number> --password <password> <recipients number> <message>
```
In Python:
```python
from telenorsms import TelenorSMS

sms = TelenorSMS(sender, password)
sms.send_message(recipient, message)
```

Enter the senders number without country prefix.

### .netrc
For command line usage you can store your credentials in your .netrc as "telenorsms".
