"""
visualize results for test image
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
import os
from os import listdir
from torch.autograd import Variable

import transforms as transforms
from skimage import io
from skimage.transform import resize
from models import *

cut_size = 44

transform_test = transforms.Compose([
    transforms.TenCrop(cut_size),
    transforms.Lambda(lambda crops: torch.stack([transforms.ToTensor()(crop) for crop in crops])),
])

def rgb2gray(rgb):
    convert_to_grayscale = []
    for i in range(0, len(rgb)):
        test = np.dot(rgb[i][...,:3], [0.299, 0.587, 0.114])
        convert_to_grayscale.append(test)
    return convert_to_grayscale
    # return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])
    
img_path = './images/'
files = listdir(img_path)

raw_imgs = []

for file in files:
    # make sure file is an image
    if file.endswith(('.jpg','jpeg')):
        raw_imgs.append(io.imread(img_path+file))



# raw_img = io.imread('images/3.jpeg')

gray = []
for i in raw_imgs:
    gray.append(rgb2gray(i))
gray = rgb2gray(raw_imgs)

img = []
# gray = resize(gray, (48,48), mode='symmetric').astype(np.uint8)

for g in gray:
    img.append(resize(g, (48,48), mode='symmetric').astype(np.uint8))


for i in img:
# img = img[:, :, np.newaxis]

# img = np.concatenate((img, img, img), axis=2)

img = np.concatenate((img, img, img))
img = Image.fromarray(img)
inputs = transform_test(img)

class_names = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

net = VGG('VGG19')
## Changes here to work on CPU
checkpoint = torch.load(os.path.join('FER2013_VGG19', 'PrivateTest_model.t7'), map_location=torch.device('cpu')) 

# checkpoint = torch.load(os.path.join('FER2013_VGG19', 'PrivateTest_model.t7'))

net.load_state_dict(checkpoint['net'])

## Don't use GPU so that we can work on CPU
# net.cuda()

net.eval()

ncrops, c, h, w = np.shape(inputs)

inputs = inputs.view(-1, c, h, w)

## Don't use GPU so that we can work on CPU
# inputs = inputs.cuda()

inputs = Variable(inputs, volatile=True)
outputs = net(inputs)

outputs_avg = outputs.view(ncrops, -1).mean(0)  # avg over crops

score = F.softmax(outputs_avg)
_, predicted = torch.max(outputs_avg.data, 0)

plt.rcParams['figure.figsize'] = (13.5,5.5)
axes=plt.subplot(1, 3, 1)
plt.imshow(raw_img)
plt.xlabel('Input Image', fontsize=16)
axes.set_xticks([])
axes.set_yticks([])
plt.tight_layout()


plt.subplots_adjust(left=0.05, bottom=0.2, right=0.95, top=0.9, hspace=0.02, wspace=0.3)

plt.subplot(1, 3, 2)
ind = 0.1+0.6*np.arange(len(class_names))    # the x locations for the groups
width = 0.4       # the width of the bars: can also be len(x) sequence
color_list = ['red','orangered','darkorange','limegreen','darkgreen','royalblue','navy']
for i in range(len(class_names)):
    plt.bar(ind[i], score.data.cpu().numpy()[i], width, color=color_list[i])

plt.title("Classification results ",fontsize=20)
plt.xlabel(" Expression Category ",fontsize=16)
plt.ylabel(" Classification Score ",fontsize=16)
plt.xticks(ind, class_names, rotation=45, fontsize=14)

axes=plt.subplot(1, 3, 3)
emojis_img = io.imread('images/emojis/%s.png' % str(class_names[int(predicted.cpu().numpy())]))
plt.imshow(emojis_img)
plt.xlabel('Emoji Expression', fontsize=16)
axes.set_xticks([])
axes.set_yticks([])
plt.tight_layout()
# show emojis

#plt.show()

# for i in range(0, len(images)):
    # plt.savefig(os.path.join('images/results/'+str(i)+'.png'))
    
# plt.close()

plt.savefig(os.path.join('images/results/l.png'))
plt.close()

print("The Expression is %s" %str(class_names[int(predicted.cpu().numpy())]))


