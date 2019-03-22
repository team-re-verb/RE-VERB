import numpy as np
from keras.models import load_model

if __name__ == "__main__":
    
    model = load_model('model.h5')
    demo_mel_fb = np.random.rand(40,1) #40 dimension filter bank

    print(f'Extracted features as:\n{model.predict(demo_mel_fb)}')