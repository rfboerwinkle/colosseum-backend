# Colosseum

Colosseum is a simple, self-hosted competitive programming platform for having quick programming matches between peers.

This is the backend repository. For the frontend repository, see [this other repository](https://github.com/Malizma333/colosseum-frontend).

## Architecture

There are 3 main parts: the main application (`main.py`), the VMs which run the submitted code, and the application which manages the VMs (`spawning_pool.py`). `main.py` and `spawning_pool.py` communicate via named pipes. `spawning_pool.py` manages the VMs via the `libvirt` library.

## Setup

1. Run `install.sh`

2. Go through `VM_setup.md`

3. Clone the frontend

4. Add the following line to the `env.cfg` file:

  `www=PATH_TO_FRONTEND`

5. Make the problem database:

  `./make_database.py problems.db example_problems`

## Running

Run these two commands in seperate terminals:

1. `# python3 spawning_pool.py` (as a root user)

2. `$ python3 main.py` (as a normal user)

## Included Files

- `install.sh` / `clean.sh`: Makes / removes generated files (except for `creep_disk.img`).

- `VM_setup.md`: A description of how to setup `creep_disk.img`. It explains the following files:
  - `boot_installer.py`
  - `boot_queen.py`
  - `boot_broodling.py`
  - `vm_setup/`

- `main.py`: The main application. It runs an HTTP server, manages parties, gets problems, etc. It uses the following files:
  - `api.py`
  - `database.py`
  - `party.py`

- `spawning_pool.py`: Manages the VMs.

- `lib_colosseum.py`: Contains a lot of generic functions. Used by several scripts.

- `xml_gen.py`: Makes XML descriptions of domains. Used by several scripts.

- `state_diagram.png`: Description of states / transitions of each individual client. This describes all possible HTTP requests which can be made to the server.

## Generated Files

- `creep_disk.img`: The virtual hard drive that all the VMs use.

- `io_template.img` / `tmp/`: Small virtual disk that is copied to insert into the VMs / the directory where the copied versions are stored.

- `test_pipe` / `result_pipe`: POSIX pipes that `main.py` and `spawning_pool.py` communicate through.

- `env.cfg`: Contains various settings.

## Contributors

[Tobias Bessler](https://github.com/Malizma333)
[Breanna Breedlove](https://github.com/BreannaBre)
[Robert Boerwinkle](https://github.com/rfboerwinkle)

