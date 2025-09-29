#!/bin/bash -x
sudo pacman -Syu docker
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
