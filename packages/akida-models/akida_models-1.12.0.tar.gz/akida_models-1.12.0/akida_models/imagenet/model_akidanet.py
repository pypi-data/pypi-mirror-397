#!/usr/bin/env python
# ******************************************************************************
# Copyright 2021 Brainchip Holdings Ltd.
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
AkidaNet model definition for ImageNet classification.

AkidaNet is an NSoC optimized model inspired from VGG and MobileNet V1
architectures. It can be used for multiple use cases through transfer learning.

"""

__all__ = ["akidanet_imagenet", "akidanet_imagenet_pretrained",
           "akidanet_faceidentification_pretrained", "akidanet_plantvillage_pretrained",
           "akidanet_vww_pretrained"]

import tensorflow as tf
from tf_keras import Model, regularizers
from tf_keras.layers import Input, Dropout, Rescaling

from .imagenet_utils import obtain_input_shape
from ..layer_blocks import conv_block, separable_conv_block, dense_block
from ..utils import fetch_file, get_params_by_version
from ..model_io import load_model, get_model_path, get_default_bitwidth


def akidanet_imagenet(input_shape=None,
                      alpha=1.0,
                      include_top=True,
                      pooling=None,
                      classes=1000,
                      input_scaling=(128, -1)):
    """Instantiates the AkidaNet architecture.

    Note: input preprocessing is included as part of the model (as a Rescaling layer). This model
    expects inputs to be float tensors of pixels with values in the [0, 255] range.

    Args:
        input_shape (tuple, optional): shape tuple. Defaults to None.
        alpha (float, optional): controls the width of the model.
            Defaults to 1.0.

            * If `alpha` < 1.0, proportionally decreases the number of filters
              in each layer.
            * If `alpha` > 1.0, proportionally increases the number of filters
              in each layer.
            * If `alpha` = 1, default number of filters from the paper are used
              at each layer.
        include_top (bool, optional): whether to include the fully-connected
            layer at the top of the model. Defaults to True.
        pooling (str, optional): optional pooling mode for feature extraction
            when `include_top` is `False`.
            Defaults to None.

            * `None` means that the output of the model will be the 4D tensor
              output of the last convolutional block.
            * `avg` means that global average pooling will be applied to the
              output of the last convolutional block, and thus the output of the
              model will be a 2D tensor.
        classes (int, optional): optional number of classes to classify images
            into, only to be specified if `include_top` is `True`. Defaults to 1000.
        input_scaling (tuple, optional): scale factor and offset to apply to
            inputs. Defaults to (128, -1). Note that following Akida convention,
            the scale factor is an integer used as a divisor.

    Returns:
        keras.Model: a Keras model for AkidaNet/ImageNet.

    Raises:
        ValueError: in case of invalid input shape.
    """
    # Define weight regularization, will apply to the convolutional layers and
    # to all pointwise weights of separable convolutional layers.
    weight_regularizer = regularizers.l2(4e-5)

    # Model version management
    fused, post_relu_gap, relu_activation = get_params_by_version(relu_v2='ReLU7.5')

    # Determine proper input shape and default size.
    if input_shape is None:
        default_size = 224
    else:
        rows = input_shape[0]
        cols = input_shape[1]

        if rows == cols and rows in [128, 160, 192, 224]:
            default_size = rows
        else:
            default_size = 224

    input_shape = obtain_input_shape(input_shape,
                                     default_size=default_size,
                                     min_size=32,
                                     include_top=include_top)

    img_input = Input(shape=input_shape, name="input", dtype=tf.uint8)

    # Use default input scaling (1, 0) if not provided
    scale, offset = (1, 0) if input_scaling is None else input_scaling
    x = Rescaling(1. / scale, offset, name="rescaling")(img_input)

    x = conv_block(x,
                   filters=int(32 * alpha),
                   name='conv_0',
                   kernel_size=(3, 3),
                   padding='same',
                   use_bias=False,
                   strides=2,
                   add_batchnorm=True,
                   relu_activation=relu_activation,
                   kernel_regularizer=weight_regularizer)

    x = conv_block(x,
                   filters=int(64 * alpha),
                   name='conv_1',
                   kernel_size=(3, 3),
                   padding='same',
                   use_bias=False,
                   add_batchnorm=True,
                   relu_activation=relu_activation,
                   kernel_regularizer=weight_regularizer)

    x = conv_block(x,
                   filters=int(128 * alpha),
                   name='conv_2',
                   kernel_size=(3, 3),
                   padding='same',
                   strides=2,
                   use_bias=False,
                   add_batchnorm=True,
                   relu_activation=relu_activation,
                   kernel_regularizer=weight_regularizer)

    x = conv_block(x,
                   filters=int(128 * alpha),
                   name='conv_3',
                   kernel_size=(3, 3),
                   padding='same',
                   use_bias=False,
                   add_batchnorm=True,
                   relu_activation=relu_activation,
                   kernel_regularizer=weight_regularizer)

    x = separable_conv_block(x,
                             filters=int(256 * alpha),
                             name='separable_4',
                             kernel_size=(3, 3),
                             padding='same',
                             strides=2,
                             use_bias=False,
                             add_batchnorm=True,
                             relu_activation=relu_activation,
                             fused=fused,
                             pointwise_regularizer=weight_regularizer)

    x = separable_conv_block(x,
                             filters=int(256 * alpha),
                             name='separable_5',
                             kernel_size=(3, 3),
                             padding='same',
                             use_bias=False,
                             add_batchnorm=True,
                             relu_activation=relu_activation,
                             fused=fused,
                             pointwise_regularizer=weight_regularizer)

    x = separable_conv_block(x,
                             filters=int(512 * alpha),
                             name='separable_6',
                             kernel_size=(3, 3),
                             padding='same',
                             strides=2,
                             use_bias=False,
                             add_batchnorm=True,
                             relu_activation=relu_activation,
                             fused=fused,
                             pointwise_regularizer=weight_regularizer)

    x = separable_conv_block(x,
                             filters=int(512 * alpha),
                             name='separable_7',
                             kernel_size=(3, 3),
                             padding='same',
                             use_bias=False,
                             add_batchnorm=True,
                             relu_activation=relu_activation,
                             fused=fused,
                             pointwise_regularizer=weight_regularizer)

    x = separable_conv_block(x,
                             filters=int(512 * alpha),
                             name='separable_8',
                             kernel_size=(3, 3),
                             padding='same',
                             use_bias=False,
                             add_batchnorm=True,
                             relu_activation=relu_activation,
                             fused=fused,
                             pointwise_regularizer=weight_regularizer)

    x = separable_conv_block(x,
                             filters=int(512 * alpha),
                             name='separable_9',
                             kernel_size=(3, 3),
                             padding='same',
                             use_bias=False,
                             add_batchnorm=True,
                             relu_activation=relu_activation,
                             fused=fused,
                             pointwise_regularizer=weight_regularizer)

    x = separable_conv_block(x,
                             filters=int(512 * alpha),
                             name='separable_10',
                             kernel_size=(3, 3),
                             padding='same',
                             use_bias=False,
                             add_batchnorm=True,
                             relu_activation=relu_activation,
                             fused=fused,
                             pointwise_regularizer=weight_regularizer)

    x = separable_conv_block(x,
                             filters=int(512 * alpha),
                             name='separable_11',
                             kernel_size=(3, 3),
                             padding='same',
                             use_bias=False,
                             add_batchnorm=True,
                             relu_activation=relu_activation,
                             fused=fused,
                             pointwise_regularizer=weight_regularizer)

    x = separable_conv_block(x,
                             filters=int(1024 * alpha),
                             name='separable_12',
                             kernel_size=(3, 3),
                             padding='same',
                             strides=2,
                             use_bias=False,
                             add_batchnorm=True,
                             relu_activation=relu_activation,
                             fused=fused,
                             pointwise_regularizer=weight_regularizer)

    # Last separable layer with global pooling
    layer_pooling = 'global_avg' if include_top or pooling == 'avg' else None
    x = separable_conv_block(x,
                             filters=int(1024 * alpha),
                             name='separable_13',
                             kernel_size=(3, 3),
                             padding='same',
                             pooling=layer_pooling,
                             use_bias=False,
                             add_batchnorm=True,
                             relu_activation=relu_activation,
                             fused=fused,
                             post_relu_gap=post_relu_gap,
                             pointwise_regularizer=weight_regularizer)

    if include_top:
        x = Dropout(1e-3, name='dropout')(x)
        x = dense_block(x,
                        classes,
                        name='classifier',
                        add_batchnorm=False,
                        relu_activation=False,
                        kernel_regularizer=weight_regularizer)

    # Create model.
    return Model(img_input, x, name='akidanet_%0.2f_%s_%s' % (alpha, input_shape[0], classes))


def akidanet_imagenet_pretrained(alpha=1.0, quantized=True, bitwidth=None):
    """
    Helper method to retrieve an `akidanet_imagenet` model that was trained on
    ImageNet dataset.

    Args:
        alpha (float, optional): width of the model, allowed values in [0.25,
            0.5, 1]. Defaults to 1.0.
        quantized (bool, optional): a boolean indicating whether the model should be loaded
            quantized or not. Defaults to True.
        bitwidth (int, optional): the number of bits for quantized model. Defaults to None.

    Returns:
        keras.Model: a Keras Model instance.

    """
    if bitwidth is None:
        bitwidth = get_default_bitwidth()

    if quantized and bitwidth not in [4, 8]:
        raise ValueError(f"bitwidth={bitwidth} is not available, use bitwidth=4 or 8 for this"
                         " model.")
    if alpha == 1.0:
        if quantized:
            if bitwidth == 4:
                model_name_v1 = 'akidanet_imagenet_224_iq8_wq4_aq4.h5'
                file_hash_v1 = '359e0ff05abbb26fe215830ca467ef40761767c0d77f8c743c6d6e4fffa7a925'
                model_name_v2 = 'akidanet_imagenet_224_alpha_1_i8_w4_a4.h5'
                file_hash_v2 = '68c50944fc5b2435879e9b524d479cbda81c0c790a37631796f8eaee7f4f478f'
            elif bitwidth == 8:
                model_name_v1, file_hash_v1 = None, None
                model_name_v2 = 'akidanet_imagenet_224_alpha_1_i8_w8_a8.h5'
                file_hash_v2 = '221c9878287036d77f063c075a184c22c9dc2d3fd1b62842147967308e8e6aa9'
        else:
            model_name_v1 = 'akidanet_imagenet_224.h5'
            file_hash_v1 = '9208233d21c3251777b1f700b7c2c51491590133f97f81f04348ab131679b00f'
            model_name_v2 = 'akidanet_imagenet_224_alpha_1.h5'
            file_hash_v2 = '70203a3ee154f3b20c4d14a2ded97a4100e811b5b280141f1166c7ca9c0663af'
    elif alpha == 0.5:
        if quantized:
            if bitwidth == 4:
                model_name_v1 = 'akidanet_imagenet_224_alpha_50_iq8_wq4_aq4.h5'
                file_hash_v1 = '1d9493115d43625f2644f8265f71b8487c4019047fc331e892a233a3d6520371'
                model_name_v2 = 'akidanet_imagenet_224_alpha_0.5_i8_w4_a4.h5'
                file_hash_v2 = '618382de99ccff3f3426b390267dd13eb5bbb94f51d50011a8820cf17ada0169'
            elif bitwidth == 8:
                model_name_v1, file_hash_v1 = None, None
                model_name_v2 = 'akidanet_imagenet_224_alpha_0.5_i8_w8_a8.h5'
                file_hash_v2 = '8f2e8b9aedf190fc4132fc457e367b9d25de30af53702a60e6a09fcb959098f9'
        else:
            model_name_v1 = 'akidanet_imagenet_224_alpha_50.h5'
            file_hash_v1 = '61f2883a6b798f922a5c0411296219a85f25581d7571f65546557b46066f058f'
            model_name_v2 = 'akidanet_imagenet_224_alpha_0.5.h5'
            file_hash_v2 = 'd818dec7c924757de2e6970b996da9c807ccdf9a9044262091ce526678c0640c'
    elif alpha == 0.25:
        if quantized:
            if bitwidth == 4:
                model_name_v1 = 'akidanet_imagenet_224_alpha_25_iq8_wq4_aq4.h5'
                file_hash_v1 = '9146d6228d859d8b8db1c1b7a795471096e5a49ee4ff5656eabc6be749d42f5e'
                model_name_v2 = 'akidanet_imagenet_224_alpha_0.25_i8_w4_a4.h5'
                file_hash_v2 = 'af06ce420f3d38b209a829fea54fc68a1819e2cd54f529680bfebdbfaa535a92'
            elif bitwidth == 8:
                model_name_v1, file_hash_v1 = None, None
                model_name_v2 = 'akidanet_imagenet_224_alpha_0.25_i8_w8_a8.h5'
                file_hash_v2 = '1afc73e04db6a1110e61e3ceba84e278840c7af7d3bea406067930915e2b3249'
        else:
            model_name_v1 = 'akidanet_imagenet_224_alpha_25.h5'
            file_hash_v1 = '23d96a1c73397a5c2060808f3843d99fa3cd96b5b1af36e03b0d039be393c001'
            model_name_v2 = 'akidanet_imagenet_224_alpha_0.25.h5'
            file_hash_v2 = 'f7da292a106861cc1356511c3f9256d8f2edd979b00ae592bdf30aff8701e128'
    else:
        raise ValueError(
            f"Requested model with alpha={alpha} is not available.")

    model_path, model_name, file_hash = get_model_path("akidanet", model_name_v1, file_hash_v1,
                                                       model_name_v2, file_hash_v2)
    model_path = fetch_file(model_path,
                            fname=model_name,
                            file_hash=file_hash,
                            cache_subdir='models')
    return load_model(model_path)


def akidanet_faceidentification_pretrained(quantized=True, bitwidth=None):
    """
    Helper method to retrieve an `akidanet_imagenet` model that was trained on
    CASIA Webface dataset and that performs face identification.

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
            model_name_v1 = 'akidanet_faceidentification_iq8_wq4_aq4.h5'
            file_hash_v1 = 'b287f86155c51dc73053f7e5f3e58be1beb4a35d543dd817a63a782ffaf5bff1'
            model_name_v2 = 'akidanet_faceidentification_i8_w4_a4.h5'
            file_hash_v2 = 'f17b00de7a849a5b5336ff49f22e0185c583f0c044d3b80e2f8fc778b0e5c702'
        elif bitwidth == 8:
            model_name_v1, file_hash_v1 = None, None
            model_name_v2 = 'akidanet_faceidentification_i8_w8_a8.h5'
            file_hash_v2 = 'cd0b3a1f687a018fbf057e369e4918c589f8dcb3e3236aeb609bab73201b1af0'
        else:
            raise ValueError(f"bitwidth={bitwidth} is not available, use bitwidth=4 or 8 for this"
                             " model.")
    else:
        model_name_v1 = 'akidanet_faceidentification.h5'
        file_hash_v1 = '998b6cdce5adbdb0b7c3e9f8eb1011c3582e05f0c159e473d226a9a94c4309a1'
        model_name_v2 = 'akidanet_faceidentification.h5'
        file_hash_v2 = 'dcb5b65e3fc1de39d5ec84166901631f5f29403a8ecf56ae1323de4c4b4f21a9'

    model_path, model_name, file_hash = get_model_path("akidanet", model_name_v1, file_hash_v1,
                                                       model_name_v2, file_hash_v2)
    model_path = fetch_file(model_path,
                            fname=model_name,
                            file_hash=file_hash,
                            cache_subdir='models')
    return load_model(model_path)


def akidanet_plantvillage_pretrained(quantized=True, bitwidth=None):
    """
    Helper method to retrieve an `akidanet_imagenet` model that was trained on
    PlantVillage dataset.

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
            model_name_v1 = 'akidanet_plantvillage_iq8_wq4_aq4.h5'
            file_hash_v1 = '1400910c774fd78a5e6ea227ff28cb28e79ecec0909a378068cd9f40ddaf4e0a'
            model_name_v2 = 'akidanet_plantvillage_i8_w4_a4.h5'
            file_hash_v2 = '29f16a1a72552740121d2b187f49996a6c882b870cde44fa76f0596b22298b98'
        elif bitwidth == 8:
            model_name_v1, file_hash_v1 = None, None
            model_name_v2 = 'akidanet_plantvillage_i8_w8_a8.h5'
            file_hash_v2 = '06393a3a2db994d916887f486fa9a5ca6b3fbfe2216438d9758ddb1bd593d637'
        else:
            raise ValueError(f"bitwidth={bitwidth} is not available, use bitwidth=4 or 8 for this"
                             " model.")
    else:
        model_name_v1, file_hash_v1 = None, None
        model_name_v2 = 'akidanet_plantvillage.h5'
        file_hash_v2 = 'db985d047493d22ef49af28eafc23007fff6908a6d23413ac81b5c5f9ee4db58'

    model_path, model_name, file_hash = get_model_path("akidanet", model_name_v1, file_hash_v1,
                                                       model_name_v2, file_hash_v2)
    model_path = fetch_file(model_path,
                            fname=model_name,
                            file_hash=file_hash,
                            cache_subdir='models')
    return load_model(model_path)


def akidanet_vww_pretrained(quantized=True, bitwidth=None):
    """
    Helper method to retrieve an `akidanet_imagenet` model that was trained on
    VWW dataset.

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
            model_name_v1 = 'akidanet_vww_iq8_wq4_aq4.h5'
            file_hash_v1 = 'cd130d90ed736447b6244dc1228e708b9dab20af0d2bf57b9a49df4362467ea8'
            model_name_v2 = 'akidanet_vww_i8_w4_a4.h5'
            file_hash_v2 = '86032e0e558528e79404fdfc360960c013a12cb2a03a6cf5cc698c4cc983abd8'
        elif bitwidth == 8:
            model_name_v1, file_hash_v1 = None, None
            model_name_v2 = 'akidanet_vww_i8_w8_a8.h5'
            file_hash_v2 = 'dae1938273100a15f3328594017f7947aabe5edf7a7a093eb7547a30c7ab5b26'
        else:
            raise ValueError(f"bitwidth={bitwidth} is not available, use bitwidth=4 or 8 for this"
                             " model.")
    else:
        model_name_v1 = 'akidanet_vww.h5'
        file_hash_v1 = '00e03f13226cd622ad92bdb3402c4b4399a69875f2dde6ccadfb235ad6994d78'
        model_name_v2 = 'akidanet_vww.h5'
        file_hash_v2 = 'b142ef9c7c0e952063440615cc0b87d28eec5a75f807d95b534dc9a15f41c8b2'

    model_path, model_name, file_hash = get_model_path("akidanet", model_name_v1, file_hash_v1,
                                                       model_name_v2, file_hash_v2)
    model_path = fetch_file(model_path,
                            fname=model_name,
                            file_hash=file_hash,
                            cache_subdir='models')
    return load_model(model_path)
