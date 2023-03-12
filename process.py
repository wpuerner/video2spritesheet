import cv2 as cv
import imutils

DEBUG = False

cap = cv.VideoCapture('testdata/walking_1_raw.mp4')
width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv.CAP_PROP_FPS)
print("Input dimensions::width=", str(width), " height=", str(height))

owidth = 800
oheight = height
output = cv.VideoWriter("output/walking_1_processed.mp4",
                        cv.VideoWriter_fourcc(*'mp4v'), 20.0, (owidth, oheight))
fgbg = cv.bgsegm.createBackgroundSubtractorMOG()

while (1):
    # grab next frame
    ret, frame = cap.read()

    # apply foreground mask
    fgmask = fgbg.apply(frame)
    frame = cv.bitwise_and(frame, frame, mask=fgmask)

    # find centers of all contours in frame
    contours = cv.findContours(
        fgmask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    centers_x = []
    centers_y = []
    points = []
    for contour in contours:
        M = cv.moments(contour)
        if M['m00'] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            points.append({"x": cX, "y": cY, "area": cv.contourArea(contour)})
            if DEBUG:
                cv.drawContours(frame, [contour], -1, (0, 255, 0), 2)
                cv.circle(frame, (cX, cY), 7, (255, 255, 255), -1)

    if len(points) == 0:
        continue   # skip this frame if we can't find a center

    center = {'x': int(sum([point['x'] * point['area']
                            for point in points]) / sum([point['area'] for point in points])),
              'y': int(sum([point['y'] * point['area']
                            for point in points]) / sum([point['area'] for point in points]))}
    points.clear()
    if DEBUG:
        cv.circle(frame, (center['x'], center['y']), 20, (0, 0, 255), -1)

    frame = cv.copyMakeBorder(frame, 0, 0, int(owidth/2), int(owidth/2),
                              cv.BORDER_CONSTANT, value=[0, 0, 0])
    center['x'] = center['x'] + int(owidth/2)
    crop = frame[0:oheight, int(center['x']-owidth/2):int(center['x']+owidth/2)]

    output.write(crop)
    if DEBUG:
        cv.imshow('frame', crop)
    k = cv.waitKey(30) & 0xff
    if k == 27:
        break


cap.release()
output.release()
cv.destroyAllWindows()
