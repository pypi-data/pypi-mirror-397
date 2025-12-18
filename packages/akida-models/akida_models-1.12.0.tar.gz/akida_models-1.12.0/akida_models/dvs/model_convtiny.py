#!/usr/bin/env python
# ******************************************************************************
# Copyright 2020 Brainchip Holdings Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************
"""
Convtiny model definition for DVS Gesture or DVS Handy classification.
"""

__all__ = ["convtiny_dvs", "convtiny_gesture_pretrained", "convtiny_handy_samsung_pretrained"]

import tensorflow as tf
from tf_keras import Model
from tf_keras.layers import Input, Reshape, Dropout, Activation, Rescaling

from ..layer_blocks import conv_block, separable_conv_block, dense_block
from ..utils import fetch_file, get_params_by_version
from ..model_io import load_model, get_model_path, get_default_bitwidth

# Locally fixed config options
# The number of neurons in the penultimate dense layer
# This layer has binary output spikes, and could be a bottleneck
# if care isn't taken to ensure enough info capacity
NUM_SPIKING_NEURONS = 256


def convtiny_dvs(input_shape=(64, 64, 10), classes=10):
    """Instantiates a CNN for the "IBM DVS Gesture" or "Brainchip dvs_handy" examples.

    Args:
        input_shape (tuple, optional): input shape tuple of the model. Defaults to (64, 64, 10).
        classes (int, optional): number of classes to classify images into. Defaults to 10.

    Returns:
        keras.Model: a Keras convolutional model for DVS Gesture or DVS Handy.
    """
    # Model version management
    fused, post_relu_gap, relu_activation = get_params_by_version()

    img_input = Input(input_shape, name="input", dtype=tf.int8)

    # Dummy rescaling layer to allow int8 inputs
    x = Rescaling(1., name="rescaling")(img_input)

    x = conv_block(x,
                   filters=16,
                   kernel_size=(3, 3),
                   name='conv_01',
                   use_bias=False,
                   add_batchnorm=True,
                   padding='same',
                   pooling='max',
                   pool_size=(2, 2),
                   relu_activation=relu_activation,
                   strides=(1, 1))

    x = conv_block(x,
                   filters=16,
                   kernel_size=(3, 3),
                   name='conv_02',
                   use_bias=False,
                   add_batchnorm=True,
                   padding='same',
                   pooling='max',
                   pool_size=(2, 2),
                   relu_activation=relu_activation,
                   strides=(1, 1))

    x = conv_block(x,
                   filters=32,
                   kernel_size=(3, 3),
                   name='conv_03',
                   use_bias=False,
                   add_batchnorm=True,
                   padding='same',
                   pooling='max',
                   pool_size=(2, 2),
                   relu_activation=relu_activation,
                   strides=(1, 1))

    x = conv_block(x,
                   filters=64,
                   kernel_size=(3, 3),
                   name='conv_04',
                   use_bias=False,
                   add_batchnorm=True,
                   padding='same',
                   pooling='max',
                   pool_size=(2, 2),
                   relu_activation=relu_activation,
                   strides=(1, 1))

    x = conv_block(x,
                   filters=128,
                   kernel_size=(3, 3),
                   name='conv_05',
                   use_bias=False,
                   add_batchnorm=True,
                   padding='same',
                   pooling='global_avg',
                   relu_activation=relu_activation,
                   post_relu_gap=post_relu_gap,
                   strides=(1, 1))

    bm_outshape = (1, 1, 128)

    x = Reshape(bm_outshape, name='reshape_1')(x)
    x = Dropout(1e-3, name='dropout')(x)

    x = separable_conv_block(x,
                             filters=NUM_SPIKING_NEURONS,
                             kernel_size=(3, 3),
                             use_bias=False,
                             padding='same',
                             name='spiking_layer',
                             add_batchnorm=True,
                             pooling=None,
                             relu_activation=relu_activation,
                             fused=fused)

    x = dense_block(x,
                    units=classes,
                    name='dense',
                    add_batchnorm=False,
                    relu_activation=False,
                    use_bias=False)
    act_function = 'softmax' if classes > 1 else 'sigmoid'
    x = Activation(act_function, name=f'act_{act_function}')(x)
    x = Reshape((classes,), name='reshape_2')(x)

    return Model(inputs=img_input, outputs=x, name='dvs_network')


def convtiny_gesture_pretrained(quantized=True, bitwidth=None):
    """ Helper method to retrieve a `convtiny_dvs_gesture` model that was
    trained on IBM DVS Gesture dataset.

    Args:
        quantized (bool, optional): a boolean indicating whether the model should be loaded
            quantized or not. Defaults to True.
        bitwidth (int, optional): the number of bits for quantized model. Defaults to None.

    Returns:
        keras.Model: a Keras Model instance.

    """
    if bitwidth is None:
        bitwidth = get_default_bitwidth()

    if quantized:
        if bitwidth == 4:
            model_name_v1 = 'convtiny_dvs_gesture_iq4_wq4_aq4.h5'
            file_hash_v1 = 'ad1a0a2ee13092921a914f25a6159dcb788540239d10ea96d3ff5fefec359281'
            model_name_v2 = 'convtiny_dvs_gesture_i4_w4_a4.h5'
            file_hash_v2 = '745796fb99ff08aa523a7cda13c1617f40d5366a60ab40991b35083c20c6df16'
        elif bitwidth == 8:
            model_name_v1, file_hash_v1 = None, None
            model_name_v2 = 'convtiny_dvs_gesture_i8_w8_a8.h5'
            file_hash_v2 = '05d07e260ebedf434d3502302bf6b8d86ce7c505b56c9213aa5ef91214b0a286'
        else:
            raise ValueError(f"bitwidth={bitwidth} is not available, use bitwidth=4 or 8 for this"
                             " model.")
    else:
        model_name_v1 = None
        file_hash_v1 = None
        model_name_v2 = 'convtiny_dvs_gesture.h5'
        file_hash_v2 = '4b7f0920c464a4a5613c9d6794efec12c2f32227aac26539999d9948c3c46a50'

    model_path, model_name, file_hash = get_model_path("convtiny", model_name_v1, file_hash_v1,
                                                       model_name_v2, file_hash_v2)
    model_path = fetch_file(model_path,
                            fname=model_name,
                            file_hash=file_hash,
                            cache_subdir='models')
    return load_model(model_path)


def convtiny_handy_samsung_pretrained(quantized=True, bitwidth=None):
    """ Helper method to retrieve a `convtiny_dvs_handy` model that was trained
    on samsung_handy dataset.
    Note that V1 models use different architecture and they are not aligned
    with DVS Gesture model.

    Args:
        quantized (bool, optional): a boolean indicating whether the model should be loaded
                quantized or not. Defaults to True.
        bitwidth (int, optional): the number of bits for quantized model. Defaults to None.

    Returns:
        keras.Model: a Keras Model instance.

    """
    if bitwidth is None:
        bitwidth = get_default_bitwidth()

    if quantized:
        if bitwidth == 4:
            model_name_v1 = 'convtiny_dvs_handy_samsung_iq4_wq4_aq4.h5'
            file_hash_v1 = 'ac5dbf1420fbedc402da4394bb22cf94ff5cff73adb428cca741d6550f663c71'
            model_name_v2 = 'convtiny_dvs_handy_samsung_i4_w4_a4.h5'
            file_hash_v2 = 'd2b1f1dbfe680455dce9e7d3603ebff18552be05c70c0271e0a241650a203599'
        elif bitwidth == 8:
            model_name_v1, file_hash_v1 = None, None
            model_name_v2 = 'convtiny_dvs_handy_samsung_i8_w8_a8.h5'
            file_hash_v2 = '013871b81b5ab83ba0036aeb7ef723276301838b8b4991c4c8686a73af95470c'
        else:
            raise ValueError(f"bitwidth={bitwidth} is not available, use bitwidth=4 or 8 for this"
                             " model.")
    else:
        model_name_v1 = None
        file_hash_v1 = None
        model_name_v2 = 'convtiny_dvs_handy_samsung.h5'
        file_hash_v2 = '122e59b1c36f73cbc9392ebf05bcbb192b2f198dc962c1346989d8830a575a09'

    model_path, model_name, file_hash = get_model_path("convtiny", model_name_v1, file_hash_v1,
                                                       model_name_v2, file_hash_v2)
    model_path = fetch_file(model_path,
                            fname=model_name,
                            file_hash=file_hash,
                            cache_subdir='models')
    return load_model(model_path)
