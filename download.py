#!/usr/bin/python

from tomorrow import threads
import os
import sys
import logging
import urllib.request
import json
from concurrent.futures.thread import ThreadPoolExecutor


# download function on multi-threads
def download(item_id, url, images_dir):
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    try:
        file_output = os.path.join(images_dir, str(item_id) + '.' + 'JPEG')
        urllib.request.urlretrieve(url, file_output)
        print(file_output)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        logging.error(sys.exc_info()[0])

# Download images for each class
def read_class(class_name, max_num_samples, url_dict, images_dir, threads):
    print('Downloading images for class ' + class_name + '...')
    file_loc = 'meta/json/train_pairs_' + class_name + '.json'
    file_json = open(file_loc, 'r')
    meta_data = json.load(file_json)
    file_json.close()
    images_list = []

    for i,data in enumerate(meta_data):
        if i >= max_num_samples:
            break
        photo_id = int(data['photo'])
        url = url_dict[photo_id]
        output_dir = os.path.join(images_dir, class_name)
        images_list.append({'item_id': photo_id, 'url': url, 'images_dir': output_dir})
        if i % args.threads == 0:
            with ThreadPoolExecutor(max_workers=args.threads) as executor:
                for x in images_list:
                    executor.submit(download, x['item_id'], x['url'], x['images_dir'])
                images_list = []
    print('Downloaded ' + str(len(next(os.walk(output_dir))[2])) + ' images for class ' + class_name)
    
def main(args):    
    print('Start downloading images from Street2Shop dataset...')
    
    if args.log is not None:
        logging.basicConfig(filename=args.log, format='%(message)s', level=logging.ERROR)
    
    # Read file that contains the urls
    f = open(args.urls, 'r')
    url_list = f.read().split('\n')
    url_dict = dict([(int(line.split(',')[0]),line.split(',')[1]) for line in url_list])
    f.close()
    
    # Check whether we want to download all images or for specified class only
    if(args.classes[0] == 'all'):
        print('Downloading all images...')
        images_list = []
        for i, (item_id, url) in enumerate(url_dict.items()):
            if i >= args.max_num_samples:
                break
            images_list.append({'item_id': item_id, 'url': url, 'images_dir': args.images_dir})
            if i % args.threads == 0:
                with ThreadPoolExecutor(max_workers=args.threads) as executor:
                    for x in images_list:
                        executor.submit(download, x['item_id'], x['url'], x['images_dir'])
                    images_list = []
        print('Downloaded ' + str(len(next(os.walk(args.images_dir))[2])) + ' images')
            
    else:
        for class_name in args.classes:
            read_class(class_name, args.max_num_samples, url_dict, args.images_dir, args.threads)

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()

    # Data handling parameters
    parser.add_argument('--urls', dest='urls', type=str, default=None, required=True, help='urls file')
    parser.add_argument('--image_dir', dest='images_dir', type=str, default='images', help='image directory')
    parser.add_argument('--log', dest='log', type=str, default=None, help='log errors')
    parser.add_argument('--start', dest='start', type=int, default=0, help='start offset')
    parser.add_argument('--threads', dest='threads', type=int, default=10, help='threads')
    parser.add_argument('--classes', nargs='+', dest='classes', type=str, default=['all'], help='specific fashion classes to download')
    parser.add_argument('--max_num_samples', dest='max_num_samples', type=int, default=10000000, help='maximum number of samples')
    args = parser.parse_args()

    main(args)
    print('Finished')
    
    exit(0)
    
