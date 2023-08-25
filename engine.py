import requests
import random
import string
import websocket
import uuid
import json
from PIL import Image
from io import BytesIO
import io

client_id = str(uuid.uuid4())

def queue_prompt(prompt, server_address):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    url = "http://{}/prompt".format(server_address)
    response = requests.post(url, data=data, headers={'Content-Type': 'application/json'})
    return response.json()

def get_image_name(prompt, server_address):
    progress = 0
    ws = websocket.WebSocket() 
    try:
        ws.connect("wss://{}/ws?clientId={}".format(server_address, client_id))
    except:
        ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))

    prompt_id = queue_prompt(prompt, server_address)['prompt_id']
    try:
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'progress':
                    value = message['data']['value']
                    max = message['data']['max']
                    progress = int(100 * value / max)
                if message['type'] == 'executed':
                    if 'images' in message['data']['output']:
                        images = message['data']['output']['images']
                        for image in images:
                            if 'type' in image and image['type'] == 'output':
                                if 'filename' in image:
                                    filename = image['filename']
                                    print(filename)
                                    url = "http://{}/view?filename={}".format(server_address, filename)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue #previews are binary data

    finally:
        ws.close()
        print("okai im done")
    return url

def image_in_base64(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return img

def generate_random_numbers(length=13):
    #Cgetting random seed
    snumbers = string.digits
    return ''.join(random.choice(snumbers) for _ in range(length))

def engine(workflow,img_path,img_name,userprompt,server_address):

    #Loading workflows
    configurations = json.loads(open("configs.json").read())
    if workflow in configurations:
        config = configurations[workflow]
        json_path = config["file_path"]
        prompt_node = str(config["promptnode"])
        image_node = str(config["imagenode"])
        ksampler_node = str(config["ksampler"])
 
    #Loading prompt
    with open(json_path, "r") as json_file:
        json_data = json_file.read()
    prompt = json.loads(json_data)
    try:
        loader = str(config["loader"])
        model = str(userprompt)
        prompt[loader]["inputs"]["ckpt_name"] = model
    except Exception as e:
        pass
    prompt[ksampler_node]["inputs"]["seed"] = generate_random_numbers()
    prompt[image_node]["inputs"]["image"] = img_name
    prompt[prompt_node]["inputs"]["Text"] = userprompt
    prompt[prompt_node]["inputs"]["text"] = userprompt

    # Construct files dict for upload  
    files = {'image': open(img_path, 'rb')}
    url = "http://{}".format(server_address)
    requests.post(url + "/upload/image", files=files)

    #getting processed images
    img = image_in_base64(get_image_name(prompt, server_address))
    return img