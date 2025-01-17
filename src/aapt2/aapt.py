#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
File: aapt2/aapt.py
Project: aapt
Description:
Created By: Tao.Hu 2019-07-08
-----
Last Modified: 2020-10-14 02:03:42 pm
Modified By: Trevor Wang
-----
'''

import os
import re
import stat
import subprocess
import platform
import io


def aapt(args='--help'):
    try:
        # Darwin: macOS Linux Windows
        system_name = platform.system()
        if (system_name != 'Darwin' and system_name != 'Linux' and system_name != 'Windows'):
            raise TypeError(
                'unknown system type, only support Darwin、Linux、Windows')

        aapt_path = os.path.join(os.path.dirname(
            __file__), 'bin', system_name, 'aapt_64')
        if system_name == 'Windows':
            aapt_path += '.exe'

        if (system_name != 'Windows' and os.access(aapt_path, os.X_OK) is not True):
            os.chmod(aapt_path, stat.S_IRWXU)

        out = subprocess.getoutput(aapt_path + ' ' + args)
        return out
    except Exception as e:
        print('aapt error:', e)
        raise e


def ls(file_path):
    return aapt('l ' + file_path)


def dump(file_path, values):
    return aapt('d ' + values + ' ' + file_path)


def packagecmd(file_path, command):
    return aapt('p ' + command + ' ' + file_path)


def remove(file_path, files):
    return aapt('r ' + file_path + ' ' + files)


def add(file_path, files):
    return aapt('a ' + file_path + ' ' + files)


def crunch(resource, output_folder):
    return aapt('c -S ' + resource + ' -C ' + output_folder)


def single_crunch(input_file, output_file):
    return aapt('s -i ' + input_file + ' -o ' + output_file)


def version():
    return aapt('v')


def get_apk_info(file_path):
    try:
        stdout = dump(file_path, 'badging')
        match = re.compile(
            "package: name='(\\S+)' versionCode='(\\d+)' versionName='(\\S+)'").match(stdout)
        if not match:
            raise Exception("can't get packageinfo")
        package_name = match.group(1)
        version_code = match.group(2)
        version_name = match.group(3)
        match = re.compile(
            "application: label='([\u4e00-\u9fa5_a-zA-Z0-9-\\S]+)'").search(stdout)
        app_name = match.group(1)
        icon_path = get_icon_path(stdout)
        permissions = get_permissions(stdout)

        launchable_activity = get_launchable_activity(stdout)
        return {
            'package_name': package_name,
            'version_code': version_code,
            'version_name': version_name,
            'app_name': app_name,
            'icon_path': icon_path,
            'permissions': permissions,
            'launchable_activity': launchable_activity
        }
    except Exception as e:
        raise e


def get_icon_path(stdout):
    match = re.compile(
        "application: label='([\w\d\s]+)'").search(stdout)
    icon_path = (match and match.group(2)) or None
    return icon_path


def get_permissions(stdout):
    permissions = []
    matches = re.compile(
        "uses-permission: name='([\w\.-]+)'").findall(stdout)
    for m in matches:
        permissions.append(m)
    return permissions


def get_launchable_activity(stdout):
    match = re.compile(
        "launchable-activity: name='([\w\.-]+)'").search(stdout)
    launchable_activity = (match and match.group(1)) or None
    return launchable_activity


def get_apk_and_icon(file_path):
    try:
        apkInfo = get_apk_info(file_path)
        if (apkInfo['icon_path']):
            out = subprocess.check_output(
                'unzip' + ' -p ' + file_path + ' ' + apkInfo['icon_path'], shell=True)
            byte_stream = io.BytesIO(out)
            apkInfo['icon_byte_value'] = byte_stream.getvalue()
            byte_stream.close()
        else:
            apkInfo['icon_byte_value'] = None
        return apkInfo
    except Exception as e:
        raise e
