import os
import io

def extract_label(root_folder, saved_txt):
    label_file = 'tmp_labels.txt'
    f = open(os.path.join(root_folder, label_file), 'r', encoding='utf8')
    with io.open(saved_txt, 'w', encoding='utf8', newline='') as saved_file:
        for x in f:
            position_space = x.find(' ')
            i_name = x[:position_space] + '.jpg'
            i_path = os.path.join(root_folder, i_name)
            text = ' '.join(x[position_space+1:].split())

            text_line = i_path +'\t'+ text
            saved_file.write(text_line)
            saved_file.write('\n')


def create_label_file(image_folder, label_folder, saved_txt):
    inames = [iname for iname in os.listdir(image_folder) if iname.split('.')[-1] == 'jpg']

    with io.open(saved_txt, 'w', encoding='utf8', newline='') as saved_file:
        for iname in inames:
            label_file = iname.split('.')[0] + '.txt'

            f = open(os.path.join(label_folder, label_file), 'r', encoding='utf8')
            text = f.readline()
            i_path = os.path.join(image_folder, iname)
            # text_line = f'{str(i_path)}\t{str(text)}'
            text_line = i_path +'\t'+ text
            f.close()
            saved_file.write(text_line)
            saved_file.write('\n')

            
extract_label('E:/POCR/POCR_OCR_dataset/output_textrenderer/output_adding_point/synthetic_adding_point', 'E:/POCR/POCR_OCR_dataset/output_textrenderer/output_adding_point/synthetic_adding_point.txt')
# image_folder = 'E:/POCR/POCR_OCR_dataset/real_data/total_real_line_OCR_20200525/total_real_line_OCR_20200525'
# label_folder = 'E:/POCR/POCR_OCR_dataset/real_data/total_real_line_OCR_20200525/texts'
# saved_txt = 'E:/POCR/POCR_OCR_dataset/real_data/total_real_line_OCR_20200525/total_real_line_OCR_20200525.txt'
# create_label_file(image_folder, label_folder, saved_txt)


# f = open(os.path.join(saved_txt), 'r', encoding='utf8')
# for x in f:
#     print(x.split('\t')[-1])