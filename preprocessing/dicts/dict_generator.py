from tqdm import tqdm
import numpy as np
import pandas as pd
import re
import wn
from wn import morphy
ewn = wn.Wordnet('ewn:2020')
m = morphy.Morphy(ewn)
pronouncing_dict_path = './cmudict.dict.txt'
# parse dict
dico = {}
with open(pronouncing_dict_path, 'r', encoding='utf-8') as file:
    for line in file.readlines():
        line = re.sub('\d', '', line)  # remove tone number
        l = line.strip().split(' ')
        word = l[0]
        pronounciation = ' '.join(l[1:])
        # filter some non standard words
        if word.islower() and word.isalpha():
            dico[word] = pronounciation

# first check if the word exists in wordnet


def validate(word):
    # check if exists
    res = wn.synsets(word)
    if res != []:
        return True
    # otherwise check if as a derivation, the lemma exists
    for lemmas_per_pos in m(word).values():
        for lemma in lemmas_per_pos:
            res = wn.synsets(lemma)
            # if there exists one, return
            if res != []:
                return True
    return False

# check if exists in wordnet
# run once then store them
# non_words = []
# for word in tqdm(dico.keys()):
#     if not validate(word):
#         non_words.append(word)

# with open('./non_wordnet_words.txt', 'w', encoding='utf-8') as file:
#     for non_word in non_words:
#         file.write(non_word+'\n')


# However, wordnet excludes some function words, they should be taken into account in dictionary
with open('./non_wordnet_words.txt', 'r', encoding='utf-8') as file:
    non_words = file.read().splitlines()
with open('./wordnet_stopwords.txt', 'r', encoding='utf-8') as file:
    stop_words = file.read().splitlines()

for non_word in non_words:
    if not non_word in stop_words:
        dico.pop(non_word)

# Notice that many of them are acronyms, which is pronounced as individual letters, we could remove them directly from the cmu dict, the acronyms will be dealed in another independent dico.
# ## Remove acronyms
# first collect single letter sound
letter_sound = {}
syllable_count = {}
for word, sound in dico.items():
    if len(word) == 1:
        letter_sound[word] = list(sound.split(' '))
        syllable_count[word] = len(sound.split(' '))
letter_sound['a'] = ['EY']  # A sounds EY1 not AH0


def is_acronym(word, sound, threshold=2, show=False):
    matched = 0
    offset = 0
    sound_list = sound.split(' ')
    for letter in word:
        step = syllable_count[letter]
        if show:
            print(letter_sound[letter])
            print(sound_list[offset:offset+step])

        if letter_sound[letter] == sound_list[offset:offset+step]:
            matched += 1
        if matched >= threshold:
            return True
        offset += step
    return False


acronyms = []
for (word, sound) in dico.items():
    if len(word) > 4:
        continue
    if is_acronym(word, sound, 2):
        acronyms.append(word)

for word in acronyms:
    dico.pop(word)

dico.pop('aaa')

# now we get a well pronounced, wordnet-validated dictionary
df = pd.DataFrame.from_dict(dico, orient='index', columns=['sound'])
df_freq = pd.read_csv('./dict_freq_en.yaml', sep='\t',
                      index_col=0, usecols=[1, 2])
df = df.join(df_freq.astype('Int64'))
df.index.name = 'word'
df.rename(columns={'COUNT': 'freq'}, inplace=True)

# ## Transcription


def encode(phonemes):
    vowels = re.compile(
        '(AO|UW|EH|AH|AA|IY|IH|UH|AE|AW|AY|ER|EY|OW|OY)\d*', re.VERBOSE)
    phonemes = re.sub(vowels, 'Q', phonemes)
    complex_consonant = re.compile('CH|DH|HH|JH|NG|SH|TH|ZH|')
    # complex consonants
    phonemes = re.sub('HH', 'H', phonemes)
    phonemes = re.sub('CH', 'C', phonemes)
    phonemes = re.sub('JH', 'J', phonemes)
    phonemes = re.sub('TH', 'X', phonemes)
    phonemes = re.sub('DH', 'X', phonemes)
    phonemes = re.sub('SH', 'U', phonemes)
    phonemes = re.sub('ZH', 'O', phonemes)
    phonemes = re.sub('NG', 'I', phonemes)

    # remove whitespaces
    phonemes = re.sub(' ', '', phonemes)

    return phonemes


def transcribe(phonemes_list):
    encoding_list = []
    for phonemes in phonemes_list:
        encoding_list.append(encode(phonemes))
    return encoding_list


encoding_list = transcribe(df.sound.astype('str'))
df['encoding'] = encoding_list

# ## delete non-initial vowels


def remove_vowels(encoding_list):
    res = []
    for encoding in encoding_list:
        if len(encoding) > 1:
            res.append(encoding[0] + re.sub('Q', '',
                       encoding[1:-1]) + encoding[-1])
        else:
            res.append(encoding)
    return res

# ## Normalization
#
# We hope that:
# 1. the plurals and the third person single form are uniformly terminated with S(instead of Z)
# 2. the past particles are uniformly terminated with E(instead of T or D)
# 3. the present particles are uniformly terminated with I(this is already done since we encode NG sound by I)
#
# you can take these terminations as a grammatical symbol


def normalize(encodings: pd.Series):
    plurals_or_third_single_form = re.compile('s$')
    past_particle = re.compile('ed$')
    present_particle = re.compile('ing$')

    # print(encodings.head())
    # normalize voiced plural suffix
    res1 = encodings.loc[(encodings.index.str.contains(
        plurals_or_third_single_form, regex=True) == True)].str.replace('Z$', 'S', regex=True)
    # print(res1.head())
    # normalize -ed, sometimes together with a vowel sound i.
    res2 = encodings.loc[(encodings.index.str.contains(
        past_particle, regex=True) == True)].str.replace('[T|D]$', 'E', regex=True)
    # print(res2.head())
    # normalize -ing, always with a vowel sound i
    # we put it here for compeleteness, though no need to do
    # res3 = encodings.loc[(encodings.index.str.contains(present_particle, regex=True) == True)].str.replace('I$', 'I', regex = True)
    # print(res3.head())

    res = pd.concat([res1, res2
                     # ,res3
                     ])
    return res


res = normalize(df.encoding)

# ## Detect inefficient encoding
df['vowel_free'] = remove_vowels(df.encoding)
acronym_residue = df.loc[(df.index.str.len() > 1) & (df.index.str.len() <= 4) & (df.index.str.len(
) < df.vowel_free.str.len()) & (~df.freq.notna()), ['sound', 'encoding', 'vowel_free', 'freq']]
df.drop(acronym_residue.index, inplace=True)
# Notice that many of them are acronyms, which is pronounced as individual letters, we could remove them directly from the cmu dict, the acronyms will be dealed in another independent dico.


# ## normalize (continued)
# notice that most of the extreme encodings have the `S` termination, which is due to enormous derivations in plurals/single third person form (we call them S-form). So it's better to spare another grammatical termination for them.
#
# To do so, we must first recognize the S-form, there are two necessary criterion (yet not proved to be sufficient, perhaps some risks of mis-recognize?)
#
# 1. phonetic criterion: end with s|z
# 2. morphological criterion: word differs its lemma by s(es,ies et etc)
#
# notice that we don't account for irregular words.
#


words_sound_end_with_s = df.loc[df.index.str.contains(
    's$', regex=True) & df.sound.str.contains('[SZ]$', regex=True)].index
words_sound_end_with_s


def get_suffix(word, lemma):
    cnt = sum(w == l for w, l in zip(word, lemma))
    return word[cnt:]


def is_s_form(word, non_s_forms: list):
    for lemmas_per_pos in m(word).values():
        for lemma in lemmas_per_pos:
            suffix = get_suffix(word, lemma)
            if suffix in ['s', 'es', 'ies']:
                return True
    non_s_forms.append(word)


non_s_forms = []
for word in tqdm(words_sound_end_with_s):
    is_s_form(word, non_s_forms)


len(non_s_forms)


# simple verification


'produces' in non_s_forms, 'bliss' in non_s_forms


s_form_candidates = words_sound_end_with_s.to_list()
for word in non_s_forms:
    s_form_candidates.remove(word)

s_forms = pd.Index(s_form_candidates)


s_forms


# reencoding s-forms by `A`-termination


df.loc[s_forms, 'encoding'] = df.loc[s_forms,
                                     'encoding'].str.replace('S$', 'A', regex=True)


df.loc[s_forms, 'encoding']


df['vowel_free'] = remove_vowels(df.encoding)


df['vowel_free']


# ## Manually correct exceptions


# Type letters, 2-grams, 3-grams by themselve


rare_2_grams = df.loc[(df.index.str.len() == 2) & (
    ~df.freq.notna()), ['encoding', 'freq']].drop('hi')


rare_2_grams


df.drop(rare_2_grams.index, inplace=True)


df.loc[(df.index.str.len() <= 3), 'vowel_free'] = df.index[(
    df.index.str.len() <= 3)].str.upper()


# ### reexaminate stats


plot_string_length_freq(df[['encoding', 'vowel_free']])


multiplicity, _, extreme_encoding = coincident_stats(df.vowel_free)


extreme_encoding


multiplicity[multiplicity > 10]


df.to_csv('./dict_en.csv')


df = pd.read_csv('./dict_en.csv', sep=',', index_col=0)


df.head()


df.vowel_free = df.vowel_free.str.lower()


df.loc[:, ['vowel_free', 'freq']].to_csv('./dict_en.yaml', sep='\t')


# ### Convenient abbr for common words use

# with pd.option_context('display.max_rows', None):
#     display(df.loc[(df.freq > 2000) & (df.index.str.len() <= 4)
#             & (df.vowel_free.str.len() > 2)])


# ### Further reductions:
#
# continue reducing the encoding length and the multiplicity (although sometimes we need to trade off between these two objectives)
#
# This will be accounted for lazy/fuzzy pronounciation and be implemented by the users and not directly in the encoding.
#
# For example we can reduce approximants whose property can be considered as an interpolation between a vowel and a consonant. Sometimes it's not easy to tell them from a continuous speech flow and usually omitted by lazy speakers.
#
# There are several phonological circumstances for approximants in English:
# `A` for approximant, `C` for consonant, `V` for vowel
#
# 1. At the beginning `A-V` (`A-C` is not possible)
# 2. At the end `-A`
# 3. `V-A-C`
# 4. `V-A-V`
# 5. `C-A-V`
#
# - for semi-vowels `Y,W`, we identify the following circumstances as reducable: 2, 3, 4, 5
# - for approximant `R,L`, we identify the following circumstances as reducable: 2, 3
#
# and even more radical reduction: e.g. nasal elision
# - for nasal `M,N,NG`: 2, 3(condition to certain trailing consonant)
#
