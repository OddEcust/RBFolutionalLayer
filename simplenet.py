import tensorflow as tf
import numpy as np

# Data Retrieval & mean/std preprocess
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')

mean = np.mean(x_train, axis=(0, 1, 2, 3))
std = np.std(x_train, axis=(0, 1, 2, 3))
x_train = (x_train - mean) / (std + 1e-7)
x_test = (x_test - mean) / (std + 1e-7)

num_classes = 10
y_train = tf.keras.utils.to_categorical(y_train, num_classes)
y_test = tf.keras.utils.to_categorical(y_test, num_classes)

# Data augmentation
datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True
)
datagen.fit(x_train)


# Define Model architecture
def create_model(s=2, weight_decay=1e-2, act="relu"):
    model = tf.keras.models.Sequential()

    # Block 1
    model.add(tf.keras.layers.Conv2D(64, (3, 3), padding='same', kernel_initializer=tf.keras.initializers.glorot_normal(), input_shape=x_train.shape[1:]))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Activation(act))
    model.add(tf.keras.layers.Dropout(0.2))

    # Block 2
    model.add(tf.keras.layers.Conv2D(128, (3, 3), padding='same', kernel_initializer=tf.keras.initializers.glorot_normal()))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Activation(act))
    model.add(tf.keras.layers.Dropout(0.2))

    # Block 3
    model.add(tf.keras.layers.Conv2D(128, (3, 3), padding='same', kernel_initializer=tf.keras.initializers.RandomNormal(stddev=0.01)))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Activation(act))
    model.add(tf.keras.layers.Dropout(0.2))

    # Block 4
    model.add(tf.keras.layers.Conv2D(128, (3, 3), padding='same', kernel_initializer=tf.keras.initializers.RandomNormal(stddev=0.01)))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Activation(act))
    # First Maxpooling
    model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=s))
    model.add(tf.keras.layers.Dropout(0.2))

    # Block 5
    model.add(tf.keras.layers.Conv2D(128, (3, 3), padding='same', kernel_initializer=tf.keras.initializers.RandomNormal(stddev=0.01)))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Activation(act))
    model.add(tf.keras.layers.Dropout(0.2))

    # Block 6
    model.add(tf.keras.layers.Conv2D(128, (3, 3), padding='same', kernel_initializer=tf.keras.initializers.glorot_normal()))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Activation(act))
    model.add(tf.keras.layers.Dropout(0.2))

    # Block 7
    model.add(tf.keras.layers.Conv2D(256, (3, 3), padding='same', kernel_initializer=tf.keras.initializers.glorot_normal()))
    # Second Maxpooling
    model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=s))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Activation(act))
    model.add(tf.keras.layers.Dropout(0.2))

    # Block 8
    model.add(tf.keras.layers.Conv2D(256, (3, 3), padding='same', kernel_initializer=tf.keras.initializers.glorot_normal()))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Activation(act))
    model.add(tf.keras.layers.Dropout(0.2))

    # Block 9
    model.add(tf.keras.layers.Conv2D(256, (3, 3), padding='same', kernel_initializer=tf.keras.initializers.glorot_normal()))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Activation(act))
    model.add(tf.keras.layers.Dropout(0.2))
    # Third Maxpooling
    model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=s))

    # Block 10
    model.add(tf.keras.layers.Conv2D(512, (3, 3), padding='same', kernel_initializer=tf.keras.initializers.glorot_normal()))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Activation(act))
    model.add(tf.keras.layers.Dropout(0.2))

    # Block 11
    model.add(tf.keras.layers.Conv2D(2048, (1, 1), padding='same', kernel_initializer=tf.keras.initializers.glorot_normal()))
    model.add(tf.keras.layers.Activation(act))
    model.add(tf.keras.layers.Dropout(0.2))

    # Block 12
    model.add(tf.keras.layers.Conv2D(256, (1, 1), padding='same', kernel_initializer=tf.keras.initializers.glorot_normal()))
    model.add(tf.keras.layers.Activation(act))
    # Fourth Maxpooling
    model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=s))
    model.add(tf.keras.layers.Dropout(0.2))

    # Block 13
    model.add(tf.keras.layers.Conv2D(256, (3, 3), padding='same', kernel_initializer=tf.keras.initializers.glorot_normal()))
    model.add(tf.keras.layers.Activation(act))
    # Fifth Maxpooling
    model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=s))

    # Final Classifier
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(num_classes, name='logits'))
    model.add(tf.keras.layers.Activation(tf.nn.softmax))

    return model


if __name__ == "__main__":
    # Prepare for training
    model = create_model(act="relu")
    batch_size = 128
    epochs = 25
    train = {}

    # First training for 50 epochs - (0-50)
    opt_adm = tf.keras.optimizers.Adadelta()
    model.compile(loss='categorical_crossentropy', optimizer=opt_adm, metrics=['accuracy'])
    train["part_1"] = model.fit_generator(datagen.flow(x_train, y_train, batch_size=batch_size),
                                          steps_per_epoch=x_train.shape[0] // batch_size, epochs=epochs,
                                          verbose=1, validation_data=(x_test, y_test))
    model.save("simplenet_generic_first.h5")
    print(train["part_1"].history)

    # Training for 25 epochs more - (50-75)
    opt_adm = tf.keras.optimizers.Adadelta(lr=0.7, rho=0.9)
    model.compile(loss='categorical_crossentropy', optimizer=opt_adm, metrics=['accuracy'])
    train["part_2"] = model.fit_generator(datagen.flow(x_train, y_train, batch_size=batch_size),
                                          steps_per_epoch=x_train.shape[0] // batch_size, epochs=epochs,
                                          verbose=1, validation_data=(x_test, y_test))
    model.save("simplenet_generic_second.h5")
    print(train["part_2"].history)

    # Training for 25 epochs more - (75-100)
    opt_adm = tf.keras.optimizers.Adadelta(lr=0.5, rho=0.85)
    model.compile(loss='categorical_crossentropy', optimizer=opt_adm, metrics=['accuracy'])
    train["part_3"] = model.fit_generator(datagen.flow(x_train, y_train, batch_size=batch_size),
                                          steps_per_epoch=x_train.shape[0] // batch_size, epochs=epochs,
                                          verbose=1, validation_data=(x_test, y_test))
    model.save("simplenet_generic_third.h5")
    print(train["part_3"].history)

    # Training for 25 epochs more  - (100-125)
    opt_adm = tf.keras.optimizers.Adadelta(lr=0.3, rho=0.75)
    model.compile(loss='categorical_crossentropy', optimizer=opt_adm, metrics=['accuracy'])
    train["part_4"] = model.fit_generator(datagen.flow(x_train, y_train, batch_size=batch_size),
                                          steps_per_epoch=x_train.shape[0] // batch_size, epochs=epochs,
                                          verbose=1, validation_data=(x_test, y_test))
    model.save("simplenet_generic_fourth.h5")
    print(train["part_4"].history)

    print("\n \n Final Logs: ", train)