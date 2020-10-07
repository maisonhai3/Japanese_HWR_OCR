from skimage.morphology import skeletonize
import numpy as np
import random
import cv2
import os


def get_digit_location(text_image, digit_image, point, size_text, random_space=True):
    h, w, c = text_image.shape
    d_h, d_w = digit_image.shape

    if random_space:
        space = random.randint(3, 5)
    else:
        space = 3

    begin_point = point.copy()
    begin_point[0] += space
    begin_point[1] = random.randint(max(1, point[1] - 7), point[1])

    # limit of digit size
    scale = 1.5
    limited_sz = (max(0, w - begin_point[0]), min(int(size_text[1] * scale), h - begin_point[1]))

    if size_text[0] > limited_sz[0] or size_text[1] > limited_sz[1]:
        ratio_w = limited_sz[0] / d_w
        ratio_h = limited_sz[1] / d_h
        ratio = min(ratio_w, ratio_h)

    # range of digit ratio
    min_h = min(size_text[1], limited_sz[1])
    max_h = max(size_text[1], limited_sz[1])

    min_w = min(size_text[0], limited_sz[0])
    max_w = max(size_text[0], limited_sz[0])

    ratio_w = [min_w / d_w, max_w / d_w]
    ratio_h = [min_h / d_h, max_h / d_h]

    ratio_list = [min(ratio_w[0], ratio_h[0]), min(ratio_w[1], ratio_h[1])]

    if ratio_list[1] > 1.0 and ratio_list[0] < 1.0:
        ratio = random.uniform(1.0, ratio_list[1])
    else:
        ratio = random.uniform(ratio_list[0], ratio_list[1])

    return begin_point, ratio


def crop_image(binary_dimage):
    clone_image = binary_dimage.copy()
    contours= cv2.findContours(clone_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 2:
        contours = contours[0]

    if len(contours) == 3:
        contours = contours[1]
    boundRect = [None] * len(contours)
    for i in range(len(contours)):
        x, y, w, h = cv2.boundingRect(contours[i])
        boundRect[i] = [x, y, x+w, y+h]
    # print(boundRect)

    x0 = sorted(boundRect, key=lambda x:x[0])[0][0]
    y0 = sorted(boundRect, key=lambda x:x[1])[0][1]
    x1 = sorted(boundRect, key=lambda x:x[2], reverse=True)[0][2]
    y1 = sorted(boundRect, key=lambda x:x[3], reverse=True)[0][3]

    # print(x0, y0, x1, y1)
    cropped_image = binary_dimage[y0:y1, x0:x1]

    return cropped_image


def resize_digit_image(digit_image, ratio):
    digit_image = cv2.resize(digit_image, None, fx = ratio, fy = ratio)
    return digit_image


def count_coutour(binary_image):
    clone_image = binary_image.copy()

    contours = cv2.findContours(clone_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 2:
        return len(contours[0])
    else:
        return len(contours[1])


def denoising(binary_image, all_mode = False):
    clone_image = binary_image.copy()
    if count_coutour(binary_image) > 1 or all_mode:
        # erosion
        kernel = np.ones((2, 2), np.uint8)
        while True:
            erosion = cv2.erode(binary_image, kernel)
            if np.count_nonzero(erosion) == 0:
                erosion = binary_image
                break
            binary_image = erosion

        i_dilate = max(binary_image.shape)
        kernel = np.ones((3, 3), np.uint8)
        for i in range(i_dilate):
            dilate = cv2.dilate(erosion, kernel)
            dilate = np.dstack((dilate, clone_image))
            erosion = np.amin(dilate, axis=2)

        return erosion
    return binary_image


def standardized_digit_image(digit_image, dilate = 1):
    _, binary_image = cv2.threshold(digit_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # cv2.namedWindow('binary_image', cv2.WINDOW_NORMAL)
    # cv2.imshow('binary_image', binary_image)
    binary_image = denoising(binary_image, all_mode=True)
    # cv2.namedWindow('denoising_image', cv2.WINDOW_NORMAL)
    # cv2.imshow('denoising_image', binary_image)
    binary_image = binary_image / 255.0
    skeleton = skeletonize(binary_image)
    skeleton = skeleton.astype(np.uint8) * 255
    # cv2.namedWindow('skeleton', cv2.WINDOW_NORMAL)
    # cv2.imshow('skeleton', skeleton)

    # dilation
    kernel = np.ones((2, 2), np.uint8)
    dilation = cv2.dilate(skeleton, kernel, iterations=dilate)
    #
    # cv2.namedWindow('dilation', cv2.WINDOW_NORMAL)
    # cv2.imshow('dilation', skeleton)
    # cv2.waitKey()
    return dilation


def thiner_image(digit_image, No_scale=4):
    _, binary_image = cv2.threshold(digit_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    erode_list = [digit_image]
    binary_image = denoising(binary_image, all_mode=True)
    No_contour = count_coutour(binary_image)
    for i in range(1, No_scale + 1):
        kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
        erode = cv2.erode(binary_image, kernel, iterations=i)
        skeleton = skeletonize(binary_image / 255).astype(np.uint8) * 255

        erode = cv2.add(erode, skeleton)
        if count_coutour(erode) != No_contour:
            break
        erode_list.append(erode)
    if len(erode_list) > 1:
        idx = random.randint(1, len(erode_list)-1)
        return erode_list[idx]
    else:
        return None


def get_digit_image(digit_number, char_folder, char_label_df):
    digit_list = char_label_df[char_label_df['label'] == int(digit_number)]
    digit_list = digit_list['filename'].unique()
    iname = random.choice(digit_list)
    ipath = os.path.join(char_folder, iname)

    # To debug
    print('-----------------------------')
    print(ipath)

    digit_image = cv2.imread(ipath, 0)

    # count amount of contour
    # _, binary_dimage = cv2.threshold(digit_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # if count_coutour(binary_dimage) > 1:
    #     binary_dimage = standardized_digit_image(digit_image)
    # else:
    #     binary_dimage = thiner_image(digit_image)
    #     if binary_dimage is None:
    #         binary_dimage = standardized_digit_image(digit_image)

    binary_dimage = standardized_digit_image(digit_image)
    cropped_image = crop_image(binary_dimage)
    # cv2.namedWindow('digit_image', cv2.WINDOW_NORMAL)
    # cv2.imshow('digit_image', digit_image)
    # cv2.namedWindow('thiner', cv2.WINDOW_NORMAL)
    # cv2.imshow('thiner', binary_dimage)
    # cv2.waitKey()
    return cropped_image


def binary_2_RGB(rgb_digit_image, binary_dimage, char_color):
    rgb_digit_image[binary_dimage == 255] = [char_color[0], char_color[1], char_color[2]]

    return rgb_digit_image


if __name__== "__main__":
    folder_test = 'E:/POCR/src_code/handwritting_renderer/handwritting_line_extraction/test'
    for iname in os.listdir(folder_test):
        print(iname)
        image = cv2.imread(os.path.join(folder_test, iname), 0)
        denoised_img = denoising(image)
        dst_img = np.hstack((image, denoised_img))

        cv2.imwrite(os.path.join(folder_test, f'rs_{iname}'), dst_img)
