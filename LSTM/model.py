#!/usr/bin/env python3
#
from tqdm import trange, tqdm
from dataset import Dataset
import numpy as np
import tensorflow as tf
from tensorflow import keras
import scipy.stats
from tensorflow.keras import layers

DATASET_IN = 6
DATASET_OUT = 6
LOOK_BACK = 5


class Model:
    def __init__(self, path_to_weights=None, training=False):
        self.construct_model(training)
        self.norm_dist = scipy.stats.norm(0, 1)
        if path_to_weights is not None:
            self.model.load_weights(path_to_weights)
        self.reset_model()

    def construct_model(self, training):
        feature_columns = []
        # if training:
        #     batch_size = None
        # else:
        #     batch_size = 1
        batch_size=None
        input_layer = layers.Input(batch_input_shape=(batch_size, None, DATASET_IN))
        output = layers.LSTM(256, dropout=0.3, name="recurrent_1")(input_layer)
        output = layers.Dense(32)(output)
        output = layers.Dense(DATASET_OUT)(output)
        self.model = keras.Model(input_layer, [output])
        self.model.compile(
            loss="mse",
            optimizer=keras.optimizers.Adam(),
            metrics=["mean_absolute_percentage_error"],
        )
        self.model.summary()

    def reset_model(self):
        self.model.reset_states()
        self.predictions = []
        self.history = []
        self.mse = []

    def run_model_init(self, Xs, look_back=5):
        self.reset_model()
        self.predictions = [self.model.predict(np.array([Xs[: look_back - 1]]))[0]]
        # self.history.append(Xs[look_back][-5:])
        # self.mse.append(((self.predictions[-1]-self.history[-1])**2).mean())

        for i in trange(look_back, len(Xs)):
            last_prediction = self.run_model_online(Xs[i])
        return last_prediction

    def run_model_online(self, Xs, look_back=10):
        self.model.reset_states()
        self.history.append(Xs)
        pred = self.model.predict(np.array([self.history[-min(look_back, len(self.history)) :]]))[0]
        pred[3] = max(0,pred[3])
        pred[4] = max(0,pred[3])
        self.predictions.append(
            pred
        )
        self.mse.append(((self.predictions[-2] - self.history[-1]) ** 2).mean())
        self.smooth_dev = smooth(
            (self.mse - np.mean(self.mse)) / np.std(self.mse), min(look_back, len(self.mse))
        )

        return {
            "Latitude": self.predictions[-1][0],
            "Longitude": self.predictions[-1][1],
            "ROT": self.predictions[-1][2],
            "SOG": max(0,self.predictions[-1][3]),
            "COG": max(0,self.predictions[-1][4]),
            "Heading": self.predictions[-1][5],
            "Deviation": self.smooth_dev[-1],
            # "Anomaly_prob": self.anomalies[-1],
        }

    def train_model(
        self, ds: Dataset, train_lim=20, look_back=10, epochs=1, batch_size=256
    ):
        Xs = []
        Ys = []
        print("Preparing data")
        for ship in tqdm(ds.Xs):
            if len(ship) < look_back:
                continue
            for i in range(look_back, len(ship) - 1):
                Xs.append(ship[i - look_back : i])
                Ys.append(ship[i])
        Xs = np.array(Xs)
        Ys = np.array(Ys)
        checkpoint = keras.callbacks.ModelCheckpoint(
            "weights-{val_loss:.2f}.hdf5",
            monitor="val_loss",
            verbose=1,
            save_best_only=True,
        )
        k = self.model.fit(
            Xs,
            Ys,
            batch_size=batch_size,
            callbacks=[checkpoint],
            validation_split=0.33,
            epochs=epochs,
        )

        self.model.save_weights("weights")
        return k
        # t = trange(len(ds.Xs), desc="Starting")
        # for p in t:
        #     if len(ds.Xs[p]) <= LOOK_BACK + 1:
        #         continue
        #     self.model.fit(
        #         np.array([ds.Xs[p][:LOOK_BACK]]),
        #         np.array([ds.Xs[p][LOOK_BACK + 1][-DATASET_OUT:]]),
        #         verbose=0,
        #     )
        #     if train_lim is None:
        #         max_train = len(ds.Xs[p]) - 2
        #     else:
        #         max_train = min(train_lim, len(ds.Xs[p]) - 2)
        #     for i in range(LOOK_BACK + 1, max_train):
        #         k = self.model.fit(
        #             np.array([[ds.Xs[p][i]]]),
        #             np.array([ds.Xs[p][i + 1][-DATASET_OUT:]]),
        #             verbose=0,
        #         )
        #         t.set_description(
        #             "{0:10.2f} {1:20.2f} {2}".format(
        #                 k.history["loss"][-1],
        #                 k.history["mean_absolute_percentage_error"][-1],
        #                 max_train,
        #             )
        #         )

        #     k = self.model.fit(
        #         np.array([[ds.Xs[p][max_train]]]),
        #         np.array([ds.Xs[p][max_train + 1][-DATASET_OUT:]]),
        #         verbose=0,
        #     )
        #     self.model.reset_states()
        # t.set_description("{0:.2f} {1:.2f} {2}".format(k.history["loss"][-1],k.history['mean_absolute_percentage_error'][-1],max_train))
        # return k


def smooth(data, window_width=3):
    cumsum_vec = np.cumsum(np.insert(data, 0, 0))
    ma_vec = (cumsum_vec[window_width:] - cumsum_vec[:-window_width]) / window_width
    return ma_vec
