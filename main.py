import bot
import random


def main():
    years = random.randint(2018, 2019)
    month = str(random.randint(0, 1)) + str(random.randint(1, 2))
    day = str(random.randint(0, 2)) + str(random.randint(1, 9))
    flickr_url_interesting = 'https://api.flickr.com/services/rest/?method=flickr.interestingn' \
                             'ess.getList&api_key=03593667c94923eef10be7a5eca89b13&per_page=300&' \
                             'page=1&date=' + str(years) + '-' + str(month) + '-' + str(day) + '&' \
                                                                                               'safe_search=1&format' \
                                                                                               '=json' \
                                                                                               '&nojsoncallback=1 '
    user_id = '4xjjeqtthyqo'
    pat = 'cd65b61ee9f94f0fbbf6a892e5549fba'
    app_id = 'New'
    model_id = 'general-image-recognition'
    model_version_id = ''

    pick = bot.get_pic_from_flickr(flickr_url_interesting, 10)
    print(pick)
    tags = bot.get_relevant_tags_from_pick(pick, pat, user_id, app_id, model_id, model_version_id)
    print(tags)


if __name__ == '__main__':
    main()
