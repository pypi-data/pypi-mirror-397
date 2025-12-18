"""ResNet architecture implementations for PyTorch.

This module provides ResNet (Residual Network) implementations adapted from
https://colab.research.google.com/github/seyrankhademi/ResNet_CIFAR10/blob/master/CIFAR10_ResNet.ipynb

Includes ResNet variants (ResNet-20, ResNet-32, ResNet-56) and a year-aware variant
that incorporates temporal information as an additional input feature.
"""

import numpy as np
import torch
import torch.nn.functional as F
from eoml.torch.cnn.torch_utils import conv_out_sizes
from torch import nn
from torch.nn import init


# taken from https://colab.research.google.com/github/seyrankhademi/ResNet_CIFAR10/blob/master/CIFAR10_ResNet.ipynb#scrollTo=V9Y2hYRwB-qg

# We define all the classes and function regarding the ResNet architecture in this code cell
#__all__ = ['resnet20']
#'ResNet','resnet32', 'resnet44', 'resnet56', 'resnet110', 'resnet1202'


def _weights_init(m):
    """Initialize CNN weights using Kaiming normal initialization.

    Applies to Linear and Conv2d layers.

    Args:
        m: PyTorch module/layer to initialize.
    """
    classname = m.__class__.__name__
    if isinstance(m, nn.Linear) or isinstance(m, nn.Conv2d):
        init.kaiming_normal_(m.weight)


class LambdaLayer(nn.Module):
    """Lambda layer for identity mapping between ResNet blocks with different feature map sizes.

    Used for handling dimension changes in skip connections when feature map sizes differ.

    Attributes:
        lambd: Lambda function to apply to input.
    """

    def __init__(self, lambd):
        """Initialize LambdaLayer.

        Args:
            lambd: Lambda function for transforming input.
        """
        super().__init__()
        self.lambd = lambd

    def forward(self, x):
        """Forward pass applying the lambda function.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Transformed tensor.
        """
        return self.lambd(x)


# A basic block as shown in Fig.3 (right) in the paper consists of two convolutional blocks, each followed by a Bach-Norm layer.
# Every basic block is shortcuted in ResNet architecture to construct f(x)+x module.
# Expansion for option 'A' in the paper is equal to identity with extra zero entries padded
# for increasing dimensions between layers with different feature map size. This option introduces no extra parameter.
class BasicBlock(nn.Module):
    """Basic residual block for ResNet architecture.

    Consists of two convolutional layers with batch normalization and a shortcut connection.
    Implements the f(x) + x residual mapping.

    Attributes:
        expansion (int): Expansion factor for output channels (always 1 for BasicBlock).
        conv1 (nn.Conv2d): First convolutional layer.
        bn1 (nn.BatchNorm2d): Batch normalization after first conv.
        conv2 (nn.Conv2d): Second convolutional layer.
        bn2 (nn.BatchNorm2d): Batch normalization after second conv.
        shortcut (nn.Sequential): Shortcut connection for identity mapping.
    """
    # the output of a block keep the same size
    expansion = 1

    def __init__(self, in_planes, planes, stride=1, option='A'):
        """Initialize BasicBlock.

        Args:
            in_planes (int): Number of input channels.
            planes (int): Number of output channels.
            stride (int, optional): Stride for first convolution. Defaults to 1.
            option (str, optional): Shortcut option - 'A' for padding (CIFAR10) or 'B' for
                projection. Defaults to 'A'.
        """
        super().__init__()
        self.conv1 = nn.Conv2d(in_planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.shortcut = nn.Sequential()
        if stride != 1 or in_planes != planes:
            if option == 'A':
                """
                For CIFAR10 experiment, ResNet paper uses option A.
                """
                ## we colapase the side by the strid of 2
                ##then then we take the output size (2 time input(B) in initial conf) =>initial +padding = B+(2B/4)*2=2B/
                self.shortcut = LambdaLayer(lambda x:
                                            F.pad(x[:, :, ::2, ::2], (0, 0, 0, 0, planes // 4, planes // 4), "constant",
                                                  0))
            elif option == 'B':
                self.shortcut = nn.Sequential(
                    nn.Conv2d(in_planes, self.expansion * planes, kernel_size=1, stride=stride, bias=False),
                    nn.BatchNorm2d(self.expansion * planes)
                )

    def forward(self, x):
        """Forward pass through the basic block.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Output tensor after residual connection and activation.
        """
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out)
        return out


# Stack of 3 times 2*n (n is the number of basic blocks) layers are used for making the ResNet model,
# where each 2n layers have feature maps of size {16,32,64}, respectively.
# The subsampling is performed by convolutions with a stride of 2.
class ResNet(nn.Module):
    """ResNet architecture for image classification.

    Implements ResNet with 3 stages of residual blocks. The number of blocks in each stage
    determines the depth (e.g., ResNet-20, ResNet-32, ResNet-56).

    Attributes:
        in_planes (int): Current number of input planes, updated as layers are built.
        conv1 (nn.Conv2d): Initial convolutional layer.
        bn1 (nn.BatchNorm2d): Batch normalization after initial conv.
        layer1 (nn.Sequential): First stage of residual blocks.
        layer2 (nn.Sequential): Second stage of residual blocks.
        layer3 (nn.Sequential): Third stage of residual blocks.
        linear (nn.Linear): Final fully connected layer for classification.
    """
    # TODO check size before dense and size
   #(in_size, n_bands, n_out, BasicBlock, [3, 3, 3])
    def __init__(self, size, in_band, n_out, block, num_blocks):
        """Initialize ResNet model.

        Args:
            size (int): Input image size (not currently used in implementation).
            in_band (int): Number of input channels/bands.
            n_out (int): Number of output classes.
            block: Block class to use (typically BasicBlock).
            num_blocks (list): List of integers specifying number of blocks in each stage.
        """

        super().__init__()
        # in plane is updated as we _make_layer (multiplied by block expansion)
        #self.in_planes = 16
        self.in_planes = 2*32
        # go from in band to in_planes == input of first block
        self.conv1 = nn.Conv2d(in_band, self.in_planes, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(self.in_planes)
        # 3 layer of n block of 2 conv N layer = 3*n*2=6n +1 input conv +1 output dense=6n+2 layer
        self.layer1 = self._make_layer(block, self.in_planes, num_blocks[0], stride=1)
        self.layer2 = self._make_layer(block, 2*64, num_blocks[1], stride=2)
        self.layer3 = self._make_layer(block, 2*128, num_blocks[2], stride=2)
        self.linear = nn.Linear(2*128, n_out)
        self.apply(_weights_init)


    def _make_layer(self, block, planes, num_blocks, stride):
        """Create a stage of residual blocks.

        Args:
            block: Block class to instantiate.
            planes (int): Number of output channels for blocks in this stage.
            num_blocks (int): Number of blocks in this stage.
            stride (int): Stride for first block (subsequent blocks use stride=1).

        Returns:
            nn.Sequential: Sequential container of residual blocks.
        """
        strides = [stride] + [1] * (num_blocks - 1)
        layers = []
        for stride in strides:
            layers.append(block(self.in_planes, planes, stride))
            self.in_planes = planes * block.expansion  # new in plane = plane * expansion factor(1 in this case)

        return nn.Sequential(*layers)

    def forward(self, x):
        """Forward pass through ResNet.

        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, in_band, height, width).

        Returns:
            torch.Tensor: Output logits of shape (batch_size, n_out).
        """
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        # todo check this one collapse 1X1Xnband fixme
        # colaps to nband
        out = F.avg_pool2d(out, (out.size(2), out.size(3)))
        ## colapse to batch time all element size
        out = out.view(out.size(0), -1)
        out = self.linear(out)
        return out


def resnet20(in_size, n_bands, n_out):
    """Create ResNet-20 model (20 layers: 6*3 + 2).

    Args:
        in_size (int): Input image size.
        n_bands (int): Number of input channels.
        n_out (int): Number of output classes.

    Returns:
        ResNet: ResNet-20 model.
    """
    return ResNet(in_size, n_bands, n_out, BasicBlock, [3, 3, 3])


def resnet32(in_size, n_bands, n_out):
    """Create ResNet-32 model (32 layers: 6*5 + 2).

    Args:
        in_size (int): Input image size.
        n_bands (int): Number of input channels.
        n_out (int): Number of output classes.

    Returns:
        ResNet: ResNet-32 model.
    """
    return ResNet(in_size, n_bands, n_out, BasicBlock, [5, 5, 5])

def resnet44():
    """Create ResNet-44 model (44 layers: 6*7 + 2).

    Note: This function has incomplete signature and may not work correctly.

    Returns:
        ResNet: ResNet-44 model.
    """
    return ResNet(BasicBlock, BasicBlock, [7, 7, 7])


def resnet56(in_size, n_bands, n_out):
    """Create ResNet-56 model (56 layers: 6*9 + 2).

    Args:
        in_size (int): Input image size.
        n_bands (int): Number of input channels.
        n_out (int): Number of output classes.

    Returns:
        ResNet: ResNet-56 model.
    """
    return ResNet(in_size, n_bands, n_out, BasicBlock, [9, 9, 9])


#def resnet110():
#    return ResNet(BasicBlock, [18, 18, 18])


#def resnet1202():
#    return ResNet(BasicBlock, [200, 200, 200])


#def test(net):
#    total_params = 0
#
#    for x in filter(lambda p: p.requires_grad, net.parameters()):
#        total_params += np.prod(x.data.numpy().shape)
#    print("Total number of params", total_params)
#    print("Total layers", len(list(filter(lambda p: p.requires_grad and len(p.data.size()) > 1, net.parameters()))))


#if __name__ == "__main__":
#    for net_name in __all__:
#        if net_name.startswith('resnet'):
#            print(net_name)
#            test(globals()[net_name]())
#            print()


class ResNetYear(nn.Module):
    """ResNet architecture with year as additional input feature.

    Similar to ResNet but accepts a year value as additional input, which is concatenated
    with the conv features before the final linear layer. Useful for temporal classification tasks.

    Attributes:
        in_planes (int): Current number of input planes, updated as layers are built.
        conv1 (nn.Conv2d): Initial convolutional layer.
        bn1 (nn.BatchNorm2d): Batch normalization after initial conv.
        layer1 (nn.Sequential): First stage of residual blocks.
        layer2 (nn.Sequential): Second stage of residual blocks.
        layer3 (nn.Sequential): Third stage of residual blocks.
        linear (nn.Linear): Final fully connected layer (takes 2*128+1 inputs for year feature).
    """
    # TODO check size before dense and size
   #(in_size, n_bands, n_out, BasicBlock, [3, 3, 3])
    def __init__(self, size, in_band, n_out, block, num_blocks):
        """Initialize ResNetYear model.

        Args:
            size (int): Input image size (not currently used in implementation).
            in_band (int): Number of input channels/bands.
            n_out (int): Number of output classes.
            block: Block class to use (typically BasicBlock).
            num_blocks (list): List of integers specifying number of blocks in each stage.
        """

        super().__init__()
        # in plane is updated as we _make_layer (multiplied by block expansion)
        #self.in_planes = 16
        self.in_planes = 2*32
        # go from in band to in_planes == input of first block
        self.conv1 = nn.Conv2d(in_band, self.in_planes, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(self.in_planes)
        # 3 layer of n block of 2 conv N layer = 3*n*2=6n +1 input conv +1 output dense=6n+2 layer
        self.layer1 = self._make_layer(block, self.in_planes, num_blocks[0], stride=1)
        self.layer2 = self._make_layer(block, 2*64, num_blocks[1], stride=2)
        self.layer3 = self._make_layer(block, 2*128, num_blocks[2], stride=2)
        self.linear = nn.Linear(2*128+1, n_out)
        self.apply(_weights_init)


    def _make_layer(self, block, planes, num_blocks, stride):
        """Create a stage of residual blocks.

        Args:
            block: Block class to instantiate.
            planes (int): Number of output channels for blocks in this stage.
            num_blocks (int): Number of blocks in this stage.
            stride (int): Stride for first block (subsequent blocks use stride=1).

        Returns:
            nn.Sequential: Sequential container of residual blocks.
        """
        strides = [stride] + [1] * (num_blocks - 1)
        layers = []
        for stride in strides:
            layers.append(block(self.in_planes, planes, stride))
            self.in_planes = planes * block.expansion  # new in plane = plane * expansion factor(1 in this case)

        return nn.Sequential(*layers)

    def forward(self, x, year):
        """Forward pass through ResNetYear with year input.

        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, in_band, height, width).
            year (torch.Tensor): Year tensor of shape (batch_size, 1) representing temporal information.

        Returns:
            torch.Tensor: Output logits of shape (batch_size, n_out).
        """
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        # todo check this one collapse 1X1Xnband fixme
        # colaps to nband
        out = F.avg_pool2d(out, (out.size(2), out.size(3)))
        ## colapse to batch time all element size
        out = out.view(out.size(0), -1)
        out = torch.cat((out, year), dim=1)
        out = self.linear(out)
        return out

def resnet_year_20(in_size, n_bands, n_out):
    """Create ResNetYear-20 model with year input.

    Args:
        in_size (int): Input image size.
        n_bands (int): Number of input channels.
        n_out (int): Number of output classes.

    Returns:
        ResNetYear: ResNetYear-20 model.
    """
    return ResNetYear(in_size, n_bands, n_out, BasicBlock, [3, 3, 3])


def resnet_year_32(in_size, n_bands, n_out):
    """Create ResNetYear-32 model with year input.

    Args:
        in_size (int): Input image size.
        n_bands (int): Number of input channels.
        n_out (int): Number of output classes.

    Returns:
        ResNetYear: ResNetYear-32 model.
    """
    return ResNetYear(in_size, n_bands, n_out, BasicBlock, [5, 5, 5])

def resnet_year_44():
    """Create ResNetYear-44 model with year input.

    Note: This function has incomplete signature and may not work correctly.

    Returns:
        ResNetYear: ResNetYear-44 model.
    """
    return ResNetYear(BasicBlock, [7, 7, 7])


def resnet_year_56(in_size, n_bands, n_out):
    """Create ResNetYear-56 model with year input.

    Args:
        in_size (int): Input image size.
        n_bands (int): Number of input channels.
        n_out (int): Number of output classes.

    Returns:
        ResNetYear: ResNetYear-56 model.
    """
    return ResNetYear(in_size, n_bands, n_out, BasicBlock, [9, 9, 9])