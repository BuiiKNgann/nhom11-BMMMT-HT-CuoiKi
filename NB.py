# -*- coding: utf-8 -*-
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix, accuracy_score, ConfusionMatrixDisplay
from sklearn.preprocessing import LabelEncoder, StandardScaler
import matplotlib.pyplot as plt

class MachineLearning():

    def __init__(self):
        print("Loading dataset ...")
        self.flow_dataset = pd.read_csv('traffic_data.csv')

        # Loại bỏ dòng có dữ liệu thiếu (NaN)
        self.flow_dataset.dropna(inplace=True)

        # Bỏ xử lý IP/PORT, chỉ LabelEncode cột string
        for col in self.flow_dataset.columns:
            if self.flow_dataset[col].dtype == 'object':
                le = LabelEncoder()
                self.flow_dataset[col] = le.fit_transform(self.flow_dataset[col])

    def flow_training(self):
        print("Flow Training ...")

        # Tách đặc trưng và nhãn
        X_flow = self.flow_dataset.iloc[:, :-1].values
        y_flow = self.flow_dataset.iloc[:, -1].values

        # Chuẩn hóa đặc trưng
        sc = StandardScaler()
        X_flow = sc.fit_transform(X_flow)

        # Tách tập train/test
        X_flow_train, X_flow_test, y_flow_train, y_flow_test = train_test_split(
            X_flow, y_flow, test_size=0.25, random_state=0)

        # Huấn luyện Naive Bayes
        classifier = GaussianNB()
        flow_model = classifier.fit(X_flow_train, y_flow_train)

        # Dự đoán
        y_flow_pred = flow_model.predict(X_flow_test)

        print("------------------------------------------------------------------------------")
        print("Confusion Matrix:")
        cm = confusion_matrix(y_flow_test, y_flow_pred)
        print(cm)

        acc = accuracy_score(y_flow_test, y_flow_pred)
        print("Success accuracy = {0:.2f} %".format(acc * 100))
        print("Fail accuracy = {0:.2f} %".format((1 - acc) * 100))
        print("------------------------------------------------------------------------------")

        # Hiển thị ma trận nhầm lẫn
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot(cmap=plt.cm.Blues)
        plt.title("Confusion Matrix - Naive Bayes")
        plt.xlabel("Predicted Labels")
        plt.ylabel("True Labels")
        plt.tight_layout()
        plt.show()

def main():
    start = datetime.now()

    ml = MachineLearning()
    ml.flow_training()

    end = datetime.now()
    print("Training time: ", (end - start))

if __name__ == "__main__":
    main()

