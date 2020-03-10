import matplotlib.pyplot as plt
import numpy as np
import cv2
import PIL
import math

class ImageProcessor:
    def __init__(self):
        self.bundler = HoughBundler()

    def process_image(self, image):
        image_y, image_x, _ = image.shape

        hsv_img = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

        red1 = (0, 100, 100)
        red2 = (5, 255, 255)
        mask1 = cv2.inRange(hsv_img, red1, red2)

        r1 = (175, 100, 100)
        r2 = (180, 255, 255)
        mask2 = cv2.inRange(hsv_img, r1, r2)
        
        combinedMask = cv2.bitwise_or(mask1, mask2)

        gaussMask = self.gaussian_blur(combinedMask, 15)
        kernel = np.ones((5,5),np.uint8)
        dilation = cv2.dilate(combinedMask, kernel)
        edges = cv2.bitwise_xor(combinedMask, dilation, 5)
        lines = cv2.HoughLinesP(edges, rho=2, theta=np.pi/180, threshold=30, minLineLength=2, maxLineGap=2)
        
        bundler = HoughBundler()
        bundled_lines = bundler.process_lines(lines)

        (midpoint, bounding_box) = self.find_midpoint_and_bounding_box(bundled_lines)

        # Find the slopes of the bundles
        slopeBundles = bundler.bundleBySlope(bundled_lines)
        index=0
        dominant_slope = 0
        max_len = 0
        average_bundle_slopes = []
        for bun in slopeBundles:
            #print(len(bun))
            #print("\n")
            bundle_length = 0
            average_orientation = 0
            for line in bun:
                x1 = line[0][0]
                y1 = line[0][1]
                x2 = line[1][0]
                y2 = line[1][1]
                length = math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2))
                line_orientation = math.atan2((line[1][1] - line[0][1]), (line[1][0] - line[0][0]))
                average_orientation += line_orientation * length # weighted orientation
                bundle_length += length
            #print(bundle_length)
            #bundle_length /= len(bun)
            average_orientation /= bundle_length
            
            #print(average_orientation)
            average_bundle_slopes.append(average_orientation)
            if bundle_length > max_len:
                max_len = bundle_length
                # Likely dominant slope
                dominant_slope = index
                #print("here")
            index += 1
        bearing = math.degrees(average_bundle_slopes[dominant_slope])
        
        return (midpoint, bearing)
        
    def gaussian_blur(self, img, kernel_size):
        """Applies a Gaussian Noise kernel"""
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

    def find_midpoint_and_bounding_box(self, bundled_lines):
        bounding_box = self.find_bounding_box(bundled_lines)
        if bounding_box:
            xmin = bounding_box[0]
            xmax = bounding_box[1]
            ymin = bounding_box[2]
            ymax = bounding_box[3]
            midpoint = ((xmax+xmin)/2, (ymax+ymin)/2)
            #print(midpoint)
            return (midpoint, bounding_box)

    def find_bounding_box(self, bundled_lines):
        if bundled_lines:
            xmin = bundled_lines[0][0][0]
            xmax = bundled_lines[0][0][0]
            ymin = bundled_lines[0][1][1]
            ymax = bundled_lines[0][1][1]
            for line in bundled_lines:
                x1 = line[0][0]
                y1 = line[0][1]
                x2 = line[1][0]
                y2 = line[1][1]
                if x1 < xmin:
                    xmin = x1
                elif x1 > xmax:
                    xmax = x1
                if x2 < xmin:
                    xmin = x2
                elif x2 > xmax:
                    xmax = x2

                if y1 < ymin:
                    ymin = y1
                elif y1 > ymax:
                    ymax = y1

                if y2 < ymin:
                    ymin = y2
                elif y2 > ymax:
                    ymax = y2
            return (xmin, xmax, ymin, ymax)


    
class HoughBundler:
    '''Clasterize and merge each cluster of cv2.HoughLinesP() output
    a = HoughBundler()
    foo = a.process_lines(houghP_lines, binary_image)
    '''

    def get_orientation(self, line):
        '''get orientation of a line, using its length
        https://en.wikipedia.org/wiki/Atan2
        '''
        orientation = math.atan2(abs((line[0] - line[2])), abs((line[1] - line[3])))
        return math.degrees(orientation)

    def checker(self, line_new, groups, min_distance_to_merge, min_angle_to_merge):
        '''Check if line have enough distance and angle to be count as similar
        '''
        for group in groups:
            # walk through existing line groups
            for line_old in group:
                # check distance
                if self.get_distance(line_old, line_new) < min_distance_to_merge:
                    # check the angle between lines
                    orientation_new = self.get_orientation(line_new)
                    orientation_old = self.get_orientation(line_old)
                    # if all is ok -- line is similar to others in group
                    if abs(orientation_new - orientation_old) < min_angle_to_merge:
                        group.append(line_new)
                        return False
        # if it is totally different line
        return True

    def DistancePointLine(self, point, line):
        """Get distance between point and line
        http://local.wasp.uwa.edu.au/~pbourke/geometry/pointline/source.vba
        """
        px, py = point
        x1, y1, x2, y2 = line

        def lineMagnitude(x1, y1, x2, y2):
            'Get line (aka vector) length'
            lineMagnitude = math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2))
            return lineMagnitude

        LineMag = lineMagnitude(x1, y1, x2, y2)
        if LineMag < 0.00000001:
            DistancePointLine = 9999
            return DistancePointLine

        u1 = (((px - x1) * (x2 - x1)) + ((py - y1) * (y2 - y1)))
        u = u1 / (LineMag * LineMag)

        if (u < 0.00001) or (u > 1):
            #// closest point does not fall within the line segment, take the shorter distance
            #// to an endpoint
            ix = lineMagnitude(px, py, x1, y1)
            iy = lineMagnitude(px, py, x2, y2)
            if ix > iy:
                DistancePointLine = iy
            else:
                DistancePointLine = ix
        else:
            # Intersecting point is on the line, use the formula
            ix = x1 + u * (x2 - x1)
            iy = y1 + u * (y2 - y1)
            DistancePointLine = lineMagnitude(px, py, ix, iy)

        return DistancePointLine

    def get_distance(self, a_line, b_line):
        """Get all possible distances between each dot of two lines and second line
        return the shortest
        """
        dist1 = self.DistancePointLine(a_line[:2], b_line)
        dist2 = self.DistancePointLine(a_line[2:], b_line)
        dist3 = self.DistancePointLine(b_line[:2], a_line)
        dist4 = self.DistancePointLine(b_line[2:], a_line)

        return min(dist1, dist2, dist3, dist4)

    def merge_lines_pipeline_2(self, lines):
        'Clusterize (group) lines'
        groups = []  # all lines groups are here
        # Parameters to play with
        min_distance_to_merge = 30
        min_angle_to_merge = 30
        # first line will create new group every time
        groups.append([lines[0]])
        # if line is different from existing gropus, create a new group
        for line_new in lines[1:]:
            if self.checker(line_new, groups, min_distance_to_merge, min_angle_to_merge):
                groups.append([line_new])

        return groups

    def merge_lines_segments1(self, lines):
        """Sort lines cluster and return first and last coordinates
        """
        orientation = self.get_orientation(lines[0])

        # special case
        if(len(lines) == 1):
            return [lines[0][:2], lines[0][2:]]

        # [[1,2,3,4],[]] to [[1,2],[3,4],[],[]]
        points = []
        for line in lines:
            points.append(line[:2])
            points.append(line[2:])
        # if vertical
        if 45 < orientation < 135:
            #sort by y
            points = sorted(points, key=lambda point: point[1])
        else:
            #sort by x
            points = sorted(points, key=lambda point: point[0])

        # return first and last point in sorted group
        # [[x,y],[x,y]]
        return [points[0], points[-1]]

    def process_lines(self, lines):
        '''Main function for lines from cv.HoughLinesP() output merging
        for OpenCV 3
        lines -- cv.HoughLinesP() output
        '''
        lines_x = []
        lines_y = []
        # for every line of cv2.HoughLinesP()
        for line_i in [l[0] for l in lines]:
                orientation = self.get_orientation(line_i)
                # if vertical
                if 45 < orientation < 135:
                    lines_y.append(line_i)
                else:
                    lines_x.append(line_i)

        lines_y = sorted(lines_y, key=lambda line: line[1])
        lines_x = sorted(lines_x, key=lambda line: line[0])
        merged_lines_all = []

        # for each cluster in vertical and horizantal lines leave only one line
        for i in [lines_x, lines_y]:
                if len(i) > 0:
                    groups = self.merge_lines_pipeline_2(i)
                    merged_lines = []
                    for group in groups:
                        merged_lines.append(self.merge_lines_segments1(group))

                    merged_lines_all.extend(merged_lines)

        return merged_lines_all
    
    def bundleBySlope(self, lines):
        groups = []
        min_angle_to_merge = 30
        groups.append([lines[0]])
        for line_new in lines[1:]:
            has_group = False
            for group in groups:
                for line_old in group:
                    old_orientation = math.atan2((line_old[0][0] - line_old[1][0]), (line_old[0][1] - line_old[1][1]))
                    new_orientation = math.atan2((line_new[0][0] - line_new[1][0]), (line_new[0][1] - line_new[1][1]))
                    if abs(math.degrees(new_orientation) - math.degrees(old_orientation)) < min_angle_to_merge:
                        group.append(line_new)
                        has_group = True
                        break
            if not has_group:
                groups.append([line_new])
        
        return groups
