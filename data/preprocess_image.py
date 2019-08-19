import os
import codecs
import pickle
import argparse
import json as js
from PIL import Image

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms


# parser
parser = argparse.ArgumentParser(description='preprocess_images.py')
parser.add_argument('-gpus', default=[], nargs='+', type=int,
                    help="Use CUDA on the listed devices.")
parser.add_argument('-batch_size', default=100, type=int,
                    help="the batch size")
parser.add_argument('-source', required=True, choices=['yidian', 'toutiao', 'sina', 'netease'],
                    help='data source')
opt = parser.parse_args()

# cuda
use_cuda = torch.cuda.is_available() and len(opt.gpus) > 0
if use_cuda:
    torch.cuda.set_device(opt.gpus[0])


def read_images(filedir):
    files = os.listdir(filedir)
    fs = [os.path.join(filedir, f) for f in files]
    transform = transforms.Compose([transforms.CenterCrop((224, 224)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
    names, datas = [], []
    for i in range(len(fs)):
        try:
            datas += [transform(Image.open(fs[i]).convert('RGB'))]
            names += [files[i]]
            #print(i)
        except:
            continue
    return names, datas


def get_batch(names, datas, batch_size=100):
    assert len(names) == len(datas)
    length = len(datas)
    for batch in range(length // batch_size):
        name = names[batch * batch_size: (batch+1) * batch_size]
        data = torch.stack(datas[batch * batch_size: (batch+1) * batch_size])
        yield name, data


def build_resnet():
    resnet34 = models.resnet34(pretrained=True)
    modules = list(resnet34.children())[:-1]
    resnet34 = nn.Sequential(*modules)
    for p in resnet34.parameters():
        p.requires_grad = False
    resnet34.eval()
    if use_cuda:
        resnet34.cuda()
    return resnet34


def extract_feature(batch_size, model, filedir, outf):
    names, datas = read_images(filedir)
    print("images loaded, containing {} pieces of data".format(len(names)))

    # files = temp_files[:(len(temp_files) // batch_size * batch_size)]
    # names, image_data = read_images(filedir, files)
    # assert len(names) == len(image_data)
    # print(len(names))

    ns, features = [], []
    for name, data in get_batch(names, datas, batch_size):
        if use_cuda:
            data = data.cuda()
        feature = model(data)
        features += [feature.reshape(feature.shape[:2])]
        ns += name
    features = torch.cat(features)  # [n_images, feature_dim]
    assert len(ns) == len(features)
    print("features extracted, with dimension ", features.size())

    features_saved = {ns[i]: features[i].tolist() for i in range(len(ns))}
    # names = [f + '\n' for f in files]
    pickle.dump(features_saved, open(outf, 'wb'))
    # with codecs.open('./data/image_data/netease_image_data/features.json', 'w', 'utf-8') as f:
    # 	f.write(js.dumps(features_saved))
    print("features saved")
# with codecs.open('./data/save_data/image_names.txt', 'w', 'utf-8') as f:
# 	f.writelines(names)
# print("names saved")


def save_model(path, model):
    model_state_dict = model.state_dict()
    torch.save(model_state_dict, './resnet152.pt')


def main(opt):
    model = build_resnet()
    print("model built")

    filedir = './{}_image'.format(opt.source)
    outf = './{}_features.pkl'.format(opt.source)
    extract_feature(opt.batch_size, model, filedir, outf)


if __name__ == '__main__':
    main(opt)

