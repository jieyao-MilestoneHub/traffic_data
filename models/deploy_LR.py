import joblib
import shutil

model_path = r"C:\Users\USER\Desktop\Develop\traffic_data\models\models\LR_model.pkl"

# 加載訓練好的模型
model = joblib.load(model_path)

# 將模型部署到生產環境（假設是複製到一個指定的目錄）
shutil.copy('LR_model.pkl', model_path)
