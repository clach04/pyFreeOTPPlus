# pyFreeOTPPlus

Python script to dump 2fa pin from Android FreeOTPPlus (FreeOTP+) export file freeotp-backup.json

Should work with almost any version of Python from 2.6 onwards.
Only tested with:

  * Python 3.7.3
  * Python 2.7.10


## Requirements/installation

Python 2.6 or 3.x

Relies on https://github.com/pyauth/pyotp but will use https://bitbucket.org/clach04/gtotp/ if pyotp is missing.

    pip install pyotp

## Usage

    python freeotp.py freeotp-backup.json

Dumps pins for all.
Also dumps a URL for qrcode scanning - NOTE browser history will expose seed - do not use!
(its there for testing purposes of test values).
