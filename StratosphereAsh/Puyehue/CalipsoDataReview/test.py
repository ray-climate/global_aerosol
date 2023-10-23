import numpy as np
import matplotlib.pyplot as plt

# Set a random seed for reproducibility
np.random.seed(0)

# Generate random 100x100 2D arrays for red, green, and blue channels
red_channel = np.random.randint(0, 256, (300, 300))
green_channel = np.random.randint(0, 256, (300, 300))
blue_channel = np.random.randint(0, 256, (300, 300))

# Stack the 2D arrays to create a 3D RGB image
rgb_image = np.stack((red_channel, green_channel, blue_channel), axis=-1)

# Create a figure of size 12x8 inches
plt.figure(figsize=(12, 8))

# Display the RGB image using imshow with aspect ratio
plt.imshow(rgb_image, aspect='auto')

plt.axis('off')  # Turn off the axis numbers
plt.tight_layout()
plt.show()
