"""Alternative CNN architectures for image classification.

This module provides various CNN architectures with different configurations
of convolutional and dense layers. Includes models with and without batch
normalization, dropout, and max pooling variations.
"""

import logging
import torch
import torch.nn.functional as F
from eoml.torch.cnn.torch_utils import conv_out_sizes
from torch import nn

logger = logging.getLogger(__name__)


class Conv2NormPlanet(nn.Module):
    def __init__(self, in_size, n_bands, n_out, p_drop=0.4):
        self.in_size = in_size
        self.n_bands = n_bands

        self.conv = [7,5,3]
        self.pad = 0
        self.stride = [2,1,2]

        self.n_filter = [256, 3*128]

        self.input_sizes = conv_out_sizes(in_size, self.conv, self.stride, self.pad)

        logger.debug(f"Conv2NormPlanet input sizes: {self.input_sizes}")

        self.denses = [2*2048, 2*2048, 2048]

        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=n_bands, out_channels=self.n_filter[0], kernel_size=self.conv[0],
                               padding=self.pad, stride= self.stride[0])
        self.conv1_bn = nn.BatchNorm2d(self.n_filter[0])
        self.conv2 = nn.Conv2d(in_channels=self.n_filter[0], out_channels=self.n_filter[1], kernel_size=self.conv[1],
                               padding=self.pad, stride= self.stride[1])
        self.conv2_bn = nn.BatchNorm2d(self.n_filter[1])
        self.pool1 = nn.MaxPool2d(self.conv[-1], stride= self.stride[2])
        self.fc1 = nn.Linear(self.n_filter[-1] * self.input_sizes[-1] * self.input_sizes[-1], self.denses[0])
        self.drop1 = nn.Dropout(p_drop)
        self.fc2 = nn.Linear(self.denses[0], self.denses[1])
        self.drop2 = nn.Dropout(p_drop)
        self.fc3 = nn.Linear(self.denses[1], self.denses[2])
        self.drop3 = nn.Dropout(p_drop)
        self.fc4 = nn.Linear(self.denses[2], n_out)

    def forward(self, x):
        x = F.relu(self.conv1_bn(self.conv1(x)))
        x = F.relu(self.conv2_bn(self.conv2(x)))
        x = self.pool1(x)
        x = torch.flatten(x, 1)
        # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = self.drop1(x)
        x = F.relu(self.fc2(x))
        x = self.drop2(x)
        x = F.relu(self.fc3(x))
        x = self.drop3(x)

        #F.softmax(
        x = self.fc4(x)

        return x




class AlexNetMod(nn.Module):
    def __init__(self, num_classes: int, bands, dropout: float = 0.5) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(bands, 128, kernel_size=5, stride=2, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=1, padding=1),
            nn.Conv2d(64, 384, kernel_size=5, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=1, padding=1),
            nn.Conv2d(384, 384, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            #nn.Conv2d(384, 256, kernel_size=3, padding=1),
            #nn.ReLU(inplace=True),
            #nn.Conv2d(256, 256, kernel_size=3, padding=1),
            #nn.ReLU(inplace=True),
            #nn.MaxPool2d(kernel_size=3, stride=2),
        )
        self.avgpool = nn.AdaptiveAvgPool2d((6, 6))
        self.classifier = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(256 * 6 * 6, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x




class Conv3Dense3(nn.Module):
    def __init__(self, in_size, n_bands, n_out, p_drop=0.4):
        self.in_size = in_size
        self.n_bands = n_bands

        self.conv = [5, 5, 3]
        self.pad = 0
        self.stride = 1

        self.n_filter = [128, 128, 256]

        self.input_sizes = conv_out_sizes(in_size, self.conv, self.stride, self.pad)

        self.denses = [2048, 2048, 2048]

        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=n_bands, out_channels=self.n_filter[0], kernel_size=self.conv[0],
                               padding=self.pad)
        # self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(in_channels=self.n_filter[0], out_channels=self.n_filter[1], kernel_size=self.conv[1],
                               padding=self.pad)
        self.conv3 = nn.Conv2d(in_channels=self.n_filter[1], out_channels=self.n_filter[2], kernel_size=self.conv[2],
                               padding=self.pad)
        self.fc1 = nn.Linear(self.n_filter[-1] * self.input_sizes[-1] * self.input_sizes[-1], self.denses[0])
        self.drop1 = nn.Dropout(p_drop)
        self.fc2 = nn.Linear(self.denses[0], self.denses[1])
        self.drop2 = nn.Dropout(p_drop)
        self.fc3 = nn.Linear(self.denses[1], self.denses[2])
        self.drop3 = nn.Dropout(p_drop)
        self.fc4 = nn.Linear(self.denses[2], n_out)

    class Conv3Dense3(nn.Module):
        def __init__(self, in_size, n_bands, n_out, p_drop=0.4):
            self.in_size = in_size
            self.n_bands = n_bands

            self.conv = [5, 5, 3]
            self.pad = 0
            self.stride = 1

            self.n_filter = [128, 128, 256]

            self.input_sizes = conv_out_sizes(in_size, self.conv, self.stride, self.pad)

            self.denses = [2048, 2048, 2048]

            super().__init__()
            self.conv1 = nn.Conv2d(in_channels=n_bands, out_channels=self.n_filter[0], kernel_size=self.conv[0],
                                   padding=self.pad)
            # self.pool = nn.MaxPool2d(2, 2)
            self.conv2 = nn.Conv2d(in_channels=self.n_filter[0], out_channels=self.n_filter[1],
                                   kernel_size=self.conv[1],
                                   padding=self.pad)
            self.conv3 = nn.Conv2d(in_channels=self.n_filter[1], out_channels=self.n_filter[2],
                                   kernel_size=self.conv[2],
                                   padding=self.pad)
            self.fc1 = nn.Linear(self.n_filter[-1] * self.input_sizes[-1] * self.input_sizes[-1], self.denses[0])
            self.drop1 = nn.Dropout(p_drop)
            self.fc2 = nn.Linear(self.denses[0], self.denses[1])
            self.drop2 = nn.Dropout(p_drop)
            self.fc3 = nn.Linear(self.denses[1], self.denses[2])
            self.drop3 = nn.Dropout(p_drop)
            self.fc4 = nn.Linear(self.denses[2], n_out)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = torch.flatten(x, 1)
        # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = self.drop1(x)
        x = F.relu(self.fc2(x))
        x = self.drop2(x)
        x = F.relu(self.fc3(x))
        x = self.drop3(x)

        x = self.fc4(x)

        return x

class Conv3Dense3Norm(nn.Module):
    def __init__(self, in_size, n_bands, n_out, p_drop=0.4):
        self.in_size = in_size
        self.n_bands = n_bands

        self.conv = [5, 5, 3]
        self.pad = 0
        self.stride = 1

        self.n_filter = [128, 128, 256]

        self.input_sizes = conv_out_sizes(in_size, self.conv, self.stride, self.pad)

        self.denses = [2048, 2048,2048]

        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=n_bands, out_channels=self.n_filter[0], kernel_size=self.conv[0],
                               padding=self.pad)
        self.conv1_bn = nn.BatchNorm2d(self.n_filter[0])
        # self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(in_channels=self.n_filter[0], out_channels=self.n_filter[1], kernel_size=self.conv[1],
                               padding=self.pad)
        self.conv2_bn = nn.BatchNorm2d(self.n_filter[1])
        self.conv3 = nn.Conv2d(in_channels=self.n_filter[1], out_channels=self.n_filter[2], kernel_size=self.conv[2],
                               padding=self.pad)
        self.conv3_bn = nn.BatchNorm2d(self.n_filter[2])
        self.fc1 = nn.Linear(self.n_filter[-1] * self.input_sizes[-1] * self.input_sizes[-1], self.denses[0])
        self.drop1 = nn.Dropout(p_drop)
        self.fc2 = nn.Linear(self.denses[0], self.denses[1])
        self.drop2 = nn.Dropout(p_drop)
        self.fc3 = nn.Linear(self.denses[1], self.denses[2])
        self.drop3 = nn.Dropout(p_drop)
        self.fc4 = nn.Linear(self.denses[2], n_out)

    def forward(self, x):

        x = F.relu(self.conv1_bn(self.conv1(x)))
        x = F.relu(self.conv2_bn(self.conv2(x)))
        x = F.relu(self.conv3_bn(self.conv3(x)))
        x = torch.flatten(x, 1)
        # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = self.drop1(x)
        x = F.relu(self.fc2(x))
        x = self.drop2(x)
        x = F.relu(self.fc3(x))
        x = self.drop3(x)

        x = self.fc4(x)

        return x


class Conv2Dense3(nn.Module):
    def __init__(self, in_size, n_bands, n_out, p_drop=0.2):
        self.in_size = in_size
        self.n_bands = n_bands

        self.conv = [4, 3]
        self.pad = 0
        self.stride = 1

        self.n_filter = [64, 128]

        self.input_sizes = conv_out_sizes(in_size, self.conv, self.stride, self.pad)

        self.denses = [2048, 2048, 2048]

        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=n_bands, out_channels=self.n_filter[0], kernel_size=self.conv[0],
                               padding=self.pad)
        # self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(in_channels=self.n_filter[0], out_channels=self.n_filter[1], kernel_size=self.conv[1],
                               padding=self.pad)
        self.fc1 = nn.Linear(self.n_filter[-1] * self.input_sizes[-1] * self.input_sizes[-1], self.denses[0])
        self.drop1 = nn.Dropout(p_drop)
        self.fc2 = nn.Linear(self.denses[0], self.denses[1])
        self.drop2 = nn.Dropout(p_drop)
        self.fc3 = nn.Linear(self.denses[1], self.denses[2])
        self.drop3 = nn.Dropout(p_drop)
        self.fc4 = nn.Linear(self.denses[2], n_out)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = torch.flatten(x, 1)
        # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = self.drop1(x)
        x = F.relu(self.fc2(x))
        x = self.drop2(x)
        x = F.relu(self.fc3(x))
        x = self.drop3(x)

        x = self.fc4(x)

        return x


class Conv2DropDense3(nn.Module):
    def __init__(self, in_size, n_bands, n_out, p_drop=0.2):
        self.in_size = in_size
        self.n_bands = n_bands

        self.conv = [4, 3]
        self.pad = 0
        self.stride = 1

        self.n_filter = [64, 128]

        self.input_sizes = conv_out_sizes(in_size, self.conv, self.stride, self.pad)

        self.denses = [2048, 2048, 2048]

        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=n_bands, out_channels=self.n_filter[0], kernel_size=self.conv[0],
                               padding=self.pad)
        # self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(in_channels=self.n_filter[0], out_channels=self.n_filter[1], kernel_size=self.conv[1],
                               padding=self.pad)
        self.fc1 = nn.Linear(self.n_filter[-1] * self.input_sizes[-1] * self.input_sizes[-1], self.denses[0])
        self.drop1 = nn.Dropout(p_drop)
        self.fc2 = nn.Linear(self.denses[0], self.denses[1])
        self.drop2 = nn.Dropout(p_drop)
        self.fc3 = nn.Linear(self.denses[1], self.denses[2])
        self.drop3 = nn.Dropout(p_drop)
        self.fc4 = nn.Linear(self.denses[2], n_out)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = torch.flatten(x, 1)
        # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = self.drop1(x)
        x = F.relu(self.fc2(x))
        x = self.drop2(x)
        x = F.relu(self.fc3(x))
        x = self.drop3(x)

        x = self.fc4(x)

        return x


class ConvJavaSmall(nn.Module):
    def __init__(self, in_size, n_bands, n_out, p_drop=0.4):
        self.in_size = in_size
        self.n_bands = n_bands

        self.conv = [4,2]
        self.pad = 0
        self.stride = [1,2]

        self.n_filter = [128]

        self.input_sizes = conv_out_sizes(in_size, self.conv, self.stride, self.pad)

        self.denses = [2048, 2048, 2048]

        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=n_bands, out_channels=self.n_filter[0], kernel_size=self.conv[0],
                               padding=self.pad)
        self.pool1 = nn.MaxPool2d(2)
        self.fc1 = nn.Linear(self.n_filter[-1] * self.input_sizes[-1] * self.input_sizes[-1], self.denses[0])
        self.drop1 = nn.Dropout(p_drop)
        self.fc2 = nn.Linear(self.denses[0], self.denses[1])
        self.drop2 = nn.Dropout(p_drop)
        self.fc3 = nn.Linear(self.denses[1], self.denses[2])
        self.drop3 = nn.Dropout(p_drop)
        self.fc4 = nn.Linear(self.denses[2], n_out)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.pool1(x)
        x = torch.flatten(x, 1)
        # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = self.drop1(x)
        x = F.relu(self.fc2(x))
        x = self.drop2(x)
        x = F.relu(self.fc3(x))
        x = self.drop3(x)

        #F.softmax(
        x = self.fc4(x)

        return x



class ConvJavaSmallNorm(nn.Module):
    def __init__(self, in_size, n_bands, n_out, p_drop=0.4):
        self.in_size = in_size
        self.n_bands = n_bands

        self.conv = [4,2]
        self.pad = 0
        self.stride = [1,2]

        self.n_filter = [128]

        self.input_sizes = conv_out_sizes(in_size, self.conv, self.stride, self.pad)

        self.denses = [2048, 2048, 2048]

        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=n_bands, out_channels=self.n_filter[0], kernel_size=self.conv[0],
                               padding=self.pad)
        self.conv1_bn = nn.BatchNorm2d(self.n_filter[0])
        self.pool1 = nn.MaxPool2d(2)
        self.fc1 = nn.Linear(self.n_filter[-1] * self.input_sizes[-1] * self.input_sizes[-1], self.denses[0])
        self.drop1 = nn.Dropout(p_drop)
        self.fc2 = nn.Linear(self.denses[0], self.denses[1])
        self.drop2 = nn.Dropout(p_drop)
        self.fc3 = nn.Linear(self.denses[1], self.denses[2])
        self.drop3 = nn.Dropout(p_drop)
        self.fc4 = nn.Linear(self.denses[2], n_out)

    def forward(self, x):
        x = F.relu(self.conv1_bn(self.conv1(x)))
        x = self.pool1(x)
        x = torch.flatten(x, 1)
        # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = self.drop1(x)
        x = F.relu(self.fc2(x))
        x = self.drop2(x)
        x = F.relu(self.fc3(x))
        x = self.drop3(x)

        #F.softmax(
        x = self.fc4(x)

        return x

class Conv2Norm(nn.Module):
    def __init__(self, in_size, n_bands, n_out, p_drop=0.4):
        self.in_size = in_size
        self.n_bands = n_bands

        self.conv = [5,3,2]
        self.pad = 0
        self.stride = [1,1,2]

        self.n_filter = [256, 384]

        self.input_sizes = conv_out_sizes(in_size, self.conv, self.stride, self.pad)

        self.denses = [2*2048, 2*2048, 2*2048]

        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=n_bands, out_channels=self.n_filter[0], kernel_size=self.conv[0],
                               padding=self.pad)
        self.conv1_bn = nn.BatchNorm2d(self.n_filter[0])
        self.conv2 = nn.Conv2d(in_channels=n_bands, out_channels=self.n_filter[1], kernel_size=self.conv[1],
                               padding=self.pad)
        self.conv2_bn = nn.BatchNorm2d(self.n_filter[1])
        self.pool1 = nn.MaxPool2d(self.conv[-1])
        self.fc1 = nn.Linear(self.n_filter[-1] * self.input_sizes[-1] * self.input_sizes[-1], self.denses[0])
        self.drop1 = nn.Dropout(p_drop)
        self.fc2 = nn.Linear(self.denses[0], self.denses[1])
        self.drop2 = nn.Dropout(p_drop)
        self.fc3 = nn.Linear(self.denses[1], self.denses[2])
        self.drop3 = nn.Dropout(p_drop)
        self.fc4 = nn.Linear(self.denses[2], n_out)

class Conv2NormV2(nn.Module):
    def __init__(self, in_size, n_bands, n_out, p_drop=0.4):
        self.in_size = in_size
        self.n_bands = n_bands

        self.conv = [5, 3, 2]
        self.pad = 0
        self.stride = [1, 1, 2]

        self.n_filter = [256, 384]

        self.input_sizes = conv_out_sizes(in_size, self.conv, self.stride, self.pad)
        logger.debug(f"Input sizes: {self.input_sizes}")
        self.denses = [2 * 2048, 2 * 2048, 2 * 2048]

        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=n_bands, out_channels=self.n_filter[0], kernel_size=self.conv[0],
                               padding=self.pad)
        self.conv1_bn = nn.BatchNorm2d(self.n_filter[0])
        self.conv2 = nn.Conv2d(in_channels=self.n_filter[0], out_channels=self.n_filter[1], kernel_size=self.conv[1],
                               padding=self.pad)
        self.conv2_bn = nn.BatchNorm2d(self.n_filter[1])
        self.pool1 = nn.MaxPool2d(self.conv[-1], stride=self.stride[-1])
        self.fc1 = nn.Linear(self.n_filter[-1] * self.input_sizes[-1] * self.input_sizes[-1], self.denses[0])
        self.drop1 = nn.Dropout(p_drop)
        self.fc2 = nn.Linear(self.denses[0], self.denses[1])
        self.drop2 = nn.Dropout(p_drop)
        self.fc3 = nn.Linear(self.denses[1], self.denses[2])
        self.drop3 = nn.Dropout(p_drop)
        self.fc4 = nn.Linear(self.denses[2], n_out)



    def forward(self, x):
        x = F.relu(self.conv1_bn(self.conv1(x)))
        x = F.relu(self.conv2_bn(self.conv2(x)))
        x = self.pool1(x)
        x = torch.flatten(x, 1)
        # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = self.drop1(x)
        x = F.relu(self.fc2(x))
        x = self.drop2(x)
        x = F.relu(self.fc3(x))
        x = self.drop3(x)

        #F.softmax(
        x = self.fc4(x)

        return x
