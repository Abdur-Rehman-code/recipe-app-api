import kagglehub

# Download latest version
path = kagglehub.dataset_download("ulrikthygepedersen/airbnb-listings")

print("Path to dataset files:", path)
