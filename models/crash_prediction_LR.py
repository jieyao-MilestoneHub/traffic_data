import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score
import joblib

# 加載數據
data = pd.read_csv('your_data.csv')

# 預處理數據
X = data[['speed', 'flow', 'occupancy']]
y = data['crash']

# 分割數據集為訓練集和測試集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 訓練Logistic回歸模型
model = LogisticRegression()
model.fit(X_train, y_train)

# 評估模型
y_pred = model.predict(X_test)
y_pred_prob = model.predict_proba(X_test)[:, 1]
accuracy = accuracy_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_prob)

print(f'Accuracy: {accuracy}')
print(f'Confusion Matrix:\n{confusion_matrix(y_test, y_pred)}')
print(f'ROC AUC: {roc_auc}')

# 保存模型
model_path = r"C:\Users\USER\Desktop\Develop\traffic_data\models\models\LR_model.pkl"
joblib.dump(model, model_path)
