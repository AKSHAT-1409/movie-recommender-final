import pickle
import gzip

# Load original pickle file
with open('similarity.pkl', 'rb') as f_in:
    data = pickle.load(f_in)

# Save it in compressed format
with gzip.open('similarity_compressed.pkl.gz', 'wb') as f_out:
    pickle.dump(data, f_out)

print("✅ similarity.pkl has been compressed to similarity_compressed.pkl.gz")
