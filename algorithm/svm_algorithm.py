
import numpy as np
import time
import datetime as dt

from sklearn import svm, metrics
import reco_to_obsv
import pickle

#############################load data###########################
players = ['player1','player2','player3']
player = players[2]
file = '%s.txt'%player
x_data,y_lable = reco_to_obsv.read_file(file,player)

#############################split data to train and test###########################
# from sklearn.cross_validation import train_test_split
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(x_data, y_lable, test_size=0.15,)

################create model###################
# param_C = 5
# classifier = svm.SVC(C=param_C,gamma='auto')
# classifier = svm.NuSVC()
# classifier = svm.LinearSVC()

#############################load model###########################
f2=open('./Model_last/%s_svm.model'%player,'rb')
s2=f2.read()
classifier=pickle.loads(s2)

#############################learn on train part###########################
start_time = dt.datetime.now()
print('Start learning at {}'.format(str(start_time)))
classifier.fit(X_train, y_train)
end_time = dt.datetime.now() 
print('Stop learning {}'.format(str(end_time)))
elapsed_time= end_time - start_time
print('Elapsed learning {}'.format(str(elapsed_time)))

#############################save model###########################
s=pickle.dumps(classifier)
f=open('./Model_last/%s_svm.model'%player, "wb+")
f.write(s)
f.close()

##########################Now predict the value of the test##############################
expected = y_test
predicted = classifier.predict(X_test)
# for i in expected:
#       print(i,predicted[expected.index(i)])
# show_some_digits(X_test,predicted,title_text="Predicted {}")

# print("Classification report for classifier %s:\n%s\n"
#       % (classifier, metrics.classification_report(expected, predicted)))
      
# cm = metrics.confusion_matrix(expected, predicted)
# print("Confusion matrix:\n%s" % cm)

print("Accuracy={}".format(metrics.accuracy_score(expected, predicted)))



