#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
"""Process freeotp-backup.json export file from FreeOTP Plus aka FreeOTP+
from https://github.com/helloworld1/FreeOTPPlus
"""

import base64
import json  # Python 2.6+
import sys
import time
import urllib
try:
    import urllib.parse
except ImportError:
    pass  # assume py2

try:
    import pyotp  # from https://github.com/pyauth/pyotp
except ImportError:
    import gauth  # from https://bitbucket.org/clach04/gtotp
    pyotp = None


b32encode = base64.b32encode

try:
    urlencode = urllib.urlencode  # py2
except AttributeError:
    urlencode = urllib.parse.urlencode  # py3


def doit(filename):
    print(filename)
    f = open(filename, 'rb')
    json_data_str = f.read()
    f.close()
    otp = json.loads(json_data_str)


    t = time.time()
    result = []
    time_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)) + time.strftime(" (%Y-%m-%d %H:%M:%S)", time.localtime(t))
    print(time_str)

    for x in otp['tokens']:
        print('')
        #print(x)
        assert x['algo'] == u'SHA1'
        assert x['type'] == 'TOTP'
        
        signed_int_array = x['secret']  # storage of secret is `signed char`, Python built-in byte array need this to be unsigned
        unsigned_int_array = [i & 0xff for i in signed_int_array]  # TODO add support for Python pre-generator support
        bin_secret = bytearray(unsigned_int_array)
        print('Binary secret length=%d' % len(bin_secret))
        secret_base32 = b32encode(bin_secret)
        secret_base32 = secret_base32.replace(b'=', b'')  # remove padding
        secret_base32 = secret_base32.decode('latin1')  # pyotp requires strings
        print('base32 secret length=%d' % len(secret_base32))
        if pyotp:
            g = pyotp.TOTP(secret_base32, digits=x['digits'], interval=x['period'])
            print('%s %s' % (x['label'], g.now()))
        else:
            #g = gauth.GoogleAuthenticator(secret=secret_base32, num_digits=x['digits'])
            g = gauth.GoogleAuthenticator(bin_secret=bin_secret, num_digits=x['digits'])
            print('%s %s' % (x['label'], g))  # TODO this assumes 30 second period window

        # Generate (at least one) URL for a qrcode
        # TODO if pyotp use its builtin support?

        # NOTE google chart has potential to leak URL into browser history
        # TODO standalone js version, see https://github.com/evgeni/qifi for demo (and https://github.com/neocotic/qrious)
        google_qrcode_url = 'https://chart.apis.google.com/chart?'

        # order is important, do not use a dict!
        # QR code will not import into FreeOTP nor FreeOTP+
        # unless the exact order below is used as some of this generates a otpauth URI
        # see https://github.com/Authenticator-Extension/Authenticator/wiki/Standard-OTP-Backup-Format-Devloper-Info
        google_qrcode_url_params = [
                ('cht', 'qr'),
                ('chs', '300x300'),
                ('chl', 'otpauth://totp/' + x['issuerExt']),
                ('secret', secret_base32)
            ]
        google_qrcode_url = google_qrcode_url + urlencode(google_qrcode_url_params)
        google_qrcode_url = google_qrcode_url.replace('&secret=', '%3Fsecret=')  # this is needed is the otpauth URI needs to be escape in the chart URL
        print(google_qrcode_url)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    print('Python %s on %s' % (sys.version, sys.platform))

    json_filename = argv[1]
    doit(json_filename)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())