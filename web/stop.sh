ps aux | grep rs_rest_manage_new.py | grep -v grep | awk '{print $2}'| xargs kill -9
