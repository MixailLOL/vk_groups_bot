import time

import bot
import configparser
import os


def main():
    config = configparser.ConfigParser()
    path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
    config.read(os.path.join(path, 'settings.ini'))
    # pick_url, tags = bot.get_interesting_pick_and_tags(config)
    # print(pick_url, tags)
    # response = bot.post_to_group(config, config['Vk']['group_id_test'], tags, pick_url)
    # print(tags)
    # pick_url, tags = bot.get_cat_pick_and_tags(config)
    # response = bot.post_to_group(config, config['Vk']['group_id_test'], tags, pick_url)
    # print(pick_url, tags)
    tag, pick_url = bot.inf_generate()
    response = bot.post_to_group(config, config['Vk']['group_id_wiki'], tag, pick_url)
    print(tag, pick_url)


if __name__ == '__main__':
    main()
