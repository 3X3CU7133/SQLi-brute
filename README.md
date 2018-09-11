# SQLi Brute ![CI status](https://img.shields.io/badge/build-passing-brightgreen.svg)

SQLi Brute is a Python program, to enumerate and download files from the vulnerable system. It also could brute force the process id-s. 

## Installation

### Requirements
* Linux
* Python 3.3 and up
* SQL Map

`$ pip install colorama`

## Usage

```bash
sqli_brute.py -m p -u http://10.10.10.10/sqlquery/someparam* -s 1 -e 1000 -t 25 -d outDir -t 25 
sqli_brute.py -u http://10.10.10.10/sqlquery/someparam* -m f -w ./linux.txt -x py -b /etc -d ./outDir

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://github.com/3X3CU7133/SQLi-brute/blob/master/LICENSE)
