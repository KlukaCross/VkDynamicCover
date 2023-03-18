#!/usr/bin/env bash

PYTHON_EXECUTABLE="python3"

function main()
{
  echo "Запуск сервиса"
  if ! ${PYTHON_EXECUTABLE} -m VkDynamicCover "$@"
  then
    echo "Программа завершилась неудачно"
    return 1
  fi
  echo "Выход"
}

main $@
