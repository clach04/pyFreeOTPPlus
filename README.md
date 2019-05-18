# pyFreeOTPPlus

Python script to dump 2fa pin from Android FreeOTPPlus (FreeOTP+) export file freeotp-backup.json

Should work with almost any version of Python from 2.6 onwards.
Only tested with:

  * Python 3.7.3
  * Python 2.7.10

Relies on https://bitbucket.org/clach04/gtotp/ - this is and old (unpackaged) module with support for very old versions of Python.

TODO consider using something pip installable, like:

  * https://github.com/pyauth/pyotp

## Usage

    python freeotp.py freeotp-backup.json

Dumps pins for all.
Also dumps a URL for qrcode scanning - NOTE browser history will expose seed - do not use!
(its there for testing purposes of test values).
