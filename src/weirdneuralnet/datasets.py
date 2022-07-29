import os
import hashlib, requests, gzip

# import numpy as np
import cupy as np
from numpy import frombuffer, setdiff1d

from .node_utils import binarize


def get_accuracy(model, X, Y):
    prediction_classes = model.predict(X, debinarize=True)
    num_correct = np.where(np.equal(prediction_classes, Y.argmax(axis=1)))[0].shape[0]
    return num_correct, len(prediction_classes)


def get_dataset(path):
    # TODO: add more datasets, or a better way to include more
    # not really sure how best to do this yet
    path = os.path.join(os.path.join(os.path.dirname(__file__), "../.."), path)

    def fetch(url):
        fp = os.path.join(path, hashlib.md5(url.encode("utf-8")).hexdigest())
        if os.path.isfile(fp):
            with open(fp, "rb") as f:
                data = f.read()
        else:
            with open(fp, "wb") as f:
                data = requests.get(url).content
                f.write(data)
        # return np.frombuffer(gzip.decompress(data), dtype=np.uint8).copy()) #numpy version
        return np.array(frombuffer(gzip.decompress(data), dtype=np.uint8).copy())

    X = fetch("http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz")[
        0x10:
    ].reshape((-1, 28, 28))
    Y = fetch("http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz")[8:]
    X_test = fetch("http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz")[
        0x10:
    ].reshape((-1, 28 * 28))
    Y_test = fetch("http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz")[8:]

    # Validation split
    rand = np.arange(60000)
    np.random.shuffle(rand)
    train_no = rand[:50000]

    # val_no=np.setdiff1d(rand,train_no) #numpy version
    val_no = np.array(setdiff1d(np.asnumpy(rand), np.asnumpy(train_no)))

    X_train, X_val = X[train_no, :, :], X[val_no, :, :]
    Y_train, Y_val = Y[train_no], Y[val_no]
    # reshape
    X_train = X_train.reshape((-1, 28 * 28))
    X_val = X_val.reshape((-1, 28 * 28))

    Y_train, Y_val, Y_test = (
        binarize(Y_train, 10),
        binarize(Y_val, 10),
        binarize(Y_test, 10),
    )
    return X_train, Y_train, X_test, Y_test, X_val, Y_val
