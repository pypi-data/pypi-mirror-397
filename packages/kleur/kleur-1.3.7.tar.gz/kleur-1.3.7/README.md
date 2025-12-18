# Kleur: [HSLuv](https://www.hsluv.org/) based color utils & theme generators

[![Poetry](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/githuib/kleur/master/assets/logo.json)](https://pypi.org/project/kleur)
[![PyPI - Version](https://img.shields.io/pypi/v/kleur)](https://pypi.org/project/kleur/#history)
[![PyPI - Python Versions](https://img.shields.io/pypi/pyversions/kleur)](https://pypi.org/project/kleur)

I'd like to give special credits to [Alexei Boronine](https://github.com/boronine) and everyone else who contributed to the [HSLuv](https://www.hsluv.org/) project.
This work provided the fundaments to build this package on (and is the only dependency used in it).

![alt text](https://github.com/githuib/kleur/raw/master/assets/screenshots/theme.png "kleur theme")
![alt text](https://github.com/githuib/kleur/raw/master/assets/screenshots/css.png "kleur css")

## Installation

```commandline
pip install kleur
```

## Usage

### Preview a color theme

#### General help

```commandline
$ kleur theme -h
usage: kleur theme [-h] [-c NAME=HUE (1-360) [NAME=HUE (1-360) ...]]
[-m] [-a] [-s NUMBER_OF_SHADES] [-v NUMBER_OF_VIBRANCES]

options:
  -h, --help            show this help message and exit
  -c, --colors NAME=HUE (1-360) [NAME=HUE (1-360) ...]
  -m, --merge-with-default-theme
  -a, --alt-default-theme
  -s, --number-of-shades NUMBER_OF_SHADES
  -v, --number-of-vibrances NUMBER_OF_VIBRANCES
```

#### Preview default theme

```commandline
$ kleur theme
```
![alt text](https://github.com/githuib/kleur/raw/master/assets/screenshots/theme/default.png "kleur theme")

#### Preview custom theme

```commandline
$ kleur theme -c green=133 blue=257 tomato=20
 ```
![alt text](https://github.com/githuib/kleur/raw/master/assets/screenshots/theme/custom.png "kleur theme -c green=133 blue=257 tomato=20")

#### Preview custom theme merged with default theme

```commandline
$ kleur theme -c green=133 blue=257 tomato=20 -m
 ```
![alt text](https://github.com/githuib/kleur/raw/master/assets/screenshots/theme/merged.png "kleur theme -c green=133 blue=257 tomato=20 -m")

### Generate shades (as CSS variables), based one 1 or 2 (hex) colors

#### General help

```commandline
$ kleur css -h
usage: kleur css [-h] [-l LABEL] -c COLOR1 [-k COLOR2]
[-s NUMBER_OF_SHADES] [-b] [-i] [-d DYNAMIC_RANGE]

options:
  -h, --help            show this help message and exit
  -l, --label LABEL
  -c, --color1 COLOR1
  -k, --color2 COLOR2
  -s, --number-of-shades NUMBER_OF_SHADES
  -b, --include-black-and-white
  -i, --include-input-shades
  -d, --dynamic-range DYNAMIC_RANGE
```

#### Based on one input color

```commandline
$ kleur css -l tables -c 7ab1e5
```
![alt text](https://github.com/githuib/kleur/raw/master/assets/screenshots/css/single.png "kleur css -l tables -c 7ab1e5 -i")

With input markers:

```commandline
$ kleur css -l tables -c 7ab1e5 -i
```
![alt text](https://github.com/githuib/kleur/raw/master/assets/screenshots/css/single_input.png "kleur css -l tables -c 7ab1e5 -i")

#### Based on two input colors

The dynamic range specifies to what degree the hue of the input colors will be used as boundaries:

- Dynamic range 0 (0%):

  *The shades will interpolate (or extrapolate) between the input colors.*

- Dynamic range between 0 and 1 (between 0% and 100%):

  *The shades will interpolate (or extrapolate) between darker / brighter shades of the input colors.*

- Dynamic range 1 (100%):

  *The shades will interpolate between the darkest & brightest shades of the input colors.*

```commandline
$ kleur css -l bad-guy -c badddd -k aa601f -d 66
```
![alt text](https://github.com/githuib/kleur/raw/master/assets/screenshots/css/double.png "kleur css -l bad-guy -c badddd -k aa601f -d 66")

With input markers, varying in dynamic range:

```commandline
$ kleur css -l bad-guy -c badddd -k aa601f -d 0 -i
```
![alt text](https://github.com/githuib/kleur/raw/master/assets/screenshots/css/double_0.png "kleur css -l bad-guy -c badddd -k aa601f -d 0 -i")

```commandline
$ kleur css -l bad-guy -c badddd -k aa601f -d 50 -i
```
![alt text](https://github.com/githuib/kleur/raw/master/assets/screenshots/css/double_50.png "kleur css -l bad-guy -c badddd -k aa601f -d 50 -i")

```commandline
$ kleur css -l bad-guy -c badddd -k aa601f -d 100 -i
```
![alt text](https://github.com/githuib/kleur/raw/master/assets/screenshots/css/double_100.png "kleur css -l bad-guy -c badddd -k aa601f -d 100 -i")
