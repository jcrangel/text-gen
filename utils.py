import string
import numpy as np

# load doc into memory
def load_doc(filename):
	# open the file as read only
	file = open(filename, 'r')
	# read all text
	text = file.read()
	# close the file
	file.close()
	return text

# turn a doc into clean tokens
def clean_doc(doc):
	# replace '--' with a space ' '
	doc = doc.replace('--', ' ')
	# split into tokens by white space
	tokens = doc.split()
	# remove punctuation from each token
	table = str.maketrans('', '', string.punctuation)
	tokens = [w.translate(table) for w in tokens]
	# remove remaining tokens that are not alphabetic
	tokens = [word for word in tokens if word.isalpha()]
	# make lower case
	tokens = [word.lower() for word in tokens]
	return tokens

# save tokens to file, one dialog per line
def save_doc(lines, filename):
	data = '\n'.join(lines)
	file = open(filename, 'w')
	file.write(data)
	file.close()


def read_glove_vecs(glove_file):
    print("Loading glove vecs . ... ")
    with open(glove_file, 'r') as f:
        words = set()
        word_to_vec_map = {}
        for line in f:
            line = line.strip().split()
            curr_word = line[0]
            words.add(curr_word)
            word_to_vec_map[curr_word] = np.array(line[1:], dtype=np.float64)
        
        i = 1
        words_to_index = {}
        index_to_words = {}
        for w in sorted(words):
            words_to_index[w] = i
            index_to_words[i] = w
            i = i + 1

    return words_to_index, index_to_words, word_to_vec_map


def sentences_to_indices(X, word_to_index, index_to_word, word_to_vec_map, max_len):
    """
    Converts an array of sentences (strings) into an array of indices corresponding to words in the sentences.
    The output shape should be such that it can be given to `Embedding()` (described in Figure 4). 
    
    Arguments:
    X -- array of sentences (strings), of shape (m, 1)
    word_to_index -- a dictionary containing the each word mapped to its index
    max_len -- maximum number of words in a sentence. You can assume every sentence in X is no longer than this. 
    
    Returns:
    X_indices -- array of indices corresponding to words in the sentences from X, of shape (m, max_len)
    """
    # X = np.array(X)
    m = X.shape[0]                                   # number of training examples
    vec_len = word_to_vec_map['baseball'].shape[0]
    ### START CODE HERE ###
    # Initialize X_indices as a numpy matrix of zeros and the correct shape (≈ 1 line)
    X_indices = np.zeros( shape = (m, max_len))
    
    for i in range(m):                               # loop over training examples
        
        # Convert the ith training sentence in lower case and split is into words. You should get a list of words.
        # sentence_words = list(map(lambda x : x.lower() , X[i].split(" ")))
        sentence_words = [i.lower() for i in X[i].split()]
        # Initialize j to 0
        j = 0
        
        # Loop over the words of sentence_words
        for w in sentence_words:
            # Set the (i,j)th entry of X_indices to the index of the correct word.
            try:
              X_indices[i, j] = word_to_index[w]
            except KeyError:
              print(w + " doesnt have index, new entry created")
              
              vocab_size = len(word_to_index) + 1
              word_to_index[w] = vocab_size
              X_indices[i, j] = vocab_size
              word_to_vec_map[w] = np.random.rand(vec_len)
              index_to_word[vocab_size] = w 
              continue
            # Increment j to j + 1
            j += 1
            if j >= max_len:
              break
    ### END CODE HERE ###
    # pdb.set_trace()
    return X_indices


def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    # import pdb; pdb.set_trace()
    preds = np.asarray(preds[0]).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


# generate a sequence from a language model
def generate_seq(model, word_to_index, index_to_word, word_to_vec_map, seed_text, max_len,n_words,temperature = 1):
  result = list()
  in_text = seed_text
  # generate a fixed number of words
  # import pdb; pdb.set_trace()
  for _ in range(n_words):
    # encode the text as integer
    # encoded = tokenizer.texts_to_sequences([in_text])[0]
    # truncate sequences to a fixed length
    # encoded = pad_sequences([encoded], maxlen=seq_length, truncating='pre')
    encoded = sentences_to_indices(np.array([in_text]),word_to_index, index_to_word, word_to_vec_map, max_len = n_words)
    # predict probabilities for each word
    # import pdb; pdb.set_trace()
    if temperature == 0 :
      index_class = model.predict_classes(encoded, verbose=0)[0]
    else:
      pred_probs = model.predict(encoded, verbose=0)
      index_class = sample(pred_probs,temperature=0.2)
    #
    # map predicted word index to word
    out_word = ''
    # for word, index in word_to_index.items():
    #   if index == index_class:
    #     out_word = word
    #     break
    out_word = index_to_word[index_class]
    # append to input
    in_text += ' ' + out_word

    #work with sentences of maximum lenght
    if len(in_text.split()) >= max_len:
    # remove the first word
      in_text = in_text.split(' ',1)[1] 
    result.append(out_word)
  return ' '.join(result)

