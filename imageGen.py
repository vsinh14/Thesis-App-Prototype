from openai import OpenAI
from database import database
import os
import wget

#OpenAI Settings
api_key = "sk-EJ5WHbYPpXuEpqqX3DOWzUDobxAT3Z6fYfUQHM87_DT3BlbkFJOMIbnG9h61jLZF1Ju3DCauH3oeUhl1LqPKaGHgZq4A"
client = OpenAI(api_key=api_key)

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
fN = fileNumber()
fileName = "genimg_" + str(fN) + ".png" 
url = makeImage()
wget.download(url,fileName)







