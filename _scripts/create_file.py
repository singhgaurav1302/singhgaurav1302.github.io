#!/usr/bin/python3

import argparse
import os
from datetime import date

def get_front_matter():
    front_matter = '''\
---
authors: [<author>]
layout: post
title: <title>
categories: [<categories>]
tags: [<tag>]
---
'''
    return front_matter

def create_file_name(file_args, ext='.md'):
    file_name = '-'.join(file_args).lower()
    file_name = '-'.join([date.today().isoformat(), file_name])
    file_name += ext
    return file_name

def create_file(file, content):
    if not os.path.exists(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))
    with open(file, mode='w+') as f:
        f.write(content)

def print_file(file):
    with open(file) as f:
        print(f.read())

def get_dest_dir(is_post, dest):
    base_dir = '_posts'
    if not is_post:
        base_dir = '_drafts'
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, base_dir, dest)

def main(args):
    file_name = create_file_name(args.filename)
    is_post = not args.drafts
    dest_dir = get_dest_dir(is_post, args.dest)
    file = os.path.join(dest_dir, file_name)
    create_file(file, get_front_matter())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='create_file',
        description='Create posts, drafts',
        epilog='By defaults create posts in _posts directory.')

    parser.add_argument('-f', '--filename', type=str, nargs='+')
    parser.add_argument('-d', '--dest')
    parser.add_argument('--drafts', action='store_true')

    main(parser.parse_args())
