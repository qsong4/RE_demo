import os, sys
import json
import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

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
    if request.method=="POST":
        try:
            ori = json.loads(request.body)
        except:
            HttpResponse("json格式错误")
        try:
            ctx['uid'] = uid = ori['uid']
            ctx['input'] = content = ori['user_say']
            ctx['flag'] = flag = ori['flag']
        except:
            HttpResponse("数据格式错误")

        # history = request.POST['answer'].strip()
        answer = json.dumps(rs.main_handle(uid, content), ensure_ascii=False)
        # history = history + "\n" + "sqy: " + in_text + "\n" + "PA_Bot: " + answer + "\n" + "*************************" + "\n"
        ctx['answer'] = answer
    else:
        return HttpResponse("请使用POST请求")

    jsonResult = json.dumps(ctx, ensure_ascii=False)
    respones = HttpResponse(jsonResult)
    return respones
    # return render(request, "index.html", ctx)





