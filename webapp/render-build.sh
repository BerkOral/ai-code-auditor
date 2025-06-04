#!/usr/bin/env bash


pip install -r requirements.txt

if ! command -v node &> /dev/null; then
  curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
  apt-get install -y nodejs
fi
npm install -g eslint

apt-get update && apt-get install -y php php-cli php-xml unzip curl git

curl -sS https://getcomposer.org/installer | php
mv composer.phar /usr/local/bin/composer

composer global require phpstan/phpstan
