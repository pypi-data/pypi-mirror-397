"""Data augmentation transformations for PyTorch image datasets.

This module provides transformation classes and functions for augmenting image data
during training. Includes rotation, flipping, cropping, scaling, shearing, and
blurring operations using torchvision's functional API.
"""

import logging
import math
import random

import torchvision.transforms.functional as TF

logger = logging.getLogger(__name__)


def rotate_crop_flip_transform(img, size=13, angle=180, vflip=False):
    """Apply rotation, crop, and optional flip to an image.

    Args:
        img: Input image tensor.
        size: Size to crop to after rotation. Defaults to 13.
        angle: Rotation angle in degrees. Defaults to 180.
        vflip: Whether to apply vertical flip. Defaults to False.

    Returns:
        Transformed image tensor.
    """
    img = TF.rotate(img, angle=angle)
    img = TF.center_crop(img, size)
    if vflip:
        img = TF.vflip(img)

    return img


# Due to memory bug in dataset, the dataset return numpy type that we cast to int Todo need to be fixed in dataset
def rotate_flip_transform(img, angle=180, vflip=False):
    """Apply rotation and optional flip to an image.

    Note:
        Due to dataset memory bug, parameters are cast from numpy types.

    Todo:
        Fix dataset to avoid numpy type issue.

    Args:
        img: Input image tensor.
        angle: Rotation angle in degrees. Defaults to 180.
        vflip: Whether to apply vertical flip. Defaults to False.

    Returns:
        Transformed image tensor.
    """
    img = TF.rotate(img, angle=int(angle))
    if bool(vflip):
        img = TF.vflip(img)

    return img


class CropTransform:
    """Crop images to a specified size.

    Useful for working with databases containing samples larger than needed,
    allowing on-the-fly cropping to the desired size.

    Attributes:
        width: Target width/size for square crop.
    """
    def __init__(self, width):
        self.width = width


    def __call__(self, inputs):

        inputs = TF.center_crop(inputs, self.width)
        return inputs

    def __repr__(self):
        return f'CropTransform(width: {self.width})'


class RandomTransform:
    """Randomly apply augmentation transformations to images.

    Applies random combinations of rotation, flip, scale, shear, and blur,
    then crops to the specified size. Useful for data augmentation during training.

    Attributes:
        width: Target width for final crop.
        p_rot: Probability of applying rotation. Defaults to 0.50.
        p_flip: Probability of applying vertical flip. Defaults to 0.50.
        p_scale: Probability of applying scaling. Defaults to 0.2.
        p_shear: Probability of applying shear. Defaults to 0.2.
        p_blur: Probability of applying Gaussian blur. Defaults to 0.2.
    """

    def __init__(self, width, p_rot=0.50, p_flip=0.50, p_scale=0.2, p_shear= 0.2, p_blur= 0.2):
        self.width = width
        self.p_rot = p_rot
        self.p_flip = p_flip
        self.p_scale = p_scale
        self.p_shear = p_shear
        self.p_blur = p_blur

    def __repr__(self):
        return f'RandomTransform(width: {self.width}, ' \
               f'p_rot: {self.p_rot} , ' \
               f'p_flip: {self.p_flip} , ' \
               f'p_scale: {self.p_scale} , ' \
               f'p_shear: {self.p_shear} , ' \
               f'p_blur: {self.p_blur})' \

    # size need to be multiplied by to avoid dark pixel
    # 1.4145
    def __call__(self, inputs):
        c, i_h, i_w = inputs.shape

        rotation_angle = random.randint(-180, 180) if self.p_rot > random.uniform(0, 1) else 0
        shear = random.randint(-15, 15) if self.p_shear > random.uniform(0, 1) else 0
        scale = random.randint(2, 4) if self.p_scale > random.uniform(0, 1) else 1
        flip = True if self.p_flip > random.uniform(0, 1) else False

        blur = True if self.p_blur > random.uniform(0, 1) else False

        # distance to the border to avoid black border du to rotation
        safe_width = math.ceil(1.4143* self.width)

        if i_h < safe_width:
            logger.warning("Transformation: the width of the input is not big enough and may be truncated.")


        #input = TF.rotate(input, rotation_angle, interpolation=TF.InterpolationMode.BILINEAR)
        # affine
        inputs = TF.affine(inputs, angle=rotation_angle, translate=[0,0], scale=scale, shear=shear,
                          interpolation=TF.InterpolationMode.NEAREST)

        inputs = TF.center_crop(inputs, self.width)

        # flip
        if flip:
            inputs = TF.vflip(inputs)

        # gaussian
        if blur:
            inputs = TF.gaussian_blur(inputs, kernel_size=[3, 3], sigma=[0.45, 0.45])

        return inputs

