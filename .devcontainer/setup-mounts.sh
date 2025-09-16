if [[ "$HOME" == /Users/* ]]; then
  echo "type=bind,source=$HOME/.aws,target=/home/${USER}/.aws"
else
  echo "type=bind,source=$HOME/.aws,target=/home/${USER}/.aws"
fi
