from django.shortcuts import render
# Create your views here.
import glob
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import xlsxwriter
from django.contrib import messages
from zipfile import ZipFile
#import xlwt
import os
import sys



def splitboxes(img):
    cols=np.hsplit(img,2)
    boxes=[]
    for c in cols:
        rows=np.vsplit(c,10)
        for box in rows:
            boxes.append(box)
            #cv2.imshow("split",box)
            #cv2.waitKey(0)
    return boxes







def demo(request):
    if request.method=="POST":
        path=request.POST.get("path")
        number=request.POST.get('number')
        print("path is", path)
        path1=path[::-1]
        index = path[::-1].index("\\")
        path2 = path[:len(path) - index]
        fname = path1[:index + 1]
        fname = fname[::-1]
        print(path2)
        ar = os.listdir(path)



        if len(path)==0:
            output='Enter the path'
            messages.info(request, 'Enter the folder path')
            return render(request,'index.html',{'output':output})
        if len(fname)==0:
            #path = 'C:/Users/Badrinath/Downloads/Cards/Cards'




            output='Enter the number'
            #messages.info(request, 'Enter the bundle number')
            return render(request,'index.html',{'output':output})
        outworkbook=xlsxwriter.Workbook(path2+fname+".xlsx")
        outsheet=outworkbook.add_worksheet()
        outsheet.write("A1","FRMID")
        outsheet.write("B1","F001")
        outsheet.write("C1","F002")
        outsheet.write("D1", "BUND")

        ar = os.listdir(path)


        images = [cv2.imread(file) for file in glob.glob(path+"/*")]


        search = cv2.imread("C:/Users/GCET/Downloads/pasha.jpeg")

        #cv2.imshow("search", search)
        #cv2.waitKey(0)

        wi = 1
        ans = []
        print("puzzele is",images)
        for puzzle in images:
            p = path + "/" + ar[wi-1]
            img = puzzle
            for code in decode(puzzle):
                r0 = code.data
            outsheet.write(wi, 0, r0)
            new_name=str(r0)
            oldname = p
            new_name = path + "\\" + str(r0) + '.bmp'
            #os.rename(oldname, new_name)
            (searchHeight, searchWidth) = search.shape[:2]

            result = cv2.matchTemplate(puzzle, search, cv2.TM_CCOEFF)
            (_, _, minLoc, maxLoc) = cv2.minMaxLoc(result)

            topLeft = maxLoc
            botRight = (topLeft[0] + searchWidth, topLeft[1] + searchHeight)
            roi = puzzle[topLeft[1]:botRight[1], topLeft[0]:botRight[0]]
            # print(i)

            # print(i,"meeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
            my_image_color = roi
            my_image_gray = cv2.cvtColor(my_image_color, cv2.COLOR_BGR2GRAY)
            ret, im_th = cv2.threshold(my_image_gray, 200, 255, cv2.THRESH_BINARY_INV)
            im_th = np.uint8(im_th)
            contours, hierarchy = cv2.findContours(im_th, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            my_image_color_org = my_image_color.copy()
            cv2.drawContours(my_image_color_org, contours, -1, (0, 255, 0), 3)
            temp2 = []
            for contour in contours:
                temp = []
                x, y, w, h = cv2.boundingRect(contour)
                temp.append(x)
                temp.append(y)
                temp.append(w)
                temp.append(h)
                if (abs(w - 63) <= 7 or abs(w - 68) <= 7) and abs(h - 280) <= 10:
                    r1, r2, r3, r4 = x, y, w, h
                    cv2.rectangle(my_image_color_org, (x, y), (x + w, y + h), (255, 0, 0), 3)
                    temp2.append(temp)

            if len(temp2) == 2:
                ans.append(temp2)
                print(wi)
                for j in temp2:
                    x, y, w, h = j[0], j[1], j[2], j[3]
                    if x >= 5 and x <= 15:
                        print("Left Block")
                        my_image = my_image_color[y:y + h, x:x + w]
                        target1 = my_image
                    else:
                        print('Right Block')
                        my_image = my_image_color[y:y + h, x:x + w]
                        target2 = my_image

                img1 = cv2.resize(target1, (70, 400))

                img2 = cv2.resize(target2, (70, 400))
                # cv2.imshow("six",img1)
                # cv2.imshow("si", img2)
                # cv2.waitKey(0)
                # print(type(img1))

                # r1=result(img1)
                bg = cv2.add(img1, np.array([40.0]))
                # cv2.imshow("bright", bg)
                # cv2.waitKey(0)

                gray = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
                # cv2.imshow("gray", gray)
                # cv2.waitKey(0)

                kernel = np.ones((5, 5), np.uint8)
                er = cv2.erode(gray, kernel, iterations=1)
                # cv2.imshow("ER", er)
                # cv2.waitKey(0)

                (thresh, bw) = cv2.threshold(er, 127, 255, cv2.THRESH_BINARY)
                # cv2.imshow("Black2white", Black2white)
                # cv2.waitKey(0)

                boxes = splitboxes(bw)
                # print("len of boes", len(boxes))

                questions = 2
                choices = 10

                # getting nonzero pixel values of each box
                mypixelval = np.zeros((questions, choices))

                countc = 0
                countr = 0

                for pic in boxes:
                    totalpixels = cv2.countNonZero(pic)
                    mypixelval[countr][countc] = totalpixels
                    countc += 1
                    if (countc == choices):
                        countr += 1
                        countc = 0

                # print(mypixelval)

                myindex = []
                for x in range(0, questions):
                    arr = mypixelval[x]
                    # print("arr",arr,arr[3])
                    minimum = np.amin(arr)
                    maximum = np.amax(arr)
                    columnindex = []
                    for i in range(10):
                        # print(arr[i],maximum,(arr[i]/maximum)*100)
                        if (arr[i] / maximum) * 100 <= 75.0:
                            columnindex.append(i)
                    # print("column indexes",columnindex)
                    if len(columnindex) != 1:
                        myindex.append("empty")
                    else:
                        myindex.append(columnindex[0])
                Numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
                #  print(myindex)
                score = ""
                for i in myindex:
                    if i == "empty":
                        score = "00000"
                        break
                    else:
                        score += Numbers[i]
                # print("the serial number is", score)
                r1 = score
                print("r1 is", r1)

                # r2=result(img2)
                r2 = "00000"

                bg = cv2.add(img2, np.array([40.0]))
                # cv2.imshow("bright", bg)
                # cv2.waitKey(0)

                gray = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
                # cv2.imshow("gray", gray)
                # cv2.waitKey(0)

                kernel = np.ones((5, 5), np.uint8)
                er = cv2.erode(gray, kernel, iterations=1)
                # cv2.imshow("ER", er)
                # cv2.waitKey(0)

                (thresh, bw) = cv2.threshold(er, 127, 255, cv2.THRESH_BINARY)
                # cv2.imshow("Black2white", Black2white)
                # cv2.waitKey(0)

                boxes = splitboxes(bw)
                # print("len of boes", len(boxes))

                questions = 2
                choices = 10

                # getting nonzero pixel values of each box
                mypixelval = np.zeros((questions, choices))

                countc = 0
                countr = 0

                for pic in boxes:
                    totalpixels = cv2.countNonZero(pic)
                    mypixelval[countr][countc] = totalpixels
                    countc += 1
                    if (countc == choices):
                        countr += 1
                        countc = 0

                # print(mypixelval)

                myindex = []
                for x in range(0, questions):
                    arr = mypixelval[x]
                    # print("arr",arr,arr[3])
                    minimum = np.amin(arr)
                    maximum = np.amax(arr)
                    columnindex = []
                    for i in range(10):
                        # print(arr[i],maximum,(arr[i]/maximum)*100)
                        if (arr[i] / maximum) * 100 <= 75.0:
                            columnindex.append(i)
                    # print("column indexes",columnindex)
                    if len(columnindex) != 1:
                        myindex.append("empty")
                    else:
                        myindex.append(columnindex[0])
                Numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
                #  print(myindex)
                score = ""
                for i in myindex:
                    if i == "empty":
                        score = ""
                        break
                    else:
                        score += Numbers[i]
                # print("the serial number is", score)
                r2 = score
             #   print("r2 is ", r2)
                r0 = str(r0)
                r0 = r0[2:-1]
               # print(r0, r1, r2)
                #outsheet.write(wi, 0, r0)
                if r1!="":
                    outsheet.write(wi, 1, int(r1))
                if r2!="":
                    outsheet.write(wi, 2, int(r2))

            outsheet.write(wi , 3, int(fname[1:]))
            wi+=1

        outworkbook.close()
        output="successfull"
        print(output)
        messages.info(request, 'Successfull!')

        return render(request,'index.html')
    else:

        return render(request, "index.html")
