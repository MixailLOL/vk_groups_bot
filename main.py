import bot
import requests
import configparser


def main():
    config = configparser.ConfigParser()
    config.read("settings.ini")
    pick_url, tags = bot.get_interesting_pick_and_tags(config)
    response = bot.post_to_group(config, config['Vk']['group_id_test'], tags, pick_url)
    print(response)


if __name__ == '__main__':
    main()
