#!/bin/bash

python -m venv venv

source venv/bin/activate

/usr/bin/python3 \
    /Applications/Positron.app/Contents/Resources/app/extensions/positron-python/python_files/shell_exec.py /usr/bin/python3 \
    -m pip install \
    -U pandas \
    /private/var/folders/qk/w71qnntx22g9xmst4qjsqh280000gp/T/tmp-71161-qe0R9C4YQBL9-.log

/usr/bin/python3 \
    /Applications/Positron.app/Contents/Resources/app/extensions/positron-python/python_files/shell_exec.py /usr/bin/python3 \
    -m pip install \
    -U pytrends \
    /private/var/folders/qk/w71qnntx22g9xmst4qjsqh280000gp/T/tmp-71161-DTvkena5kB6S-.log
