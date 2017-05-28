# **Finding Lane Lines on the Road** 


## Table of Contents

* [Introduction](#introduction)
* [Image Processing Pipeline](#image-processing-pipeline)
  * [Procedure](#procedure)
  * [Parameters](#parameters)
* [Draw\_lines()](#draw_lines)
  * [Heuristics for classifying line segments to left lane and right lane](#heuristics-for-classifying-line-segments-to-left-lane-and-right-lane)
  * [Line generation using weighted linear fit](#line-generation-using-weighted-linear-fit)
  * [Diagnostic information in debug mode](#diagnostic-information-in-debug-mode)
* [Notes on generating grayscale images using HSV](#notes-on-generating-grayscale-images-using-hsv)
* [Discussions on shortcomings and possible improvements](#discussions-on-shortcomings-and-possible-improvements)
  * [Better conversion color image into grayscale](#better-conversion-color-image-into-grayscale)
  * [More adaptively setting model parameters](#more-adaptively-setting-model-parameters)
  * [Lane\-detection\-specific Canny and Hough algorithms](#lane-detection-specific-canny-and-hough-algorithms)
  * [Persistence of previously detected lanes](#persistence-of-previously-detected-lanes)
  

## Introduction

The goals of this project are the following:
* Make a pipeline that finds lane lines on the road in still images and videos
* Reflect on your work in a written report

Before diving into the details, here are a few quick showcases of the final results

**Images**: (All labeled images are in [test_images_output](test_images_output))

<img src="test_images_output/solidWhiteCurve.jpg" width="250"> <img src="test_images_output/solidYellowCurve.jpg" width="250"> <img src="test_images_output/whiteCarLaneSwitch.jpg" width="250">


**Videos:** (All labeled videos are in [test_videos_output](test_videos_output))

<img src="showcase1.gif" width="250"> <img src="showcase2.gif" width="250"> <img src="showcase3.gif" width="250">


## Image Processing Pipeline

### Procedure

The image processing pipeline consists of the following steps

  1. Covert color image to grayscale: 
  
        ```python
        img_gray = grayscale(image)
        ```
  
  2. Smooth image to suppress noise and spurious gradients in preparation of Canny edge detection: 
    
        ```python
        img_blur = gaussian_blur(img_gray, params.kernel_size)
        ```
  
  3. Canny edge detection:
  
        ```python
        img_canny = canny(img_blur, params.low_threshold, params.high_threshold)
        ```
  
  4. Define region of interest (ROI) 
        
        ```python
        masked_canny = region_of_interest(img_canny, vertices)
        ```
    
  5. Use Hough trasform to detect lines within ROI
        
        ```python
        line_img = hough_lines(masked_canny, 
                               params.rho, params.theta, params.threshold, 
                               params.min_line_len, params.max_line_gap)
        ```
  
  6. Overlay detected lines on image
  
        ```python 
        result  = weighted_img(line_img, image)
        ```

### Parameters

A set of parameters are defined for Gaussian blur, Canney edge detection, and Hough transform

```python

class piplineParameters():
    def __init__(self):
        self.kernel_size=11 # for gaussian blur
        self.low_threshold = 30
        self.high_threshold = 100 # for canny edge detection
        # hough transformation parameters
        self.rho = 2 # distance resolution in pixels of the Hough grid
        self.theta = np.pi/180 # angular resolution in radians of the Hough grid
        self.threshold = 20 # minimum number of votes (intersections in Hough grid cell)
        self.min_line_len = 40 #minimum number of pixels making up a line
        self.max_line_gap = 40 # maximum gap in pixels between connectable line segments)

```

In addition the ROI is defined as follows, where ```imshape[0]``` and ```imshape[1]``` are the Y and X size of the image

```python

vertices = np.array([[(0,imshape[0]),
                    (imshape[1]*0.48, imshape[0]*0.6), 
                    (imshape[1]*0.52, imshape[0]*0.6), 
                    (imshape[1],imshape[0])]], dtype=np.int32)

```

## Draw_lines()

The function draw_lines() is modified to achieve the following:

  1. Determined if a certain line segment returned by Hough transform belongs to left lane or right lane, or it does not belong to either lane and should be reject

  2. Based on accepted line segments, generate and draw one line for the left lane and the right lane respectively
  
  3. In debug mode (controlled by flag ```DEBUG```), output diagnostic information about accepted left /right lane line segments, rejected line segments and overall confidence in final lane lines.


### Heuristics for classifying line segments to left lane and right lane
For item 1, the heuristics implemented are:

  * Left lane line segments should have slope s < 0 and right lane line segments should have slope s > 0, where s = (y2-y1) / (x2-x1)
  This heuristic is further narrowed down to 
      ```math
      left lane: -5 < s < -0.4
      right lane: 5 > s > 0.4
      ```
  * Sometimes a line segment appear on the left of the screen but has a slope that satisfy the right lane condition, this can be detected and rejected by checking if the end points of the line is on the correct half of the screen
    ```math
    left lane: x1 < mid_x*1.1 and x2 < mid_x*1.1
    right lane: x1 > mid_x*0.9 and x2 > mid_x*0.9
    ```
    where mid_x is half of the image size in X direction.
  
  * Additionally, we can also check the x interception point at the bottom of the screen fall in the right range
    ```python
    s = float((y2-y1)/(x2-x1))  # slope                        
    b = float(y1*x2 - y2*x1) / (x2-x1)  # interscept as in y=s*x+b
    if s !=0:
        x_intercept = (img.shape[0]-b)/s
    else:
        x_intercept = np.inf
    ```
    The heuristic is
    ```math
    left alne: 0.0 < x_intercept/max_x < 0.5
    right lane: 0.5 < x_intercept/max_x < 1.0
    ```
    where max_x is the size of the image along the x direction.
    
### Line generation using weighted linear fit

After the line segments are properly classified, the overall lane lines are generated using linear fit of all accepted points belonging to the lane, 
and the points are weighted according the original length (in fact length squared) of the line segments. 
Longer line segments have large weights.


### Diagnostic information in debug mode

Diagnostic information is helpful to see what is happening under the hood and provides insight in tuning parameters especially when working on the more challenging cases.

The following is an example video output in debug mode

![debug video](showcase4.gif)

In debug mode, the draw_lines() function does the following:

  * line segments classified into right lane are marked blue
  * line segments classified into left lane are marked green
  * Rejected line segments are marked magenta
  * Final lane lines are marked red
  * When goodness-of-fit (GOF) falls below 0.7, print out relevant message in terminal

We can see that, in addition to correct classification of line segments into left lane and right lane, 
the program is effective in rejecting a lot of line segments due to shadows from the hood of the car, tree on the side of the road, 
skid marks on the road and road color changes.


## Notes on generating grayscale images using HSV

In working on images with yellow lanes, and especially in working with challenge.mp4, I noticed that direct conversion from RGB to grayscale would yield
very weak contrast between yellow color lane marking and light grey color road surface.

One thing I did to alleviate this is to use the V channel (brightness) in HSV mode image as the "grayscale" image instead of actual grayscale image
generated by ```cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)```

Here is a frame from challenge.mp4, with yellow lane on the right and light grey road surface.

![](test_images/challenge_trouble.jpg)

First we use the grayscale image generated by ```cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)```

![gray scale](using_gray.png)

As we can see, even though the yellow lanes are fairly visible in the color image, once converted into grayscale, it lost its contract to the road surface.
Consequently, the Canny edge detection and Hough transform missed it.

On the other hand, if we use the V channel of HSV colorspace, we get the following higher contrast grayscale image 
and lane lines are properly generated, as shown below.

![hsv v](using_HSV_v.png)



## Discussions on shortcomings and possible improvements

In this section I will discuss the possible improvements all of which ties to shortcomings of the current implementation of the program.

### Better conversion color image into grayscale

As discussed in the section [Notes on generating grayscale images](#notes-on-generating-grayscale-images), even though the yellow lane marking are
very visible to human eyes, when converted to grayscale image, it lost its contract. My solution was using the V channel of the HSV colorspace of 
the image. However, I suspect they are better ways. 

Given the goal is to specifically enhance lane marking visibility, an lane markings are usually white or yellow-ish. We can perhaps selectively boost
these colors. This would make all the down stream processing more robust.

### More adaptively setting model parameters

Currently all model parameters are hand-crafted and hard-coded. A one-size-fit-all set of parameters would have incur some compromises under
different road conditions and camera configurations. It would be better to let the program determine the best ROI, and parameters for smoothing,
edge detection and line detection, given certain image characteristics. This would allow optimized performance under all conditions.
 
### Lane-detection-specific Canny and Hough algorithms

In lane detection, we have the prior knowledge that lanes are roughly pointing 45 degress forward, the lane markings are lines with certain typical width, 
and as lanes go forward if, it is segmented lane, each segments become shorter.

If we could use this knowledge, we could implement application specific Canny edge detection and Hough line detection algorithms. For example, we could
preferentially detect edges gradient around our typical lane angles. In Hough transformation, we could require line means double lines that are close to 
each other (two edges of a lane marking). Within different portions of the image, we could use different sets of Hough parameters. For eaxmple, in the middle
of the image where lanes almost meet the horizon, we allow shorter lines to be detected compared to the bottom of the images, where lanes are closer to us.

### Persistence of previously detected lanes
 
For lane detection in the challenge.mp4, there are still a few frames near t = 4s, where the right lane lacked line segments and 
right lane line was not generated successfully. In addition, in most of the videos, the lanes are jittering (rapidly making small adjustment). 
These are because in the way the program is written, it only considers the present moment, without retaining any history of detected lanes in 
previous frames.

Because we know that lanes change gradually in reality, so the current and successive frames should yield lanes with a small and gradual adjustment from the 
previous frame. This would allows us to (1) more easily reject irrelevant line segments (2) have estimated lane lines even if current frame lacks good
features to generate them (3) provide smooth lane guidance without unnecessary jitteirng.
