import bot
import requests
import configparser


def main():
    config = configparser.ConfigParser()
    config.read("settings.ini")
    pick_url = bot.get_pic_from_flickr(config['Flickr']['interesting'], 10)
    print(pick_url)
    tags = ' '.join(bot.get_relevant_tags_from_pick(pick_url, config['Clarifai']['pat'], config['Clarifai']['user_id'],
                                                    config['Clarifai']['app_id'], config['Clarifai']['model_id'],
                                                    config['Clarifai']['model_version_id']))
    print(tags)
    bot.download_pick(pick_url)
    upload_url = bot.get_wall_upload_server(config['Vk']['token'], config['Vk']['group_id_test'])
    file = {'file1': open('pictures/Cat' + '.jpg', 'rb')}
    upload_response = requests.post(upload_url, files=file).json()
    save_result = bot.save_r(config['Vk']['token'], config['Vk']['group_id_test'], upload_response)
    wall_post_response = requests.get('https://api.vk.com/method/wall.post?',
                                      params={'attachments': save_result,
                                              'owner_id': -int(config['Vk']['group_id_test']),
                                              'access_token': config['Vk']['token'],
                                              'from_group': '1',
                                              'message': str(tags),
                                              'v': '5.101'}).json()
    print(wall_post_response)


if __name__ == '__main__':
    main()
