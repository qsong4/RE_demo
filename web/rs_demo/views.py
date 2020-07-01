import os, sys
import json
import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

cur_dir = os.path.dirname( os.path.abspath(__file__)) or os.getcwd()
sys.path.append(cur_dir + '/../../')
sessionID = "1"
history = ""
from recommend import Recommend
rs = Recommend()

## receive the post input data and process.
@csrf_exempt
def analyze(request):
    ctx ={}
    if 'user_say' in request.POST:
        ctx['uid'] = uid = request.POST['uid'].strip()
        ctx['input'] = content = request.POST['user_say'].strip()
        ctx['flag'] = flag = request.POST['flag'].strip()

        # history = request.POST['answer'].strip()
        answer = json.dumps(rs.main_handle(uid, content), ensure_ascii=False)
        # history = history + "\n" + "sqy: " + in_text + "\n" + "PA_Bot: " + answer + "\n" + "*************************" + "\n"
        ctx['answer'] = answer

    return render(request, "index.html", ctx)





