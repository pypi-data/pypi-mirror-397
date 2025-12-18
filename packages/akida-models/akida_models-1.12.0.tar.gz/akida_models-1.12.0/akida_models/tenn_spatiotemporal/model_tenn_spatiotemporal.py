#!/usr/bin/env python
# ******************************************************************************
# Copyright 2023 Brainchip Holdings Ltd.
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
TENN spatiotemporal architecture definition.
"""

__all__ = ['tenn_spatiotemporal_dvs128', 'tenn_spatiotemporal_dvs128_pretrained',
           'tenn_spatiotemporal_eye',  'tenn_spatiotemporal_eye_pretrained',
           'tenn_spatiotemporal_jester', 'tenn_spatiotemporal_jester_pretrained']

import tensorflow as tf
from tf_keras.models import Model
from tf_keras.layers import Input, AveragePooling3D, Dense, ReLU, Rescaling

from ..utils import fetch_file
from ..model_io import load_model, get_model_path
from ..layer_blocks import spatiotemporal_block, conv3d_block


def tenn_spatiotemporal_dvs128(input_length=15, input_shape=(128, 128, 2), num_classes=10):
    """ Instantiates a TENN spatiotemporal DVS128 architecture.

    Args:
        input_length (int, optional): the input length. Defaults to 15.
        input_shape (tuple, optional): the input shape. Defaults to (128, 128, 2).
        num_classes (int, optional): number of classes. Defaults to 10.

    Returns:
        keras.Model: a TENN spatiotemporal model for DVS128
    """
    # architecture parameters
    channels = [8, 8, 16, 32, 48, 64, 80, 96, 112, 128, 256]
    t_dws = [False, False, True, True, True]
    s_dws = [False, False, True, True, True]
    t_kernel_size = 5

    input_shape = (input_length,) + input_shape
    inputs = Input(shape=input_shape, name='input', dtype=tf.int8)

    # Dummy rescaling layer to allow int8 inputs
    x = Rescaling(1., name="rescaling")(inputs)

    x = conv3d_block(x, channels[0], (1, 3, 3), add_batchnorm=True,
                     relu_activation='ReLU', name="input_conv", strides=(1, 2, 2),
                     use_bias=False, padding='same')

    for index, (i_chan, m_chan, o_chan, temp_dw, spa_dw) in \
            enumerate(zip(channels[0::2], channels[1::2], channels[2::2], t_dws, s_dws)):
        x = spatiotemporal_block(x, i_chan, m_chan, o_chan, t_kernel_size, temp_dw, spa_dw, index)

    # apply GAP over the spatial dimensions but not the temporal dimension
    x = AveragePooling3D(pool_size=(1, x.shape[2], x.shape[3]), name='gap')(x)
    x = Dense(256)(x)
    x = ReLU()(x)
    x = Dense(num_classes)(x)

    return Model(inputs, x, name="pleiades_st_dvs128")


def tenn_spatiotemporal_dvs128_pretrained(quantized=True):
    """
    Helper method to retrieve a `tenn_spatiotemporal_dvs128` model that was trained on DVS128
    dataset.

    Args:
        quantized (bool, optional): a boolean indicating whether the model should be loaded
            quantized or not. Defaults to True.

    Returns:
        keras.Model: a Keras Model instance.

    """
    if quantized:
        model_name_v2 = 'tenn_spatiotemporal_dvs128_buffer_i8_w8_a8.h5'
        file_hash_v2 = '76cf8c739f13910849370680cdbd88ccd3441cd84cdeceb4180d9ce95739d2d7'
    else:
        model_name_v2 = 'tenn_spatiotemporal_dvs128.h5'
        file_hash_v2 = '470ef9c5cf558e3851b22f67c7fbf10d9f0ebf590cd650ad1e993308a2784cc3'

    model_path, model_name, file_hash = get_model_path(
        "tenn_spatiotemporal", model_name_v2=model_name_v2, file_hash_v2=file_hash_v2)
    model_path = fetch_file(model_path, fname=model_name, file_hash=file_hash,
                            cache_subdir='models')
    return load_model(model_path)


def tenn_spatiotemporal_eye(input_length=50, input_shape=(80, 106, 2), input_scaling=(127, 0),
                            reg_factor=None):
    """ Instantiates a TENN spatiotemporal Eye Tracking architecture.

    Args:
        input_length (int, optional): the input length. Defaults to 50.
        input_shape (tuple, optional): the input shape. Defaults to (80, 106, 2).
        input_scaling (None or tuple, optional): scale factor set to the max value of a 8-bits
            unsigned inputs and offset set to 0. Note that following Akida convention, the scale
            factor is a number used as a divisor. If None, no Rescaling layer is added.
            Defaults to (255, 0).
        reg_factor (float, optional): the L1-regularization factor of the ActivityRegularization
            layers that are added after the ReLU layers if reg_factor is not None.
            Defaults to None.

    Returns:
        keras.Model: a TENN spatiotemporal model for Eye Tracking.
    """
    # architecture parameters
    channels = [8, 16, 32, 48, 64, 80, 96, 112, 128, 256]
    t_dws = [False, False, False, True, True]
    s_dws = [False, False, False, True, True]
    t_kernel_size = 5

    in_channels = input_shape[-1]
    channels = [in_channels] + channels

    input_shape = (input_length,) + input_shape
    inputs = Input(shape=input_shape, name='input', dtype=tf.int8)

    # Use default input scaling (1, 0) if not provided
    scale, offset = (1, 0) if input_scaling is None else input_scaling
    x = Rescaling(1. / scale, offset, name="rescaling")(inputs)

    for index, (i_chan, m_chan, o_chan, temp_dw, spa_dw) in \
            enumerate(zip(channels[0::2], channels[1::2], channels[2::2], t_dws, s_dws)):
        x = spatiotemporal_block(x, i_chan, m_chan, o_chan, t_kernel_size, temp_dw,
                                 spa_dw, index, temporal_first=False, reg_factor=reg_factor)

    # Head convolutions
    x = conv3d_block(
        x, channels[-1],
        (t_kernel_size, 1, 1),
        add_batchnorm=True, relu_activation='ReLU', strides=(1, 1, 1),
        padding='same', groups=channels[-1],
        use_bias=False, name=f'HEAD_convt_dw_{index}', reg_factor=reg_factor)
    x = conv3d_block(x, channels[-1], (1, 1, 1), add_batchnorm=True,
                     relu_activation='ReLU', use_bias=False, name=f'HEAD_convt_pw_{index}',
                     reg_factor=reg_factor)

    x = conv3d_block(x, channels[-1], (1, 3, 3), groups=channels[-1], strides=(1, 1, 1),
                     padding='same', use_bias=False, add_batchnorm=False, relu_activation='ReLU',
                     name=f'HEAD_convs_dw_{index}', reg_factor=reg_factor)
    x = conv3d_block(x, 3, (1, 1, 1), strides=(1, 1, 1), use_bias=False,
                     add_batchnorm=False, relu_activation=False, name=f'HEAD_convs_pw_{index}',
                     reg_factor=reg_factor)

    return Model(inputs, x, name="AIS2024_eyetracking")


def tenn_spatiotemporal_eye_pretrained(quantized=True):
    """
    Helper method to retrieve a `tenn_spatiotemporal_eye` model that was trained on Event-based Eye
    Tracking AI for Streaming CVPR 2024 Challenge dataset.

    Args:
        quantized (bool, optional): a boolean indicating whether the model should be loaded
            quantized or not. Defaults to True.

    Returns:
        keras.Model: a Keras Model instance.

    """
    if quantized:
        model_name_v2 = 'tenn_spatiotemporal_eye_buffer_i8_w8_a8.h5'
        file_hash_v2 = '2c699a16e4fe1a4bac210e384e7e2075db584c30c62c196c4e6ee4c00f037902'
    else:
        model_name_v2 = 'tenn_spatiotemporal_eye.h5'
        file_hash_v2 = '47845ee6cf2457fa40c1e86395c33f7f4fc590444815f9870057d79d050114e5'

    model_path, model_name, file_hash = get_model_path(
        "tenn_spatiotemporal", model_name_v2=model_name_v2, file_hash_v2=file_hash_v2)
    model_path = fetch_file(model_path, fname=model_name, file_hash=file_hash,
                            cache_subdir='models')
    return load_model(model_path)


def tenn_spatiotemporal_jester(input_shape=(16, 100, 100, 3), n_classes=27):
    """ Instantiates a TENN spatiotemporal Jester architecture.

    Args:
        input_shape (tuple, optional): the input shape. Defaults to (16, 100, 100, 3).
        n_classes (int, optional): number of output features. Defaults to 27.

    Returns:
        keras.Model: a spatiotemporal model relying on TENNS convolutions.
    """
    # architecture parameters
    channels = [8, 20, 40, 80, 120, 160, 200, 240, 280, 320, 640]
    t_dws = [False, False, False, True, True]
    s_dws = [False, False, False, True, True]
    t_kernel_size = 5

    inputs = Input(shape=input_shape, name='input', dtype=tf.uint8)

    # This model trains better without rescaling. A dummy layer is added to allow uint8 inputs.
    x = Rescaling(1., name="rescaling")(inputs)

    x = conv3d_block(x, channels[0], (1, 3, 3), add_batchnorm=True,
                     relu_activation='ReLU', name="input_conv", strides=(1, 2, 2),
                     use_bias=False, padding='same', reg_factor=1e-8, normalize_reg=True)

    for layer_index, (i_chan, m_chan, o_chan, temp_dw, spa_dw) in \
            enumerate(zip(channels[0::2], channels[1::2], channels[2::2], t_dws, s_dws)):
        index = f"{layer_index}_0"
        x = spatiotemporal_block(x, i_chan, m_chan, o_chan, t_kernel_size, temp_dw, spa_dw, index,
                                 reg_factor=1e-8, normalize_reg=True)

    # apply GAP over the spatial dimensions but not the temporal dimension
    x = AveragePooling3D(pool_size=(1, x.shape[2], x.shape[3]), name='gap')(x)
    x = Dense(channels[-1])(x)
    x = ReLU()(x)
    x = Dense(n_classes)(x)

    return Model(inputs, x, name="jester_video")


def tenn_spatiotemporal_jester_pretrained(quantized=True):
    """
    Helper method to retrieve a `tenn_spatiotemporal_jester` model that was trained on Jester
    dataset.

    Args:
        quantized (bool, optional): a boolean indicating whether the model should be loaded
            quantized or not. Defaults to True.

    Returns:
        keras.Model: a Keras Model instance.

    """
    if quantized:
        model_name_v2 = 'tenn_spatiotemporal_jester_buffer_i8_w8_a8.h5'
        file_hash_v2 = '388f0e312499190ed2cc839fb4c4e6c791e54e5ee4d35736f33fc36acae24015'
    else:
        model_name_v2 = 'tenn_spatiotemporal_jester.h5'
        file_hash_v2 = 'fca52a23152f7c56be1f0db59844a5babb443aaf55babed7669df35b516b8204'

    model_path, model_name, file_hash = get_model_path(
        "tenn_spatiotemporal", model_name_v2=model_name_v2, file_hash_v2=file_hash_v2)
    model_path = fetch_file(model_path, fname=model_name, file_hash=file_hash,
                            cache_subdir='models')
    return load_model(model_path)
