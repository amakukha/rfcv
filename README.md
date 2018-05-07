# rfcv
`rfcv` is a tiny command-line tool written in Python and Bash to read colored 
[RFCs](http://www.ietf.org/rfc.html) (Requests for Comments) from the 
Linux terminal. It fetches RFCs from the Web and caches them locally.

`rfcv` displays RFC text with colors, to make it more readable and easier to understand.


## Usage

Just type `rfcv` followed by the RFC number. For example:

```sh
rfcv 2549
rfcv 5541
```


## Install

### Basic install

```sh
mkdir -p ~/bin
curl -sL https://raw.github.com/amakukha/rfcv/master/rfc_color.py > ~/bin/rfc_color.py
curl -sL https://raw.github.com/amakukha/rfcv/master/rfcv > ~/bin/rfcv
chmod u+x ~/bin/rfcv
```

This creates the `~/bin` directory if it doesn’t exist, and downloads the files into it.
If it’s not in your `PATH`, you have to add it:

```sh
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
```


### Requirements

- Python 3
- `less`


## Inspired by

- Baptiste Fontaine's [rfc](https://github.com/bfontaine/rfc)
- monsieurh's [rfc_reader](https://github.com/monsieurh/rfc_reader), with which it can share local copies of RFCs
