# Multi Monitor

## en
### Features
+ Moving the mouse cursor between monitors using keyboard shortcuts
+ The ability to lock the mouse cursor within one monitor

Default hotkeys:
+ lock/unlock mouse cursor on current monitor: ```<ctrl>+<alt>+L```
+ move mouse cursor to next monitor: ```<ctrl>+<cmd>+<right>```
+ move mouse cursor to previous monitor: ```<ctrl>+<cmd>+<left>```
+ exit: ```<ctrl>+<f12>```

### Running
#### Ubuntu
```bash
sudo apt update
sudo apt install git
git --version
cd ~/Downloads
git clone https://github.com/purgy/multi_monitor.git
sudo apt install pipx
pipx install ~/Downloads/multi_monitor/
multi_monitor
```

Default config file will be created: ```~/multi_monitor_config.yaml```

## ru
### Возможности
+ Перемещение курсора мыши между мониторами с помощью горячих клавиш
+ Возможность блокировки курсора мыши в пределах одного монитора

Предустановленные горячие клавиши:
+ блокировка/разблокировка курсора мыши на текущем мониторе: ```<ctrl>+<alt>+L```
+ перемещение курсора мыши на следующий монитор: ```<ctrl>+<cmd>+<право>```
+ перемещение курсора мыши на предыдущий монитор: ```<ctrl>+<cmd>+<лево>```
+ выход: ```<ctrl>+<f12>```

### Запуск
#### Ubuntu
```bash
sudo apt update
sudo apt install git
git --version
cd ~/Downloads
git clone https://github.com/purgy/multi_monitor.git
sudo apt install pipx
pipx install ~/Downloads/multi_monitor/
multi_monitor
```

Будет создан файл настроек по умолчанию: ```~/multi_monitor_config.yaml```
