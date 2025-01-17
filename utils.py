import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import cv2

def test_accuracy(model, X_test, y_test):
    """Evaluate the test accuracy of a model.
    
    Args:
        model (keras.models.Model): The trained model to evaluate.
        X_test (numpy.ndarray): The test data.
        y_test (numpy.ndarray): The test labels.
    """
    test_loss, test_accuracy = model.evaluate(X_test, y_test)
    print("Test Loss:", test_loss)
    print("Test Accuracy:", test_accuracy)
    
    
def plot_loss(history):
    """Plot the training and validation loss curves.
    
    Args:
        history (keras.callbacks.History): The history object obtained from model training.
    """
    train_loss = history.history['loss']
    val_loss = history.history['val_loss']
    epochs = range(1, len(train_loss) + 1)
    plt.plot(epochs, train_loss, 'b', label='Train Loss')
    plt.plot(epochs, val_loss, 'r', label='Validation Loss')
    plt.title('Training and Validation Losses')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.savefig('loss_curve.png')
    plt.show()
    
    
def plot_accuracy(history):
    """Plot the training and validation accuracy curves.
    
    Args:
        history (keras.callbacks.History): The history object obtained from model training.
    """
    train_accuracy = history.history['accuracy']
    val_accuracy = history.history['val_accuracy']
    epochs = range(1, len(train_accuracy) + 1)
    plt.plot(epochs, train_accuracy, 'b', label='Train Accuracy')
    plt.plot(epochs, val_accuracy, 'r', label='Validation Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.savefig('accuracy_curve.png')
    plt.show()
    
    
def predicting_on_dataset(X_pred, model):
    """Make predictions on a dataset and visualize the results.
    
    Args:
        X_pred (list): List containing the images to make predictions on.
        model (keras.models.Model): The trained model for prediction.
    """
    subset_size = 300
    X_subset = X_pred[:subset_size]
    predictions = model.predict(X_subset)
    fig, axes = plt.subplots(subset_size, 2, figsize=(10, subset_size*2))
    for i in range(subset_size):
        axes[i, 0].imshow(X_subset[0][i])
        axes[i, 0].axis('off')
        axes[i, 1].imshow(X_subset[1][i])
        axes[i, 1].axis('off')
        score = predictions[i]
        axes[i, 1].set_title(score)
    plt.tight_layout()
    plt.savefig('predict_result')
    plt.show()
    

def plot_ranking_predict(ranking_model, X_pred, save_path):
    """Plot the ranking predictions for a set of images.
    
    Args:
        ranking_model (keras.models.Model): The trained ranking model.
        X_pred (list): List containing the images to make predictions on.
        save_path (str): Path to save the plot.
    """
    scores = ranking_model.predict(X_pred[0])
    indices = np.arange(len(scores))
    sorted_indices = sorted(indices, key=lambda x: scores[x], reverse=True)
    num_columns = 5
    num_images = len(X_pred[0])
    num_rows = int(np.ceil(num_images / num_columns))
    fig, axes = plt.subplots(num_rows, num_columns, figsize=(15, 3*num_rows))
    for i, index in enumerate(sorted_indices):
        row = i // num_columns
        col = i % num_columns
        ax = axes[row, col]
        ax.imshow(X_pred[0][index])
        ax.axis('off')
        ax.set_title(f"Score: {scores[index]}")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.show()

def generate_saliency_map(model, image1, image2):
    # Calculez les gradients de sortie par rapport aux entrées
    with tf.GradientTape() as tape:
        tape.watch(image1)
        tape.watch(image2)
        outputs = model([image1[None, ...], image2[None, ...]])
        predictions = outputs[0]  # Supposons que les prédictions se trouvent dans le premier élément de la sortie

    # Calculez les poids de saillance
    gradients = tape.gradient(predictions, [image1, image2])
    saliency_weights = np.mean(np.abs(gradients[0]), axis=-1) + np.mean(np.abs(gradients[1]), axis=-1)

    # Normalisez les poids de saillance dans la plage [0, 1]
    saliency_map = saliency_weights / np.max(saliency_weights)

    # Superposez la carte de saillance sur l'image d'origine
    saliency_map = saliency_map[..., np.newaxis]  # Ajouter une dimension pour correspondre aux canaux de couleur
    heatmap = np.uint8(255 * saliency_map)  # Convertir en échelle de gris
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)  # Appliquer la coloration du jet

    # Normalisez l'image d'origine entre 0 et 1 pour la superposition
    image1_normalized = image1 / np.max(image1)
    image1_normalized = np.uint8(255 * image1_normalized)  # Convertir en échelle de gris

    # Combine l'image d'origine avec la carte de saillance
    superimposed_image = cv2.addWeighted(image1_normalized, 0.6, heatmap, 0.4, 0)

    return superimposed_image