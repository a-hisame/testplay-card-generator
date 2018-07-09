# Testplay Card Generator

[![Build Status](https://travis-ci.org/a-hisame/testplay-card-generator.svg?branch=develop)](https://travis-ci.org/a-hisame/testplay-card-generator)
[![codecov](https://codecov.io/gh/a-hisame/testplay-card-generator/branch/master/graph/badge.svg)](https://codecov.io/gh/a-hisame/testplay-card-generator)
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

[->日本語で読みたい方はこちら](README_ja.md).

```
Note: Not it is alpha version so documentation is not completed.
Moreover, how to use may be changed in future.
```

How do you do when you want to play card game but the card is nothing?

Especially, when you design your board game which uses several cards,
you want to print out alpha-version card and try to adjust by using printed ones, don't you?

I hope following for the test play cards generator.

* Draw basic components, like rectangle and lines
* Draw text in the bounds
* Make multiple card images from layout file and contents file
* Generate file easy to print, like pdf format

This project can provide above features for you.


## Example

From [layout yml file](layout-sample.yml) and [card data csv file](data-sample.csv),
this project generates following image(s) and PDF file.

* PNG Image

![](output0001.png)

![](output0002.png)

* [PDF file for print](output.pdf)


## Install

I tested it on ubuntu 18.04 and Python 3.6.5 (virtualenv).

```
# setup virtualenv
virtualenv .venv
source .venv/bin/activate

# only use and install
python scripts/install.py

# if you are developer, needs to install development tools additionally
python scripts/install.py requirements-dev.txt
```


## Preparation

And you have to prepare `layout file (yml format)` , `data file (csv format)` .

You can use `layout-sample.yml` and `data-sample.csv` for checking to work the program on your local computer well.


## How to use

By following command you can run program and get the `output.pdf` file for printing.

```
tcgen --layout <your layout file> --data <your data file> --output output.pdf
```

## Layout File

Layout File describe what are drawn and used from data file.
`layout-sample.yml` explains what is valid so please read if needed.


## Data File

It is CSV format and each row data is mapped for a card.
If you want to make the cards, read `layout-sample.yml` and `data.csv` and make yourself contents.


## LICENSE

This project source codes and sample resources are under [MIT LICENSE](LICENSE) .

But it contains Noto Font as default text rendering and the fonts are licensed under the SIL Open Font License 1.1.

* [Noto Sans CJK JP Light](data/fonts/NotoSansCJKjp-Light.ttf) - https://www.google.com/get/noto/
* [Noto Sans CJK JP Bold](data/fonts/NotoSansCJKjp-Bold.ttf) - https://www.google.com/get/noto/
