import numpy as np
import sounddevice as sd
import librosa
import librosa.display
from dtw import dtw
from scipy.spatial.distance import euclidean

# Function to record audio from the user
def record_audio(duration, sample_rate=16000):
    print(f"Recording for {duration} seconds...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float64')
    sd.wait()
    print("Recording finished.")
    return audio.flatten(), sample_rate

# Function to extract MFCC features from audio
def extract_mfcc(audio, sample_rate=16000, num_cepstral=13):
    mfcc_features = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=num_cepstral)
    return mfcc_features.T

# Enrollment: Record and store multiple words from the user
enrolled_features = []
num_enrollment_words = 3
for i in range(num_enrollment_words):
    print(f"Please say word {i+1}:")
    audio, sr = record_audio(3)
    mfcc_features = extract_mfcc(audio, sr)
    enrolled_features.append(mfcc_features)

# Authentication: Record a word and authenticate
print("Please say the authentication word:")
auth_audio, sr = record_audio(3)
auth_mfcc_features = extract_mfcc(auth_audio, sr)

# Calculate DTW distance and determine if it matches any enrolled words
threshold = 200  # You may need to adjust this threshold based on testing
min_distance = float('inf')
for i, mfcc_features in enumerate(enrolled_features):
    distance, _ = dtw(auth_mfcc_features, mfcc_features, dist=euclidean)
    if distance < min_distance:
        min_distance = distance

# Display the result
print(f"DTW Distance: {min_distance}")
if min_distance < threshold:
    print("Voice authentication successful!")
else:
    print("Voice not recognized. Authentication failed.")
