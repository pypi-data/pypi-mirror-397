#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os

import imgkit


def from_string(**kwargs):
    """
    @see https://pypi.org/project/imgkit/
    :param kwargs: imgkit.from_string(**kwargs)
    :return: state,output_path
    """
    kwargs = kwargs if isinstance(kwargs, dict) else dict()
    kwargs.setdefault("output_path", None)
    if isinstance(kwargs.get("output_path", None), str) and len(kwargs.get("output_path", "")):
        os.makedirs(os.path.dirname(kwargs.get("output_path")), exist_ok=True)
    if imgkit.from_string(**kwargs):
        return True, kwargs.get("output_path", None)
    return None, kwargs.get("output_path", None)


def from_url(**kwargs):
    """
    @see https://pypi.org/project/imgkit/
    :param kwargs: imgkit.from_url(**kwargs)
    :return: state,output_path
    """
    kwargs = kwargs if isinstance(kwargs, dict) else dict()
    kwargs.setdefault("output_path", None)
    if isinstance(kwargs.get("output_path", None), str) and len(kwargs.get("output_path", "")):
        os.makedirs(os.path.dirname(kwargs.get("output_path")), exist_ok=True)
    if imgkit.from_url(**kwargs):
        return True, kwargs.get("output_path", None)
    return None, kwargs.get("output_path", None)


def from_file(**kwargs):
    """
    @see https://pypi.org/project/imgkit/
    :param kwargs: imgkit.from_file(**kwargs)
    :return: state,output_path
    """
    kwargs = kwargs if isinstance(kwargs, dict) else dict()
    kwargs.setdefault("output_path", None)
    if isinstance(kwargs.get("output_path", None), str) and len(kwargs.get("output_path", "")):
        os.makedirs(os.path.dirname(kwargs.get("output_path")), exist_ok=True)
    if imgkit.from_file(**kwargs):
        return True, kwargs.get("output_path", None)
    return None, kwargs.get("output_path", None)
