import cv2 as cv
import imutils
import fire


class Video2Spritesheet:
    def process(self, input, output, debug=False):
        cap = cv.VideoCapture('testdata/' + input)
        height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

        owidth = 800
        oheight = height
        output = cv.VideoWriter("output/" + output,
                                cv.VideoWriter_fourcc(*'mp4v'), 20.0, (owidth, oheight))
        fgbg = cv.bgsegm.createBackgroundSubtractorMOG()

        while (1):
            ret, frame = cap.read()

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
            points.clear()
            if debug:
                cv.circle(
                    frame, (center['x'], center['y']), 20, (0, 0, 255), -1)

            frame = cv.copyMakeBorder(frame, 0, 0, int(owidth/2), int(owidth/2),
                                      cv.BORDER_CONSTANT, value=[0, 0, 0])
            center['x'] = center['x'] + int(owidth/2)
            crop = frame[0:oheight, int(
                center['x']-owidth/2):int(center['x']+owidth/2)]

            output.write(crop)
            if debug:
                cv.imshow('frame', crop)
            k = cv.waitKey(30) & 0xff
            if k == 27:
                break

        cap.release()
        output.release()
        cv.destroyAllWindows()


if __name__ == '__main__':
    fire.Fire(Video2Spritesheet)
