# `fcc` - A CLI for Frappe Cloud

This is very early and highly WIP. Anything can change :)

If you want to try this, then

1. Clone this repo and cd to it
2. Execute `pip install -e .`
3. use `fcc`

## Usage

### Login
```sh
$ fcc login
Frappe Cloud Username: 
Frappe Cloud Password:
```

Enter your login credentials here and `fcc` will login to your account and generate an API key. This API key will be stored in the `~/.config/fcc/.fcc` file.

#### Verifying

```sh
$ fcc getme
{'message': {'user': 'athul@erpnext.com', 'team': 'athul@erpnext.com'}}
```
`getme` returns your username and current-team associated with your account 


### Sites

```sh
$ fcc sites
Usage: fcc sites [OPTIONS] COMMAND [ARGS]...

  Access Sites and Execute actions on Sites

Options:
  --help  Show this message and exit.

Commands:
  list  List the sites
```

#### List Sites

```sh
$ fcc sites list

                     All Sites of athul@erpnext.com                      
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Site Name               ┃ Status ┃ Version ┃ RegionCreated ┃          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ athul-test.frappe.cloud │ Active │ Nightly │ Mumbai        │ 7 months │
└─────────────────────────┴────────┴─────────┴───────────────┴──────────┘
```
You will be given a menu to select your team for listing your sites


### Benches

```sh
$ fcc bench
Usage: fcc bench [OPTIONS] COMMAND [ARGS]...

  Access Benches and execute actions on Benches

Options:
  --help  Show this message and exit.

Commands:
  deploy  Deploy a new version of the Bench
  list    List all Private benches under a team
  ssh     Login to Bench
  update  Update a Bench
```

### List Benches

```sh
$ fcc bench list
                               All Benches of athul@erpnext.com                                
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Bench Title       ┃ Status ┃ Number of Sites ┃ Total Apps ┃ Version ┃ Bench Name ┃ Created  ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Self Hosted Bench │ Active │ 1               │ 2          │ Nightly │ bench-4219 │ 7 months │
└───────────────────┴────────┴─────────────────┴────────────┴─────────┴────────────┴──────────┘
```

You'll be prompted to select the team.

### Deploy Bench

```sh
$ fc bench deploy
fcc bench deploy --help
Usage: fcc bench deploy [OPTIONS]

  Deploy a new version of the Bench

Options:
  --team TEXT   Team owning the Private Bench
  --bench TEXT  The Name of the bench. eg: bench-4219
  --help        Show this message and exit.
```

### SSH to Bench

```sh
$  fcc bench ssh --help
Usage: fcc bench ssh [OPTIONS]

  Login to Bench

Options:
  --team TEXT  Team owning the Private Bench
  --site TEXT  The Frappe Cloud Site
  --help       Show this message and exit.
```


---

I want to dedicate this project to Abraham Raji, who was my dearest friend, an awesome engineer and a great human. He passed away due to a [Kayaking accident on September 13th 2023](https://www.debian.org/News/2023/20230914).