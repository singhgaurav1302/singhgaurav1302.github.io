#!/usr/bin/env bash

self=${0##*/}
root=`dirname "$(realpath $0)"`/..
cd $root

echo "Executing build script: $self"

dest='_site'

if [ "$1" = 'clean' ] || [ "$1" = '-c' ]; then
  bundle exec jekyll clean
fi

bundle exec jekyll b $dest
bundle exec htmlproofer $dest --disable-external --check-html --allow_hash_href
bundle exec jekyll s
