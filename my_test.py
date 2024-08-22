import os
import itertools
import pickle
from tqdm import tqdm
from scipy.stats import entropy
from collections import defaultdict, Counter


DICT_FILE = 'words.txt'



# FUNCTIONS !!!!!!!!!

def calculate_pattern(guess, true):
    """Generate a pattern list that Wordle would return if you guessed
    `guess` and the true word is `true`
    """
    wrong = [i for i, v in enumerate(guess) if v != true[i]]
    counts = Counter(true[i] for i in wrong)
    pattern = [2] * 5
    for i in wrong:
        v = guess[i]
        if counts[v] > 0:
            pattern[i] = 1
            counts[v] -= 1
        else:
            pattern[i] = 0
    return tuple(pattern)

def generate_pattern_dict(dictionary):
    """For each word and possible information returned, store a list
    of candidate words
    >>> pattern_dict = generate_pattern_dict(['weary', 'bears', 'crane'])
    >>> pattern_dict['crane'][(2, 2, 2, 2, 2)]
    {'crane'}
    >>> sorted(pattern_dict['crane'][(0, 1, 2, 0, 1)])
    ['bears', 'weary']
    """
    pattern_dict = defaultdict(lambda: defaultdict(set))
    for word in tqdm(dictionary):
        for word2 in dictionary:
            pattern = calculate_pattern(word, word2)
            pattern_dict[word][pattern].add(word2)
    return dict(pattern_dict)


def calculate_entropies(words, possible_words, pattern_dict):
    """Calculate the entropy for every word in `words`, taking into account
    the remaining `possible_words`"""
    entropies = {}
    for word in words:
        counts = []
        for pattern in all_patterns:
            matches = pattern_dict[word][pattern]
            matches = matches.intersection(possible_words)
            counts.append(len(matches))
        entropies[word] = entropy(counts)
    return entropies

# END FUNCTIONS!!!!!!

# Load our dictionary
with open(DICT_FILE) as ifp:
    dictionary = list(map(lambda x: x.strip(), ifp.readlines()))
error_msg = 'Dictionary contains different length words.'
assert len({len(x) for x in dictionary}) == 1, error_msg
print(f'Loaded dictionary with {len(dictionary)} words...')
WORD_LEN = len(dictionary[0])

# Generate the possible patterns of information we can get
all_patterns = list(itertools.product([0, 1, 2], repeat=WORD_LEN))

# Calculate the pattern_dict and cache it, or load the cache.
if 'pattern_dict.p' in os.listdir('.'):
    pattern_dict = pickle.load(open('pattern_dict.p', 'rb'))
else:
    pattern_dict = generate_pattern_dict(dictionary)
    pickle.dump(pattern_dict, open('pattern_dict.p', 'wb+'))


## START OF THE WHILE LOOP

word_not_guessed = True


#A list of all remaining words
all_words = set(dictionary)
while word_not_guessed:
    # Calculate entropies
    if len(all_words) < 10:
        candidates = all_words
    else:
        candidates = dictionary
    entropies = calculate_entropies(candidates, all_words, pattern_dict)

    # Guess the candiate with highest entropy
    guess_word = max(entropies.items(), key=lambda x: x[1])[0]
    print(f"Guess this word: {guess_word}")



    #get info on the colors
    ar = [2,2,2,2,2]
    for i in range(5):
        inputVal = int(input('Enter 0(Gray), 1(Yellow), or 2(Green), 3(WORD IS CORRECT):'))
        if inputVal == 3:
            word_not_guessed = False
            break
        ar[i] = inputVal

    info_on_word_colors = tuple(ar)

    words = pattern_dict[guess_word][info_on_word_colors]
    all_words = all_words.intersection(words)


"""
# Simulate games
for _ in range(N_GAMES):

    # Pick a random word for the bot to guess
    WORD_TO_GUESS = random.choice(dictionary)
    print('-'*100)
    print('Word to guess:', WORD_TO_GUESS)

    # Keep a list of the remaining possible words
    all_words = set(dictionary)
    for n_round in range(N_GUESSES):
        # Calculate entropies
        if len(all_words) < 10:
            candidates = all_words
        else:
            candidates = dictionary
        entropies = calculate_entropies(candidates, all_words, pattern_dict)

        # Guess the candiate with highest entropy
        guess_word = max(entropies.items(), key=lambda x: x[1])[0]
        info = calculate_pattern(guess_word, WORD_TO_GUESS)

        # Print round information
        print('Guessing:     ', guess_word)
        print('Info:         ', info)
        if guess_word == WORD_TO_GUESS:
            print(f'WIN IN {n_round + 1} GUESSES!\n\n\n')
            break

        # Filter our list of remaining possible words
        words = pattern_dict[guess_word][info]
        all_words = all_words.intersection(words)
        """

