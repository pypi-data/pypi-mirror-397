"""Model factory and custom neural network architectures for PyTorch.

This module provides a factory pattern for creating and managing neural network models,
along with custom CNN architectures for image classification tasks. It includes
initialization utilities and pre-configured model variants with batch normalization
and dropout layers.
"""

import torch
import torch.nn.functional as F
from eoml.torch.resnet import ResNet, resnet20, resnet56, resnet32
from eoml.torch.cnn.torch_utils import conv_out_sizes
from eoml.torch.model_low_use import Conv2Dense3, Conv3Dense3, Conv2DropDense3, ConvJavaSmall, \
    Conv3Dense3Norm, \
    Conv2Norm, Conv2NormV2
from torch import nn


def initialize_weights(m):
    """Initialize weights for neural network layers using Kaiming initialization.

    Applies appropriate initialization based on layer type:
    - Conv2d: Kaiming uniform initialization for weights, zeros for bias
    - BatchNorm2d: Ones for weights, zeros for bias
    - Linear: Kaiming uniform initialization for weights, zeros for bias

    Args:
        m: PyTorch module/layer to initialize.
    """
    if isinstance(m, nn.Conv2d):
        nn.init.kaiming_uniform_(m.weight.data, nonlinearity='relu')
        if m.bias is not None:
            nn.init.constant_(m.bias.data, 0)
    elif isinstance(m, nn.BatchNorm2d):
        nn.init.constant_(m.weight.data, 1)
        nn.init.constant_(m.bias.data, 0)
    elif isinstance(m, nn.Linear):
        nn.init.kaiming_uniform_(m.weight.data)
        nn.init.constant_(m.bias.data, 0)

class ModelFactory:
    """Factory class for creating and managing neural network models.

    Provides a registry of pre-configured model architectures and handles
    model instantiation, including loading from saved weights or JIT-compiled models.

    Attributes:
        libray (dict): Dictionary mapping model names to their constructor functions.
    """

    def __init__(self):
        """Initialize the model factory with default model registry."""
        self.libray = {}
        self.libray["Conv2Dense3"] = Conv2Dense3
        self.libray["Conv3Dense3"] = Conv3Dense3
        self.libray["Conv3Dense3Norm"] = Conv3Dense3Norm
        self.libray["Conv2DropDense3"] = Conv2DropDense3
        self.libray["ConvJavaSmall"] = ConvJavaSmall
        self.libray["ConvJavaSmallNorm"] = ConvSmallNorm
        self.libray["ConvJavaTinyNorm"] = ConvTinyNorm


        self.libray["Conv2Norm"] = Conv2Norm
        self.libray["Conv2NormV2"] = Conv2NormV2

        self.libray["Resnet20"] = resnet20
        self.libray["Resnet32"] = resnet32
        self.libray["Resnet56"] = resnet56


    def register(self, name, model):
        """Register a new model in the factory.

        Args:
            name (str): Name identifier for the model.
            model: Model constructor or factory function.
        """
        self.libray[name] = model

    def __call__(self, name, type="normal", path=None, model_args=None ):
        """Create a model instance from the factory.

        Args:
            name (str): Name of the model to create.
            type (str, optional): Type of model - "normal" for standard PyTorch model or
                "jitted" for TorchScript JIT-compiled model. Defaults to "normal".
            path (str, optional): Path to saved model weights or JIT model. If None,
                model uses random initialization. Defaults to None.
            model_args (dict, optional): Arguments to pass to model constructor.
                Defaults to None.

        Returns:
            torch.nn.Module: Instantiated model.

        Raises:
            Exception: If type is not "normal" or "jitted".
        """

        if type == "jitted":
            return torch.jit.load(path)

        if type == "normal":
            constructor = self.libray[name]
            model = constructor(**model_args)
        else:
            raise Exception("wrong args expected jitted or normal")

        if path is not None:
            model.load_state_dict(torch.load(path))

        return model



class ConvSmallNorm(nn.Module):
    """Convolutional neural network with batch normalization and dropout.

    Architecture: Conv2d -> BatchNorm -> ReLU -> MaxPool -> 4x Dense layers with dropout.
    Designed for small input images with configurable number of input bands.

    Attributes:
        in_size (int): Input image size (height and width).
        n_bands (int): Number of input channels/bands.
        conv (list): Convolutional kernel sizes.
        pad (int): Padding for convolutional layers.
        stride (list): Stride values for convolutions.
        n_filter (list): Number of filters in convolutional layers.
        input_sizes (list): Computed output sizes after each conv operation.
        denses (list): Sizes of dense layers.
        conv1 (nn.Conv2d): First convolutional layer.
        conv1_bn (nn.BatchNorm2d): Batch normalization for first conv layer.
        pool1 (nn.MaxPool2d): Max pooling layer.
        fc1 (nn.Linear): First fully connected layer.
        drop1 (nn.Dropout): Dropout after first FC layer.
        fc2 (nn.Linear): Second fully connected layer.
        drop2 (nn.Dropout): Dropout after second FC layer.
        fc3 (nn.Linear): Third fully connected layer.
        drop3 (nn.Dropout): Dropout after third FC layer.
        fc4 (nn.Linear): Output fully connected layer.
    """

    def __init__(self, in_size, n_bands, n_out, p_drop=0.4):
        """Initialize ConvJavaSmallNorm model.

        Args:
            in_size (int): Input image size (assumes square images).
            n_bands (int): Number of input channels/bands.
            n_out (int): Number of output classes.
            p_drop (float, optional): Dropout probability. Defaults to 0.4.
        """
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
        """Forward pass through the network.

        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, n_bands, height, width).

        Returns:
            torch.Tensor: Output tensor of shape (batch_size, n_out).
        """
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


class ConvTinyNorm(nn.Module):
    """Tiny convolutional neural network with batch normalization.

    A smaller variant of ConvJavaSmallNorm with fewer filters and dense units.
    Architecture: Conv2d -> BatchNorm -> ReLU -> MaxPool -> 3x Dense layers with dropout.

    Attributes:
        in_size (int): Input image size (height and width).
        n_bands (int): Number of input channels/bands.
        conv (list): Convolutional kernel sizes.
        pad (int): Padding for convolutional layers.
        stride (list): Stride values for convolutions.
        n_filter (list): Number of filters in convolutional layers.
        input_sizes (list): Computed output sizes after each conv operation.
        denses (list): Sizes of dense layers.
        conv1 (nn.Conv2d): First convolutional layer.
        conv1_bn (nn.BatchNorm2d): Batch normalization for first conv layer.
        pool1 (nn.MaxPool2d): Max pooling layer.
        fc1 (nn.Linear): First fully connected layer.
        drop1 (nn.Dropout): Dropout after first FC layer.
        fc2 (nn.Linear): Second fully connected layer.
        drop2 (nn.Dropout): Dropout after second FC layer.
        fc3 (nn.Linear): Output fully connected layer.
    """

    def __init__(self, in_size, n_bands, n_out, p_drop=0.4):
        """Initialize ConvJavaTinyNorm model.

        Args:
            in_size (int): Input image size (assumes square images).
            n_bands (int): Number of input channels/bands.
            n_out (int): Number of output classes.
            p_drop (float, optional): Dropout probability. Defaults to 0.4.
        """
        self.in_size = in_size
        self.n_bands = n_bands

        self.conv = [4,2]
        self.pad = 0
        self.stride = [1,2]

        self.n_filter = [64, 64] #we repeat 256 for the drop out

        self.input_sizes = conv_out_sizes(in_size, self.conv, self.stride, self.pad)

        self.denses = [1024, 1024]

        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=n_bands, out_channels=self.n_filter[0], kernel_size=self.conv[0],
                               padding=self.pad)
        self.conv1_bn = nn.BatchNorm2d(self.n_filter[0])
        self.pool1 = nn.MaxPool2d(2)
        self.fc1 = nn.Linear(self.n_filter[0] * self.input_sizes[-1] * self.input_sizes[-1], self.denses[0])
        self.drop1 = nn.Dropout(p_drop)
        self.fc2 = nn.Linear(self.denses[0], self.denses[1])
        self.drop2 = nn.Dropout(p_drop)
        self.fc3 = nn.Linear(self.denses[1], n_out)

    def forward(self, x):
        """Forward pass through the network.

        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, n_bands, height, width).

        Returns:
            torch.Tensor: Output tensor of shape (batch_size, n_out).
        """
        x = F.relu(self.conv1_bn(self.conv1(x)))
        x = self.pool1(x)
        x = torch.flatten(x, 1)
        # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = self.drop1(x)
        x = F.relu(self.fc2(x))
        x = self.drop2(x)

        #F.softmax(
        x = self.fc3(x)

        return x
