import yaml
import random
import os

def read_cf(tel_cf):
    with open(tel_cf, 'r', encoding='utf8') as stream:
        data_loaded = yaml.safe_load(stream)

    return data_loaded

def gen_tel(tel_cf):
    # pre_string
    pre_text = ''
    for id, info in tel_cf['pre_string'].items():
        p = random.random()
        if info['fraction'] <= p:
            pre_text += random.choice(info['text'])
            # number_space = random.randint(0, )
            # pre_text += number_space * ' '

    # hidden string
    hidden_str = ''
    if len(pre_text) > 0:
        hidden_str = random.choice(tel_cf['hidden_string']['text'])
        num_space = random.randint(0, 2)
        hidden_str += num_space * ' '

    # number of telephone
    number_tel = ''
    min_length = tel_cf['num_tel']['min_length']
    max_length = tel_cf['num_tel']['max_length']
    length_tel = random.randint(min_length, max_length)

    if length_tel >= 10:
        number_tel = random.randint(10 ** (length_tel -2), 10 ** (length_tel-1))
    else:
        number_tel = random.randint(10 ** (length_tel - 1), 10 ** length_tel)

    # adding sign in tel number
    p_sign = random.random()
    if p_sign < tel_cf['num_tel']['sign']['fraction']:
        sign = random.choice(['-', '('])
        if sign == '-':
            number_tel = "{:,}".format(number_tel)
            number_tel = number_tel.replace(',', '-')
        else:
            number_tel = str(number_tel)
            index = random.randint(0, length_tel - 3)
            number_tel = number_tel[:index] + '(' + number_tel[index:index+3] +')'+ number_tel[index+3:]
    else: number_tel = str(number_tel)
    if length_tel >= 10: number_tel = '0' + number_tel

    dst_str = pre_text + hidden_str + number_tel
    return dst_str


def get_amount(config):
    num_space = random.randint(1, 5)
    total = num_space * ' '

    min_length = config['amount']['min_length']
    max_length = config['amount']['max_length']
    length_total = random.randint(min_length, max_length)
    amount = random.randint(0, 10 ** length_total)
    amount = "{:,}".format(amount)

    sign = random.choice(config['amount']['sign']['text'])
    if sign == '円':
        total = amount + random.randint(0, 2) * ' ' + sign
    elif sign == '￥':
        total = sign + random.randint(0, 2) * ' ' + amount
    else:
        total = sign + amount

    return total


def gen_total(total_cf):
    # get pre_string
    pre_text =''
    p_brace = random.random()
    if p_brace <= 0.1:
        pre_text += '('
    pre_text += random.choice(total_cf['pre_string']['text'])

    # Hidden string
    num_space = random.randint(1, 5)
    hidden_str = num_space * ' '
    p = random.random()
    if p <= total_cf['hidden_string']['fraction']:
        hidden_str += str(random.randint(1, 9)) + total_cf['hidden_string']['text']
        num_space = random.randint(5, 7)
        hidden_str += num_space * ' '
    else:
        num_space = random.randint(5, 10)
        hidden_str += num_space * ' '

    # amount total
    total = get_amount(total_cf)
    if p_brace <= 0.1: total += ')'

    dst_string = pre_text + hidden_str + total
    return dst_string


def gen_target(target_cf):
    # get pre_string
    pre_text =''
    p_brace = random.random()
    p_type = random.random()
    p_percent = random.random()
    if p_brace <= 0.1:
        pre_text += '('
    if p_type <= target_cf['pre_string']['type']['fraction']:
        pre_text += random.choice(target_cf['pre_string']['type']['text'])
        number_space = random.randint(0, 2)
        pre_text += ' ' * number_space

    pre_text += random.choice(target_cf['pre_string']['target']['text'])
    number_space = random.randint(1, 5)
    pre_text += ' ' * number_space

    if p_percent <= target_cf['pre_string']['percent']['fraction']:
        pre_text += random.choice(target_cf['pre_string']['percent']['text'])
        number_space = random.randint(0, 5)
        pre_text += ' ' * number_space

    # amount total
    total = get_amount(target_cf)
    if p_brace <= 0.1: total += ')'

    dst_string = pre_text + total
    return dst_string


def gen_point(point_cf):
    # get pre_string
    pre_text =''
    p_brace = random.random()
    p_hidden = random.random()
    if p_brace <= 0.1:
        pre_text += '('

    pre_text += random.choice(point_cf['pre_string']['text'])
    number_space = random.randint(2, 5)
    pre_text += ' ' * number_space

    # amount of point
    total = get_amount(point_cf)
    if p_brace <= 0.1: total += ')'

    dst_string = pre_text + total
    return dst_string


if __name__ == "__main__":
    file_cf = 'tax.yaml'
    out_corpus_path = "../data/hand_corpus/tax.txt"
    config = read_cf(file_cf)
    with open(out_corpus_path, "w+", encoding="utf-8") as f:
        for _ in range(50000):
            rand_tel = gen_target(config) +'\n'
            f.writelines(rand_tel)











