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
``
python3 -m VkDynamicCover
``

Для вывода доступных параметров введите ``python3 -m VkDynamicCover --help``