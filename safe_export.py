#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
"""Export a freeotp-backup.json export file for FreeOTP Plus aka FreeOTP+
from https://github.com/helloworld1/FreeOTPPlus

Processes json file that might not be valid for FreeOTPPlus due to use of base64 values or missing/incomplete token order
"""

import sys

import freeotp

try:
    filename = sys.argv[1]
except IndexError:
    filename = 'freeotp-backup.json'
otp = freeotp.load_freeotpplus_json(filename)

# remove binary, non-standard and not supported by json module by default (and FreeOTPPlus isn't expecting it)
for x in otp['tokens']:
    int_secret_list = []
    for single_byte in x['bin_secret']:
        #print(single_byte)
        int_secret_list.append(single_byte)
    #print('')
    x['secret'] = int_secret_list
    del x['bin_secret']

tokenOrder = otp.get('tokenOrder', [])
if len(tokenOrder) != len(otp['tokens']):
    # FreeOTPPlus as of 2026-05-31, version 3.3 (25) will silently skip items not in the tokenOrder
    # Also if tokenOrder is missing, then will fail to import with: Toast that is briefly displayed, "Failed to import JSON. The file is malformed"
    # for now ignore existing order and just use the order in the file, do not attempt to append to order
    new_token_order = []
    for x in otp['tokens']:
        new_token_order.append(x['issuerExt'] + ':' + x['label'])  # if either of these are missing, FreeOTPPlus will silently skip them on import - For now, allow error and do NOT attempt to auto generate
    otp['tokenOrder'] = new_token_order

json_str = freeotp.json.dumps(otp, indent=True)
print('%s' % (json_str,))
