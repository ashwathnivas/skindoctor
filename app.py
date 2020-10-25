import os

import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np

from firebase.firebase import FirebaseApplication
from flask import Flask,render_template , request

__author__="ashwath_nivas"


app = Flask(__name__)

APP_ROOT=os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return render_template("submit.html")

@app.route("/screenshot")
def screenshot():
    return render_template("submit.html")

@app.route('/submit',methods=["POST","GET"])
def submit():
    image=request.args.get('image')
    return render_template("upload.html")

@app.route("/upload",methods=['POST'])
def upload():

    udata={}
    name = request.form['name']
    udata['name']=str(name)
    email = request.form['email']
    udata['email']=str(email)
    date = request.form['date']
    udata['date']=str(date)
    gender = request.form['gender']
    udata['gender']=str(gender)
    bloodgroup = request.form['bloodgroup']
    udata['bloodgroup']=str(bloodgroup)
    city = request.form['city']
    udata['city']=str(city)
    country = request.form['country']
    udata['country']=str(country)
    
    target=os.path.join(APP_ROOT,'files/')
    print("target",target)

    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("file"):
        print("file",file)
        print("file.filename",file.filename)
        filename=file.filename
        destination="".join([target,filename])
        print("destination",destination)
        file.save(destination)
        #filename="../files/"+filename
        print(filename)

    print("start")
    np.set_printoptions(suppress=True)
    model = tensorflow.keras.models.load_model('keras_model.h5')
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    image = Image.open(destination)
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)
    image_array = np.asarray(image)
    #image.show()
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array


    label=["actinic keratoses","bullous impetigo","dermatitis","flea bites","healthy skin","lyme disease","miliaria","no skin present","sunburn","tinea pedis"]

    prediction = model.predict(data)
    print(prediction)

    test_keys=label
    test_values=prediction.tolist()
    test_values=list(prediction[0])

    print(test_values)

    res = {} 
    for key in test_keys: 
        for value in test_values: 
            res[key] = value 
            test_values.remove(value) 
            break
        
    val=max(res,key=res.get)
    print(val,res)
    print("end")

    print(udata)

    if(val=="no skin present"):
        return render_template("no_skin.html")
    elif(val=="healthy skin"):
        return render_template("healthy_skin.html")
    else:
        udata['disease']=val
        fb = FirebaseApplication("https://skindoctor-e6294.firebaseio.com/",None)
        result=fb.post('patients',udata)
        if(val=="actinic keratoses"):
            return render_template("actinic_keratosis.html")
        elif(val=="bullous impetigo"):
            return render_template("bullous_impetigo.html")
        elif(val=="dermatitis"):
            return render_template("dermatitis.html")
        elif(val=="flea bites"):
            return render_template("flea_bites.html")
        elif(val=="lyme disease"):
            return render_template("lyme_disease.html")
        elif(val=="miliaria"):
            return render_template("miliaria.html")
        elif(val=="sunburn"):
            return render_template("sunburn.html")
        elif(val=="tinea pedis"):
            return render_template("tinea_pedis.html")
        print(result)
        


if __name__=="__main__":
    app.run(debug=True)




