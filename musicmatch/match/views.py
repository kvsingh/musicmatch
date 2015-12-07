from django.shortcuts import render
from django.http import HttpResponse
from allauth.socialaccount.models import SocialApp
from django.template import RequestContext, loader
from allauth.socialaccount.models import SocialAccount

def index(request):
    #SocialApp.objects.all()
    from allauth.socialaccount.models import Site
    account_uid = SocialAccount.objects.filter(user_id=request.user.id, provider='facebook')
    if(len(account_uid)>0):
        b = account_uid[0]
        b.authenticate()
        a = b.extra_data
    else:
        a = None
    context = RequestContext(request, {
        'a': a,
    })
    template = loader.get_template('match/index.html')
    return HttpResponse(template.render(context))

