"""!cute #: get a random cute picture"""

import re
import random

LIB = [
    "http://images2.fanpop.com/image/photos/9700000/Kittens-cute-kittens-9781982-800-600.jpg",
    "http://2.bp.blogspot.com/-Tjcg8gq082I/UZsikSuPb6I/AAAAAAAAATs/KMlDHHPs2sk/s640/cute_animals_25.jpg",
    "http://www.barnorama.com/wp-content/images/2012/03/expect-bunnies/01-expect-bunnies.jpg",
    "http://funnymama.com/store/130813/204215_v0_600x.jpg",
    "http://img3.wikia.nocookie.net/__cb20140614000321/clubpenguinpookie/images/d/d0/Extremely-cute-kitten_large.jpg",
    "http://cdn.attackofthecute.com/January-04-2012-01-27-24-tumblrlx5078frXc1qi23vmo1500.jpeg",
    "http://s1.zerochan.net/Pikachu.600.1198588.jpg",
    "http://img.washingtonpost.com/blogs/local/files/2014/10/4-kittens1.jpg",
    "http://1.bp.blogspot.com/-2MmAH0H9QAg/T-U35qfHX5I/AAAAAAAAEB0/JfJ2FtKGHzU/s1600/Bunny%252BWabbit_766-718770.jpg",
    "http://36.media.tumblr.com/tumblr_m3skgvKarf1qfyzelo1_400.jpg",
    "https://33.media.tumblr.com/5440fd4c60ff1c009b6f907dfcb3f463/tumblr_mt826fQwSO1r9fg7wo7_500.gif",
    "http://images.viralnova.com/000/085/544/desktop-1413926829.png",
    "http://giadalton.com/wp-content/uploads/2013/09/happy-kitty-.jpg",
    "http://cache.desktopnexus.com/thumbnails/430148-bigthumbnail.jpg",
    "http://i.picresize.com/images/2014/11/18/Pt1wH.jpg",
    "http://img0.joyreactor.com/pics/comment/gif-kitten-animals-chase-651517.gif",
    "http://24.media.tumblr.com/db6a115dce1ce1ef2cb50b3fe3fba5db/tumblr_mftulzieLc1qbxi45o2_r1_500.gif",
    "http://cutearoo.com/wp-content/uploads/2011/04/Squirrel-and-Kitty.jpg",
    "http://www.funnyjunksite.com/pictures/funnypics/animals/hamsters/funny_hamsters_picture_5.jpg",
    "http://shechive.files.wordpress.com/2011/06/tumblr_ljesp3da4m1qikh6fo1_500.gif?w=477&h=342",
    "https://www.youtube.com/watch?v=J9VQxhJczLA#t=23",
    "http://i.imgur.com/AtRn2qs.jpg",
    "http://media.giphy.com/media/LPCjVh9odU3FS/giphy.gif",
    "http://media1.giphy.com/media/Puc4FZWExJc0E/giphy.gif",
    "http://media.giphy.com/media/rOScDjyggnKNy/giphy.gif",
    "http://static.tumblr.com/vlykcdf/lN2l9mwte/cute-kitten-303.jpg",
    "http://40.media.tumblr.com/tumblr_kp3jpdIHWK1qzbpaho1_500.jpg",
    "http://img3.wikia.nocookie.net/__cb20140614000321/clubpenguinpookie/images/d/d0/Extremely-cute-kitten_large.jpg",
    "http://fc02.deviantart.net/fs71/i/2010/335/f/5/kawaii_kitten_by_pure_poison89-d33zj7m.jpg",
    "https://31.media.tumblr.com/769f8a35de635559ef5fbe13325adca7/tumblr_mgjc0g5GJI1s080geo1_400.gif",
    "http://38.media.tumblr.com/9408b73d447199c766eb139d0400b2ea/tumblr_mm9n3sdycy1ry1y7qo9_r1_500.gif",
    "https://s-media-cache-ak0.pinimg.com/236x/8f/f1/75/8ff1752e67a2d4f3b2ff8ece703c0fb0.jpg",
    "http://i98.photobucket.com/albums/l269/autumn_10_2006/cute-kitten.jpg",
    "http://i.imgur.com/dkI0lsX.jpg",
    "http://media.steampowered.com/steamcommunity/public/images/avatars/ab/aba959be0200c086035ea821ffcf1a0caff7574a_full.jpg",
    "http://speckycdn.sdm.netdna-cdn.com/wp-content/uploads/2012/03/Cute-kitten.jpg",
    "http://media.steampowered.com/steamcommunity/public/images/avatars/ab/aba959be0200c086035ea821ffcf1a0caff7574a_full.jpg",
    "http://images4.fanpop.com/image/photos/20600000/Cute-Wallpaper-teddybear64-20682571-1280-1024.jpg",
    "https://vanosslife.files.wordpress.com/2013/04/dsc_0309.jpg",
]


def cute_response(text):
    match = re.match(r'!cute ?([0-9])?', text)
    if not match:
        return False

    response = ""

    if match.group(1):
        count = int(match.group(1))
    else:
        count = 1

    count = min(len(LIB), count)

    cutes = []

    for i in range(count):
        while cuteness in cutes:
            cuteness = random.choice(LIB)
        cutes.append(cuteness)

    return '\n'.join(cutes)

def on_message(msg, server):
    text = msg.get("text", "")
    return cute_response(text)
