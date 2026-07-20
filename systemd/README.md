# Systemd namestitev na Raspberry Pi

Predloga predvideva končno pot `/home/<USERNAME>/pixel_console`. Oznako
`<USERNAME>` zamenjaj šele na Raspberry Piju, potem ko preveriš dejanske poti.

## 1. Preverjanje uporabnika, projekta in Pythona

V korenu projekta zaženi:

```bash
whoami
pwd
.venv/bin/python --version
groups
ls -l /dev/serial0 /dev/spidev0.0
```

`pwd` mora izpisati `/home/<USERNAME>/pixel_console`. Uporabnik mora imeti
dostop do primarnega UART-a in SPI naprave.

## 2. Ročni zagon identičnega ukaza

Pred namestitvijo servisa uporabi isti absolutni ukaz kot poznejši
`ExecStart`:

```bash
/home/<USERNAME>/pixel_console/.venv/bin/python -m src.device
```

Preveri boot zaslon, idle srce, NFC kartico in OLED. Nato pritisni `Ctrl+C` ter
preveri, da se OLED počisti.

## 3. Izpolnitev predloge

```bash
cp systemd/pixel-console.service.template /tmp/pixel-console.service
nano /tmp/pixel-console.service
```

V obeh vrsticah `User` in v vseh poteh zamenjaj `<USERNAME>` z rezultatom
ukaza `whoami`. Nato preveri, da ni ostal noben placeholder:

```bash
grep -n '<USERNAME>' /tmp/pixel-console.service
sudo systemd-analyze verify /tmp/pixel-console.service
```

`grep` ob pravilno izpolnjeni datoteki ne izpiše ničesar.

## 4. Namestitev in zagon

```bash
sudo cp /tmp/pixel-console.service /etc/systemd/system/pixel-console.service
sudo systemctl daemon-reload
sudo systemctl enable pixel-console.service
sudo systemctl start pixel-console.service
sudo systemctl status --no-pager pixel-console.service
```

Spremljanje logov:

```bash
journalctl -u pixel-console.service -f
```

Ponovni zagon ali ustavitev:

```bash
sudo systemctl restart pixel-console.service
sudo systemctl stop pixel-console.service
```

Pri `stop` systemd pošlje `SIGTERM`. Aplikacija ga prestreže in pred izhodom
poskusi blankati OLED.

## 5. Ročni boot acceptance test

```bash
sudo reboot
```

Po ponovnem zagonu preveri:

```bash
systemctl is-enabled pixel-console.service
systemctl is-active pixel-console.service
systemctl status --no-pager pixel-console.service
journalctl -u pixel-console.service -b --no-pager
```

Ta fizični boot test mora biti opravljen na ciljnem Raspberry Piju.
