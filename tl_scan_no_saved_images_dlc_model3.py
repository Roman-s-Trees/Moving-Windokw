

import os, PIL, pandas, glob
import deeplabcut ## uncomment when ready to test in DLC
import numpy as np
from PIL import Image, ImageDraw

## uncomment this bit if you want to train overnight and then have it immediately go into testing.xdcfvgyhjuk
path_config = 'C:\\Users\\wlwee\\Documents\\python\\moving_treeline\\CODE\\moving_treeline_model3-Willem-2020-04-11\\config.yaml'

# if you uncomment this and dont change iteration in .yaml file or change the shuffle it will overright your previous model
#deeplabcut.train_network(path_config, shuffle=2, maxiters=300000,gputouse=0,displayiters=1000)

os.chdir('C:/Users/wlwee/Documents/python/moving_treeline/CODE/deeplabcut')

def moving_window (x_1, y_1, x_2, y_2, stp, path_img_big, path_image_tree, config_path):

    textFile_filter_results = path_image_tree + 'results_image_filter.txt'
    ## filePath = String(date) + '_' + String(time) + '_datalog.txt'
    ## File filePath = SD.open (filePath , FILE_WRITE)
    ## filePath.println('date, hour, min, sec, T1, R1, T2, R2, R, G, B, L')
    ##
    textFile_filter_results = open(textFile_filter_results, 'w')
    textFile_filter_results.write('y_pixel,n_trees,n,n_caught_by_dlc_prob,n_caught_by_slope,n_caught_by_array_error,n_caught_by_tree_pixels\n')
    
    x_rows = range(x_1, x_2, stp)
    y_rows = range(y_1, y_2, stp)
    
    for ypixel in y_rows:
        
        if 'img' in locals():
            img.close()
            print('closed img')
        
        Image.MAX_IMAGE_PIXELS = 265568257
        img = PIL.Image.open(path_img_big)
        img.load()
        
        path_im_crop_yrow = path_image_tree + str(ypixel) + '/'
        
        if os.path.exists(path_im_crop_yrow):
            print(path_im_crop_yrow + ' exists')
        else:
            print(path_im_crop_yrow + ' made')
            os.mkdir(path_im_crop_yrow)
            
        textFile = path_im_crop_yrow + 'predicted_tree_coordinates.txt'
        textFile = open(textFile, 'w')
        textFile.write('raster,x_1,y_1,x_2,y_2,slope,intercept,tree_px,delta_tree,image_px\n')
        
        cropped_images = []
        
        for xpixel in x_rows: 
            
            left = xpixel; upper = ypixel - 50; right = xpixel + 50; lower = ypixel
            path_im_crop = path_im_crop_yrow +  str(left) + '_' + str(upper) + '_' + str(right) + '_' + str(lower) + '.png'
            
            cropped_images.append(path_im_crop)
            
            if os.path.exists(path_im_crop):
                print (path_im_crop + ' exists')
            else:
                im_crop = img.crop((left, upper, right, lower))
                im_crop.save(path_im_crop)
                im_crop.close()
        
        img.close()
                
        deeplabcut.analyze_time_lapse_frames(config_path, path_im_crop_yrow, frametype = '.png', shuffle = 2, save_as_csv = True)
        
        path_dlc_csv = glob.glob(path_im_crop_yrow + '*.csv')
        
        path_dlc_h5 = glob.glob(path_im_crop_yrow + '*.h5') ## costs a lot of storage space
        path_dlc_pickle = glob.glob(path_im_crop_yrow + '*.pickle') ## costs a lot of storage space
        
        ## we want to get rid of both the .pickle and .h5 files since we will not be using them
        for h5 in path_dlc_h5: 
            os.remove(h5)
        for pickle in path_dlc_pickle:
            os.remove(pickle)
        
        dat = pandas.read_csv(path_dlc_csv[0]) ## opens up the .csv file created by dlc
        
        os.remove(path_dlc_csv[0])
        
        dat = dat.iloc[2:] # gets rid of the first two rows of dat, which are strings and will cause erros
        
        n_caught_by_dlc_prob = 0; n_caught_by_slope = 0
        n_caught_by_array_error = 0; n_caught_by_tree_pixels = 0
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
            
            path_img = path_im_crop_yrow + image_dat
            
            if p1l >= 0.9 and p2l >= 0.9:
                
                if slope > -2 and slope < -0.5:
                    
                    img = Image.open(path_img).convert('L')
                    m = np.array(img)
                    x_min = round(x_b,0); x_max = round(x_t,0)
                    
                    m_mean = np.mean(m)
                    
                    pixel_values = []
                    
                    if x_min < 50 and x_max < 50:
                        for i in range(int(x_min),int(x_max)):
                            pixel_i = slope * i + intercept
                            pixel_i = round(pixel_i,0)
                            
                            if pixel_i < 50:
                                pixel_values.append(m[int(pixel_i), i])
                        
                        if len(pixel_values) > 0:
                            tree_px = float(sum(pixel_values)/len(pixel_values))
                            delta_tree = m_mean - tree_px
                        
                        if tree_px is not None and tree_px > 45 and tree_px < 114 and delta_tree > 42 and delta_tree < 137:
                            n_trees = n_trees + 1

                            img.close()
                            os.remove(path_img)
                            
                            '''
                            img = Image.open(path_img)
                            draw = ImageDraw.Draw(img)
                            shape_line = [(x_b,y_b),(x_t,y_t)]
                            draw.line(shape_line, fill = 'blue', width = 0)
                            draw.point((x_b, y_b), fill = 'red')
                            draw.point((x_t, y_t), fill = 'red')
                            img.save(path_img)
                            
                            img.close()
                            '''
                            textFile.write(os.path.basename(path_img).split('.')[0] + ',')
                            textFile.write(str(x_b) + ',' + str(y_b) + ',' + str(x_t) + ',' + str(y_t) + ',' + str(slope) + ',')
                            textFile.write(str(intercept) + ',' + str(tree_px) + ',')
                            textFile.write(str(delta_tree) + ',' + str(m_mean) + '\n')
                            
                        else:
                            n_caught_by_tree_pixels = n_caught_by_tree_pixels + 1
                            
                            img.close()
                            os.remove(path_img)
                            
                            '''
                            path_img = path_im_crop_yrow + image_dat
                            img = Image.open(path_img)
                            draw = ImageDraw.Draw(img)
                            shape_line = [(x_b,y_b),(x_t,y_t)]
                            draw.line(shape_line, fill = 'green', width = 0)
                            draw.point((x_b, y_b), fill = 'cyan')
                            draw.point((x_t, y_t), fill = 'cyan')
                            img.save(path_img)
                            
                            img.close()
                            '''
                    else:
                        n_caught_by_array_error = n_caught_by_array_error + 1
                        
                        img.close()
                        os.remove(path_img)
                else:
                    n_caught_by_slope = n_caught_by_slope + 1
                    
                    img.close()
                    os.remove(path_img)
                    
                    '''
                    path_img = path_im_crop_yrow + image_dat
                    img = Image.open(path_img)
                    draw = ImageDraw.Draw(img)
                    shape_line = [(x_b,y_b),(x_t,y_t)]
                    draw.line(shape_line, fill = 'orange', width = 0)
                    draw.point((x_b, y_b), fill = 'yellow')
                    draw.point((x_t, y_t), fill = 'yellow')
                    img.save(path_img)
                            
                    img.close()
                    '''
            else:
                n_caught_by_dlc_prob = n_caught_by_dlc_prob + 1
                os.remove(path_img)
                
                '''
                path_img = path_im_crop_yrow + image_dat
                img = Image.open(path_img)
                draw = ImageDraw.Draw(img)
                shape_line = [(x_b,y_b),(x_t,y_t)]
                draw.line(shape_line, fill = 'red', width = 0)
                draw.point((x_b, y_b), fill = 'cyan')
                draw.point((x_t, y_t), fill = 'cyan')
                img.save(path_img)
                            
                img.close()
                '''
        textFile.close()
        textFile_filter_results.write(str(ypixel) + ',')
        textFile_filter_results.write(str(n_trees) + ',')
        textFile_filter_results.write(str(n) + ',')
        textFile_filter_results.write(str(n_caught_by_dlc_prob) + ',')
        textFile_filter_results.write(str(n_caught_by_slope) + ',')
        textFile_filter_results.write(str(n_caught_by_array_error) + ',')
        textFile_filter_results.write(str(n_caught_by_tree_pixels) + '\n')
    textFile_filter_results.close()
        
x1 = 5140; x2 = 11200
y1 = 1170; y2 = 16000 #maxy 16208
step = 5

path_config = 'C:\\Users\\wlwee\\Documents\\python\\moving_treeline\\CODE\\moving_treeline_model3-Willem-2020-04-11\\config.yaml'
#path_config =  'C:\\Users\\wlwee\\Documents\\python\\moving_treeline\\CODE\\moving_treeline_model4-Willem-2020-04-14\\config.yaml'

path_firstwood = 'C:/Users/wlwee/Documents/python/moving_treeline/DATA/first_woods/Undistort_001_FirstWoods_A_1_R1C1.tif'
path_root_image_tree = 'C:/Users/wlwee/Documents/python/moving_treeline/DATA/dlc_tl_scan/'
     
moving_window (x1, y1, x2, y2, step, path_firstwood, path_root_image_tree, path_config)