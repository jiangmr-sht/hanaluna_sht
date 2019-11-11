#First, load the image processing module
import cv2
import numpy as np
from scipy import stats
from matplotlib import pyplot as plt

class EdgeCropper:
    def __init__(self, path, filters=None):
        #Load image
        self.im = cv2.imread(path)
        self.im_gray = cv2.imread(path, 0)
        self.row_count, self.column_count, _ = self.im.shape
        self.result = None
        self.save_path = './untitled.jpg'

        if filters == None:
            #Use the default thresholds
            self.mode_exclude_threshold = self.column_count * 0.1 #If the mode of certain rows has counts less than this value, it will be excluded.
            self.low_effective_length_threshold_by_row = self.column_count * 0.05 #If pixels other than the color with the most presence exist in number lower
                                                                 #than this value, the row will be regarded as illegal.
            self.low_effective_length_threshold_by_column = self.row_count * 0.05

        #Custom filters
        else:
            if filters[0] <= 1:
                self.mode_exclude_threshold = self.column_count * filters[0]
            else:
                self.mode_exclude_threshold = filters[0]
            if filters[1] <= 1:
                self.low_effective_length_threshold_by_row = self.column_count * filters[1]
            else:
                self.low_effective_length_threshold_by_row = filters[1]
            if filters[2] <= 1:
                self.low_effective_length_threshold_by_column = self.row_count * filters[2]
            else:
                self.low_effective_length_threshold_by_column = filters[2]


    def call(self):
        #Execute the general flow
        legal_region = self.GetLegalRegion()
        self.result = self.Crop(legal_region)
        self.Save()

    def AddSavePath(self, path):
        self.save_path = path

    def GetLegalRegion(self):
        row_modes = []

        #Process by row
        for row in range(self.row_count):
            imrow = self.im_gray[row]
            mode, count = stats.mode(imrow)
            if count <= self.mode_exclude_threshold:
                pass
            else:
                row_modes.append(mode)

        greatest_grayscale = stats.mode(row_modes)[0][0]
        row_start = None
        row_end = None

        #Find the first legal row
        for row in range(self.row_count):
            imrow = self.im_gray[row]
            mode, count = stats.mode(imrow)
            if mode == greatest_grayscale and count > (self.column_count - self.low_effective_length_threshold_by_row):
                pass
            else:
                row_start = row
                break

        if row_start == None:
            raise ValueError('Legal rows are not found. Please adjust thresholds.')

        #Find the last legal row
        for row in range(self.row_count):
            row = self.row_count-1 - row
            imrow = self.im_gray[row]
            mode, count = stats.mode(imrow)
            if mode == greatest_grayscale and count > (self.column_count - self.low_effective_length_threshold_by_row):
                pass
            else:
                row_end = row + 1 #Watch out for the border.
                break

        column_start = None
        column_end = None

        #Find the first legal column
        for column in range(self.column_count):
            imcolumn = self.im_gray[:,column]
            mode, count = stats.mode(imcolumn)
            if mode == greatest_grayscale and count > (self.row_count - self.low_effective_length_threshold_by_column):
                pass
            else:
                column_start = column
                break

        if column_start == None:
            raise ValueError('Legal columns are not found. Please adjust thresholds.')

        #Find the last legal column
        for column in range(self.column_count):
            column = self.column_count-1 - column
            imcolumn = self.im_gray[:,column]
            mode, count = stats.mode(imcolumn)
            if mode == greatest_grayscale and count > (self.row_count - self.low_effective_length_threshold_by_column):
                pass
            else:
                column_end = column + 1
                break

        return row_start, row_end, column_start, column_end

    def Crop(self, parameters):
        #Crop the image
        #Parameters: 0 for row_start, 1 for row_end, 2 for column_start, 3 for column_end
        im_cropped = self.im[parameters[0]:parameters[1], parameters[2]:parameters[3]]
        return im_cropped

    def Save(self):
        #Save the cropped image
        cv2.imwrite(self.save_path, self.result)

    def Plot(self):
        #Plot the original and cropped image
        plt.subplot(121)
        plt.imshow(self.im)
        plt.subplot(122)
        plt.imshow(self.result)
        plt.show()
