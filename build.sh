#!/bin/bash -e

install() {
  python -m pip install --upgrade pip
  pip install flake8
  pip install wheel
  cd trails-viz-app
  npm install
  cd ..
  cd trails-viz-api
  pip install -r requirements.txt
  cd ..
  exit 0
}

package() {
  cd trails-viz-app
  npm run lint
  npm run build
  cd ..
  cd trails-viz-api
  flake8 . --count --max-line-length=119 --exclude trailsvizapi/__init__.py --show-source --statistics
  python setup.py bdist_wheel
  cd ..
  exit 0
}

setup_config() {
  # setup git
  git config --global user.email "fake@travis-bot"
  git config --global user.name "Travis CI Bot"

  git remote set-url origin https://"$GITHUB_USER_NAME":"$GITHUB_ACCESS_TOKEN"@github.com/OutdoorRD/trails-viz

  # setup docker
  echo "$TRAVIS_DOCKER_PASSWORD" | docker login -u "$TRAVIS_DOCKER_USERNAME" --password-stdin
}

update_version() {
  # get the version bump part from commit message
  echo "$TRAVIS_COMMIT_MESSAGE"
  if [[ "$TRAVIS_COMMIT_MESSAGE" == *"release=major"* ]]; then
    version_bump="major"
  elif [[ "$TRAVIS_COMMIT_MESSAGE" == *"release=minor"* ]]; then
    version_bump="minor"
  elif [[ "$TRAVIS_COMMIT_MESSAGE" == *"release=patch"* ]]; then
    version_bump="patch"
  else
    version_bump="patch"
  fi

  # update the version in package.json as it's the easiest thing to do using npm
  git checkout master
  cd trails-viz-app
  new_version=$(npm version $version_bump)  # this returs the new version number with 'v' as prefix
  new_version=$(echo "$new_version" | awk -Fv '{print $2}')
  cd ..
  cd trails-viz-api
  sed -i "s/__version__.*/__version__ = '$new_version'/" trailsvizapi/__init__.py
  cd ..
  echo "local version bump successful $new_version"

  git add trails-viz-app/package.json
  git add trails-viz-app/package-lock.json
  git add trails-viz-api/trailsvizapi/__init__.py
  git commit -m "auto update version to $new_version, travis build: $TRAVIS_BUILD_NUMBER"
  echo "commited after version update"
  git push origin master
  git tag v"$new_version"
  git push origin --tags
  echo "pushed new version to master"
}

deploy() {
  setup_config
  update_version
  docker build -t trails-viz:"$TRAVIS_COMMIT" .

  docker tag trails-viz:"$TRAVIS_COMMIT" vivekkr12/trails-viz:"$TRAVIS_COMMIT"
  docker tag trails-viz:"$TRAVIS_COMMIT" vivekkr12/trails-viz:"$new_version"
  docker tag trails-viz:"$TRAVIS_COMMIT" vivekkr12/trails-viz:latest

  docker push vivekkr12/trails-viz:"$TRAVIS_COMMIT"
  docker push vivekkr12/trails-viz:"$new_version"
  docker push vivekkr12/trails-viz:latest
}

if [ $# -eq 0 ]
  then
    echo "no command line argument passed, required one of: install | package | deploy"
    exit 1
fi

action=$1
if [ "$action" = "install" ]; then
  install
elif [ "$action" = "package" ]; then
  package
elif [ "$action" = "deploy" ]; then
  deploy
else
  echo "invalid command line argument $action, required one of install | package | deploy"
  exit 1
fi
