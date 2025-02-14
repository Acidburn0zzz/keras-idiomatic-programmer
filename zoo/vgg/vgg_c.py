# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# VGG (16 and 19 & Composable) (2014)
# Paper: https://arxiv.org/pdf/1409.1556.pdf

import tensorflow as tf
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

class VGG(object):
    """ VGG (composable)
    """
    # Meta-parameter: list of groups: number of layers and filter size
    groups = { 16 : [ (1, 64), (2, 128), (3, 256), (3, 512), (3, 512) ],	# VGG16
               19 : [ (1, 64), (2, 128), (4, 256), (4, 256), (4, 256) ] }	# VGG19

    init_weights='glorot_uniform'
    _model = None
 

    def __init__(self, n_layers, input_shape=(224, 224, 3), n_classes=1000):
        """ Construct a VGG model
            n_layers    : number of layers (16 or 19)
            input_shape : input shape to the model
            n_classes:  : number of output classes
        """
        if n_layers not in [16, 19]:
            raise Exception("VGG: Invalid value for n_layers")
            
        # The input vector 
        inputs = Input( input_shape )

        # The stem group
        x = self.stem(inputs)

        # The learner
        x = self.learner(x, self.groups[n_layers])

        # The classifier
        outputs = self.classifier(x, n_classes)

        # Instantiate the Model
        self._model = Model(inputs, outputs)

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, _model):
        self._model = _model
    
    def stem(self, inputs):
        """ Construct the Stem Convolutional Group
            inputs : the input vector
        """
        x = Conv2D(64, (3, 3), strides=(1, 1), padding="same", activation="relu",
                   kernel_initializer=self.init_weights)(inputs)
        return x
    
    def learner(self, x, blocks):
        """ Construct the (Feature) Learner
            x        : input to the learner
            blocks   : list of groups: filter size and number of conv layers
        """ 
        # The convolutional groups
        for n_layers, n_filters in blocks:
            x = self.group(x, n_layers, n_filters)
        return x

    @staticmethod
    def group(x, n_layers, n_filters, init_weights=None):
        """ Construct a Convolutional Group
            x        : input to the group
            n_layers : number of convolutional layers
            n_filters: number of filters
        """
        if init_weights is None:
            init_weights = VGG.init_weights
        # Block of convolutional layers
        for n in range(n_layers):
            x = Conv2D(n_filters, (3, 3), strides=(1, 1), padding="same", activation="relu",
                       kernel_initializer=init_weights)(x)
        
        # Max pooling at the end of the block
        x = MaxPooling2D(2, strides=(2, 2))(x)
        return x
    
    def classifier(self, x, n_classes):
        """ Construct the Classifier
            x         : input to the classifier
            n_classes : number of output classes
        """
        # Flatten the feature maps
        x = Flatten()(x)
    
        # Two fully connected dense layers
        x = Dense(4096, activation='relu', kernel_initializer=self.init_weights)(x)
        x = Dense(4096, activation='relu', kernel_initializer=self.init_weights)(x)

        # Output layer for classification 
        x = Dense(n_classes, activation='softmax', kernel_initializer=self.init_weights)(x)
        return x

# Example of constructing a VGG 16
# vgg = VGG(16)
# model = vgg.model

