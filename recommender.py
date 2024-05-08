import pandas as pd
import numpy as np
import pickle
import h5py
from tabulate import tabulate

# Function to extract weights from HDF5 file for a given layer
def extract_weights(file_path, layer_name):
    with h5py.File(file_path, 'r') as h5_file:
        if layer_name in h5_file:
            weight_layer = h5_file[layer_name]
            # Check if the layer is a dataset
            if isinstance(weight_layer, h5py.Dataset):
                # Normalize the weights using L2 norm
                weights = weight_layer[()]
                weights = weights / np.linalg.norm(weights, axis=1).reshape((-1, 1))
                return weights
            
    # Raise error if layer is not found in the HDF5 file
    raise KeyError(f"Unable to find weights for layer '{layer_name}' in the HDF5 file.")

# File path for the HDF5 file containing anime weights
file_path = '../models/myanimeweights.h5'

# Function to find similar animes based on provided anime name
def find_similar_animes(name, n=10):
    # Extract anime weights from the HDF5 file
    anime_weights = extract_weights(file_path, 'anime_embedding/anime_embedding/embeddings:0')

    # Load anime encoder from pickle file
    with open('../models/anime_encoder.pkl', 'rb') as file:
        anime_encoder = pickle.load(file)

    # Load anime dataset from pickle file
    with open('../models/anime-dataset-2023.pkl', 'rb') as file:
        df_anime = pickle.load(file)

    # Replace "UNKNOWN" values with empty string
    df_anime = df_anime.replace("UNKNOWN", "")

    # Get the row corresponding to the provided anime name
    anime_row = df_anime[df_anime['Name'] == name].iloc[0]
    index = anime_row['anime_id']
    
    # Encode the anime index
    encoded_index = anime_encoder.transform([index])[0]
    
    # Calculate distances between the provided anime and all others
    weights = anime_weights
    dists = np.dot(weights, weights[encoded_index])
    sorted_dists = np.argsort(dists)
    n = n + 1
    closest = sorted_dists[-n:]
    SimilarityArr = []
    id = 11
    
    # Iterate over the closest animes and gather information
    for close in closest:
        id = id - 1
        decoded_id = anime_encoder.inverse_transform([close])[0]
        anime_frame = df_anime[df_anime['anime_id'] == decoded_id]
        anime_name = anime_frame['Name'].values[0]
        similarity = dists[close]
        similarity = "{:.2f}%".format(similarity * 100)
        score = float(anime_frame['Score'].values[0])

        # Add anime information to similarity array if it's not the provided anime itself
        if anime_name != name:
            SimilarityArr.append(
                {
                    "id": id,
                    "Name": anime_name,
                    "Similarity": similarity,
                    "Score": score,
                } 
            )
    SimilarityArr = list(reversed(SimilarityArr))
    # Return the array containing similar animes
    return SimilarityArr