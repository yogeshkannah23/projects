import tensorflow as tf
from tensorflow.keras import layers, Model, Input

def conv_block(x, filters):
    x = layers.Conv2D(filters, 3, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.Conv2D(filters, 3, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    return x

def unet_plus_plus(input_shape, num_classes):
    inputs = Input(input_shape)
    filters = [64, 128, 256, 512, 1024]

    # Encoder
    conv0_0 = conv_block(inputs, filters[0])
    pool0 = layers.MaxPooling2D((2, 2))(conv0_0)

    conv1_0 = conv_block(pool0, filters[1])
    pool1 = layers.MaxPooling2D((2, 2))(conv1_0)

    conv2_0 = conv_block(pool1, filters[2])
    pool2 = layers.MaxPooling2D((2, 2))(conv2_0)

    conv3_0 = conv_block(pool2, filters[3])
    pool3 = layers.MaxPooling2D((2, 2))(conv3_0)

    conv4_0 = conv_block(pool3, filters[4])

    # Decoder with nested skip connections
    up0_1 = layers.Conv2DTranspose(filters[0], 2, strides=(2, 2), padding='same')(conv1_0)
    up1_1 = layers.Conv2DTranspose(filters[1], 2, strides=(2, 2), padding='same')(conv2_0)
    up2_1 = layers.Conv2DTranspose(filters[2], 2, strides=(2, 2), padding='same')(conv3_0)
    up3_1 = layers.Conv2DTranspose(filters[3], 2, strides=(2, 2), padding='same')(conv4_0)

    conv0_1 = conv_block(layers.concatenate([conv0_0, up0_1]), filters[0])
    conv1_1 = conv_block(layers.concatenate([conv1_0, up1_1]), filters[1])
    conv2_1 = conv_block(layers.concatenate([conv2_0, up2_1]), filters[2])
    conv3_1 = conv_block(layers.concatenate([conv3_0, up3_1]), filters[3])

    # Further decoder layers (skipping some for brevity)
    # You can add more nested connections similar to this.

    outputs = layers.Conv2D(num_classes, 1, activation='softmax')(conv0_1)

    return Model(inputs, outputs)

input_shape = (256, 256, 3)  # Example input shape
num_classes = 2  # Example number of classes 
model = unet_plus_plus(input_shape, num_classes)
model.summary()


