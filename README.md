# pyFreeOTPPlus

Python script to dump TOTP RFC 6238 2fa/otp pin from [Android FreeOTPPlus (FreeOTP+)](https://github.com/helloworld1/FreeOTPPlus) export file freeotp-backup.json

Should work with almost any version of Python from 2.6 onwards.
Only tested with:

  * Python 3.7.3
  * Python 2.7.10


## Requirements/installation

Python 2.6 or 3.x

Relies on https://github.com/pyauth/pyotp but will use https://hg.sr.ht/~clach04/gtotp/ if pyotp is missing.

    pip install pyotp

Optionally install QR code generator for console output:

  * segno (preffered)
  * pyqrcodeng

I.e. `pip install pyotp segno`

## Usage

    python freeotp.py freeotp-backup.json

Dumps pins for all.
Also dumps a URL for qrcode scanning - NOTE browser history will expose seed - do not use!
(its there for testing purposes of test values).

## Also see

  * https://github.com/helloworld1/FreeOTPPlus
  * https://authenticator.cc/docs/en/otp-backup
  * https://github.com/slandx/tfat
  * https://github.com/pepa65/twofat
