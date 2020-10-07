from textrenderer.digit_processing import *
from PIL import ImageFont, Image, ImageDraw
from easydict import EasyDict
import pandas as pd
import numpy as np
import random
import yaml
import cv2
import os


def put_digit(text_image, point, digit_image, size_text, char_color, bounding_text, random_space = True):
    clone_image = text_image.copy()
    begin_point, ratio = get_digit_location(text_image, digit_image, point, size_text, random_space)

    d_h, d_w = digit_image.shape

    rgb_digit_image = clone_image[0 : d_h, begin_point[0] : begin_point[0] + d_w]
    if min(rgb_digit_image.shape) == 0:
        print('shape rgb digit is O')
        return None, None, None

    if rgb_digit_image.shape[0] != digit_image.shape[0] or rgb_digit_image.shape[1] != digit_image.shape[1]:
        rgb_digit_image = cv2.resize(rgb_digit_image, (digit_image.shape[1], digit_image.shape[0]))

    rgb_digit_image = binary_2_RGB(rgb_digit_image, digit_image, char_color)
    rgb_digit_image = resize_digit_image(rgb_digit_image, ratio)

    rd_h, rd_w, rc = rgb_digit_image.shape
    end_point = [begin_point[0] + rd_w, begin_point[1] + rd_h]
    text_image[begin_point[1] : end_point[1], begin_point[0]:end_point[0]] = rgb_digit_image

    end_point = [begin_point[0] + rd_w, point[1]]
    bounding_text = update_bb_text(bounding_text, begin_point, [rd_w, rd_h])
    return end_point, text_image, bounding_text


def put_letter(text_img, point, char, char_color, font, bounding_text):
    pil_img = Image.fromarray(np.uint8(text_img))
    draw = ImageDraw.Draw(pil_img)
    # y_offset = font.getoffset(char)
    char_size = font.getsize(char)
    draw.text((point[0], point[1]), char, fill=char_color, font=font)

    drawed_image = np.array(pil_img)
    end_point = [point[0] + char_size[0], point[1]]

    if is_abnormal_point(text_img, end_point):
        return None, None, None
    bounding_text = update_bb_text(bounding_text, end_point, char_size)
    return end_point, drawed_image, bounding_text


def get_word_size(font, word):

        offset = font.getoffset(word)
        size = font.getsize(word)
        size = (size[0] - offset[0], size[1] - offset[1])
        return size


def gen_bg_from_image(bg_list, width, height):
    assert width > height

    bg_path = random.choice(bg_list)
    bg = cv2.imread(bg_path)
    out = cv2.resize(bg, (width, height))

    return out


def get_char_color(cfg):
    p = []
    colors = []
    for k, v in cfg.font_color.items():
        if k == 'enable':
            continue
        p.append(v.fraction)
        colors.append(k)
    color_name = np.random.choice(colors, p=p)
    l_boundary = cfg.font_color[color_name].l_boundary
    h_boundary = cfg.font_color[color_name].h_boundary

    # random color by low and high RGB boundary
    r = np.random.randint(l_boundary[0], h_boundary[0])
    g = np.random.randint(l_boundary[1], h_boundary[1])
    b = np.random.randint(l_boundary[2], h_boundary[2])
    return (b, g, r)


def is_abnormal_point(text_image, point):
    h, w, c = text_image.shape

    if point[0] > w or point[0] < 0:
        return True
    if point[1] > h or point[1] < 0:
        return True
    return False


def update_bb_text(lastest_bb, point, char_sz):

    bb = [lastest_bb[0], point[0] + char_sz[0], point[1], point[1] + char_sz[1]]
    updated_bb = [lastest_bb[0], bb[1], min(lastest_bb[2], bb[2]), max(lastest_bb[3], bb[3])]
    return updated_bb


def select_digit_image(char, char_folder):
    char_folder = os.path.join(char_folder, char)

    inames = [iname for iname in os.listdir(char_folder) if iname.split('.')[-1] == 'jpg']

    iname = random.choice(inames)
    digit_image = cv2.imread(os.path.join(char_folder, iname), 0)
    _, binary_image = cv2.threshold(digit_image, 170, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return binary_image


def text_2_image(corpus_text, cfg, char_label, font):
    # get size of word
    word_sz = get_word_size(font, corpus_text) # width, height
    bg_sz = [int(word_sz[0] * 8), int(word_sz[1] * 8)]

    # gen BG
    bg_list = [os.path.join(cfg.backgrounds.path, bgname) for bgname in os.listdir(cfg.backgrounds.path)]
    bg = gen_bg_from_image(bg_list, bg_sz[0], bg_sz[1])

    begin_point = [int((bg_sz[0] - word_sz[0]) / 2), int((bg_sz[1] - word_sz[1]) / 2)]
    bounding_text = [begin_point[0], begin_point[0], begin_point[1], begin_point[1]]
    print(f'Begin with point: {begin_point}')
    print(f'size of text image: {bg.shape}')
    text_img = bg.copy()
    # char_color = get_char_color(cfg)
    letter_color = get_char_color(cfg)
    for char in corpus_text:
        if '0' <= char <= '9':
            # digit_img = get_digit_image(char, cfg.char_folder.path, char_label)
            digit_img = select_digit_image(char, cfg.char_folder.path)
            if is_abnormal_point(text_img, begin_point):
                print(f"Begin point is abnormal point {begin_point}")
                return text_img, None, None
            begin_point, text_img, bounding_text = put_digit(text_img, begin_point, digit_img, font.getsize(char),
                                                             letter_color, bounding_text)
            if bounding_text is None:
                return None, None, None

        else:
            begin_point, text_img, bounding_text = put_letter(text_img, begin_point, char, letter_color, font, bounding_text)
            if bounding_text is None:
                return None, None, None

    text_box_pnts = []
    text_box_pnts.append([bounding_text[0], bounding_text[2]])
    text_box_pnts.append([bounding_text[1], bounding_text[2]])
    text_box_pnts.append([bounding_text[1], bounding_text[3]])
    text_box_pnts.append([bounding_text[0], bounding_text[3]])

    return text_img, text_box_pnts, letter_color


def read_corpus(corpus_file):
    with open(corpus_file, encoding='utf-8') as f:
        data = f.readlines()

    lines = []
    for line in data:
        line_striped = line.strip()
        line_striped = line_striped.replace('\u3000', '')
        line_striped = line_striped.replace('&nbsp', '')
        line_striped = line_striped.replace("\00", "")

        if line_striped != u'' and len(line.strip()) > 1:
            lines.append(line_striped)
    return lines


# if __name__== "__main__":
#     corpus_file = 'corpus/all_corpus.txt'
#     number_image = 300000
#     cfg_file = 'configure.yaml'
#
#     # configuration reading
#     with open(cfg_file, mode='r', encoding='utf-8') as f:
#         cfg = yaml.load(f.read(),Loader=yaml.FullLoader)
#         cfg = EasyDict(cfg)
#
#     # load character label
#     char_label = pd.read_csv(cfg.char_label.path)
#
#     # load corpus file
#     corpus_lines = read_corpus(corpus_file)
#
#     # load annotation file
#     annotation_file = cfg.saved_folder.annotation
#     if not os.path.exists(annotation_file):
#         df = pd.DataFrame(columns = ['filename', "label"])
#         df.to_csv(annotation_file, index=False)
#     df = pd.read_csv(annotation_file, encoding='utf8')
#
#     for i in range(number_image):
#         print(i)
#         if i >=  len(corpus_lines):
#             corpus_text = random.choice(corpus_lines)
#         else:
#             corpus_text = corpus_lines[i]
#
#         bounding_text = None
#         while bounding_text is None:
#             text_img, bounding_text = text_2_image(corpus_text, cfg, char_label)
#             if bounding_text is not None:
#                 croped_img = text_img[bounding_text[2] : bounding_text[3], bounding_text[0] : bounding_text[1]]
#
#                 if not os.path.exists(cfg.saved_folder.path):
#                     os.makedirs(cfg.saved_folder.path)
#
#                 ipath = os.path.join(cfg.saved_folder.path, f'{i}.jpg')
#                 cv2.imwrite(ipath, croped_img)
#         print(corpus_text)
#         df.loc[len(df)] = [f'{i}.jpg', corpus_text]
#         df.to_csv(annotation_file, index=False, encoding='utf-8')
#     #
#     # image = cv2.imread('E:/POCR/handwritten/handwriting_character/gen_0806/Mnist/data_gen/1.jpg', 0)
#     # smoothed_image = smoothed_digit(image)