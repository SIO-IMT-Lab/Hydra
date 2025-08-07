import argparse
import os
import sys
from time import sleep

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from bubblecam import BubbleCam
from config import *
from common.state import State

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--roll_buf_size', dest='roll_buf_size', action='store_true', default=150,
                        help='Set size of the rolling buffer of images.')
    parser.add_argument('--img_type', dest='img_type', action='store_true', default='.png',
                        help='Set image format.')
    parser.add_argument('--exposure', dest='exposure', action='store_true', default=100000,
                        help='Set camera exposure value.')
    parser.add_argument('--gain', dest='gain', action='store_true', default=10,
                        help='Set camera gain value.')
    parser.add_argument('--brightness', dest='brigtness', action='store_true', default=10,
                        help='Set camera brightness value.')
    parser.add_argument('--gamma', dest='gamma', action='store_true', default=0.25,
                        help='Set camera gamma value.')
    parser.add_argument('--fps', dest='fps', action='store_true', default=8,
                        help='Set camera fps value.')
    parser.add_argument('--backlight', dest='backlight', action='store_true', default=1,
                        help='Set camera backlight value.')
    parser.add_argument('--event_delay', dest='event_delay', action='store_true', default=60,
                        help='Set delay between subsequent events.')
    return parser.parse_args()

if __name__ == '__main__':
    print(
        '''This script tests if the bubble cam system properly locksout after 2 events are received in rapid succession.
        If events are received in rapid succession, it's expected that the camera system only captures images for the inital event received,
        as after the system will be locked out from recording any other images for roughly 1 minute.
        This script tests that behavior by comparing'''
    )

    args = parse_args()

    # save num images in target directory BEFORE new images are captured
    num_images_before_test = len([img for img in os.listdir('IMAGE_DIR') if os.path.isfile(img)])

    # init camera
    cam = BubbleCam(
        args['exposure'], 
        args['gain'], 
        args['brightness'], 
        args['fps'], 
        args['backlight'], 
        State.STORM, 
        args['event_delay'], 
        args['img_type'], 
        args['roll_buf_size'])

    cam.power_on()
    cam.set_state(State.STORM)
    # sleep for time it takes to fill up buffer and then a little bit more
    sleep(args['roll_buf_size'] / args['fps'] + 10)
    cam.detect_event()
    cam.detect_event()

    num_images_captured = num_images_before_test - len([img for img in os.listdir('IMAGE_DIR') if os.path.isfile(img)])
    expected_num_images_to_capture = args['roll_buf_size']
    print(f'Captured {num_images_before_test} images, expected {expected_num_images_to_capture}.')

    cam.power_off()