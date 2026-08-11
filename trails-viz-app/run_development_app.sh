#!/usr/bin/env bash
# This script follows the steps outlined in https://github.com/OutdoorRD/trails-viz/wiki/Development#3-dashboard-frontend-setup
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash

# Source whichever file(s) exist
[ -f ~/.bashrc ] && source ~/.bashrc
[ -f ~/.zshrc ] && source ~/.zshrc

# Setup NVM
nvm install 12

nvm use 12

npm install

npm run serve
