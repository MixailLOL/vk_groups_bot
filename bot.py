import urllib
import requests
import random
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from google_trans_new import google_translator
import re


def get_pic_from_flickr(url, size):
    years = random.randint(2018, 2019)
    month = str(random.randint(0, 1)) + str(random.randint(1, 2))
    day = str(random.randint(0, 2)) + str(random.randint(1, 9))
    url = url.replace('years', str(years))
    url = url.replace('day', str(day))
    url = url.replace('month', str(month))
    pic_list = requests.get(url).json()
    pic_number = random.randint(1, len(pic_list['photos']['photo']) - 1)
    pic_urls = requests.get(
        'https://api.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key=03593667c94923eef10be7a5eca89b13'
        '&photo_id=' + str(pic_list['photos']['photo'][pic_number]['id']) + '&format=json&nojsoncallback=1').json()
    try:
        return str(pic_urls['sizes']['size'][size]['source'])
    except IndexError:
        print("Pick size not found. Researching new pick")
        return get_pic_from_flickr(url, size)


def download_pick(pic_url):
    img = urllib.request.urlopen(pic_url).read()
    out = open('pictures/Cat' + '.jpg', 'wb')
    out.write(img)
    out.close()


def get_relevant_tags_from_pick(pick_url, pat, user_id, app_id, model_id, model_version_id):
    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)
    metadata = (('authorization', 'Key ' + pat),)

    user_data_object = resources_pb2.UserAppIDSet(user_id=user_id, app_id=app_id)
    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
            user_app_id=user_data_object,
            model_id=model_id,
            version_id=model_version_id,
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            url=pick_url
                        )
                    )
                )
            ]
        ),
        metadata=metadata
    )
    if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
        print(post_model_outputs_response.status)
        raise Exception("Post model outputs failed, status: " + post_model_outputs_response.status.description)
    output = post_model_outputs_response.outputs[0]
    tags = []
    tags_exceptions = ['no person', 'nude', 'son', 'daughter', 'mother', 'father']
    for concept in output.data.concepts:
        if concept.name not in tags_exceptions:
            tags.append(concept.name)
    print(tags)
    return tags


def translate_tags(text):
    translator = google_translator()
    result = translator.translate(text, lang_tgt='ru')
    char_tags = re.findall(r"«([^«»]*)»", result)
    return char_tags[0: random.randint(1, 10)]


def get_wall_upload_server(token, group_id):
    r = requests.get('https://api.vk.com/method/photos.getWallUploadServer?', params={'access_token': token,
                                                                                      'group_id': group_id,
                                                                                      'v': '5.101'}).json()
    return r['response']['upload_url']


def save_r(token, group_id, upload_response):
    save_result = requests.get('https://api.vk.com/method/photos.saveWallPhoto?', params={'access_token': token,
                                                                                          'group_id': group_id,
                                                                                          'photo': upload_response[
                                                                                              'photo'],
                                                                                          'server': upload_response[
                                                                                              'server'],
                                                                                          'hash': upload_response[
                                                                                              'hash'],
                                                                                          'v': '5.101'}).json()
    return ('photo' + str(save_result['response'][0]['owner_id']) + '_' + str(
        save_result['response'][0]['id']) + '&access_key=' + str(save_result['response'][0]['access_key']))


def get_cat_pick_and_tags(config):
    pick_url = ''
    tags = []
    cats = ['Cat', 'cat', 'kitten', 'Kitten', 'Cats', 'cats']
    tags_set = set(tags)
    cats_set = set(cats)
    while not tags_set.intersection(cats_set):
        pick_url = get_pic_from_flickr(config['Flickr']['cats'], 10)
        tags = get_relevant_tags_from_pick(pick_url, config['Clarifai']['pat'], config['Clarifai']['user_id'],
                                           config['Clarifai']['app_id'], config['Clarifai']['model_id'],
                                           config['Clarifai']['model_version_id'])
        tags_set = set(tags)
        cats_set = set(cats)
    tags = ' '.join(translate_tags(tags))
    return pick_url, tags


def get_interesting_pick_and_tags(config):
    pick_url = get_pic_from_flickr(config['Flickr']['interesting'], 10)
    tags = get_relevant_tags_from_pick(pick_url, config['Clarifai']['pat'], config['Clarifai']['user_id'],
                                       config['Clarifai']['app_id'], config['Clarifai']['model_id'],
                                       config['Clarifai']['model_version_id'])
    tags = ' '.join(translate_tags(tags))
    return pick_url, tags


def post_to_group(config, group_id, tags, pick_url):
    download_pick(pick_url)
    upload_url = get_wall_upload_server(config['Vk']['token'], group_id)
    upload_response = requests.post(upload_url, files={'file1': open('pictures/Cat' + '.jpg', 'rb')}).json()
    save_result = save_r(config['Vk']['token'], config['Vk']['group_id_test'], upload_response)
    wall_post_response = requests.get('https://api.vk.com/method/wall.post?',
                                      params={'attachments': save_result,
                                              'owner_id': -int(config['Vk']['group_id_test']),
                                              'access_token': config['Vk']['token'],
                                              'from_group': '1',
                                              'message': str(tags),
                                              'v': '5.101'}).json()
    return wall_post_response



