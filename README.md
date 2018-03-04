# Grzegorz API
<img align="right" width="250" src="res/logo.png">

Grzegorz is simple REST API for managing an instance of MPV.

Why the name Grzegorz? [We have a bad tast in humor!](https://youtu.be/t-fcrn1Edik)

When Grzegorz starts, it launches an instance of MPV and maintains it. It is designed to be used as an infoscreen or HTPC, and supports multiple users to push changes to the MPV instance.

The API id described and can be tested on `http:/localhost:8080/swagger` when the server is running. All API endpoints are available under `/api`


## How to run it

First of we need to install any needed dependencies. If you want to, you may do so in a virtual environment.

To install the needed dependencies, run this with sufficient rights (as root?):

```
pip install -r requirements.txt
```

Gregorz managesa MPV process, meaning you need MPV installed on your system. Look for it in your package manager.

When finished, you may run the server with:

```
python3 main.py
```

The server should now be available at `http://localhost:8080/`.
You may change the address and port in the file named `config.py`


## Making Grzegorz run on boot

When setting up a infoscreen or HTPC using Grzegors, you may configure it to run automatically on startup.

We recommend installing a headless linux, and create a user for Grzegorz to run as. (We named ours `grzegorz`, obviously)
Then make systemd automatically spin up a X session to run Grzegorz in: Copy the files in the folder `dist` into `$HOME/.config/systemd/user` and run the following commands as your user:

```
$ systemd --user enable grzegorz@0.service
$ systemd --user start grzegorz@0.service
```
