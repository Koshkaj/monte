# My Main Repository

This repository contains submodules for the following projects:

- microapi
- microgames
- micronotif-balance
- microsockets

## Cloning the Repository

To clone this repository with all submodules, use the following command:

git clone --recurse-submodules https://gitlab.com/montecsgo/monte_manager.git


## Updating Submodules

To update all submodules to their latest commits, run the following commands:

git submodule update --remote --merge
git commit -am "Update submodules"
git push

## To run, do this 

`make full`

## Technologies used

- Python
- Golang
- gRPC
- Docker
