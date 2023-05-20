# JumpType

A pronunciation-designed English input method based on [Rime](https://rime.im/)

An online demo can be found [here](https://jumptype.netlify.app/), which is based on [LibreService/my_rime](https://github.com/LibreService/my_rime)

A video demo: [JumpType：基于音节的英文输入方案](https://www.bilibili.com/video/BV1nA41197x6/?share_source=copy_web&vd_source=cd8f52b3a67ef0e85985b32a4f622eef)

## Prologue

`xs ln is kmpzd by jmp tp wx the abv kd.`

This line is composed by JumpType with the above code.

JumpType, by its name, is an input method that aims at saving keystroke times, i.e. type by jumping over the letters.

In English(perhaps also in most of the phonograms), words are redundant in written form compare to their oral form. Examples are everywhere: silent gh in straight, redundant u after q, silent b after m. Although people are lazy, they get used to type letters key by key. However, ideogram users cannot type their mother language without an input method which foreigners seldom hear about, and I have once been asked about how chinese people type their language on computer, "Does your keyboard have thousands of keys?"

I laughed for a while and show him my input method, but he was not convinced. He became more doubtful when I said I could type even faster than him. This should definitely thanks to the concise and compact virtue of chinese, but also don't forget those inventors of chinese input methods. There was a latinization movement to abolish Chinese characters and embrace the letters, calls and critics raised to the peak when the information era came. Dramatically, together with the anxiety the computer brings the solution to digital adaptation for such an ancient language.

Now back to our story. To fill up the gap between the oral and written form of a phonogram language, as well as reducing the keystroke times, is it possible to implement an input method for english? With a little search, **Rime**, an open input method comes into my eyes. Rime is created by a group of input method fans, who aims at building a smart and uniform framework that supports kinds of input need such as Middle Chinese, Cantonese and so on. Rime is absolutely a fancy tool for language geeks, whose needs are ignored by big companies.

Based on rime, input method design became doable for me. I don't need to code anything except customize my own encoding table. After two weeks' working, now let me introduce you my input method designed for English: JumpType.

## Pronounced based encoding

The input method logic is simple: choose something else to represent the words itself and type it instead. Such a thing is called an encoding. The principle to design encodings may be different, but the target is the same: to save information (in space or in time or in secret). In our practice, the target is a bit more, that is to be easily memorized(design for humans not the machines)

Our encoding is based on word's pronunciation. we notice that generally the spelling of a word is always longer than its pronunciation. thus word's pronunciation offers a natural encoding scheme. Now forget about what you see and listen to your internal voice.

## Abjad

Encoding by pronunciation is only a first and a conservative step. In fact, we can also remove all the vowel sounds. Amazing right? In linguistics, there is called _Abjad_(alphabet in Arabic), means a written system that omits vowels and contains only consonants(e.g. Arabic). Although unlike Arabic, English vowels can also been removed in price of a mild unreadability, this in other words proves the redundancy of English.

A side product of Abjad encoding is that, it's more friendly to different spelling customs and also more robust against various types of accents because the differences are eliminated after removing the vowels.

## Encoding rules

The encoding is based on the CMU pronunciation dictionary, which in general serves for NLP/speech recognition purpose, till I found it's a ready made material for this project. So almost all the encoding rules are inherited from it.

All english consonant are illustrated in the following table in CMU notation.

|  stop   |   affricative   |    fricative    |    nasal    | approximant |
| :-----: | :-------------: | :-------------: | :---------: | :---------: |
| `p`/`b` | ch(`c`)/jh(`j`) | th(`x`)/dh(`x`) | m/n/ng(`i`) |   `l`/`r`   |
| `t`/`d` |                 |     `f`/`v`     |             |     `w`     |
| `k`/`g` |                 |     `s`/`z`     |             |     `y`     |
|         |                 | sh(`u`)/zh(`o`) |             |             |
|         |                 |     hh(`h`)     |             |             |

All single consonants are encoded as is, while the complex consonants are encoded as letters in parentheses. Vowels, since removed, are not encoded by default, but for completeness all of them are encoded by `q`.

## Coincident codes, compromises and special cases

Just in all practice, when you try to optimize something, a kind of trade-off occurs. In our setting, our goal is to reduce the keystroke times, i.e. the encoding length. However, the more compressed an encoding is, the more possible words it encodes, this is so-called chongma(coincident codes). Intuitively, the coincidence rate is negative correlated to the average encoding length. Coincident codes are not inevitable neither disastrous unless their are too much.

To reduce the coincidence rate and multiplicity, we made some compromises.

1. words ~~begin or~~ end with vowels are added a `q` in the ~~beginning or~~ the end. (beginning vowels are replaced by the initial letter)
2. words less than three letters are encoded as is(in the original form).
3. ~~some grammatical termination are used for several types of words: plurals and third person single forms (`s`-forms) uses `a` termination instead of `s` or `z`; past particles (`ed`-forms) uses `e` instead of `t` or `d`.~~ they are now reverted to the phonetic ending to be more intuitive.

## Statistics

A word/encoding length diagram briefly illustrates how much reduction we have done by JumpType.

<img src='./preprocessing/encoding comparison.png'>
where word is the original word, encoding denotes the encoding before abjad while the vowel free denotes the encoding after abjad.

A more detailed analysis is provided [here](./preprocessing/dicts/encoding_syllabi.ipynb)

## Todo

JumpType is far more than accomplished, as this doc is the first time I tried it in practice and already found some inconvenience during typing. I will continue to refine it and welcome any insights from whomever in interest.

**the encoding map is not fully determined, may be largely changed in the future.**

- [x] space auto input
- [ ] ~~build acronym dictionary~~ (directly type is enough)
- [ ] support initial capitalization transform
- [ ] support full capitalization transform

- [ ] continue optimizing encoding logic
- [x] make a web version (based on my-rime)
- [ ] build French version

## Usage

We assume you are already familiar with Rime, if not, maybe take some look first in its official [wiki](https://github.com/rime/home/wiki).

Add `jump_type_en.dict.yaml` and `jump_type.schema.yaml` file to your user directory, add `schema: jump_type` to the `schema_list` in `default.custom.yaml`, click redeploy and enjoy!
