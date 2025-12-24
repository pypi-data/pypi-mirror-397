
import inspect

program1 = """

1. Design a single unit perceptron for classification of a linearly
separable binary dataset without using pre-defined models. Use
the Perceptron() from sklearn.

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.linear_model import Perceptron
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Generate a synthetic linearly separable dataset
X, y = make_classification(
    n_samples=100,
    n_features=2,
    n_informative=2,
    n_redundant=0,
    n_clusters_per_class=1,
    flip_y=0,
    random_state=42
)

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Train the Perceptron
perceptron = Perceptron(max_iter=1000, eta0=1, random_state=42)
perceptron.fit(X_train, y_train)

# Evaluate
accuracy = accuracy_score(y_test, perceptron.predict(X_test))
print(f"Accuracy: {accuracy:.2f}")

# Plot decision boundary
xx, yy = np.meshgrid(
    np.linspace(X[:, 0].min() - 1, X[:, 0].max() + 1, 200),
    np.linspace(X[:, 1].min() - 1, X[:, 1].max() + 1, 200)
)

Z = perceptron.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

plt.figure(figsize=(10, 6))
plt.contourf(xx, yy, Z, alpha=0.3, cmap="coolwarm")
plt.scatter(X[:, 0], X[:, 1], c=y, edgecolor="k", cmap="coolwarm")
plt.title("Perceptron Classification")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
plt.show()

"""

program2 = """
2. Identify the problem with single unit Perceptron. Classify us
ing Or-, Andand Xor-ed data and analyze the result.

import numpy as np
from sklearn.linear_model import Perceptron
from sklearn.metrics import accuracy_score

# Data for AND, OR, XOR gates
data = {
    'AND': (np.array([[0, 0], [0, 1], [1, 0], [1, 1]]),
            np.array([0, 0, 0, 1])),
    
    'OR': (np.array([[0, 0], [0, 1], [1, 0], [1, 1]]),
           np.array([0, 1, 1, 1])),
    
    'XOR': (np.array([[0, 0], [0, 1], [1, 0], [1, 1]]),
            np.array([0, 1, 1, 0])),
}

# Classify AND, OR, XOR gates
for gate, (X, y) in data.items():
    perceptron = Perceptron(max_iter=1000, eta0=1, random_state=42)
    perceptron.fit(X, y)

    y_pred = perceptron.predict(X)
    acc = accuracy_score(y, y_pred) * 100

    print(f"\n{gate} gate accuracy: {acc:.2f}%")
    print(f"Predictions: {y_pred}")
    print(f"True Labels: {y}")


"""

program3 = """
3.  Build an Artificial Neural Network by implementing the Back
propagation algorithm and test the same using appropriate data
sets. Vary the activation functions used and compare the re
sults.


import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load and preprocess the Iris dataset
iris = load_iris()
X = iris.data
y = iris.target

# One-hot encode labels
y = to_categorical(y)

# Standardize features
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Build the neural network with exactly four hidden layers
model = Sequential([
    Dense(64, activation='relu', input_shape=(X_train.shape[1],)),  # Input layer
    Dense(64, activation='relu'),  # Hidden layer 1
    Dense(64, activation='relu'),  # Hidden layer 2
    Dense(64, activation='relu'),  # Hidden layer 3
    Dense(64, activation='relu'),  # Hidden layer 4
    Dense(3, activation='softmax') # Output layer
])

# Compile the model
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Train the model
history = model.fit(
    X_train, y_train,
    epochs=10,
    batch_size=10,
    validation_split=0.2,
    verbose=1
)

# Evaluate the model
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Loss: {loss:.4f}")
print(f"Test Accuracy: {accuracy * 100:.2f}%")

# Predictions
predictions = model.predict(X_test)
predicted_classes = tf.argmax(predictions, axis=1)
true_classes = tf.argmax(y_test, axis=1)

final_accuracy = tf.reduce_mean(
    tf.cast(predicted_classes == true_classes, tf.float32)
)

print(f"Predicted Accuracy: {final_accuracy.numpy() * 100:.2f}%")



"""

program4 = """
4. Build a Deep Feed Forward ANN by implementing the Back
propagation algorithm and test the same using appropriate data
sets. Use the number of hidden layers ¿=4.


import tensorflow as tf
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# -----------------------------
# 1. Load and Preprocess Data
# -----------------------------
iris = load_iris()
X = iris.data
y = iris.target.reshape(-1, 1)

encoder = OneHotEncoder(sparse_output=False)
y = encoder.fit_transform(y)

scaler = StandardScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# -----------------------------
# 2. Define Deep Feed Forward ANN
# -----------------------------
class DeepANN(tf.keras.Model):
    def __init__(self):
        super(DeepANN, self).__init__()
        self.dense1 = tf.keras.layers.Dense(64, activation='relu')
        self.dense2 = tf.keras.layers.Dense(64, activation='relu')
        self.dense3 = tf.keras.layers.Dense(64, activation='relu')
        self.dense4 = tf.keras.layers.Dense(64, activation='relu')
        self.output_layer = tf.keras.layers.Dense(3, activation='softmax')

    def call(self, inputs):
        x = self.dense1(inputs)
        x = self.dense2(x)
        x = self.dense3(x)
        x = self.dense4(x)
        return self.output_layer(x)

model = DeepANN()

# -----------------------------
# 3. Loss Function and Optimizer
# -----------------------------
loss_function = tf.keras.losses.CategoricalCrossentropy()
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

# -----------------------------
# 4. Backpropagation Step
# -----------------------------
@tf.function
def train_step(x_batch, y_batch):
    with tf.GradientTape() as tape:
        predictions = model(x_batch, training=True)
        loss = loss_function(y_batch, predictions)

    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    return loss

# -----------------------------
# 5. Training Loop
# -----------------------------
epochs = 100
batch_size = 16

for epoch in range(epochs):
    for i in range(0, len(X_train), batch_size):
        x_batch = X_train[i:i + batch_size]
        y_batch = y_train[i:i + batch_size]
        loss = train_step(x_batch, y_batch)

    if epoch % 10 == 0:
        print(f"Epoch {epoch}, Loss: {loss.numpy():.4f}")

# -----------------------------
# 6. Model Evaluation
# -----------------------------
def evaluate_model(x, y):
    predictions = model(x, training=False)
    predicted_labels = tf.argmax(predictions, axis=1)
    true_labels = tf.argmax(y, axis=1)
    accuracy = tf.reduce_mean(
        tf.cast(predicted_labels == true_labels, tf.float32)
    )
    return accuracy.numpy()

accuracy = evaluate_model(X_test, y_test)
print(f"\nTest Accuracy: {accuracy * 100:.2f}%")



"""

program5 = """
5. Design and implement an Image classification model to clas
sify a dataset of images using Deep Feed Forward NN. Record
the accuracy corresponding to the number of epochs. Use the
MNIST, CIFAR-10 datasets

import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.utils import to_categorical

# Load and preprocess the MNIST dataset
(X_train, y_train), (X_test, y_test) = mnist.load_data()

# Normalize the input data
X_train = X_train.astype('float32') / 255.0
X_test = X_test.astype('float32') / 255.0

# Convert labels to one-hot encoding
y_train = to_categorical(y_train, num_classes=10)
y_test = to_categorical(y_test, num_classes=10)

# Define the model
model = Sequential([
    Flatten(input_shape=(28, 28)),
    Dense(128, activation='relu'),
    Dense(256, activation='relu'),
    Dense(10, activation='softmax')
])

# Compile the model
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Train the model
model.fit(
    X_train,
    y_train,
    epochs=5,
    batch_size=64,
    validation_split=0.2
)

# Evaluate the model on the test set
test_loss, test_accuracy = model.evaluate(X_test, y_test)
print(f"Test Loss: {test_loss:.4f}")
print(f"Test Accuracy: {test_accuracy:.2f}")



"""

program6 = """
6.  Design and implement a CNN model (with 2 and with 4+ lay
ers of convolutions) to classify multi category image datasets.
Use the MNIST, Fashion MNIST, CIFAR-10 datasets. Set the
No. of Epoch as 5, 10 and 20. Make the necessary changes
whenever required. Record the accuracy corresponding to the
number of epochs. Record the time required to run the pro
gram, using CPU as well as using GPU in Colab. and Test
accuracy corresponding to the following architectures:
• Base Model
• Model with L1 Regularization
• Model with L2 Regularization
• Model with Dropout
• Model with both L2 (or L1) and Dropout.

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.datasets import fashion_mnist
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.regularizers import l1, l2

# Load and preprocess dataset
(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

train_images = train_images.reshape((60000, 28, 28, 1)).astype('float32') / 255.0
test_images  = test_images.reshape((10000, 28, 28, 1)).astype('float32') / 255.0

train_labels = to_categorical(train_labels, 10)
test_labels  = to_categorical(test_labels, 10)

# Build CNN model
def build_model(regularizer=None, dropout_rate=None):
    model = models.Sequential()

    model.add(layers.Conv2D(
        32, (3, 3), activation='relu',
        input_shape=(28, 28, 1),
        kernel_regularizer=regularizer
    ))
    model.add(layers.Conv2D(64, (3, 3), activation='relu',
                            kernel_regularizer=regularizer))
    model.add(layers.MaxPooling2D((2, 2)))

    if dropout_rate is not None:
        model.add(layers.Dropout(dropout_rate))

    model.add(layers.Conv2D(128, (3, 3), activation='relu',
                            kernel_regularizer=regularizer))
    model.add(layers.Conv2D(128, (3, 3), activation='relu',
                            kernel_regularizer=regularizer))
    model.add(layers.MaxPooling2D((2, 2)))

    if dropout_rate is not None:
        model.add(layers.Dropout(dropout_rate))

    model.add(layers.Flatten())
    model.add(layers.Dense(128, activation='relu',
                           kernel_regularizer=regularizer))

    if dropout_rate is not None:
        model.add(layers.Dropout(dropout_rate))

    model.add(layers.Dense(10, activation='softmax'))
    return model

# Compile, train, evaluate
def compile_and_train(model, name):
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    model.fit(
        train_images, train_labels,
        epochs=5,
        batch_size=64,
        validation_split=0.2,
        verbose=2
    )

    loss, acc = model.evaluate(test_images, test_labels, verbose=0)
    print(f"{name} Test Accuracy: {acc:.4f}")

# Experiments
print("\nTraining Base Model...")
base_model = build_model()
compile_and_train(base_model, "Base Model")

print("\nTraining L1 Regularization Model...")
l1_model = build_model(regularizer=l1(0.001))
compile_and_train(l1_model, "L1 Regularization Model")

print("\nTraining L2 Regularization Model...")
l2_model = build_model(regularizer=l2(0.001))
compile_and_train(l2_model, "L2 Regularization Model")

print("\nTraining Dropout Model...")
dropout_model = build_model(dropout_rate=0.5)
compile_and_train(dropout_model, "Dropout Model")


"""

program_all = (
    program1
    + "\n\n"
    + program2
    + "\n\n"
    + program3
    + "\n\n"
    + program4
    + "\n\n"
    + program5
    + "\n\n"
    + program6
)


# ============================================================
# PRINT FUNCTIONS
# ============================================================

def print_program1():
    print(program1)

def print_program2():
    print(program2)

def print_program3():
    print(program3)

def print_program4():
    print(program4)

def print_program5():
    print(program5)

def print_program6():
    print(program6)

def print_programall():
    print(program_all)
