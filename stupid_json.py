"""json support
TODO consider:
  * http://pypi.python.org/pypi/omnijson
  * http://opensource.xhaus.com/projects/show/jyson
"""

import os

try:
    # Python 2.6+
    import json
except ImportError:
    try:
        # from http://code.google.com/p/simplejson
        import simplejson as json
    except ImportError:
        json = None

if json is None:
    warnings.warn('Using naive json handlers')
    import pprint
    
    def dump_json(x, indent=None):
        """dumb not safe!
        Works for the purposes of this specific script as quotes never
        appear in data set.
        
        Parameter indent ignored"""
        return pprint.pformat(x).replace("'", '"')
    
    def load_json(x):
        """dumb not safe! Works for the purposes of this specific script"""
        x = x.replace('\r', '')
        try:
            # Dumb literals for json/javascript/ecmascript emulation
            true = True
            null = None
            false = False
            result = eval(x)
        except Exception:
            logging.error('parsing json string data: %r', x)
            print('')
            print('** ERROR parsing json string data')
            print('')
            raise
        return result
else:
    dump_json = json.dumps
    load_json = json.loads


def load_json_file(json_filename,fail_if_missing=True):
    # Perform own file IO....
    if os.path.exists(json_filename):
        f = open(json_filename, 'rb')
        json_data_str = f.read()
        f.close()
        json_data = load_json(json_data_str)
    else:
        if fail_if_missing:
            raise Exception('Missing json file %s' % json_filename)
        json_data = {}
    return json_data
