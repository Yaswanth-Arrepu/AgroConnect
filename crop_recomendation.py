from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import pandas as pd
data=pd.read_csv("E:/Capstone Project-2/IEEE_dataset.csv")
data=data.drop(columns=["Unnamed: 0"])
X=data.drop(columns=["Crop"])
Y=data["Crop"]
x_train,x_test,y_train,y_test=train_test_split(X,Y,test_size=0.4,random_state=49)
model=RandomForestClassifier()
model.fit(x_train,y_train)
feature_names = ["N", "P", "K", "pH", "rainfall", "temperature"]
def crop_predict(input_features):
    input_features=pd.DataFrame(input_features,columns=feature_names,index=[0])
    return model.predict(input_features)[0]