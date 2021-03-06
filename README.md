# ticket2rtm

A Trac plugin that synchronizes Trac tickets and RTM tasks.

- when a ticket is created, a RTM task also will be added.
- when you close a ticket, the associated RTM task will be completed.

## Install

### build
1. edit Makefile and set `PLUGINS_DIR` to your Trac plugin dir
2. `make`

or:

1. `python setup.py --bdist_egg`
2. copy `dist/TracTicket2RTMPlugin*.egg` into your Trac plugin dir

### RTM API key, token

This plugin requires RTM API key, shared secret, and write-permitted token.
You can obtain your API key and shared secret from [here](http://www.rememberthemilk.com/services/api/requestkey.rtm).

After acquired key and shared secret, you can get your token by using bundled script.
Run as follow:

```
% python get_token.py <API key> <shared secret>
```

## Configuration
1. copy/paste contents of trac_ini_sample.txt to your trac.ini
2. set rtm_api_key, rtm_api_secret, rtm_api_token to ones acquired above

## License
BSD

## Author
[@mootoh](https://github.com/mootoh)
