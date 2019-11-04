from tomorrow import threads
import imghdr
import requests
import os
from itertools import islice
import sys
import logging
import urllib.request
import json


# def split(x):
#     first = x.find(',')
#     return (x[:first], x[first+1:])

        

    
def main(args):
    print(args)
    
    # Run the download function on multi-threads
    @threads(args.threads)
    def download(item_id, url, i, images_dir):
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        try:
            file_output = os.path.join(images_dir, str(item_id) + '.' + 'JPEG')
            urllib.request.urlretrieve(url, file_output)
            print(file_output)
        except KeyboardException:
            raise
        except:
            print("Unexpected error:", sys.exc_info()[0])
            logging.error(sys.exc_info()[0])
    
    # Download images for each class
    def read_class(class_name, max_num_samples, url_dict, images_dir):
        print('Downloading images for class ' + class_name + '...')
        file_loc = 'meta/json/train_pairs_' + class_name + '.json'
        file_json = open(file_loc, 'r')
        meta_data = json.load(file_json)
        file_json.close()

        for i,data in enumerate(meta_data):
            if i >= max_num_samples:
                break
            photo_id = int(data['photo'])
            url = url_dict[photo_id]
            output_dir = os.path.join(images_dir, class_name)
            download(photo_id, url, i, output_dir)
        print('Downloaded ' + str(i) + ' images for class ' + class_name)
    
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
        for i,(item_id, url) in enumerate(url_dict.items()):
            download(item_id, url, i, args.images_dir)
        print('Downloaded ' + str(i) + ' images')
    else:
        for i, class_name in enumerate(args.classes):
            read_class(class_name, args.max_num_samples, url_dict, args.images_dir)


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

    exit(0)
    
