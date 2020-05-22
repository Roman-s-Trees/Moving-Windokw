# -*- coding: utf-8 -*-
"""
Created on Thu May 21 18:03:08 2020

@author: wlwee
"""

import os, PIL, pandas, glob
import deeplabcut ## uncomment when ready to test in DLC
import numpy as np
from PIL import Image, ImageDraw

os.chdir('C:/Users/wlwee/Documents/python/moving_treeline/CODE/Moving_Treeline')

def moving_window (x_1, y_1, x_2, y_2, stp, path_img_big, big_img_size, path_image_tree, config_path):
   
    textFile_filter_results = path_image_tree + 'results_image_filter.txt'
    ## filePath = String(date) + '_' + String(time) + '_datalog.txt'
    ## File filePath = SD.open (filePath , FILE_WRITE)
    ## filePath.println('date, hour, min, sec, T1, R1, T2, R2, R, G, B, L')
    ##
    textFile_filter_results = open(textFile_filter_results, 'w')
    textFile_filter_results.write('y_pixel,n_trees,n,n_caught_by_dlc_prob,n_caught_by_slope\n')
    
    x_rows = range(x_1, x_2, stp)
    y_rows = range(y_1, y_2, stp)
    
    for xpixel in x_rows:
        
        if 'img' in locals():
            img.close()
            print('closed img')
        
        Image.MAX_IMAGE_PIXELS = big_img_size
        img = PIL.Image.open(path_img_big)
        img.load()
        
        path_im_crop_xrow = path_image_tree + str(xpixel) + '/'
        
        if os.path.exists(path_im_crop_xrow):
            print(path_im_crop_xrow + ' exists')
        else:
            print(path_im_crop_xrow + ' made')
            os.mkdir(path_im_crop_xrow)
            
        textFile = path_im_crop_xrow + 'predicted_tree_coordinates.txt'
        textFile = open(textFile, 'w')
        textFile.write('raster,x_1,y_1,x_2,y_2,slope,intercept,tree_px,delta_tree,image_px\n')
        
        cropped_images = []     
        
        for ypixel in y_rows: 
            
            left = xpixel; upper = ypixel - 50; right = xpixel + 50; lower = ypixel
            path_im_crop = path_im_crop_xrow +  str(left) + '_' + str(upper) + '_' + str(right) + '_' + str(lower) + '.png'
            
            cropped_images.append(path_im_crop)
            
            if os.path.exists(path_im_crop):
                print (path_im_crop + ' exists')
            else:
                im_crop = img.crop((left, upper, right, lower))
                im_crop.save(path_im_crop)
                im_crop.close()        
                
        img.close()
        
        deeplabcut.analyze_time_lapse_frames(config_path, path_im_crop_xrow, frametype = '.png', shuffle = 2, save_as_csv = True)

        path_dlc_csv = glob.glob(path_im_crop_xrow + '*.csv')
        
        path_dlc_h5 = glob.glob(path_im_crop_xrow + '*.h5') ## costs a lot of storage space
        path_dlc_pickle = glob.glob(path_im_crop_xrow + '*.pickle') ## costs a lot of storage space

        ## we want to get rid of both the .pickle and .h5 files since we will not be using them
        for h5 in path_dlc_h5: 
            os.remove(h5)
        for pickle in path_dlc_pickle:
            os.remove(pickle)

        dat = pandas.read_csv(path_dlc_csv[0]) ## opens up the .csv file created by dlc

        dat = dat.iloc[2:] # gets rid of the first two rows of dat, which are strings and will cause erros
        
        n_caught_by_dlc_prob = 0; n_caught_by_slope = 0
        n_trees = 0; n = 0

        for row in dat.iterrows():

            n = n + 1

            crap, data = row
            
            image_dat = data[0]
            x_b = float(data[1]); y_b = float(data[2]); p1l = float(data[3])
            x_t = float(data[4]); y_t = float(data[5]); p2l = float(data[6])
            
            if (x_t - x_b) != 0:
                slope = (y_t - y_b)/(x_t - x_b)
            else:
                slope = 0
            
            intercept = y_b - slope * x_b
            path_img = path_im_crop_xrow + image_dat

            if p1l >= 0.9 and p2l >= 0.9:
                
                if slope > -2 and slope < -0.5:

                    n_trees = n_trees + 1
                    
                    textFile.write(os.path.basename(path_img).split('.')[0] + ',')
                    textFile.write(str(x_b) + ',' + str(y_b) + ',' + str(x_t) + ',' + str(y_t) + ',' + str(slope) + ',')
                    textFile.write(str(intercept) + '\n')
                    
                else:
                    n_caught_by_slope = n_caught_by_slope + 1                    
                    #os.remove(path_img)
                    
            else:
                
                n_caught_by_dlc_prob = n_caught_by_dlc_prob + 1
                os.remove(path_img)      

        img.close()
        
        textFile.close()
        textFile_filter_results.write(str(ypixel) + ',')
        textFile_filter_results.write(str(n_trees) + ',')
        textFile_filter_results.write(str(n) + ',')
        textFile_filter_results.write(str(n_caught_by_dlc_prob) + ',')
        textFile_filter_results.write(str(n_caught_by_slope) + '\n')
        
    textFile_filter_results.close()
            
x1 = 8000; x2 = 8001
y1 = 100; y2 = 12121 #maxy 16208
step = 5

im_size = 265568257

path_config = 'C:\\Users\\wlwee\\Documents\\python\\moving_treeline\\CODE\\moving_treeline_model3-Willem-2020-04-11\\config.yaml'
#path_config =  'C:\\Users\\wlwee\\Documents\\python\\moving_treeline\\CODE\\moving_treeline_model4-Willem-2020-04-14\\config.yaml'

path_firstwood = 'C:/Users/wlwee/Documents/python/moving_treeline/DATA/first_woods/Undistort_001_FirstWoods_A_1_R1C1.tif'
path_root_image_tree = 'C:/Users/wlwee/Documents/python/moving_treeline/DATA/moving_treeline/5_21_2020_testone/'
     
moving_window (x1, y1, x2, y2, step, path_firstwood, im_size, path_root_image_tree, path_config)            
            
            
            
            
            
            
            