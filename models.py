import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Embedding
from tensorflow.keras.layers import Bidirectional 
from tensorflow.keras.optimizers import Adam


def pretrained_embedding_layer(word_to_vec_map, word_to_index, trainable = False):
    """
    Creates a Keras Embedding() layer and loads in pre-trained GloVe 50-dimensional vectors.
    
    Arguments:
    word_to_vec_map -- dictionary mapping words to their GloVe vector representation.
    word_to_index -- dictionary mapping from words to their indices in the vocabulary (400,001 words)

    Returns:
    embedding_layer -- pretrained layer Keras instance
    """
    
    vocab_len = len(word_to_index) + 1                  # adding 1 to fit Keras embedding (requirement)
    emb_dim = word_to_vec_map["cucumber"].shape[0]      # define dimensionality of your GloVe word vectors (= 50)
    
    ### START CODE HERE ###
    # Initialize the embedding matrix as a numpy array of zeros of shape (vocab_len, dimensions of word vectors = emb_dim)
    emb_matrix = np.zeros(shape=(vocab_len,emb_dim))
    
    # Set each row "index" of the embedding matrix to be the word vector representation of the "index"th word of the vocabulary
    for word, index in word_to_index.items():
        emb_matrix[index, :] = word_to_vec_map[word]

    # Define Keras embedding layer with the correct output/input sizes, make it non-trainable. Use Embedding(...). Make sure to set trainable=False. 
    embedding_layer = Embedding(vocab_len,emb_dim,trainable=trainable)
    
    ### END CODE HERE ###

    # Build the embedding layer, it is required before setting the weights of the embedding layer. Do not modify the "None".
    embedding_layer.build((None,))
    
    # Set the weights of the embedding layer to the embedding matrix. Your layer is now pretrained.
    embedding_layer.set_weights([emb_matrix])
    
    return embedding_layer



def bidi_model(word_to_vec_map,word_to_index):
  model = Sequential()
  # in : (batch, input_lengh) , [12,3,2,3,4,5,12,..., input_lentgh]
  vocab_size = len(word_to_index) + 1  
  model.add(pretrained_embedding_layer(word_to_vec_map,word_to_index,trainable = False))
  model.add(Bidirectional(LSTM(100, return_sequences=True)) )
  model.add(Bidirectional(LSTM(100)) )
  model.add(Dense(100, activation='relu'))
  model.add(Dense(vocab_size, activation='softmax'))
  print(model.summary())
  # compile model
  opt = Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, amsgrad=False)
  model.compile(loss='sparse_categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
  return model




