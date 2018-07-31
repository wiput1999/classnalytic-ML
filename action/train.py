import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from keras.preprocessing import image
from keras.models import Sequential, model_from_json
from keras.layers import Input
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras import utils, optimizers, applications
from collections import OrderedDict

import os

train_data_dir = os.path.abspath("data/labels/train")
test_data_dir = os.path.abspath("data/labels/test")

batch_size = 35

def resnet_model(class_num):
    model = Sequential()
    model.add(applications.resnet50.ResNet50(include_top=False, weights='imagenet', input_tensor=Input(shape=(224, 224, 3))))
    model.add(Flatten())
    model.add(Dense(class_num, activation='softmax'))

    return model

def dataset(img_width=224, img_height=224):
    train_datagen = image.ImageDataGenerator(
                        rescale=1./255,
                        shear_range=0.2,
                        zoom_range=0.3,
                        rotation_range=0.3)

    test_datagen = image.ImageDataGenerator(
                        rescale=1./255,)

    train_generator = train_datagen.flow_from_directory(
        train_data_dir,
        target_size=(img_height, img_width),
        batch_size=batch_size,
        class_mode='categorical')
    
    test_generator = test_datagen.flow_from_directory(
        test_data_dir,
        target_size=(img_height, img_width),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False)
    
    class_dictionary = train_generator.class_indices
    print("[Class dictionary] {}".format(class_dictionary))
    sorted_class_dictionary = OrderedDict(sorted(class_dictionary.items()))
    sorted_class_dictionary = sorted_class_dictionary.values()
    print("[Sorted Class dictionary] {}".format(sorted_class_dictionary))

    return train_generator, test_generator

def train():
    model = resnet_model(2)
    model.summary()
    
    train_generator, test_generator = dataset()

    optimizer = optimizers.Adam()
    model.compile(loss="categorical_crossentropy",
                optimizer=optimizer,
                metrics=['accuracy'])

    nb_epoch = 50

    history = model.fit_generator(
        train_generator,
        steps_per_epoch=189 // batch_size,
        epochs=nb_epoch,
        validation_data=test_generator,
        validation_steps=214 // batch_size)
    # history = model.fit_generator(
    #         train_generator,
    #         samples_per_epoch=187,
    #         nb_epoch=nb_epoch,
    #         validation_data=train_generator,
    #         nb_val_samples=187)
    
    model_json = model.to_json()
    with open("model.json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    print("Saved model to disk")

    model.save_weights("test3.h5")

    # list all data in history
    print(history.history.keys())
    # summarize history for accuracy
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig('accuracy.png')

    # summarize history for loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig('loss.png')


if __name__ == "__main__":
    train()