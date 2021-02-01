#!/usr/bin/env python3
#
from tqdm import trange
from dataset import Dataset
import numpy as np
import tensorflow as tf
from tensorflow import keras
import scipy.stats
from tensorflow.keras import layers

DATASET_IN = 10
DATASET_OUT = 5
LOOK_BACK = 5


class Model:
    def __init__(self, path_to_weights=None):
        self.construct_model()
        self.norm_dist = scipy.stats.norm(0, 1)
        if path_to_weights is not None:
            self.model.load_weights(path_to_weights)
        self.reset_model()
        # self.model.reset_states()
        # self.predictions = np.array([])
        # self.history = np.array([])
        # self.mse = np.array([])
        # self._anomaly_prob = np.array([])
        # self.anomalies = []
        # self.anomaly_prob = []

    def construct_model(self):
        feature_columns = []
        input_layer = layers.Input(batch_input_shape=(1, None, DATASET_IN))
        output = layers.GRU(128, stateful=True, dropout=0.3, name="recurrent_1")(
            input_layer
        )
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
        self.anomalies = [0]
        self.predictions = np.array([])
        self.history = np.array([[]])
        self.mse = np.array([])
        self._anomaly_prob = np.array([])
        self.anomaly_prob = []
        self.prev_val=[]

    def run_model_init(self, Xs, look_back=5):
        self.reset_model()
        self.predictions = self.model.predict(np.array([Xs[: look_back - 1]]))
        # self.history.append(Xs[look_back][-5:])
        # self.mse.append(((self.predictions[-1]-self.history[-1])**2).mean())

        for i in trange(look_back, len(Xs)):
            last_prediction = self.run_model_online(Xs[i])
        return last_prediction

    def run_model_online(self, Xs):
        if len(self.predictions)>0:
            self.predictions = np.append(
            self.predictions, self.model.predict(np.array([[Xs]])), axis=0
        )
        else:
            self.predictions = self.model.predict(np.array([[Xs]]))

        if len(self.mse) > 0:
            self.history = np.append(self.history, [Xs[-5:]], axis=0)
            self.mse = np.append(
                self.mse, ((self.predictions[-2] - Xs[-5:]) ** 2).mean()
            )
        else:
            self.history = np.array([Xs[-5:]])
            if len(self.predictions)>1:
                self.mse = np.array([((self.predictions[-2] - Xs[-5:]) ** 2).mean()])

        if len(self.mse) > 1:
            self.smooth_dev = smooth(
                (self.mse - self.mse.mean()) / self.mse.std(), min(3, len(self.mse))
            )

            self._anomaly_prob = np.append(
                self._anomaly_prob, self.norm_dist.cdf(self.smooth_dev[-1])
            )
        else:
            self.smooth_dev = np.array([0])
            self._anomaly_prob = np.array([0])

        self.anomaly_prob.append(min(self._anomaly_prob[-min(5, len(self._anomaly_prob)):]))
        if len(self.smooth_dev)>5:
            self.anomalies.append(min(smooth(self.smooth_dev>=np.quantile(self.smooth_dev,0.95),5)[-5:]))

        return {
            "Latitude": self.predictions[-1][0],
            "Longitude": self.predictions[-1][1],
            "ROT": self.predictions[-1][2],
            "SOG": self.predictions[-1][3],
            "COG": self.predictions[-1][4],
            "Deviation": self.smooth_dev[-1],
            "Anomaly_prob": self.anomalies[-1]
        }

    def train_model(self, ds: Dataset, train_lim=20):
        t = trange(len(ds.Xs), desc="Starting")
        for p in t:
            if len(ds.Xs[p]) <= LOOK_BACK + 1:
                continue
            self.model.fit(
                np.array([ds.Xs[p][:LOOK_BACK]]),
                np.array([ds.Xs[p][LOOK_BACK + 1][-DATASET_OUT:]]),
                verbose=0,
            )
            if train_lim is None:
                max_train = len(ds.Xs[p]) - 2
            else:
                max_train = min(train_lim, len(ds.Xs[p]) - 2)
            for i in range(LOOK_BACK + 1, max_train):
                k = self.model.fit(
                    np.array([[ds.Xs[p][i]]]),
                    np.array([ds.Xs[p][i + 1][-DATASET_OUT:]]),
                    verbose=0,
                )
                t.set_description(
                    "{0:10.2f} {1:20.2f} {2}".format(
                        k.history["loss"][-1],
                        k.history["mean_absolute_percentage_error"][-1],
                        max_train,
                    )
                )

            k = self.model.fit(
                np.array([[ds.Xs[p][max_train]]]),
                np.array([ds.Xs[p][max_train + 1][-DATASET_OUT:]]),
                verbose=0,
            )
            self.model.reset_states()
            # t.set_description("{0:.2f} {1:.2f} {2}".format(k.history["loss"][-1],k.history['mean_absolute_percentage_error'][-1],max_train))
            # return k

        self.model.save_weights("weights")
        return k


def smooth(data, window_width=3):
    cumsum_vec = np.cumsum(np.insert(data, 0, 0))
    ma_vec = (cumsum_vec[window_width:] - cumsum_vec[:-window_width]) / window_width
    return ma_vec
