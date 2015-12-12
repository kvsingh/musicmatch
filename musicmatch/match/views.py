from django.shortcuts import render
from django.http import HttpResponse
from allauth.socialaccount.models import SocialApp
from django.template import RequestContext, loader
from allauth.socialaccount.models import SocialAccount
import requests

def similarity(user1, user2):
    a = len(user1)
    b = len(user2)
    print a, b
    c = 0
    for music in user2:
        if music in user1:
            c += 1
    print c
    return float(2*c)/(a+b)

def authenticate(user_id):
    account_uid = SocialAccount.objects.filter(user_id=user_id, provider='facebook')
    if(len(account_uid)>0):
        b = account_uid[0]
        b.authenticate()
    else:
        b = None
    return b

def get_data(uid):
    account_uid = SocialAccount.objects.filter(uid=uid, provider='facebook')
    if(len(account_uid)>0):
        b = account_uid[0]
    else:
        return None
    return b.extra_data

def get_music_uuids(data):
    music_ids = []
    while(True):
        try:
            for music in data['data']:
                music_ids.append(music['id'])
            #print musics['paging']['next']
            data = requests.get(data['paging']['next']).json()
        except KeyError:
            break
    return music_ids

def index(request):
    #SocialApp.objects.all()

    b = authenticate(request.user.id)
    if b is not None:
        my_data = b.extra_data

    similarities = []
    for friend in my_data['friends']['data']:
        uid = friend['id']
        friend_data = get_data(uid)
        my_data_music = get_music_uuids(my_data['music'])
        friend_data_music = get_music_uuids(friend_data['music'])
        music_similarity = similarity(my_data_music, friend_data_music)
        print music_similarity
        similarities.append((friend['name'], music_similarity))

    context = RequestContext(request, {
        'similarities': similarities,
    })

    template = loader.get_template('match/index.html')
    return HttpResponse(template.render(context))

