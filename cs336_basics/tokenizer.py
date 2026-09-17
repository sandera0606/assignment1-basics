import cProfile
# python -m cProfile -o profile.stats script.py
# python -m pstats profile.stats
# # Profile just this specific function call
#    cProfile.run('my_function()')
#    results = pstats.Stats(cProfile.Profile())
#    results.sort_stats(pstats.SortKey.TIME)
# can use tuna to visualize
from pretokenization_example import pretokenize
import heapq
from collections import Counter

from dataclasses import dataclass, field

@dataclass(order=False)
class HeapItem:
    freq: int
    pair: tuple

    def __lt__(self, other):
        if self.freq != other.freq:
            return self.freq > other.freq      # higher freq pops first
        return self.pair > other.pair          # on tie, lexicographically GREATER pair pops first

    def __eq__(self, other):
        return self.freq == other.freq and self.pair == other.pair


# py-spyrun -p $PID --duration 60 ??? --format raw

def initialize_mergedata(freq_table):
    master_pair_freqs = {}
    pair_pos = {}

    for word, freq in freq_table.items():
        for b in range(0, len(word) - 1):
            cur_tuple = (word[b], word[b+1])
            master_pair_freqs[cur_tuple] = master_pair_freqs.get(cur_tuple, 0) + freq
            pair_pos.setdefault(cur_tuple, {})
            pair_pos[cur_tuple].setdefault(word, [])
            pair_pos[cur_tuple][word].append(b)

    freq_heap = [HeapItem(freq, pair) for pair, freq in master_pair_freqs.items()]
    heapq.heapify(freq_heap)

    return master_pair_freqs, pair_pos, freq_heap

def merge_word(word, pair, new_token):
    result = []
    i = 0

    while i < len(word):
        if i < len(word) - 1 and (word[i], word[i + 1]) == pair:
            result.append(new_token)
            i += 2
        else:
            result.append(word[i])
            i += 1

    return tuple(result)


def apply_merge(
    pair,
    my_freq_table,
    pair_pos,
    master_pair_freqs,
    freq_heap
):
    new_token = pair[0] + pair[1]

    # ONLY words containing this pair
    affected_words = list(pair_pos[pair].keys())

    for old_word in affected_words:
        freq = my_freq_table[old_word]

        # Old pairs in this word
        old_pairs = Counter(
            (old_word[i], old_word[i + 1])
            for i in range(len(old_word) - 1)
        )

        # Merge
        new_word = merge_word(old_word, pair, new_token)

        # New pairs in this word
        new_pairs = Counter(
            (new_word[i], new_word[i + 1])
            for i in range(len(new_word) - 1)
        )

        # Update global pair frequencies
        for p, count in old_pairs.items():
            master_pair_freqs[p] -= count * freq

        for p, count in new_pairs.items():
            master_pair_freqs[p] = (
                master_pair_freqs.get(p, 0)
                + count * freq
            )

            # push
            heapq.heappush(freq_heap, HeapItem(master_pair_freqs[p], p))

        # Update frequency table
        del my_freq_table[old_word]
        my_freq_table[new_word] = freq

        # Remove old pair positions
        for p in old_pairs:
            if p in pair_pos and old_word in pair_pos[p]:
                del pair_pos[p][old_word]

                if not pair_pos[p]:
                    del pair_pos[p]

        # Add new pair positions
        for i in range(len(new_word) - 1):
            p = (new_word[i], new_word[i + 1])

            pair_pos.setdefault(p, {})
            pair_pos[p].setdefault(new_word, [])
            pair_pos[p][new_word].append(i)

    return new_token

def train_bpe(filepath="data/TinyStoriesSubset.txt", vocab_size=262, special_tokens=[]):
    # algorithm 1 (inefficient implementation)
    # 1. represent this as a dict[tuple[bytes, ...], int]
    freq_table = {"low": 5, "lower": 2, "widest": 3, "newest": 6} #pretokenize(filepath, special_tokens)

    temp_dict = {}
    for word, freq in freq_table.items():
        utf_encoded = tuple(bytes([b]) for b in word.encode("utf-8"))
        temp_dict[utf_encoded] = freq
    
    my_freq_table = temp_dict

    # starting vocabulary
    vocabulary = []
    for i in range(0, 256):
        vocabulary.append(bytes([i]))
    for token in special_tokens:
        vocabulary.append(token.encode("utf-8"))

    merged_pairs = []
    num_merges = vocab_size - len(vocabulary)
    # merge until vocabulary is _ byte chars
    master_pair_freqs, pair_pos, freq_heap = initialize_mergedata(my_freq_table)
    for i in range(num_merges):
        # Get most frequent valid pair
        new_merge = heapq.heappop(freq_heap)
        while master_pair_freqs[new_merge.pair] != new_merge.freq:
            new_merge = heapq.heappop(freq_heap)
        pair = new_merge.pair

        # Apply merge
        new_token = apply_merge(
            pair,
            my_freq_table,
            pair_pos,
            master_pair_freqs,
            freq_heap
        )

        merged_pairs.append((pair, new_token))



    vocabulary.extend(merged_pairs)
    # return vocab, merges
    print(merged_pairs)
    print(my_freq_table)
    return (merged_pairs, vocabulary)

train_bpe()