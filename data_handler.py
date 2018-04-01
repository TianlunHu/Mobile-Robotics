import cv2
import sys, os
from random import randint, sample
import numpy as np

class Process:
    '''
    functions:
    OSWalk() = walks through directory and lists all the images in the directory
    generateData(num) = selects a random set of 'num' images from the listed images
    process(num, indices) = converts the selected 'num' images to 128*num samples
    fetch(num) = selects a random set of 'num' samples from the produced samples using process()

    helper functions:
    getLabels() = walks through directory and populates the labels
    getName(name) = converts ./path/to/here/img.png to here/img.png
    reset() = resets the counters when you have used up all the images
    numimages() = prints total number of images in the directory
    numsamples() = prints total number of samples generated from selected images
    remimages() = prints total number of images that remain in the directory
    remsamples() = prints total number of samples that remain from the selected lot of images
    '''

    def __init__(self, location, height = 224, width = 224, depth = 3):
        self.img2labels = dict()
        self.idx2img = dict()

        self.location = location
        self.height = height
        self.width = width
        self.depth = depth
        self.numImages = 0
        self.numSamples = 0
        self.imageLocs = []

        self.sampleImages = []
        self.remImages = []
        self.remSamples = []

        # OS Walk for getting all image files
        self.OSWalk()
        # print number of images
        self.numimages()
        # populate labels dict
        self.getLabels()


    def OSWalk(self):
        images = [os.path.join(root, name) for root, dirs, files in os.walk(self.location)
             for name in files if name.endswith((".png", ".jpg", ".jpeg", ".gif"))]
        self.imageLocs = images

        for i in range(len(images)):
            a,b = images[i].split('\\')
            self.imageLocs[i] = a + '/' + b

        # array to store which image has been used
        self.numImages = len(self.imageLocs)
        self.remImages = np.ones((self.numImages), dtype = bool)



    def generateData(self, num):
        ctr = 0
        indices = ['']*num
        rem = np.sum(self.remImages)

        # Pick random images
        if rem < num:
            print('Number of Images left to select: ', rem)
            print('Generating samples for the remaining images')

        num = min(rem, num) # only activated when the number of images left is less than the request

        while ctr<num:
            idx = randint(0,self.numImages-1)
            if self.remImages[idx]==True:
                self.remImages[idx] = False
                indices[ctr] = self.imageLocs[idx]
                ctr += 1

        # array to store which sample has been used
        self.numSamples = 128*num
        self.remSamples = np.ones((self.numSamples), dtype = bool)

        # generate samples
        self.process(num, indices)



    def process(self, num, indices):
        print('Generating Samples .... ')

        self.sampleImages = np.zeros((num*128, self.height, self.width, self.depth), dtype=np.uint8)

        idx = 0
        for i in range(num):
            # read image
            img = cv2.resize(cv2.imread(indices[i], 1), (455,256), interpolation = cv2.INTER_CUBIC)
            name = self.getName(indices[i])

            # generate 128 random indices for crop
            for j in range(idx, idx+128):
                x = randint(0,31)
                y = randint(0,230)
                self.sampleImages[j, :, :, :] = img[x:x + self.height, y:y + self.width, :].copy()
                self.idx2img[j] = name
            idx += 128



    def fetch(self, num):
        samples = np.zeros((num, self.height, self.width, self.depth), dtype=np.float)
        labels = ['']*num
        ctr = 0
        flag = True
        # number of remaining samples
        rem = np.sum(self.remSamples)

        if rem<num:
            flag = False
            print("Number of samples left to select: ", rem)

        else:
            while ctr<num:
                idx = randint(0,self.numSamples-1)
                if self.remSamples[idx]==True:
                    self.remSamples[idx] = False

                    # normalize image to be in 0-1 range
                    temp = self.sampleImages[idx, :, :, :].astype(float)
                    temp *= 1/temp.max()

                    # assign sample and labels
                    samples[ctr,:,:,:] = temp
                    labels[ctr] = self.img2labels[self.idx2img[idx]]
                    ctr += 1

        return [flag, samples, labels]



    def getLabels(self):
        f1 = open(self.location+'dataset_test.txt')
        lines = f1.readlines()
        f2 = open(self.location+'dataset_train.txt')
        lines2 = f2.readlines()

        # append the total list and process labels
        lines.extend(lines2)
        numLines = len(lines)

        for i in range(numLines):
            line = lines[i].strip()
            line = line.split()
            self.img2labels[line[0]] = list(map(float,line[1:8]))



    def getName(self, loc):
        ctr = 0
        for i in range(len(loc)):
            if loc[i]=='/':
                ctr += 1
            if ctr==2:
                return loc[i+1:]



    def reset(self):
        self.remImages = np.ones((self.numImages), dtype = bool)



    def numimages(self):
        print('The total number of images are: ', self.numImages)



    def numsamples(self):
        print('The total number of samples are: ', self.numSamples)



    def remsamples(self):
        print('The number of samples that remain are: ',np.sum(self.remSamples))



    def remimages(self):
        print('The number of images that remain are: ',np.sum(self.remImages))