# Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import torch
import paddle
import numpy as np
from typing import Union


def init_logger(save_path: str=None):
    """
    benchmark logger
    """
    # Init logger
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_output = save_path
    if not os.path.exists(os.path.dirname(log_output)):
        os.makedirs(os.path.dirname(log_output))
    if save_path is None:
        logging.basicConfig(level=logging.INFO, format=FORMAT)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format=FORMAT,
            handlers=[
                logging.FileHandler(
                    filename=log_output, mode='w'),
                logging.StreamHandler(),
            ])
    logger = logging.getLogger(__name__)
    logger.info("Init logger done!")
    return logger


def np2torch(data: dict):
    assert isinstance(data, dict)
    torch_input = {}
    for k, v in data.items():
        if isinstance(v, np.ndarray):
            torch_input[k] = torch.Tensor(v)
        else:
            torch_input[k] = v
    return torch_input


def np2paddle(data: dict):
    assert isinstance(data, dict)
    paddle_input = {}
    for k, v in data.items():
        if isinstance(v, np.ndarray):
            paddle_input[k] = paddle.Tensor(v)
        else:
            paddle_input[k] = v
    return paddle_input


def paddle2np(data: Union[paddle.Tensor, dict]=None):
    if isinstance(data, dict):
        np_data = {}
        for k, v in data.items():
            np_data[k] = v.numpy()
        return np_data
    else:
        return {'output': data.numpy()}


def torch2np(data: Union[torch.Tensor, dict]=None):
    if isinstance(data, dict):
        np_data = {}
        for k, v in data.items():
            np_data[k] = v.detach().numpy()
        return np_data
    else:
        return {'output': data.detach().numpy()}


def check_print_diff(diff_dict,
                     diff_method='mean',
                     diff_threshold: float=1e-6,
                     print_func=print,
                     indent: str='\t',
                     level: int=0):
    assert diff_threshold in ['min', 'max', 'mean']
    passed = True
    cur_indent = '' if level == 0 else indent
    for k, v in diff_dict.items():
        if 'mean' in v and 'min' in v and 'max' in v and len(v) == 3:
            v = v[diff_method]
            print_func("{}{}:\t {}".format(cur_indent, k, v))
            if v > diff_threshold:
                print_func('{}diff in {} failed the acceptance'.format(
                    cur_indent, k))
                passed = False
        else:
            print_func('{}{}'.format(cur_indent, k))
            sub_passed = check_print_diff(v, diff_method, diff_threshold,
                                          print_func, cur_indent + indent,
                                          level + 1)
            passed = passed and sub_passed
    return passed
