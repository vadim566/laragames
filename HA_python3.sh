#!/bin/bash
##get the app.py from process ps aux
pid_info=` ps aux|grep python3|grep __init__.py|awk '{print $12}'`
#python_expected="/laragames/app.py"
pid_name="__init__.py"


##if there is process name running
if [[ $pid_info = $pid_name ]]
then
        echo 'works'
        date
else
##if not runing then start ve env and start app
        echo 'not works'
        date
        echo 'starting virtual env'
        source /laragames/venv/bin/activate
        cd /laragames/
        python3 __init__.py

fi
