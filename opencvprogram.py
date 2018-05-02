#
# Leila Suasnabar
# lsuasnab@usc.edu
#
# Compiled on OS X El Capitan Version 10.11.6 python 2.7.9, opencv 3.2.0,
#               numpy 1.12.1, pandas 0.20.1 and XlsxWriter 0.9.6
#
# Execution:    All windows appear at the same position

import cv2
import numpy as np
import pandas as pd
import sys

# Write the path and names of the files
filename = ""
filename_excel = ""
filename_mask = ""

drawing = False # draw free hand phase (2)
mode = False    # draw rectangle phase
phase2 = False  # flag to know when to move to phase 2
done = False    # program is finished and has stopped all user input
coord = []
pts = []

# Offset purely applied for complete visualization of images
# Value can be changed if necessary. No modifications on data
OFFSET = 25

# Mouse callback function
def check_mouse(event,x,y,flags,param):
        global coord,drawing,mode,copy,previousx,previousy
        global binary,pts,done

        if event == cv2.EVENT_LBUTTONDOWN:
                if done == False:
                        if phase2 == False:
                                coord.append((x, y))
                                mode = True
                                # Create copy to update rectangle position
                                copy = image.copy()
                                cv2.rectangle(copy,coord[0],(x,y),255, 1)
                        else:
                                drawing = True
                                previousx = x
                                previousy = y
                                coord[0] = (x,y)
                                pts.append((x,y))

        elif event == cv2.EVENT_MOUSEMOVE:
                if mode == True:
                        copy = image.copy()
                        cv2.rectangle(copy,coord[0],(x,y),255, 1)
                if drawing == True:
                        cv2.line(crop,(previousx,previousy),(x,y),255,1)
                        previousx = x
                        previousy = y
                        pts.append((x,y))
                        
        elif event == cv2.EVENT_LBUTTONUP:
                if mode == True:
                        coord.append((x, y))
                        # Set coordinates as top left, and bottom right regardless of original coordinates
                        temp = list(coord)
                        temp[0] = (min(coord[0][0],coord[1][0]),min(coord[0][1],coord[1][1]))
                        temp[1] = (max(coord[0][0],coord[1][0]),max(coord[0][1],coord[1][1]))
                        coord = list(temp)

                        copy = image.copy()
                        cv2.rectangle(copy,coord[0],coord[1],255, 1)
                        mode = False # Finished phase 1 - drawing rectangle
                        
                if drawing == True:
                        cv2.line(crop,(previousx,previousy),(x,y),255,1)
                        cv2.line(crop,(x,y),coord[0],255,1)
                        pts.append((x,y))
                        pts = np.asarray(pts,dtype=np.int32)
                        drawing = False

                        # Output binary/mask image and save as tif uint16 file
                        binary = np.zeros(crop.shape)
                        cv2.fillConvexPoly(binary,pts,255)
                        cv2.imshow("Binary Image",binary)
                        binary = binary.astype(np.uint16)
                        cv2.imwrite(filename_mask,binary)
                        done = True # Stop receiving user input
 
# Load image
image = cv2.imread(filename,-1)

# Convert to uint8 from uint16
image = cv2.convertScaleAbs(image,alpha=(255.0/np.max(image)))
copy = image.copy()

# Set up windows and callback function
cv2.namedWindow("Original Image",cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback("Original Image", check_mouse)
cv2.namedWindow("Binary Image",cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("Cropped Image",cv2.WINDOW_NORMAL)
cv2.setMouseCallback("Cropped Image", check_mouse)

while True:
        # Display original image
        cv2.imshow("Original Image", copy)

        # Press esc to stop program
        if cv2.waitKey(1)&0xFF == 27:
                break

        # Display cropped image and perform drawing on the new image
        if len(coord) == 2:
                if phase2 == False:
                        crop = image[coord[0][1]:coord[1][1], coord[0][0]:coord[1][0]]
                                        
                        # Save information in excel file
                        df = pd.DataFrame({
                            'Var1':['top','bottom','right','width'],
                            'Var2':[coord[0][1],coord[1][1],coord[1][0],coord[1][0]-coord[0][0]]
                            })
                        writer = pd.ExcelWriter(filename_excel,engine='xlsxwriter')
                        df.to_excel(writer,sheet_name='Sheet1')
                        writer.save()

                cv2.resizeWindow("Cropped Image",crop.shape[1],crop.shape[0]+OFFSET)
                cv2.imshow("Cropped Image", crop)

                # Set up for drawing phase and mask/binary phase
                phase2 = True

        # Show all windows for 2 seconds after all phases
        # Change to any desired viewing time
        if done == True:
                cv2.waitKey(2000)
                break

# Close all windows
cv2.destroyAllWindows()
sys.exit()

