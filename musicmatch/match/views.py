from django.shortcuts import render
from django.http import HttpResponse
from allauth.socialaccount.models import SocialApp
from django.template import RequestContext, loader
from allauth.socialaccount.models import SocialAccount
from models import Likes
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

def get_music_uuids(data, uid):
    #try to find music ids in db:
    music_ids = Likes.objects.filter(user_id=uid)
    print len(music_ids)
    if (len(music_ids)==0):
        music_ids = []
        while(True):
            try:
                for music in data['data']:
                    music_ids.append(music['id'])
                    Likes.objects.create(music_id = music['id'], user_id=uid)
                #print musics['paging']['next']
                data = requests.get(data['paging']['next']).json()
            except KeyError:
                break
        return music_ids
    return map(lambda a: a.music_id, music_ids)

def index(request):
    #SocialApp.objects.all()

    b = authenticate(request.user.id)
    print request.user.id
    similarities = None
    my_data = None
    data = None
    templateFile = "match/landingpage.html"
    if b is not None:
        my_data = b.extra_data
        print my_data
        similarities = []
        num_friends = my_data['friends']['summary']['total_count']
        my_data_music = get_music_uuids(my_data['music'], request.user.id)

        for friend in my_data['friends']['data']:
            uid = friend['id']
            friend_data = get_data(uid)
            print uid, friend_data, friend['name']
            try:
                friend_data_music = get_music_uuids(friend_data['music'], uid)
            except:
                friend_data_music = None
            music_similarity = similarity(my_data_music, friend_data_music)
            music_similarity *= 100
            if friend_data is not None and 'picture' in friend_data.keys():
                url = friend_data['picture']['data']['url']
            else:
                url = ''
            similarities.append((friend['name'], url, "{0:.2f}".format(music_similarity)))

        data = {
            'similarities': similarities,
            'my_picture': my_data['picture']['data']['url'],
            'num_friends': num_friends,
        }
        templateFile = "match/friendspage.html"
    context = data
    return render(request, templateFile, context)