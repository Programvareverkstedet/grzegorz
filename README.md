# Grzegorz API
<img align="right" width="250" src="grzegorz/res/logo.png">

Grzegorz is simple REST API for managing an instance of MPV.
Why the name Grzegorz? [We have a bad taste in humor!](https://youtu.be/t-fcrn1Edik)

When Grzegorz starts, it launches an instance of MPV and maintains it. It is designed to be used as an info screen or HTPC, and supports multiple users to push changes to the MPV instance.

The API is described and can be tested at `http:/localhost:8080/swagger` while the server is running. All API endpoints are available under `/api`


## How install and run it

Gregorz manages a MPV process, meaning you need to have MPV installed on your system. Look for it in your package manager.

    sudo pip install git+https://github.com/Programvareverkstedet/grzegorz#master
    sanic grzegorz.app --host :: --port 80 --fast

Details are over [here](https://sanic.dev/en/guide/deployment/running.html#running-via-command).


## Development server

Setup local virtual environment and run with auto-reload:

    poetry install
    poetry run sanic grzegorz.app --host localhost --port 8000 --debug

The server should now be available at `http://localhost:8000/`.

## A word of caution

Grzegors will make a unix socket in the current working directory. Make sure it is somewhere writeable!


## Making Grzegorz run on boot

When setting up a info screen or HTPC using Grzegors, you may configure it to run automatically on startup.

We recommend installing a headless linux, and create a user for Grzegorz to run as. (We named ours `grzegorz`, obviously)
Clone this repo into the home directory. Then make systemd automatically spin up a X session to run Grzegorz in: Copy the files in the folder `dist` into the folder `$HOME/.config/systemd/user` and run the following commands as your user:

    $ systemctl --user enable grzegorz@0.service
    $ systemctl --user start grzegorz@0.service
