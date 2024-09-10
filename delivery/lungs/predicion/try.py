import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import matplotlib.pyplot as plt

# Load the trained U-Net model
model = load_model('unet_model.h5')  # Replace with your model file

# Load and preprocess the image
image_path = 'path_to_your_image.jpg'  # Replace with your image path
image = load_img(image_path, target_size=(256, 256))  # Resize to match model input size
image_array = img_to_array(image) / 255.0  # Normalize to [0, 1]
image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension

# Predict the segmentation mask
predicted_mask = model.predict(image_array)[0]  # Remove batch dimension

# Threshold the mask (optional, if your model outputs probabilities)
predicted_mask = (predicted_mask > 0.5).astype(np.uint8)

# Plot the original image and the predicted mask
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.title('Original Image')
plt.imshow(image)

plt.subplot(1, 2, 2)
plt.title('Predicted Mask')
plt.imshow(predicted_mask, cmap='gray')

plt.show()
