import os
import cv2
import pickle
import cv2
import shutil
from tqdm import tqdm

def copy_and_rename(image_path, idx, output_folder):
    """Copy the image to the output folder and rename it based on the index."""
    new_name = os.path.join(output_folder, f"frame_{idx}.png")
    shutil.copy(image_path, new_name)

def extract_features(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    orb = cv2.ORB_create()
    _, des = orb.detectAndCompute(img, None)
    return des

def compute_similarity(des1, des2, distance_threshold=30):  # threshold value is very important for proper sorting
    if des1 is None or des2 is None or len(des1) == 0 or len(des2) == 0:
        return float('inf')

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    
    # Filter matches based on the threshold
    good_matches = [m for m in matches if m.distance < distance_threshold]
    
    # If there are no good matches, return a large distance
    if not good_matches:
        return float('inf')
    
    # Using the sum of distances of good matches as the score
    return sum([m.distance for m in good_matches])

###############

def cache_features(image_folder, cache_path):
    if os.path.exists(cache_path):
        with open(cache_path, 'rb') as f:
            features_cache = pickle.load(f)
    else:
        features_cache = {}

    # sort the input directory alphabetically - slice [:n] if truncating the input dir
    images = sorted([os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith('.png')])
    # images = sorted([os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith('.png')])[:100]

    
    # Compute and save missing features
    for image_path in tqdm(images, desc="Caching features"):
        if image_path not in features_cache:
            features_cache[image_path] = extract_features(image_path)

    with open(cache_path, 'wb') as f:
        pickle.dump(features_cache, f)

    return features_cache


def iterative_sorting(image_folder, cache_path, num_iterations=3, window_size=10):
    features_cache = cache_features(image_folder, cache_path)
    images = list(features_cache.keys())
    seed_image_path = images[0]  # Initial seed
    
    # Initial Sort
    sorted_images = sort_using_cache(seed_image_path, features_cache)

    # Refined Iterative Sorts
    for iteration in range(num_iterations):
        print(f"Refining sort: Iteration {iteration + 1}")
        for i in tqdm(range(0, len(sorted_images) - window_size), desc="Windowed refinement"):
            window = sorted_images[i:i+window_size]
            seed_in_window = window[0]
            sorted_window = sort_using_cache(seed_in_window, features_cache, specific_images=window)
            sorted_images[i:i+window_size] = sorted_window

    return sorted_images

def sort_using_cache(seed_image_path, features_cache, specific_images=None):
    seed_features = features_cache[seed_image_path]
    
    if specific_images:
        images = specific_images
    else:
        images = list(features_cache.keys())

    # Compute similarity scores
    scores = []
    for image_path in images:
        img_features = features_cache[image_path]
        similarity = compute_similarity(seed_features, img_features)
        scores.append((image_path, similarity))

    sorted_images = sorted(scores, key=lambda x: x[1], reverse=True)
    return [img[0] for img in sorted_images]


def main(image_folder, output_folder, num_iterations=3, window_size=10):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Path to save/load cached features
    cache_path = os.path.join(image_folder, "features_cache.pkl")

    # Use iterative sorting
    sorted_image_paths = iterative_sorting(image_folder, cache_path, num_iterations, window_size)

    # Copy and rename the images
    print("Copying and renaming the images based on similarity...")
    for idx, image_path in tqdm(enumerate(sorted_image_paths)):
        copy_and_rename(image_path, idx, output_folder)
    
    print("done.")


if __name__ == "__main__":
    folder_path = "/Users/matthewheaton/Documents/DOCENTS/lp1_design/assets/CIL_square_images"  
    output_path = "/Users/matthewheaton/Documents/DOCENTS/lp1_design/assets/sorted_test"  

    # You can adjust num_iterations and window_size as needed
    main(folder_path, output_path, num_iterations=5, window_size=30)