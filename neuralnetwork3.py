import numpy as np
import pandas as pd
import os.path
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

file_path = './data.csv'
num_rows = 0
with open(file_path) as f:
	for line in f:
		num_rows+=1

batch_size = 256

def generate_arrays_from_file(path, batchsize):
	inputs = []
	targets = []
	batchcount = 0
	while True:
		with open(path) as f:
			for line in f:
				arr = line.split(',')
				inputs.append(arr[0:768])
				targets.append(arr[768])
				batchcount += 1
				if batchcount > batchsize:
					x = np.array(inputs, dtype='int')
					y = np.array(targets, dtype='float32')
					yield (x, y)
					inputs = []
					targets = []
					batchcount = 0

checkpoint_path = 'best_model.hdf5'
if os.path.exists(checkpoint_path):
	chess_model = tf.keras.models.load_model(checkpoint_path)
else:
	chess_model = tf.keras.Sequential([
		layers.Dense(2048, activation = 'elu', input_shape=(1,768)),
		layers.Dense(2048, activation = 'elu'),
		layers.Dense(2048, activation = 'elu'),
		layers.Dense(1, activation = 'elu')
	])
	chess_model.compile(
		loss = tf.losses.MeanSquaredError(), 
		optimizer = tf.keras.optimizers.SGD(learning_rate=0.001, momentum=0.7, nesterov=True)
	)


checkpoint = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path, 
                             verbose=1,)

chess_model.fit(generate_arrays_from_file(file_path, batch_size),steps_per_epoch=num_rows/batch_size, 
shuffle=True, epochs=100, callbacks = [checkpoint])

#results = chess_model.evaluate(x=x_test, y=y_test, batch_size=256)
#print(results)

chess_model.save('saved_model')
