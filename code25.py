import numpy as np


def check_code25(imc):
    im = imc[0:3, :]
    check = imc[3, :]
    check2 = imc[4, :]
    tmp = np.ones(6)
    pas = 0
    for i in range(3):
        if np.sum(im[i]) % 2 == check[i]:
            tmp[i] = 0
        else:
            tmp[i] = 1
            return pas
    if np.sum(im[:, 0:3]) % 2 == check[3]:
        tmp[3] = 0
    else:
        tmp[3] = 1
        return pas
    if np.sum(im[:, 3:5]) % 2 == check[4]:
        tmp[4] = 0
    else:
        tmp[4] = 1
        return pas
    if all(check[::-1] == check2):
        tmp[5] = 0
    else:
        tmp[5] = 1
        return pas
    if np.sum(tmp) > 0.5:
        pas = 0
    else:
        pas = 1
    return pas


def checkOrs25(imc):
    check = np.ones(4)
    codes = np.zeros((4, 25))
    pass_bin = False
    number = 0
    codesFinal = np.zeros(25)
    orientation = -1
    for i in range(1, 5):
        imcr = np.rot90(imc, i)
        check[i-1] = check_code25(imcr)
        codes[i-1] = np.reshape(imcr, (1, 25))
    if sum(check) == 1:
        pass_bin = True
    else:
        pass_bin = False
        return pass_bin, number, codesFinal, orientation, codes
    orientation = np.where(check == 1)[0][0]
    codesFinal = codes[orientation]
    number = [str(i) for i in np.array(codesFinal[0:15], int)]
    number = ''.join(number)
    number = int(number, 2)
    return pass_bin, number, codesFinal, orientation, codes


def number_to_code(number):
    str_number = bin(number)[2:]
    numbers = [int(x) for x in str_number]
    raw_code = np.zeros(15)
    raw_code[15-len(numbers):] = np.array(numbers)
    raw_code = raw_code.reshape(3, 5)
    code = np.zeros((5, 5))
    code[:3] = raw_code
    check = np.zeros(10)
    check[:3] = np.sum(raw_code, axis=1) % 2
    check[3] = np.sum(raw_code[:, :3]) % 2
    check[4] = np.sum(raw_code[:, 3:]) % 2
    check[5:] = np.flip(check[:5])
    code[3:] = check.reshape(2, 5)
    return code


if __name__ == '__main__':
    # im = np.array([[0, 0, 0, 0, 1], [0, 0, 1, 1, 1], [0, 0, 0, 1, 1], [0, 1, 0, 1, 1], [0, 0, 0, 1, 0]])
    # pas = check_code25(im.transpose())
    # pass_bin, number, _, _, _ = checkOrs25(im.transpose())
    # print(pass_bin, number)
    code = number_to_code(3)
    for i in range(4):
        new_code = np.rot90(code, i)
        new = new_code.transpose()
        pas = check_code25(new)
        print(new_code, pas)


