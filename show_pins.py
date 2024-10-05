#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
"""Process freeotp-backup.json export file from FreeOTP Plus aka FreeOTP+
from https://github.com/helloworld1/FreeOTPPlus
"""

import freeotp

filename = 'freeotp-backup.json'
freeotp.doit(filename, verbose=False, display_registration_details=False)
