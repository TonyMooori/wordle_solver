import numpy as np
import math
from tqdm import tqdm
from typing import List, Dict, Tuple, Union


def load_words(fname: str, n_letter: int = None) -> List[str]:
    """ load words from file

    :param fname: file name
    :type fname: str
    :param n_letter: number of letters, None for all
    :type n_letter: int
    :return: list of words in file
    :rtype: list
    """
    with open(fname) as f:
        words = f.readlines()
    words = [word.strip() for word in words]

    if n_letter is None:
        return words
    else:
        return [word for word in words if len(word) == n_letter]


def wordle_result(true_answer: str, estimated_word: str) -> int:
    """calculate wordle result

    :param true_answer: correct answer
    :type true_answer: str
    :param estimated_word: word you input
    :type estimated_word: str
    :return: n_letter digit ternary number(0: same, 1: exists, 2: not exists)) 
    :rtype: int
    """
    result = 0
    true_answer_chars: List[str] = list(true_answer)
    for i, c in enumerate(estimated_word):
        if true_answer_chars[i] == c:
            true_answer_chars[i] = "*"

    multiplier = 1
    for i, c in enumerate(estimated_word):
        if true_answer_chars[i] == "*":
            result += 0 * multiplier
        elif c in true_answer_chars:
            result += 1 * multiplier
        else:
            result += 2 * multiplier
        multiplier *= 3

    return result


def calc_entropy(distribution: Dict[int, int], n_word: int) -> float:
    """calc entropy of result distribution

    :param distribution: dictionary from wordle result to number of filtered words
    :type distribution: Dict[str, int]
    :param n_word: total number of words
    :type n_word: int
    :return: entropy of result distribution
    :rtype: float
    """
    entropy = 0
    for key in distribution.keys():
        p = distribution[key] / n_word
        entropy += p * math.log(p, 2)
    return -entropy


def calc_word_distribution(
        estimated_word: str,
        candidate_words:
        List[str],
        only_count: bool) -> Dict[int, Union[int, List[str]]]:
    """[summary]

    :param estimated_word: [description]
    :type estimated_word: str
    :param candidate_words: [description]
    :type candidate_words: List[str]
    :param only_count: [description]
    :type only_count: bool
    :return: [description]
    :rtype: Dict[int, Union[int, List[str]]]
    """
    word_distribution = {}
    for word in candidate_words:
        result = wordle_result(word, estimated_word)

        if only_count:
            if result in word_distribution:
                word_distribution[result] += 1
            else:
                word_distribution[result] = 1
        else:
            if result in word_distribution:
                word_distribution[result].append(word)
            else:
                word_distribution[result] = [word]
    return word_distribution


def select_best_word(all_words, candidate_words):
    scores = []
    bar = tqdm(total=len(all_words))
    for estimated_word in all_words:
        bar.update(1)

        word_distribution = calc_word_distribution(
            estimated_word, candidate_words, True)

        scores.append(calc_entropy(word_distribution, len(candidate_words)))

    return scores


def main():
    n_letter = 5
    # https://github.com/dwyl/english-words
    whole_words = load_words("./secret/whole_words.txt", n_letter)
    whole_words = load_words("./secret/candidate_words.txt", n_letter)
    candidate_words = load_words("./secret/candidate_words.txt", n_letter)

    # input answer
    while True:
        answer = input('Enter the %d letter word: ' % n_letter).strip()
        if len(answer) == n_letter:
            if answer in candidate_words:
                break
            else:
                print("The word is not in the candidate list.")
        else:
            print("The word is not %d letter." % n_letter)

    count = 0
    # solve
    while True:
        print("*" * 50)
        print("now candidates are: %d (e.g. %s)" %
              (len(candidate_words), str(candidate_words[:10])))

        # select best word
        if len(candidate_words) <= 2:
            estimated_word = candidate_words[0]
        else:
            scores = select_best_word(whole_words, candidate_words)
            args = np.argsort(scores)[::-1]

            print("below the list of scores:")
            for i in args[:10]:
                print(whole_words[i], ":", scores[i])

            estimated_word = whole_words[args[0]]
        print("estimated_word is ", estimated_word)

        # filter words with result
        result = wordle_result(answer, estimated_word)
        count += 1

        if result == 0:
            break
        else:
            distribution = calc_word_distribution(
                estimated_word, candidate_words, False)
            candidate_words = distribution[result]

    print("number of trial:", count)


if __name__ == '__main__':
    main()
