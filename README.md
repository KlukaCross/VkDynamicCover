VkDynamicCover
==============
Программа для динамического обновления обложки в группе или паблике Вконтакте.
***
### Архитектура
![](doc/scheme.png)

[диаграмма классов](doc/VkDynamicCover_scheme.png)

***
### Установка
```
git clone https://github.com/KlukaCross/VkDynamicCover
pip3 install ./VkDynamicCover
```

***
### Настройка
Создать файл `main_config.json` и `cover_config.json` и заполнить их. 

[Настройка файла main_config.json и cover_config.json](doc/CONFIG_SETTINGS.md)

[Примеры](examples)

***
### Запуск
```
python3 -m VkDynamicCover
```

Для вывода доступных параметров ввести ```python3 -m VkDynamicCover --help```

***
### Сборка и запуск Docker контейнера
```
docker build -t vk_dynamic_cover .
docker run -it --name vkdynamiccover vk_dynamic_cover [параметры запуска]
```

Если конфигурационные файлы или файлы, необходимые для создания обложки, находятся не в корне проекта или пути к ним абсолютны в файле конфигурации, то необходимо примонтировать том с помощью конструкции `-v <путь к каталогу или файлу на хост-машине>:<путь, по которому файл или каталог будут смонтированы в контейнере>`
Например:
```
docker run -it --name vkdynamiccover -v ~/my_confs:/conf vk_dynamic_cover -m /conf/main_config.json -c /conf/cover_config.json 
```
