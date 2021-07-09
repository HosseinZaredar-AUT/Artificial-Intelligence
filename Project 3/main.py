from striprtf.striprtf import rtf_to_text
import re


def read_file(file_path):
    file = open(file_path, 'r')
    text = rtf_to_text(file.read())
    file.close()
    return text


def remove_skip_words(words):
    skip_words = {'.', ',', ':', '!', '?', "'", '"', '(', ')', '/', '-', '--', ';', '_'}
    return [word.lower() for word in words if word.lower() not in skip_words]


def train(train_text):

    n = 0  # total number of words

    sentences = train_text.split('\n')

    unigram = dict()
    bigram = dict()
    trigram = dict()

    for sentence in sentences:

        words = sentence.split()

        # removing skip words
        words = remove_skip_words(words)
        n += len(words)

        # train unigram, bigram and trigram
        for i in range(len(words)):

            # unigram
            if words[i] in unigram:
                unigram[words[i]] += 1
            else:
                unigram[words[i]] = 1

            # bigram
            if i == len(words) - 1:
                continue

            if words[i] in bigram:
                if words[i + 1] in bigram[words[i]]:
                    bigram[words[i]][words[i + 1]] += 1
                else:
                    bigram[words[i]][words[i + 1]] = 1
            else:
                bigram[words[i]] = {words[i + 1]: 1}

            # trigram
            if i == len(words) - 2:
                continue

            if (words[i], words[i + 1]) in trigram:
                if words[i + 2] in trigram[(words[i], words[i + 1])]:
                    trigram[(words[i], words[i + 1])][words[i + 2]] += 1
                else:
                    trigram[(words[i], words[i + 1])][words[i + 2]] = 1
            else:
                trigram[(words[i], words[i + 1])] = {words[i + 2]: 1}

    return n, unigram, bigram, trigram


def guess_words(unigram, bigram, trigram, test_text, n):

    # backoff model coefficients
    l1 = 0.1  # unigram
    l2 = 0.7  # bigram
    l3 = 0.2  # trigram

    guessed_words = []

    sentences = test_text.split('\n')

    for sentence in sentences:

        test_words = sentence.split()
        test_words = remove_skip_words(test_words)

        for i in range(len(test_words)):

            if test_words[i] == '$':

                max_p = 0
                best_word = ''

                for candidate_word in unigram:

                    # unigram probability
                    p1 = unigram[candidate_word] / n

                    # bigram probability
                    p2 = 0
                    if i > 0 and test_words[i - 1] in bigram \
                            and candidate_word in bigram[test_words[i - 1]]:
                        p2 = bigram[test_words[i - 1]][candidate_word] / unigram[test_words[i - 1]]

                    # trigram probability
                    p3 = 0
                    if i > 1 and (test_words[i - 2], test_words[i - 1]) in trigram \
                            and candidate_word in trigram[(test_words[i - 2], test_words[i - 1])]:
                        p3 = trigram[(test_words[i - 2], test_words[i - 1])][candidate_word] \
                             / bigram[test_words[i - 2]][test_words[i - 1]]

                    # calculating the total probability using backoff model
                    p = l1 * p1 + l2 * p2 + l3 * p3

                    # if this candidate is better than the previous ones, select it
                    if p > max_p:
                        max_p = p
                        best_word = candidate_word

                guessed_words.append(best_word)

    return guessed_words


def evaluate_model(guessed_words, actual_words):
    n = len(guessed_words)
    right_guess_count = 0
    for i in range(n):
        if actual_words[i].lower() == guessed_words[i].lower():
            right_guess_count += 1
    return f"Accuracy = {right_guess_count}/{n} = {right_guess_count/n}"


def main():

    # reading the train text
    train_text = read_file('Train_data.rtf')

    # training the model
    n, unigram, bigram, trigram = train(train_text)

    # reading test text
    test_text = read_file('Test_data.rtf')
    test_text = re.sub('\x94', '', test_text)

    # guessing the missing words
    guessed_words = guess_words(unigram, bigram, trigram, test_text, n)
    print('Guessed Words:', guessed_words)

    # reading the real values
    actual_words_text = read_file('labels.rtf')
    actual_words_text = re.sub('[0-9]|,| ', '', actual_words_text)
    actual_words = actual_words_text.split('\n')
    print('Actual Words:', actual_words)

    # evaluating the result
    evaluation = evaluate_model(guessed_words, actual_words)
    print('Accuracy =', evaluation)


if __name__ == '__main__':
    main()