#!/usr/bin/python

import os
import sys
import logging
import urllib.request
import json
import cv2
from concurrent.futures.thread import ThreadPoolExecutor
from progress.bar import Bar
from PIL import Image
import socket


# download function on multi-threads
def download(item_id, url, images_dir, bbox, crop):
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    try:
        file_output = os.path.join(images_dir, str(item_id) + '.' + 'JPEG')
        socket.setdefaulttimeout(15)
        urllib.request.urlretrieve(url, file_output)
        if (verify_image(file_output)):
            image = cv2.imread(file_output)
            image = image[bbox['top']:bbox['top'] + bbox['height'],
                            bbox['left']: bbox['left'] + bbox['width']] if (bbox is not None and crop) else image
            cv2.imwrite(file_output, image)
        else:
            os.remove(file_output)
            print('Remove '+file_output)
    except:
        # print("Unexpected error:", sys.exc_info()[0])
        logging.error(sys.exc_info()[0])

# Function to verify image


def verify_image(image_file):
    try:
        img = Image.open(image_file)
        img.verify()
    except:
        return False
    return True

# Download images for each class


def read_class(class_name, max_num_samples, url_dict, images_dir, threads, is_retrieval, is_match=False):
    if not is_retrieval:
        domain = 'train_pairs_'
    else:
        domain = 'retrieval_' if not is_match else 'retrieval_with_match_'
    file_loc = 'meta/json/' + domain + class_name + '.json'
    with open(file_loc, 'r') as file_json:
        meta_data = json.load(file_json)
    images_list = []
    bar = Bar('Downloading '+class_name.title(), max=(len(meta_data)
                                                      if (args.max_num_samples == None) or (args.max_num_samples > len(meta_data)) else args.max_num_samples), suffix='%(percent)d%%')

    output_dir = os.path.join(images_dir, 'street', class_name) if not is_retrieval else os.path.join(images_dir, 'shop', class_name)
    for i, data in enumerate(meta_data):
        if max_num_samples != None and i >= max_num_samples:
            break
        photo_id = int(data['photo'])
        url = url_dict[photo_id]
        bbox = data['bbox'] if not is_retrieval else None
        images_list.append(
            {'item_id': photo_id, 'url': url, 'images_dir': output_dir, 'bbox': bbox})
        if i % args.threads == 0:
            with ThreadPoolExecutor(max_workers=args.threads) as executor:
                for x in images_list:
                    executor.submit(
                        download, x['item_id'], x['url'], x['images_dir'], x['bbox'], args.crop)
                images_list = []
        bar.next()
    bar.finish()
    print('Downloaded ' + str(len(next(os.walk(output_dir))
                                  [2])) + ' images for class ' + class_name)


def main(args):
    print('Start downloading images from Street2Shop dataset...')

    if args.log is not None:
        logging.basicConfig(filename=args.log,
                            format='%(message)s', level=logging.ERROR)

    # Read file that contains the urls
    f = open(args.urls, 'r')
    url_list = f.read().split('\n')
    url_dict = dict([(int(line.split(',')[0]), line.split(',')[1])
                     for line in url_list])
    f.close()

    # Create the retrieval meta json files for matched shop images when necessary
    if args.match:
        for class_name in args.classes:
            out_file = 'meta/json/' + 'retrieval_with_match_' + class_name + '.json'
            if os.path.isfile(out_file):
                break
            with open('meta/json/' + 'train_pairs_' + class_name + '.json', 'r') as f:
                dicts = json.load(f)
            ci_pids = set()
            for x in dicts:
                ci_pids.add(x['product'])
            with open('meta/json/' + 'retrieval_' + class_name + '.json', 'r') as f:
                dicts = json.load(f)
            inner_join_dicts = []
            for x in dicts:
                if x['product'] in ci_pids:
                    inner_join_dicts.append(x)
            with open(out_file, 'w') as json_file:
                json.dump(inner_join_dicts, json_file)
            print('Created the retrieval meta json files for the matching {:^10} images in the shop domain.'.format(class_name))
    print()

    if 'street' in args.domains:
        for class_name in args.classes:
            read_class(class_name, args.max_num_samples,
                       url_dict, args.images_dir, args.threads, False)
    if 'shop' in args.domains:
        for class_name in args.classes:
            read_class(class_name, args.max_num_samples,
                       url_dict, args.images_dir, args.threads, True, args.match)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    all_classes = ['bags','belts','dresses','eyewear','footwear','hats','leggings','outerwear','pants','skirts','tops']

    # Data handling parameters
    parser.add_argument('--urls', dest='urls', type=str,
                        default=None, required=True, help='urls file')
    parser.add_argument('--image_dir', dest='images_dir',
                        type=str, default='images', help='image directory')
    parser.add_argument('--domains', nargs='+', dest='domains', type=str,
                        default='street', help='specific photo domains to download')
    parser.add_argument('--match', dest='match',
                        action='store_true', help='download shop photos that have a matching street photo only')
    parser.add_argument('--log', dest='log', type=str,
                        default=None, help='log errors')
    parser.add_argument('--threads', dest='threads',
                        type=int, default=10, help='threads')
    parser.add_argument('--classes', nargs='+', dest='classes', type=str,
                        default=all_classes, help='specific fashion classes to download')
    parser.add_argument('--max_num_samples', dest='max_num_samples',
                        type=int, default=None, help='maximum number of samples')
    parser.add_argument('--crop', dest='crop',
                        action='store_true', help='crop image based on given bounding box')
    args = parser.parse_args()

    main(args)
    print('Finished')

    exit(0)
