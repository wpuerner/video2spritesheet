import fire
import threading
import time
from gui import gui
import queue
from frames import process_raw, preview_frames


class Video2Spritesheet:

    def process(self, filename, name, debug=False):

        frames, oheight, owidth = process_raw(filename, debug)

        command_queue = queue.Queue()

        preview = threading.Thread(target=preview_frames, args=[
                                   command_queue, frames, name, owidth, oheight], name='preview')
        preview.start()

        gui(command_queue, len(frames))
        preview.join()

    def info(self, input):
        import cv2 as cv
        cap = cv.VideoCapture('testdata/' + input)
        print("=== Video Settings for ", input, "===")
        print("Width      ", cap.get(cv.CAP_PROP_FRAME_WIDTH))
        print("Height     ", cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        print("Frames     ", cap.get(cv.CAP_PROP_FRAME_COUNT))
        print("FPS        ", cap.get(cv.CAP_PROP_FPS))
        cap.release()


if __name__ == '__main__':
    fire.Fire(Video2Spritesheet)
