#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
"""Process freeotp-backup.json export file from FreeOTP Plus aka FreeOTP+
from https://github.com/helloworld1/FreeOTPPlus
"""

import sys
import time
import urllib

import gauth  # from https://bitbucket.org/clach04/gtotp

from stupid_json import load_json, load_json_file


b32encode = gauth.base64.b32encode


def doit(filename):
    print(filename)
    otp = load_json_file(filename)

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
        secret_base32 = b32encode(bin_secret)
        secret_base32 = secret_base32.replace('=', '')  # remove padding
        g = gauth.GoogleAuthenticator(secret=secret_base32, num_digits=x['digits'])
        #g = gauth.GoogleAuthenticator(bin_secret=bin_secret, num_digits=x['digits'])
        print('%s %s' % (x['label'], g))

        # Generate (at least one) URL for a qrcode

        # NOTE google chart has potential to leak URL into browser history
        # TODO standalone js version, see https://github.com/evgeni/qifi for demo
        google_qrcode_url = 'https://chart.apis.google.com/chart?'

        # order is important, do not use a dict!
        # no idea why but QR code will not import into FreeOTP nor FreeOTP+
        # unless the exact order below is used
        google_qrcode_url_params = [
                ('cht', 'qr'),
                ('chs', '300x300'),
                ('chl', 'otpauth://totp/' + x['issuerExt']),
                ('secret', secret_base32)
            ]
        google_qrcode_url = google_qrcode_url + urllib.urlencode(google_qrcode_url_params)
        google_qrcode_url = google_qrcode_url.replace('&secret=', '%3Fsecret=')  # no idea why this is needed but qrcode doesn't import otherwise
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