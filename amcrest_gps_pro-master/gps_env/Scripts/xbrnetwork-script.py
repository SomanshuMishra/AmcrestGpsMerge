#!d:\odisoft\amcrest_gps_pro-master\gps_env\scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'autobahn==21.11.1','console_scripts','xbrnetwork'
__requires__ = 'autobahn==21.11.1'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('autobahn==21.11.1', 'console_scripts', 'xbrnetwork')()
    )
