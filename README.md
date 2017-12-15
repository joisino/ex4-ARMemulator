# ex4-ARMemulator

![screenshot](https://raw.githubusercontent.com/joisino/ex4-ARMemulator/img/screenshot.gif)

This is an ARM emulator for [KUIS compilar experiment](http://www.fos.kuis.kyoto-u.ac.jp/~umatani/le4/index.html) built with `python` and `curses`.

## Getting Started

```
$ git clone https://github.com/joisino/ex4-ARMemulator.git
$ cd ex4-ARMemulator
$ python3 ./emulator.py path/to/assembly/file.s
```

## Usage

### Basic mode

* `q`: quit the emulation
* left_arrow: undo
* `:`: go to input mode
* other keys: emulate 1 step

### input mode

* `q`: quit the emulation
* `c`: go to basic mode
* `0-9`: input
* `x`: emulate n stemps (n is the input number)
