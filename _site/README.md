# Dev Setup

``` shell
brew install ruby
brew install rbenv

rbenv init
echo 'eval "$(rbenv init -)"' >>~/.bash_profile

rbenv install 2.7.0
rbenv global 2.7.0

gem install --user-install bundler jekyll

echo 'export PATH="$HOME/.gem/ruby/2.7.0/bin:$PATH"' >>~/.bash_profile

gem env

bundle install

```


# Run Locally

``` shell
bundle exec jekyll serve

```

