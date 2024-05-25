import pandas as pd
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, LayerNormalization, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.layers import MultiHeadAttention
import numpy as np


# 載入數據
data = pd.read_csv('your_data.csv')

# 預處理數據
X = data[['speed', 'flow', 'occupancy']]
y = data['crash']

# 分割資料集為訓練集和測試集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)


# 定義位置編碼層
class PositionalEncoding(tf.keras.layers.Layer):
    def __init__(self, position, d_model):
        super(PositionalEncoding, self).__init__()
        self.position = position
        self.d_model = d_model

    def get_angles(self, pos, i, d_model):
        angle_rates = 1 / np.power(10000, (2 * (i // 2)) / np.float32(d_model))
        return pos * angle_rates

    def call(self, inputs):
        angle_rads = self.get_angles(np.arange(self.position)[:, np.newaxis],
                                    np.arange(self.d_model)[np.newaxis, :],
                                    self.d_model)

        # apply sin to even indices in the array; 2i
        angle_rads[:, 0::2] = np.sin(angle_rads[:, 0::2])

        # apply cos to odd indices in the array; 2i+1
        angle_rads[:, 1::2] = np.cos(angle_rads[:, 1::2])

        pos_encoding = angle_rads[np.newaxis, ...]

        return inputs + tf.cast(pos_encoding, tf.float32)

# 定義Transformer編碼器層
def transformer_encoder_layer(units, d_model, num_heads, dropout, name="transformer_encoder_layer"):
    inputs = tf.keras.Input(shape=(None, d_model), name="inputs")
    padding_mask = tf.keras.Input(shape=(1, 1, None), name="padding_mask")

    attention = MultiHeadAttention(
        num_heads=num_heads, key_dim=d_model, dropout=dropout)(inputs, inputs, attention_mask=padding_mask)
    attention = Dropout(rate=dropout)(attention)
    attention = LayerNormalization(epsilon=1e-6)(attention + inputs)

    outputs = tf.keras.layers.Dense(units=units, activation='relu')(attention)
    outputs = tf.keras.layers.Dense(units=d_model)(outputs)
    outputs = Dropout(rate=dropout)(outputs)
    outputs = LayerNormalization(epsilon=1e-6)(outputs + attention)

    return tf.keras.Model(inputs=[inputs, padding_mask], outputs=outputs, name=name)

# 定義Transformer解碼器圖層
def transformer_decoder_layer(units, d_model, num_heads, dropout, name="transformer_decoder_layer"):
    inputs = tf.keras.Input(shape=(None, d_model), name="inputs")
    enc_outputs = tf.keras.Input(shape=(None, d_model), name="encoder_outputs")
    look_ahead_mask = tf.keras.Input(shape=(1, None, None), name="look_ahead_mask")
    padding_mask = tf.keras.Input(shape=(1, 1, None), name="padding_mask")

    attention1 = MultiHeadAttention(
        num_heads=num_heads, key_dim=d_model, dropout=dropout)(inputs, inputs, attention_mask=look_ahead_mask)
    attention1 = Dropout(rate=dropout)(attention1)
    attention1 = LayerNormalization(epsilon=1e-6)(attention1 + inputs)

    attention2 = MultiHeadAttention(
        num_heads=num_heads, key_dim=d_model, dropout=dropout)(attention1, enc_outputs, attention_mask=padding_mask)
    attention2 = Dropout(rate=dropout)(attention2)
    attention2 = LayerNormalization(epsilon=1e-6)(attention2 + attention1)

    outputs = tf.keras.layers.Dense(units=units, activation='relu')(attention2)
    outputs = tf.keras.layers.Dense(units=d_model)(outputs)
    outputs = Dropout(rate=dropout)(outputs)
    outputs = LayerNormalization(epsilon=1e-6)(outputs + attention2)

    return tf.keras.Model(inputs=[inputs, enc_outputs, look_ahead_mask, padding_mask], outputs=outputs, name=name)

# 定義Transformer模型
def transformer(vocab_size, num_layers, units, d_model, num_heads, dropout, name="transformer"):
    inputs = tf.keras.Input(shape=(None,), name="inputs")
    dec_inputs = tf.keras.Input(shape=(None,), name="dec_inputs")

    enc_padding_mask = tf.keras.layers.Lambda(create_padding_mask, output_shape=(1, 1, None),
                                            name='enc_padding_mask')(inputs)
    look_ahead_mask = tf.keras.layers.Lambda(create_look_ahead_mask, output_shape=(1, None, None),
                                            name='look_ahead_mask')(dec_inputs)
    dec_padding_mask = tf.keras.layers.Lambda(create_padding_mask, output_shape=(1, 1, None),
                                            name='dec_padding_mask')(inputs)

    enc_outputs = PositionalEncoding(vocab_size, d_model)(inputs)

    for i in range(num_layers):
        enc_outputs = transformer_encoder_layer(units=units, d_model=d_model, num_heads=num_heads, dropout=dropout,
                                                name="encoder_layer_{}".format(i), )(inputs=[enc_outputs, enc_padding_mask])

    dec_outputs = PositionalEncoding(vocab_size, d_model)(dec_inputs)

    for i in range(num_layers):
        dec_outputs = transformer_decoder_layer(units=units, d_model=d_model, num_heads=num_heads, dropout=dropout,
                                                name="decoder_layer_{}".format(i), )(
            inputs=[dec_outputs, enc_outputs, look_ahead_mask, dec_padding_mask])

    outputs = tf.keras.layers.Dense(units=vocab_size, name="outputs")(dec_outputs)

    return tf.keras.Model(inputs=[inputs, dec_inputs], outputs=outputs, name=name)

# ------------ 建立 Transformer 模型 ------------ #
num_layers = 2
d_model = 128
num_heads = 8
units = 512
dropout = 0.1

transformer = transformer(
    vocab_size=8500,
    num_layers=num_layers,
    units=units,
    d_model=d_model,
    num_heads=num_heads,
    dropout=dropout)

# 編譯模型
transformer.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# 列印模型摘要
transformer.summary()

# ------------ 準備數據 ------------ #
# 將資料調整為適合 Transformer 輸入的形狀
X_train_trans = np.expand_dims(X_train, axis=1)
y_train_trans = np.expand_dims(y_train, axis=1)

X_test_trans = np.expand_dims(X_test, axis=1)
y_test_trans = np.expand_dims(y_test, axis=1)

# ------------ 訓練模型 ------------ #
history = transformer.fit([X_train_trans, y_train_trans], y_train_trans, epochs=10, batch_size=64, validation_split=0.2)

# 評估模型
loss, accuracy = transformer.evaluate([X_test_trans, y_test_trans], y_test_trans)
print(f'Test Loss: {loss}')
print(f'Test Accuracy: {accuracy}')



# ------------ 使用模型進行預測 ------------ #
y_pred = transformer.predict([X_test_trans, y_test_trans])

# 將預測結果轉換為二進位標籤
y_pred_binary = (y_pred > 0.5).astype(int)

# ------------ 計算準確度 ------------ #
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score

accuracy = accuracy_score(y_test, y_pred_binary)
conf_matrix = confusion_matrix(y_test, y_pred_binary)
roc_auc = roc_auc_score(y_test, y_pred)

print(f'Accuracy: {accuracy}')
print(f'Confusion Matrix:\n{conf_matrix}')
print(f'ROC AUC: {roc_auc}')

# 保存模型
model_path = r"C:\Users\USER\Desktop\Develop\traffic_data\models\models\transformer_model.h5"
transformer.save(model_path)

# 載入模型
loaded_model = tf.keras.models.load_model(model_path)

# 使用載入的模型進行預測
y_pred_loaded = loaded_model.predict([X_test_trans, y_test_trans])