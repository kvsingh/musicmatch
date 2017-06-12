from django.shortcuts import render
from django.http import HttpResponse
from allauth.socialaccount.models import SocialApp
from django.template import RequestContext, loader
from allauth.socialaccount.models import SocialAccount
import requests

def similarity(user1, user2):
    if user1 is None or user2 is None:
        return 0
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
    try:
        account_uid = SocialAccount.objects.filter(uid=uid, provider='facebook')
        if(len(account_uid)>0):
            b = account_uid[0]
        else:
            return None
        return b.extra_data
    except:
        return None

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
    similarities = None
    my_data = None
    data = None
    if b is not None:
        my_data = b.extra_data
        print my_data
        similarities = []
        for friend in my_data['friends']['data']:
            uid = friend['id']
            friend_data = get_data(uid)
            print uid, friend_data, friend['name']
            my_data_music = get_music_uuids(my_data['music'])
            try:
                friend_data_music = get_music_uuids(friend_data['music'])
            except:
                friend_data_music = None
            music_similarity = similarity(my_data_music, friend_data_music)
            music_similarity *= 100
            similarities.append((friend['name'], '''friend['picture']['data']['url']''', "{0:.2f}".format(music_similarity)))

        data = {
            'similarities': similarities,
            'my_picture': my_data['picture']['data']['url']
        }
    #context = RequestContext(request, data)
    context = data
    template = loader.get_template('match/index.html')
    return render(request, 'match/index.html', context)
    #return HttpResponse(template.render(context, request))

