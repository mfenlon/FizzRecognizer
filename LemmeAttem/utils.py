import numpy as np
import matplotlib.pyplot as plt
import h5py
import glob
from PIL import Image
import imageio

def format_data(data, m, num_px):
    
    image_list = []
    for filename in glob.glob("data/" + data + "_x_images/*.jpg"):
        image = np.array(Image.fromarray(imageio.imread(filename)).resize((num_px, num_px)))
        image_list.append(image)
        
    images = np.array(image_list)
    
    with h5py.File("dataset/" + data + "_dataset.hdf5", "w") as f:
        dataset_x = f.create_dataset(
            data + "_set_x", np.shape(image_list), data=image_list
        )
        
        output_y = np.loadtxt(
            "data/" + data + "_y.txt", comments="#", delimiter=",", unpack=False
        ).reshape((m, 1)).astype(int)
        
        dataset_y = f.create_dataset(
            data + "_set_y", np.shape(output_y), data=output_y
        )
        

def load_data():
    train_dataset = h5py.File("dataset/train_dataset.hdf5", "r")
    train_set_x_orig = np.array(train_dataset["train_set_x"][:])
    train_set_y_orig = np.array(train_dataset["train_set_y"][:])
    
    test_dataset = h5py.File("dataset/test_dataset.hdf5", "r")
    test_set_x_orig = np.array(test_dataset["test_set_x"][:])
    test_set_y_orig = np.array(test_dataset["test_set_y"][:])
    
    classes = ["not Fizz", "Fizz"]
    
    train_set_y_orig = train_set_y_orig.reshape((1, train_set_y_orig.shape[0]))
    test_set_y_orig = test_set_y_orig.reshape((1, test_set_y_orig.shape[0]))
    
    return train_set_x_orig, train_set_y_orig, test_set_x_orig, test_set_y_orig, classes


def sigmoid(Z):
    """
    Implements the sigmoid activation in numpy
    
    Arguments:
    Z -- output of the linear layer, of any shape
    
    Return:
    A -- output of sigmoid(Z), as shape as Z
    cache -- returns Z as well, useful during backpropagation
    """
    
    A = 1 / (1 + np.exp(-Z))
    
    assert(A.shape == Z.shape)
    cache = Z
    
    return A, cache

    
def relu(Z):
    """
    Implements the ReLU function
    
    Arguments:
    Z -- output of the linear layer, of any shape
    
    Returns:
    A -- Post-activation parameter, of the same shape as Z
    cache -- a python dictionary containing "A"; stored for computing the backward pass efficiently
    """
    
    A = np.maximum(0,Z)
    
    assert(A.shape == Z.shape)
    cache = Z
    
    return A, cache


def sigmoid_backward(dA, cache):
    """
    Implements the backward propagation for a single SIGMOID unit.
    
    Arguments:
    dA -- post-activation gradient, of any shape
    cache -- 'Z' where we store for computing backward propagation efficiently
    
    Returns:
    dZ -- Gradient of the cost with respect to Z
    """
    
    Z = cache
    
    s = 1 / (1 + np.exp(-Z))
    dZ = dA * s * (1 - s)
    
    assert(dZ.shape == Z.shape)
    
    return dZ


def relu_backward(dA, cache):
    """
    Implements the backward propagation for a single RELU unit.
    
    Arguments:
    dA -- post-activation gradient, of any shape
    cache -- 'Z' where we store for computing backward propagation efficiently
    
    Returns:
    dZ -- Gradient of the cost with respect to Z
    """
    
    Z = cache
    dZ = np.array(dA, copy=True)
    
    # When z <= 0, set dz to 0 as well
    dZ[Z <= 0] = 0
    
    assert(dZ.shape == Z.shape)
    
    return dZ


def initialize_parameters(layer_dims):
    """
    Initializes weight and bias vectors
    
    Arguments:
    layer_dims -- python array (list) containing the dimensions of each layer in our network
    
    Returns:
    parameters -- python dictionary containing our parameters "W1", "b1", ..., "WL", "bL":
                    Wl -- weight matrix of shape (layer_dims[l], layer_dims[l-1])
                    bl -- bias vector of shape (layer_dims[l], 1)
    """
    parameters = {}
    L = len(layer_dims)
    
    for l in range(1, L):
        parameters['W' + str(l)] = np.random.randn(layer_dims[l], layer_dims[l-1]) * 0.01
        parameters['b' + str(l)] = np.zeros((layer_dims[l], 1))
        
        assert(parameters['W' + str(l)].shape == (layer_dims[l], layer_dims[l-1]))
        assert(parameters['b' + str(l)].shape == (layer_dims[l], 1))
        
    return parameters


def linear_forward(A, W, b):
    """
    Implements the linear part of a layer's forward propagation.
    
    Arguments:
    A -- activations from previous layer (or input data): (size of previous layer, number of examples
    W -- weights matrix: numpy array of shape (size of current layer, size of previous layer)
    b -- bias vector, numpy array of shape (size of the current layer, 1)
    
    Return:
    Z -- the input of the activation function, also called pre-activation parameters
    cache -- a python tuple containing "A", "W", and "b"; stored for computing the backward pass efficiently
    """
    
    Z = np.dot(W, A) + b
    
    assert(Z.shape == (W.shape[0], A.shape[1]))
    cache = (A, W, b)
    
    return Z, cache


def linear_activation_forward(A_prev, W, b, activation):
    """
    Implements the forward propagation for the LINEAR->ACTIVATION layer
    
    Arguments:
    A_prev -- activations from previous layer (or input data): (size of previous layer, number of examples)
    W -- weight matrix: numpy array of shape (size of current layer, size of previous layer)
    b -- bias vector, numpy array of shape (size of current layer, 1)
    activation -- the activation to be used in this layer, stored as a text string: "sigmoid" or "relu"
    
    Returns:
    A -- the output of the activation function, also called the post-activation value
    cache -- a python tuple containing "linear_cache" and "activation_cache";
             stored for computing the backward pass efficiently
    """
    
    if activation == "sigmoid":
        Z, linear_cache = linear_forward(A_prev, W, b)
        A, activation_cache = sigmoid(Z)
    
    elif activation == "relu":
        Z, linear_cache = linear_forward(A_prev, W, b)
        A, activation_cache = relu(Z)
        
    assert (A.shape == (W.shape[0], A_prev.shape[1]))
    cache = (linear_cache, activation_cache)
    
    return A, cache

def L_model_forward(X, parameters):
    """
    Implements forward propagation for the [LINEAR->RELU]*(L-1)->LINEAR->SIGMOID computation
    
    Arguments:
    X -- data, numpy array of shape (input size, number of examples)
    parameters -- output of initialize_parameters()
    
    Returns:
    AL -- last post-activation value
    caches -- list of caches containing:
                every cache of linear_activation_forward() (there are L-1 of them, indexed from 1 to L-1)
    """
    
    caches = []
    A = X
    L = len(parameters) // 2
    
    # Implements [LINEAR -> RELU]*(L-1). Add "cache" to the "caches" list
    for l in range(1, L):
        A_prev = A
        A, cache = linear_activation_forward(A_prev, parameters['W' + str(l)], parameters['b' + str(l)], "relu")
        caches.append(cache)
    
    # Implements LINEAR -> SIGMOID. Add "cache" to the "caches" list
    AL, cache = linear_activation_forward(A, parameters['W' + str(L)], parameters['b' + str(L)], "sigmoid")
    caches.append(cache)
    
    assert(AL.shape == (1, X.shape[1]))
    
    return AL, caches


def compute_cost(AL, Y):
    """
    Implements the cost function
    
    Arguments:
    AL -- probability vector corresponding to your label predictions, shape (1, number of examples)
    Y -- true "label" vector (for example: containing 0 if not Fizz, 1 if Fizz), shape (1, number of examples)
    
    Returns:
    cost -- cross-entropy cost
    """
    
    m = Y.shape[1]
    
    cost = - 1 / m * np.sum(Y * np.log(AL) + (1 - Y) * np.log(1 - AL))
    
    cost = np.squeeze(cost)  # To make sure the cost's shape is what we expect (e.g. turns [[17]] into 17).
    assert(cost.shape == ())
    
    return cost


def linear_backward(dZ, cache):
    """
    Implements the linear portion of backward propagation for a single layer (layer l)
    
    Arguments:
    dZ -- Gradient of the cost with respect to the linear output (of current layer l)
    cache -- tuple of values (A_prev, W, b) coming from the forward propagation in current layer
    
    Returns:
    dA_prev -- Gradient of the cost with respect to the activation (of the previous layer l-1), same shape as A_prev
    dW -- Gradient of the cost with respect to W (current layer l), same shape as W
    db -- Gradient of the cost with respect to b (current layer l), same shape as b
    """
    
    A_prev, W, b = cache
    m = A_prev.shape[1]
    
    dW = 1 / m * np.dot(dZ, A_prev.T)
    db = 1 / m * np.sum(dZ, axis=1, keepdims=True)
    dA_prev = np.dot(W.T, dZ)
    
    assert(dA_prev.shape == A_prev.shape)
    assert(dW.shape == W.shape)
    assert(db.shape == b.shape)
    
    return dA_prev, dW, db


def linear_activation_backward(dA, cache, activation):
    """
    Implements the backward propagation of the LINEAR->ACTIVATION layer
    
    Arguments:
    dA -- post-activation gradient for current layer l
    cache -- tuple of values (linear_cache, activation_cache) we store for computing backward propagation efficiently
    activation -- the activation to be used in this layer, stored as a text string: "sigmoid" or "relu"
    
    Returns:
    dA_prev -- Gradient of the cost with respect to the activation (of the previous layer l-1), same shape as A_prev
    dW -- Gradient of the cost with respect to W (current layer l), same shape as W
    db -- Gradient of the cost with respect to b (current layer l), same shape as b
    """
    
    linear_cache, activation_cache = cache
    
    if activation == "relu":
        dZ = relu_backward(dA, activation_cache)
        dA_prev, dW, db = linear_backward(dZ, linear_cache)
        
    elif activation == "sigmoid":
        dZ = sigmoid_backward(dA, activation_cache)
        dA_prev, dW, db = linear_backward(dZ, linear_cache)
        
    return dA_prev, dW, db


def L_model_backward(AL, Y, caches):
    """
    Implements the backward propagation for the [LINEAR->RELU] * (L-1) -> LINEAR -> SIGMOID group
    
    Arguments:
    AL -- probability vector, output of the forward_propagation (L_model_forward())
    Y -- true "label" vector (containing 0 if not Fizz, 1 if Fizz)
    caches -- list of caches containing:
                every cache of linear_activation_forward() with "relu" (it's caches[l], for l in range(L-1) i.e l = 0...L-2)
                the cache of linear_activation_forward() with "sigmoid" (it's caches[L-1])
    
    Returns:
    grads -- A dictionary with the gradients
             grads["dA" + str(l)] = ...
             grads["dW" + str(l)] = ...
             grads["db" + str(l)] = ...
    """
    
    grads = {}
    L = len(caches) # number of layers
    m = AL.shape[1]
    Y = Y.reshape(AL.shape)
    
    # Initializing the backpropagation
    dAL = - (np.divide(Y , AL) - np.divide(1 - Y, 1 - AL))
    
    # lth layer (SIGMOID -> LINEAR) gradients
    current_cache = caches[L-1]
    grads["dA" + str(L-1)], grads["dW" + str(L)], grads["db" + str(L)] = linear_activation_backward(dAL, current_cache, "sigmoid")
    
    for l in reversed(range(L-1)):
        # lth layer: (RELU -> LINEAR) gradients
        current_cache = caches[l]
        dA_prev_temp, dW_temp, db_temp = linear_activation_backward(grads["dA" + str(l+1)], current_cache, "relu")
        grads["dA" + str(l)] = dA_prev_temp
        grads["dW" + str(l+1)] = dW_temp
        grads["db" + str(l+1)] = db_temp
        
    return grads


def update_parameters(parameters, grads, learning_rate):
    """
    Update parameters using gradient descent
    
    Arguments:
    parameters -- python dictionary containing your parameters
    grads -- python dictionary containing your gradients, output from L_model_backward()
    
    Returns:
    parameters -- python dictionary containing your updated parameters
                  parameters["W" + str(l)] = ...
                  parameters["b" + str(l)] = ...
    """
    
    L = len(parameters) // 2
    
    for l in range(L):
        parameters["W" + str(l+1)] -= learning_rate * grads["dW" + str(l+1)]
        parameters["b" + str(l+1)] -= learning_rate * grads["db" + str(l+1)]
        
    return parameters


def predict(X, y, parameters):
    """
    Predicts the results of an L-layer neural network
    
    Arguments:
    X -- data set of examples you would like to label
    parameters -- parameters of the trained model
    
    Returns:
    p -- predictions for the given dataset X
    """
    
    m = X.shape[1]
    n = len(parameters) // 2
    p = np.zeros((1, m))
    
    # Forward propagation
    probabilities, caches = L_model_forward(X, parameters)
    
    # Convert probabilities to 0/1 predictions
    for i in range(0, probabilities.shape[1]):
        if probabilities[0,i] > 0.5: p[0,i] = 1
        else: p[0,i] = 0
            
    # Print results
    print("Accuracy: " + str(np.sum((p == y) / m)))
    
    return p
                