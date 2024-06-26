# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
""""Classes and functions for Initializer"""

import math
import numpy as np
from mindspore.common.initializer import Initializer, _calculate_fan_in_and_fan_out, _assignment
try:
    from mindspore._c_expression import random_normal as _random_normal
except: # pylint: disable=bare-except
    from mindspore._c_expression import _random_normal

def _numpy_seed():
    r"""
    Generates and returns a random integer value within the specified range.
    
    Returns:
        int: A random integer value between 1 and 1 << 63.
    
    Raises:
        None.
    """
    # This will produce same value after call numpy.random.seed with same seed.
    return np.random.randint(low=1, high=(1 << 63), dtype=np.int64)

def _init_random_normal(mean, sigma, shape):
    r"""
    Initializes a numpy array with random numbers drawn from a normal distribution.
    
    Args:
        mean (float): The mean of the normal distribution.
        sigma (float): The standard deviation of the normal distribution. Must be greater than or equal to zero.
        shape (tuple): The shape of the output array.
    
    Returns:
        numpy.ndarray: A numpy array of the specified shape filled with random numbers drawn from a normal distribution.
    
    Raises:
        ValueError: If the value of sigma is less than zero.
    
    Note:
        The random numbers are generated using the numpy random number generator seeded with the current system time.
    
    """
    if sigma < 0:
        raise ValueError("sigma < 0")
    data = np.ndarray(shape=shape, dtype=np.float32)
    _random_normal(_numpy_seed(), data, mean, sigma)
    return data

class XavierNormal(Initializer):
    r"""
    Generates an array with values sampled from Xavier normal distribution
    :math::math:`\mathcal{N}(0, \text{std}^2)` in order to initialize a tensor, where

    .. math::
        boundary = gain * \sqrt{\frac{2}{n_{in} + n_{out}}}

    where :math:`gain` is an optional scaling factor, :math:`n_{in}` is the number of input units in the weight tensor,
    :math:`n_{out}` is the number of output units in the weight tensor.

    Args:
        gain (float): An optional scaling factor. Default: 1.

    Examples:
        >>> import mindspore
        >>> from mindspore.common.initializer import initializer
        >>> from text.common.initializer import XavierNormal
        >>> tensor1 = initializer(XavierNormal(), [1, 2, 3], mindspore.float32)
        >>> tensor2 = initializer('XavierNormal', [1, 2, 3], mindspore.float32)
    """
    def __init__(self, gain=1):
        r"""
        __init__
        
        Args:
            self: The instance of the class.
            gain (float, optional): The gain value for Xavier normal initialization. Defaults to 1. It represents the scale factor for the normal distribution.
        
        Returns:
            None. The method initializes the XavierNormal class with the specified gain value.
        
        Raises:
            N/A
        """
        super().__init__(gain=gain)
        self.gain = gain

    def _initialize(self, arr):
        r"""
        Initializes the given array with values drawn from a Xavier Normal distribution.
        
        Args:
            self (XavierNormal): An instance of the XavierNormal class.
            arr (ndarray): The array to be initialized.
        
        Returns:
            None. This method modifies the input array in-place.
        
        Raises:
            None.
        
        This method calculates the fan-in and fan-out values based on the shape of the input array. The fan-in represents the number of input units to a layer, while the fan-out represents the number of output
units. It then computes the standard deviation using the gain value specified in the XavierNormal instance and the fan-in and fan-out values. The Xavier Normal distribution is defined as a Gaussian
distribution with zero mean and variance equal to 2.0 / (fan_in + fan_out). Finally, random values are generated from this distribution and assigned to the array.
        """
        fan_in, fan_out = _calculate_fan_in_and_fan_out(arr.shape)

        std = self.gain * math.sqrt(2.0 / float(fan_in + fan_out))
        data = _init_random_normal(0, std, arr.shape)

        _assignment(arr, data)
