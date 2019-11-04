from tomorrow import threads
import imghdr
import requests
import os
from itertools import islice
import sys
import logging


def split(x):
    first = x.find(',')
    return (x[:first], x[first+1:])

# Run the download function on multi-threads
@threads(args.threads)
def download(item_id, url, i, images_dir=''):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            image_type = imghdr.what(None, r.content)
            if image_type is not None:
                with open(os.path.join(images_dir, item_id + '.' + image_type), 'wb') as f:
                    f.write(r.content)
                    f.close()
            else:
                logging.error('%s\t%s\tunknown_type' % (item_id, url))
        else:
            logging.error('%s\t%s\tstatus:%d' % (item_id, url, r.status_code))

    except KeyboardException:
        raise
    except:
        print "Unexpected error:", sys.exc_info()[0]
        logging.error(sys.exc_info()[0])

    if i % 200 == 0:
        print i
        
def read_class(class_name):
    print('Downloading images for class ' + class_name + '...')
    file_loc = 'meta/json/train_pairs_' + class_name + '.json'
    file_json = open(file_loc, 'r')
    meta_data = json.load(file_json)
    file_json.close()
    
    for i,data in enumerate(meta_data):
        if i >= args.max_num_samples:
            break
        photo_id = int(data['photo'])
        url = url_dict[photo_id]
        images_dir = os.path.join(images_dir, class_name)
        download(photo_id, url, i, images_dir)
    print('Downloaded ' + i + ' images for class ' + class_name)
    
def main(args):
    print('Start downloading images from Street2Shop dataset...')
    # Handle if the file is not found
    if args.fail_file is not None:
        logging.basicConfig(filename=args.fail_file, format='%(message)s', level=logging.ERROR)
    
    # Read file that contains the urls
    f = open(args.urls, 'r')
    url_list = f.read().split('\n')
    url_dict = dict([(int(line.split(',')[0]),line.split(',')[1]) for line in url_list])
    f.close()
    
    #check all or class
    
#     url_dict = dict([])
#     itr = enumerate(f)
#     itr = islice(itr, args.start, None)
    
    

    for i, line in itr:
        [item_id, url] = split(line.strip())
        download(item_id, url, i, images_dir=args.images_dir)



if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()

    # Data handling parameters
    parser.add_argument('--urls', dest='urls', type=str, default=None, required=True, help='urls file')
    parser.add_argument('--image_dir', dest='images_dir', type=str, default='images', help='image directory')
    parser.add_argument('--failures', dest='fail_file', type=str, default=None, help='failure records')
    parser.add_argument('--start', dest='start', type=int, default=0, help='start offset')
    parser.add_argument('--threads', dest='threads', type=int, default=10, help='threads')
    parser.add_argument('--class', nargs='+', dest='class', type=str, default='all', help='specific fashion classes to download')
    parser.add_argument('--max_num_samples', dest='max_num_samples', type=int, default=10000000, help='maximum number of samples')
    args = parser.parse_args()


    main(args)

    exit(0)
    
