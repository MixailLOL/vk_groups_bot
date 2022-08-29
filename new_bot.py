import requests
import urllib.request
import time
from time import sleep
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
import wikipedia
import random

# https://oauth.vk.com/authorize?client_id=6957898&scope=photos,wall,groups,
# photos&redirect_uri=http://api.vk.com/blank.html&display=page&response_type=token
H = time.strftime('%H')
M = time.strftime('%M')
years = random.randint(2018, 2019)
month = str(random.randint(0, 1)) + str(random.randint(1, 2))
day = str(random.randint(0, 2)) + str(random.randint(1, 9))
token = 'vk1.a.hjBdfwgFlyPqaCIyGSiNB5UFZctvkOf6daXb9L837u2ZGYIr3AkxHOqCRmrfNPuaGI' \
        '-wK5ZKsIQt_Xqjry6CzQV0PYoLlpZ2KKwp172RmvVSdBIpIdoPO6nTkkuEAdowpCkRJ8HF313x1sACW9855FsU3dOuz_8h1OlaQRvCMf02sk' \
        'iJKwfm354IwjgsETRJ '
group_id_cats = 192603988
group_id_rand = 181476474
flickr_url_cat = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key' \
                 '=03593667c94923eef10be7a5eca89b13&tags=Cat,kitten,cats&' \
                 'max_upload_date=' + str(years) + '-' + str(month) + '-' + str(day) + '&safe_search=1&per_page=300' \
                                                                                       '&tag_mode=any&page=1&format=json' \
                                                                                       '&nojsoncallback=1 '
flickr_url_interesting = 'https://api.flickr.com/services/rest/?method=flickr.interestingn' \
                         'ess.getList&api_key=03593667c94923eef10be7a5eca89b13&per_page=300&' \
                         'page=1&date=' + str(years) + '-' + str(month) + '-' + str(day) + '&' \
                                                                                           'safe_search=1&format=json' \
                                                                                           '&nojsoncallback=1 '
USER_ID = '4xjjeqtthyqo'
PAT = 'cd65b61ee9f94f0fbbf6a892e5549fba'
APP_ID = 'New'
MODEL_ID = 'general-image-recognition'
MODEL_VERSION_ID = ''


def get_flickr_pic(url, size):
    pic_list = requests.get(url).json()
    # print('pic_list response = ',json.dumps(pic_list, indent=4, sort_keys=True))
    pic_number = random.randint(1, len(pic_list['photos']['photo']) - 1)
    print("pic num = ", len(pic_list['photos']['photo']), "; my pic = ", pic_number)
    get_size = requests.get(
        'https://api.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key=03593667c94923eef10be7a5eca89b13'
        '&photo_id=' + str(
            pic_list['photos']['photo'][pic_number]['id']) + '&format=json&nojsoncallback=1').json()
    try:
        url_size = get_size['sizes']['size'][size]['source']
        return str(get_size['sizes']['size'][size]['source'])
    except:
        return get_flickr_pic(url, size)


def get_wall_upload_server(group_id):
    r = requests.get('https://api.vk.com/method/photos.getWallUploadServer?', params={'access_token': token,
                                                                                      'group_id': group_id,
                                                                                      'v': '5.101'}).json()
    # print('getWallUploadServer = ',json.dumps(r, indent=4, sort_keys=True))
    return r['response']['upload_url']


def save_r(group_id, upload_response):
    save_result = requests.get('https://api.vk.com/method/photos.saveWallPhoto?', params={'access_token': token,
                                                                                          'group_id': group_id,
                                                                                          'photo': upload_response[
                                                                                              'photo'],
                                                                                          'server': upload_response[
                                                                                              'server'],
                                                                                          'hash': upload_response[
                                                                                              'hash'],
                                                                                          'v': '5.101'}).json()
    # print('save_result response = ',json.dumps(save_result, indent=4, sort_keys=True))
    return ('photo' + str(save_result['response'][0]['owner_id']) + '_' + str(
        save_result['response'][0]['id']) + '&access_key=' + str(save_result['response'][0]['access_key']))


def get_relevant_tags(url):
    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    metadata = (('authorization', 'Key ' + PAT),)

    user_data_object = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)
    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
            user_app_id=user_data_object,
            model_id=MODEL_ID,
            version_id=MODEL_VERSION_ID,
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            url=url
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

    tag = []
    tags_number = 1
    for concept in output.data.concepts:
        no_per = (concept.name).replace(' ', '_')
        if no_per == 'no_person' or no_per == 'nude' or tags_number == 5:
            continue
        tag.append('#' + no_per)
        tags_number += 1
    return tag


def get_relevant_cat_tags(url):
    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    metadata = (('authorization', 'Key ' + PAT),)

    user_data_object = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)
    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
            user_app_id=user_data_object,
            model_id=MODEL_ID,
            version_id=MODEL_VERSION_ID,
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            url=url
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

    tag = []
    tags_number = 1
    for concept in output.data.concepts:
        no_per = (concept.name).replace(' ', '_')
        if no_per == 'no_person' or no_per == 'nude' or tags_number == 5:
            continue
        tag.append('#' + no_per)
        tags_number += 1
    return tag


def inf_generate():
    number_image = 0
    file_f = ''
    wikipedia.set_lang("ru")
    line = random.choice(open('RUS.txt').readlines())
    print(line)
    try:
        complete_content = wikipedia.search(line)
        print('len(complete_content) =', len(complete_content))
    except:
        post_content, file_name = inf_generate()
        return post_content, file_name
    try:
        content = (complete_content[random.randint(1, (len(complete_content)))])
        print('content random number =', content)
    except:
        print('Out index of the range. But Ok')
        post_content, file_name = inf_generate()
        return post_content, file_name

    print(content)
    page_image = wikipedia.page(content)
    image_down_link = page_image.images[number_image]
    x = 3
    while x > 0:
        file_f = file_f + image_down_link[(len(image_down_link) - x)]
        x = x - 1
    print(file_f)
    if (file_f != 'jpg') and (file_f != 'png'):
        while (file_f != 'jpg') and (file_f != 'png'):
            print(file_f)
            number_image = number_image + 1
            x = 3
            file_f = ''
            while x > 0:
                try:
                    image_down_link = page_image.images[number_image]
                except:
                    print('Pikchi Net, but OK')
                    post_content, file_name = inf_generate()
                    return post_content, file_name
                file_f = file_f + image_down_link[(len(image_down_link) - x)]
                x = x - 1
    urllib.request.urlretrieve(image_down_link, 'pictures/Cat' + "." + file_f)
    file_name = str("Cat." + file_f)
    post_content = wikipedia.summary(content)
    # print('post_content = ',post_content)
    content = content.replace(' ', '_')
    content = content.replace('(', '')
    content = content.replace(')', '')
    content = content.replace('.', '')
    content = content.replace(',', '')
    content = content.replace(':', '')
    content = content.replace('—', '')
    content = content.replace('-', '')
    post_content = "#" + content + "\n" + post_content
    post_content = post_content.split('\n', 2)
    # print('post_content = ',post_content)
    return post_content[0] + '\n' + post_content[1], file_name


def main():
    while 1:
        while 1:
            years = random.randint(2018, 2019)
            month = str(random.randint(0, 1)) + str(random.randint(1, 2))
            day = str(random.randint(0, 2)) + str(random.randint(1, 9))
            size = 10
            cat_pic_url = get_flickr_pic(flickr_url_cat, size)
            print("pic_url cat = ", cat_pic_url)
            caption = ' '.join(get_relevant_cat_tags(cat_pic_url))

            if caption != 'e r r o r':
                break

        img = urllib.request.urlopen(cat_pic_url).read()
        out = open('pictures/Cat' + '.jpg', 'wb')
        out.write(img)
        out.close()
        upload_url = get_wall_upload_server(group_id_cats)
        file = {'file1': open('pictures/Cat' + '.jpg', 'rb')}
        upload_response = requests.post(upload_url, files=file).json()
        save_result = save_r(group_id_cats, upload_response)
        wall_post_response = requests.get('https://api.vk.com/method/wall.post?', params={'attachments': save_result,
                                                                                          'owner_id': -group_id_cats,
                                                                                          'access_token': token,
                                                                                          'from_group': '1',
                                                                                          'message': caption,
                                                                                          'v': '5.101'}).json()
        print(wall_post_response, time.strftime('%H') + ':' + time.strftime('%M') + ' CATS', years, '-', month, '-',
              day)
        post_type = random.randint(1, 7)
        print("post_type = ", post_type)
        if post_type == 1:
            upload_url = get_wall_upload_server(group_id_rand)
            caption, file_name = inf_generate()
            file = {'file1': open('pictures/' + file_name, 'rb')}
            upload_response = requests.post(upload_url, files=file).json()
            save_result = save_r(group_id_rand, upload_response)
            wall_post_response = requests.get('https://api.vk.com/method/wall.post?',
                                              params={'attachments': save_result,
                                                      'owner_id': -group_id_rand,
                                                      'access_token': token,
                                                      'from_group': '1',
                                                      'message': caption,
                                                      'v': '5.101'}).json()
            print(wall_post_response, time.strftime('%H') + ':' + time.strftime('%M'), years, '-', month, '-', day)
        else:
            pic_url = get_flickr_pic(flickr_url_interesting, size)
            print("pic_url interest = ", pic_url)
            caption = ' '.join(get_relevant_tags(pic_url))
            img = urllib.request.urlopen(pic_url).read()
            out = open('pictures/Cat' + '.jpg', 'wb')
            out.write(img)
            out.close()
            upload_url = get_wall_upload_server(group_id_rand)
            file = {'file1': open('pictures/Cat' + '.jpg', 'rb')}
            upload_response = requests.post(upload_url, files=file).json()
            save_result = save_r(group_id_rand, upload_response)
            wall_post_response = requests.get('https://api.vk.com/method/wall.post?',
                                              params={'attachments': save_result,
                                                      'owner_id': -group_id_rand,
                                                      'access_token': token,
                                                      'from_group': '1',
                                                      'message': str(caption),
                                                      'v': '5.101'}).json()
            print(wall_post_response, time.strftime('%H') + ':' + time.strftime('%M'), years, '-', month, '-', day)
        time_stop = random.randint(5400, 7200)
        print(time_stop)
        sleep(time_stop)


if __name__ == '__main__':
    main()
