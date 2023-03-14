import cv2 as cv
import imutils
import fire
import time


class Video2Spritesheet:
    def process(self, ifile, ofile, startframe=0, endframe=-1, preview=False, debug=False):
        cap = cv.VideoCapture('testdata/' + ifile)
        if endframe == -1:
            endframe = cap.get(cv.CAP_PROP_FRAME_COUNT) - 1
        height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

        owidth = 800
        oheight = height

        fgbg = cv.bgsegm.createBackgroundSubtractorMOG()

        frames = []
        while True:
            if cap.get(cv.CAP_PROP_POS_FRAMES) < startframe:
                cap.read()
                continue
            if endframe < cap.get(cv.CAP_PROP_POS_FRAMES):
                break

            ret, frame = cap.read()
            if frame is None:
                break

            fgmask = fgbg.apply(frame)
            frame = cv.bitwise_and(frame, frame, mask=fgmask)

            points = []
            contours = cv.findContours(
                fgmask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(contours)
            for contour in contours:
                moments = cv.moments(contour)
                if moments['m00'] != 0:
                    c_x = int(moments["m10"] / moments["m00"])
                    c_y = int(moments["m01"] / moments["m00"])
                    points.append(
                        {"x": c_x, "y": c_y, "area": cv.contourArea(contour)})
                    if debug:
                        cv.drawContours(frame, [contour], -1, (0, 255, 0), 2)
                        cv.circle(frame, (c_x, c_y), 7, (255, 255, 255), -1)

            if len(points) == 0:
                continue   # skip this frame if we can't find a center

            center = {'x': int(sum([point['x'] * point['area']
                                    for point in points]) / sum([point['area'] for point in points])),
                      'y': int(sum([point['y'] * point['area']
                                    for point in points]) / sum([point['area'] for point in points]))}
            if debug:
                cv.circle(
                    frame, (center['x'], center['y']), 20, (0, 0, 255), -1)

            frame = cv.copyMakeBorder(frame, 0, 0, int(owidth/2), int(owidth/2),
                                      cv.BORDER_CONSTANT, value=[0, 0, 0])
            center['x'] = center['x'] + int(owidth/2)
            frame = frame[0:oheight, int(
                center['x']-owidth/2):int(center['x']+owidth/2)]

            frames.append(frame)

        if preview:
            i = 0
            while True:
                cv.imshow("Preview", frames[i])
                cv.waitKey(100)
                i = i + 1
                if i == len(frames):
                    i = 0

        if not preview:
            output = cv.VideoWriter("output/" + ofile,
                                    cv.VideoWriter_fourcc(*'mp4v'), 20.0, (owidth, oheight))
            for frame in frames:
                output.write(frame)
            output.release()

        cap.release()
        cv.destroyAllWindows()

    def info(self, input):
        cap = cv.VideoCapture('testdata/' + input)
        print("=== Video Settings for ", input, "===")
        print("Width      ", cap.get(cv.CAP_PROP_FRAME_WIDTH))
        print("Height     ", cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        print("Frames     ", cap.get(cv.CAP_PROP_FRAME_COUNT))
        print("FPS        ", cap.get(cv.CAP_PROP_FPS))
        cap.release()


if __name__ == '__main__':
    fire.Fire(Video2Spritesheet)
