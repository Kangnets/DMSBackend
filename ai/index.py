import sys
import re
import json
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers

# Preload model and tokenizer
DATA_CONFIGS = 'data_configs.json'
prepro_configs = json.load(open(DATA_CONFIGS, 'r'))
tokenizer = tf.keras.preprocessing.text.Tokenizer()
tokenizer.fit_on_texts(prepro_configs['vocab'])

MAX_LENGTH = 8

class CNNClassifier(tf.keras.Model):
    def __init__(self, **kargs):
        super(CNNClassifier, self).__init__(name=kargs['model_name'])
        self.embedding = layers.Embedding(input_dim=kargs['vocab_size'], output_dim=kargs['embbeding_size'])
        self.conv_list = [layers.Conv1D(filters=kargs['num_filters'], kernel_size=kernel_size, padding='valid',
                                        activation=tf.keras.activations.relu) for kernel_size in [3, 4, 5]]
        self.pooling = layers.GlobalMaxPooling1D()
        self.dropout = layers.Dropout(kargs['dropout_rate'])
        self.fc1 = layers.Dense(units=kargs['hidden_dimension'], activation=tf.keras.activations.relu)
        self.fc2 = layers.Dense(units=kargs['output_dimension'], activation=tf.keras.activations.sigmoid)

    def call(self, x):
        x = self.embedding(x)
        x = self.dropout(x)
        x = tf.concat([self.pooling(conv(x)) for conv in self.conv_list], axis=1)
        x = self.fc1(x)
        x = self.fc2(x)
        return x


# Load the pre-trained model
kargs = {
    'model_name': 'cnn_classifier_kr',
    'vocab_size': prepro_configs['vocab_size'],
    'embbeding_size': 128,
    'num_filters': 100,
    'dropout_rate': 0.5,
    'hidden_dimension': 250,
    'output_dimension': 1,
}
model = CNNClassifier(**kargs)
model.load_weights('../DATA_OUT/cnn_classifier_kr/weights.weights.h5')

# Text preprocessing and sentiment analysis
def analyze_sentiment(sentence):
    sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣\\s ]', '', sentence)
    stopwords = ['은', '는', '이', '가', '하', '아', '것', '들', '의', '있', '되', '수', '보', '주', '등', '한']
    okt = Okt()
    sentence = okt.morphs(sentence, stem=True)
    sentence = [word for word in sentence if not word in stopwords]
    vector = tokenizer.texts_to_sequences([sentence])
    pad_new = pad_sequences(vector, maxlen=MAX_LENGTH)

    prediction = model.predict(pad_new)
    predictions = float(prediction.squeeze(-1))

    return 'positive' if predictions > 0.5 else 'negative'


if __name__ == '__main__':
    input_sentence = sys.argv[1]
    sentiment = analyze_sentiment(input_sentence)
    print(sentiment)
