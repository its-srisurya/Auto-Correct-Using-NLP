from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# 1. Tokenization Module
def word_tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

# 2. Weighted Levenshtein Distance
def weighted_levenshtein_distance(s1, s2, insertion_cost=1, deletion_cost=1, substitution_cost=1):
    if len(s1) < len(s2):
        return weighted_levenshtein_distance(s2, s1, insertion_cost, deletion_cost, substitution_cost)

    if len(s2) == 0:
        return len(s1) * deletion_cost

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insert_cost = previous_row[j + 1] + insertion_cost
            delete_cost = current_row[j] + deletion_cost
            substitute_cost = previous_row[j] + (substitution_cost if c1 != c2 else 0)
            current_row.append(min(insert_cost, delete_cost, substitute_cost))
        previous_row = current_row
    return previous_row[-1]

# 3. Load Dictionary
def load_dictionary():
    dictionary = set()  # Initialize an empty set to store words
    with open("dataset.txt", "r") as file:
#    with open("words_alpha.txt", "r") as file:        
        for line in file:
            dictionary.add(line.strip().lower())  # Add each word to the dictionary
    return dictionary  # Return the complete set of words

# 4. Main Autocorrect System
def autocorrect_system(input_text, dictionary):
    processed_text = word_tokenize(input_text)
    corrections = {}
    
    for word in processed_text:
        # Find closest match in the dictionary using weighted Levenshtein distance
        closest_match = min(dictionary, key=lambda dict_word: weighted_levenshtein_distance(word, dict_word))
        # Set correction only if the distance is less than a threshold
        distance = weighted_levenshtein_distance(word, closest_match)
        if distance < 3:  # Adjust the threshold as needed
            corrections[word] = closest_match
        else:
            corrections[word] = word  # No correction if distance is too high

    return corrections

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/correct', methods=['POST'])
def correct():
    user_input = request.form['inputText']
    dictionary = load_dictionary()
    corrected_text = autocorrect_system(user_input, dictionary)
    return jsonify(corrected_text)

if __name__ == '__main__':
    app.run(debug=True)
