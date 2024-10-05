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

try:
    #raise ImportError  # debug as seeing issues - appears to be a python 3 specific issue for both segno and pyqrcodeng
    import segno  # preferred - https://github.com/heuer/segno
except ImportError:
    segno = None

try:
    import pyqrcodeng  # https://github.com/pyqrcode/pyqrcodeNG
except ImportError:
    pyqrcodeng = None


b32encode = base64.b32encode

try:
    urlencode = urllib.urlencode  # py2
except AttributeError:
    urlencode = urllib.parse.urlencode  # py3


def doit(filename, verbose=True, display_registration_details=True):
    print(filename)
    f = open(filename, 'rb')
    json_data_str = f.read()
    f.close()
    otp = json.loads(json_data_str)


    t = time.time()
    result = []
    time_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)) + time.strftime(" (%Y-%m-%d %H:%M:%S)", time.localtime(t))  # ISO 8601 datetime format, Zulu/GMT/UTC based
    print(time_str)

    for x in otp['tokens']:
        print('')
        if verbose:
            print(x)
        print('issuer', x['issuerExt'])
        print('label', x['label'])
        assert x['algo'] == u'SHA1'
        assert x['type'] == 'TOTP'

        try:
            signed_int_array = x['secret']  # storage of secret is `signed char`, Python built-in byte array need this to be unsigned
            unsigned_int_array = [i & 0xff for i in signed_int_array]  # TODO add support for Python pre-generator support
            bin_secret = bytearray(unsigned_int_array)
        except KeyError:
            # standard value missing, now check for (non-standard) extension to format,
            # check for "secret_base32" instead, this allows for manual updates of json file to be easier/possible
            try:
                bin_secret = base64.b32decode(x['secret_base32'])
            except KeyError:
                raise ValueError('Missing secret in (json) config, both standard "secret" and extension "secret_base32"')
        if verbose:
            print('Binary secret length=%d' % len(bin_secret))
        secret_base32 = b32encode(bin_secret)
        secret_base32 = secret_base32.replace(b'=', b'')  # remove padding
        secret_base32 = secret_base32.decode('latin1')  # pyotp requires strings
        if verbose:
            print('base32 secret length=%d' % len(secret_base32))
            print('base32 secret %s' % secret_base32)
        if pyotp:
            g = pyotp.TOTP(secret_base32, digits=x['digits'], interval=x['period'])
            print('Current 2FA/OTP PIN for %s %s' % (x['label'], g.now()))
        else:
            #g = gauth.GoogleAuthenticator(secret=secret_base32, num_digits=x['digits'])
            g = gauth.GoogleAuthenticator(bin_secret=bin_secret, num_digits=x['digits'])
            print('Current 2FA/OTP PIN for %s %s' % (x['label'], g))  # TODO this assumes 30 second period window

        if display_registration_details:
            # Generate (at least one) URL for a qrcode
            # TODO if pyotp use its builtin support?

            # NOTE google chart has potential to leak URL into browser history as well as possible Google history
            # TODO 1 - standalone js version, see https://github.com/evgeni/qifi for demo (and https://github.com/neocotic/qrious)
            # TODO 2 - console block qr code
            google_qrcode_url = 'https://chart.apis.google.com/chart?'

            ######## hack!
            #secret_base32 = 'MZXW633PN5XW6==='
            #secret_base32 = 'MZXW633PN5XW6'
            #x['issuerExt'] = 'Demo value from GitHub google/google-authenticator/issues/70'  # slashes in name appear to be allowed
            #x['issuerExt'] = 'Demo value from GitHub issues 70'  # Shorter name
            ######## hack!

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
            print('WARNING Google URL not secure!')
            print(google_qrcode_url)

        # generate OTPAUTH_URI otpauth://totp/.. URL -format mentioned in https://github.com/helloworld1/FreeOTPPlus/issues/30
        """
        From https://authenticator.cc/docs/en/otp-backup-developer

        otpauth://totp/example.com?secret=FLIQ7AABIXF2DBUYE7VYAV2T7232KVYB
        otpauth://totp/Test%20Account:?secret=R6TTJ5T26NWTHPIPXAOYQ6BVWEBLE6W2&issuer=Test%20Account
        otpauth://totp/Another%20Test%20Account:example.com?secret=5W6HHVETUEPLR26KRQOPHTR6Q4JYRVJQ&issuer=Another%20Test%20Account
        otpauth://totp/?secret=AFKVXHTAZZQKCHI3XSZPX5NKQRFXL3AD
        otpauth://totp/Account%20with%20Period:example.com?secret=LJL6765YQRQQ533ACSI6YUXTLZYY7GBI&issuer=Account%20with%20Period&period=60

        Tips:

            * Remember that the issuer and account name cannot contain a colon (: or %3A)
            * Save the file as text/plain
        """
        # TODO issuer and account
        """
        tmp_str = urlencode(url_params)
        if not tmp_str.startswith('chl='):
            raise NotImplemented('proper URL escaping')
        tmp_str = tmp_str[len('chl='):]  # FIXME chl not needed
        url = 'otpauth://totp/' + tmp_str
        """

        if display_registration_details:
            url = 'otpauth://totp/' + x['issuerExt'] + '?secret=' + secret_base32  # FIXME escape name? base32 Secret should be fine as-is?
            print(url)

            if segno:
                # NOTE segno could be used for desktop (maybe) web browser launching with locally generated SVG and/or PNG
                qr = segno.make(url)
                qr.terminal()
            elif pyqrcodeng:
                qr = pyqrcodeng.create(url)
                qr.term()  # this "prints" to stdout/tty/console (works for win32)
                # print(qr.terminal())  # this generates ANSI/VT100 escape sequences (not suitable for win32)


def main(argv=None):
    if argv is None:
        argv = sys.argv

    print('Python %s on %s' % (sys.version, sys.platform))

    json_filename = argv[1] # FIXME default filename to 'freeotp-backup.json' if missing
    doit(json_filename)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
