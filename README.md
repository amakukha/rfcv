# rfcv
`rfcv` is a tiny command-line tool written in Python and Bash to display
colored [RFCs](http://www.ietf.org/rfc.html) (Requests for Comments) in the 
Linux terminal. It fetches RFCs from the Web and caches them locally.

`rfcv` makes use of a simple RFC parser to apply color coding to the plain text.
It makes the text more readable and easier to understand.


## Usage

Type `rfcv` followed by the RFC number. For example:

```sh
rfcv 2549
rfcv 6214
```

Example screenshots:
<p align="center">
  <img src="https://github.com/amakukha/rfcv/raw/master/screenshots/RFC_6665_rfcv_screenshot.png" width="250" alt="RFC6665 viewed in rfcv utility">
  <img src="https://github.com/amakukha/rfcv/raw/master/screenshots/RFC_3428_rfcv_screenshot.png" width="250" title="RFC3428 viewed in rfcv utility">
</p>

## Prerequisites

- Python 3
- Python [Requests](http://docs.python-requests.org/en/master/)
- `less`
- `curl` (for installing only)


## Install

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


## Inspired by

- Baptiste Fontaine's [rfc](https://github.com/bfontaine/rfc)
- monsieurh's [rfc_reader](https://github.com/monsieurh/rfc_reader), with which it can share local copies of RFCs
