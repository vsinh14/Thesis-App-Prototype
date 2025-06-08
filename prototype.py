from openai import OpenAI
import sqlite3
import os
import base64
import requests
import wget
from database import database

#OpenAI Settings
api_key = ""
client = OpenAI(api_key=api_key)

#Encode Image in base64
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

#Upload and Process Image
def image_process(image_path):
    image_query = ['provide a caption for this image in fewer than 10 words',
                    'provide 10 tags for this image in CSV format',
                    'provide a description for this image']

    base64_image = encode_image(image_path)

    response_list =[]
    for query in image_query:
    # Getting the base64 string

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": query
                },
                {
                    "type": "image_url",
                    "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
                ]
            }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response = response.json()
        print(response)
        response = response['choices'][0]['message']['content']
        response_list.append(response)

    return response_list
def begin_process():
    #Create Database if does not exist
    database.db_create()

    # ADD NEW IMAGES TO DATABASE
    current_directory = os.path.dirname(os.path.abspath(__file__))

    image_list = os.listdir(f'{current_directory}/static/')

    #Processes and Adds Image to Database if No Record Exists Yet
    #Set to only recognize png files, ad "or" to if statement to add additional image types
    for image in image_list:
        if 'jpg' in image:
            image_path = os.path.join(f'{current_directory}/static/', image)

            file_path = database.path()
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            sql = f"select * from image_table where image_name = '{image}'"
            cursor.execute(sql)
            record = cursor.fetchall()
            conn.commit()
            conn.close()

            if not record:
                response = image_process(image_path)
                database.db_insert(image, response)
                print(f'Added {image}\n{response}')
            else:
                print('Already in Database')
def index():
    record = database.db_select()
    setList = [] 
    for x in record:
        xList = x[3].split("```")
        keys = xList[1].split(',')
        for i in keys:
            iden = i.replace('"','')
            noNew = iden.replace("\n",'')
            value = noNew.replace(" ",'')
            setList.append(value)
    setValues = set(setList)
    return setValues

def makeImage():
    prompt = index() 
    promptString = ""
    for i in prompt:
        if len(promptString) == 0:
            promptString = promptString + i
        promptString = promptString + "," + i
    print(promptString)
    response = client.images.generate(
      model="dall-e-3",
      prompt=promptString,
      size="1024x1024",
      quality="standard",
      n=1,
    )
    image_url = response.data[0].url

    return image_url

def fileNumber():
    directoryList = os.listdir()
    counter = 0
    for i in directoryList:
        name = i.split("_")
        if(name[0] == "test"):
            counter +=1
    return counter       

begin_process()
fN = fileNumber()
fileName = "test_" + str(fN) + ".png" 
url = makeImage()
wget.download(url,fileName)

