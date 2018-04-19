# Dependencies
- `php`
- `python3`
- `pygments`
- `zip` and `unzip`

# Running
## Temporarily
`php -t . -S localhost:<port>`

## Permanently
```sh
ln -s -t /var/www/html *
sudo service apache3 start
```

# Directory structure

***WARNING***: THIS VERSION IS VERY INSECURE, YOU SHOULD NOT USE THIS ON NETWORK CONNECTED DEVICES DUE TO THE POSSIBILITY OF ACCESS OF STORAGE DEVICE THROUGH THE WEB INTERFACE
```
/var/www/html
|
|-snaps/
| |
| | - timestamp1
|     | - code.html
|     | - output.html
|
|-zip/
  |-timestamp1.zip
  |-timestamp/
    |- src
```
