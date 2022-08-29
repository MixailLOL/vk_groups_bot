import requests
import random
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2


def get_pic_from_flickr(url, size):
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
    tags_exceptions = ['no_person', 'nude']
    for concept in output.data.concepts:
        tag = concept.name.replace(' ', '_')
        if tag not in tags_exceptions:
            tags.append('#' + tag)
    return tags[0:3]