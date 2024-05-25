import joblib
import shutil

# 加載訓練好的模型
model = joblib.load('LR_model.pkl')

# 將模型部署到生產環境（假設是複製到一個指定的目錄）
shutil.copy('LR_model.pkl', 'models/models/LR_model.pkl')
