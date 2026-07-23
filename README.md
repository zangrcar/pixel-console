# Raspberry Pi NFC Pixel Console

Pixel Console prebere program s kartice NTAG216, preveri PXL1 container in
bytecode ter ga izvede na 128×64 OLED zaslonu. Programi so napisani v majhnem
jeziku PXLA. Projekt deluje brez interneta.

```text
.pxla → assembler → PXL1 → preview/NFC → validator → VM → SSD1309 OLED
```

## Struktura

- `prog/` – primeri PXLA in opcijske datoteke `<ime>_sprites.py`;
- `src/assembler.py` – UTF-8 PXLA assembler;
- `src/container.py` – PXL1 v1, sprite bank in CRC-16;
- `src/validator.py` – preverjanje bytecodea pred izvedbo;
- `src/vm.py` – 128×64 Pixel VM;
- `src/display.py` – Waveshare OLED_2in42 SSD1309 SPI backend;
- `src/nfc.py` – PN532 UART in NTAG216 branje/zapis;
- `src/device.py` – produkcijska Raspberry Pi aplikacija;
- `tools/preview.py` – PNG preview;
- `tools/play.py` – pygame player;
- `tools/write_card.py` – NFC write, read-back in verify;
- `systemd/` – service predloga in navodila.

Podrobna specifikacija jezika je v [PXLA.md](PXLA.md).

## Namestitev

Na Raspberry Pi OS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

Na Windows uporabi `.venv\Scripts\python.exe` namesto `.venv/bin/python`.
Projekt uporablja vendorizirani uradni Waveshare driver; SSD1306 knjižnica ni
uporabljena.

## Build, run in preview

Sestavi program v `output/slovenian_text.bin`, izpiši inspector podatke in ga
izvedi v VM-ju:

```bash
.venv/bin/python run.py slovenian_text
```

Če želiš program samo prevesti in validirati, brez izvajanja:

```bash
.venv/bin/python run.py slovenian_text --build-only
```

Ukaz ustvari `output/slovenian_text.bin`, preveri PXL1 in bytecode, vendar ne
zažene VM-ja in ne ustvari frameov.

Pot in lasten output:

```bash
.venv/bin/python run.py prog/slovenian_text.pxla --output output/birthday.bin
```

PNG preview:

```bash
.venv/bin/python tools/preview.py slovenian_text
```

PNG-ji in trajanje frameov se shranijo v `output/slovenian_text_preview/`.
Preview ima zaradi neskončnih programov privzeti limit 120 frameov. Za daljši
program ga zvišaj eksplicitno:

```bash
.venv/bin/python tools/preview.py animated_sprite --max-frames 5000 --max-steps 200000
```

Pygame preview, ki ga zapreš z `ESC`:

```bash
.venv/bin/python tools/play.py slovenian_text --max-frames 5000 --max-steps 200000
```

Inspector `.bin` datoteke:

```bash
.venv/bin/python -m src.inspect output/slovenian_text.bin
```

Inspector izpiše uporabljeno velikost, NTAG216 status, preostanek, verzijo,
CRC, code size in card sprite ID-je.

## NFC write in verify

PN532 je podprt samo prek UART. Writer sprejme `.pxla`, ime programa ali
veljaven PXL1 `.bin`:

```bash
.venv/bin/python tools/write_card.py output/slovenian_text.bin
```

Po zapisu ponovno prebere vseh 888 bajtov, primerja uporabljene bajte in
preveri PXL1 CRC. Nato čaka, da kartico odstraniš.

Writer prepiše vseh 888 uporabniških bajtov in izbriše prejšnjo NDEF vsebino.
Kartica mora biti nezaklenjena NTAG216.

## Raspberry Pi hardware

PINS:
PN532: 2, 6, 8, 10, 38
OLED:  1, 9, 13, 19, 22, 23, 24

### OLED

Podprt je samo Waveshare 2.42inch OLED Module, 128×64, SSD1309, 4-wire SPI:

| OLED | Raspberry Pi |
| --- | --- |
| VCC | 3.3 V |
| GND | GND |
| DIN | GPIO10 / MOSI / pin 19 |
| CLK | GPIO11 / SCLK / pin 23 |
| CS | GPIO8 / CE0 / pin 24 |
| DC | GPIO25 / pin 22 |
| RST | GPIO27 / pin 13 |

Driver uporablja `/dev/spidev0.0`, SPI mode 3 in 10 MHz.

### NFC

PN532 mora biti nastavljen v UART način. Uporabljen je primarni Raspberry Pi
UART pri 115200 baud:

| Raspberry Pi | PN532 |
| --- | --- |
| GPIO14 / TX / pin 8 | RX |
| GPIO15 / RX / pin 10 | TX |
| GND | GND |

Napajanje PN532 poveži skladno s specifikacijo modula. V `raspi-config` omogoči
serial hardware, izključi serial login shell in omogoči SPI.

## Produkcijska aplikacija

```bash
.venv/bin/python -m src.device
```

```text
boot → idle (heart + TAP CARD) → reading → playing/error
     → wait for removal → idle
```

Privzete produkcijske omejitve:

- boot zaslon: 2 sekundi;
- error zaslon: 5 sekund;
- dodatni hold zadnjega framea: 1 sekunda;
- 60 tickov na sekundo;
- brez produkcijskega frame limita;
- največ 500000 VM korakov.

Konzola zato ne prekine veljavne daljše animacije samo zaradi števila frameov.
`MAX_STEPS` ostane zaščita pred poškodovanim ali neskončnim programom.

`SIGTERM`, `Ctrl+C` in normalen shutdown poskusijo blankati OLED.

Systemd namestitev je v [systemd/README.md](systemd/README.md), predloga pa v
[systemd/pixel-console.service.template](systemd/pixel-console.service.template).

## PXLA osnove

Source datoteke so UTF-8. Ukazi niso občutljivi na velikost črk. Podprti so
labeli in komentarji `#`, `;` ter `//`; markerji znotraj quoted stringa niso
komentar. VM ima spremenljivke `V0–V7`. Zaslon sega od `(0,0)` do `(127,63)`;
risanje izven zaslona se odreže.

### Opcode tabela

| Vrednost | Ukaz | Argumenti |
| --- | --- | --- |
| `0x00` | `END` | – |
| `0x01` | `NOP` | – |
| `0x02` | `CLEAR` | `color` |
| `0x03` | `MODE` | `mode` |
| `0x04` | `SHOW` | – |
| `0x05` | `WAIT` | `ticks` |
| `0x06` | `FRAME` | `ticks` |
| `0x07` | `JMP` | `label` |
| `0x08` | `SETV` | `variable value` |
| `0x09` | `ADDV` | `variable signed_delta` |
| `0x0A` | `RANDV` | `variable maximum` |
| `0x0B` | `JNZ` | `variable label` |
| `0x0C` | `JLT` | `variable value label` |
| `0x0D` | `DJNZ` | `variable label` |
| `0x0E` | `ORIGIN` | `x y` |
| `0x0F` | `ORIGINV` | `Vx,Vy` |
| `0x10` | `PSET` | `x y` |
| `0x11` | `LINE` | `x0 y0 x1 y1` |
| `0x12` | `RECT` | `x y width height` |
| `0x13` | `FRECT` | `x y width height` |
| `0x14` | `INVRECT` | `x y width height` |
| `0x15` | `TEXT` | `x y "text"` |
| `0x16` | `FONT` | `font_id scale` |
| `0x17` | `SPR` | `x y sprite frame` |
| `0x18` | `SPRV` | `Vx,Vy sprite frame` |
| `0x19` | `MOVE` | `signed_dx signed_dy` |

Relativni skoki so merjeni od naslova za celotnim jump ukazom. Assembler zaradi
združljivosti sprejme alias `moveorig`, nova koda pa naj uporablja `MOVE`.
`SHOW` odda frame z enim tickom, `FRAME` z navedenim trajanjem, `WAIT` pa
podaljša trenutno prikazani frame.

## Fonti in tekst

```asm
font font_id scale
text x y "Besedilo"
```

| ID | Ime | Osnovni glyph |
| --- | --- | --- |
| 0 | Classic | 5×8 |
| 1 | Tall | 5×10 |
| 2 | Wide | 7×8 |
| 3 | Italic | 7×8 |
| 4 | Bold | 6×8 |

Scale je `1–4` in uporablja integer pixel scaling brez antialiasinga. Vsi fonti
vsebujejo `A–Z`, `a–z`, `0–9`, zahtevana ločila in slovenske znake.

| Znak | Bajt |
| --- | --- |
| `Č` | `0x80` |
| `Š` | `0x81` |
| `Ž` | `0x82` |
| `č` | `0x83` |
| `š` | `0x84` |
| `ž` | `0x85` |

En `TEXT` lahko shrani največ 64 bajtov. Nepodprt Unicode povzroči assembler
napako; neznan bajt v neposrednem rendererju se prikaže kot `?`.

## Sprite-i

- vgrajeni sprite-i imajo stabilne ID-je `0–127`;
- card sprite-i imajo zaporedne ID-je `128–255`;
- na kartici je dovoljenih največ 128 sprite-ov;
- PXL1 v1 podpira samo raw encoding.

`prog/demo_sprites.py` se samodejno uporabi ob `prog/demo.pxla`, če vsebuje
seznam `SPRITES`. Prvi card sprite dobi ID 128.

## PXL1 v1

Header je dolg 11 bajtov:

| Offset | Vsebina |
| --- | --- |
| `0–3` | magic `PXL1` |
| `4` | verzija `1` |
| `5–6` | total length, little-endian |
| `7–8` | sprite-bank length, little-endian |
| `9–10` | CRC-16-CCITT, little-endian |

CRC uporablja polinom `0x1021` in začetno vrednost `0xFFFF`; CRC polje je med
izračunom nič. Privzeti build limit je 888 bajtov za trenutno kartico NTAG216.
To je avtorsko preverjanje in ga lahko za drugo kartico spremeniš:

```bash
.venv/bin/python run.py program --max-size 2048
```

`unwrap_program()` in Raspberry Pi validator ne uporabljata NTAG216 capacity
limita. Upoštevata deklarirani PXL1 `total length`, zato veljaven večji
container ni zavrnjen samo zato, ker presega 888 bajtov. Formatno polje podpira
do 65535 uporabljenih bajtov. Trenutni PN532 reader/writer je še vedno
namenjen NTAG216, zato bere in zapisuje 888 uporabniških bajtov ter pravilno
zavrne večji zapis. Pri prihodnji kartici je treba prilagoditi samo hardware
read/write obseg, ne PXL1 validatorja.

Ničelni padding za dodatno fizično kapaciteto se pri branju ignorira.

## Error kode

| Koda | OLED naslov | Koda | OLED naslov |
| --- | --- | --- | --- |
| `ERR 01` | `BAD CARD` | `ERR 12` | `TRUNC BYTECODE` |
| `ERR 02` | `BAD CHECKSUM` | `ERR 13` | `BAD VARIABLE` |
| `ERR 03` | `BAD VERSION` | `ERR 14` | `BAD JUMP` |
| `ERR 04` | `BAD PROGRAM` | `ERR 15` | `BAD TEXT` |
| `ERR 05` | `EXEC LIMIT` | `ERR 16` | `BAD DRAW MODE` |
| `ERR 06` | `BAD ASSET` | `ERR 17` | `BAD FONT` |
| `ERR 07` | `HARDWARE ERROR` | `ERR 18` | `BAD SPRITE` |
| `ERR 08` | `BAD LENGTH` | `ERR 19` | `NFC ERROR` |
| `ERR 09` | `BAD SPR BANK` | `ERR 20` | `DISPLAY ERROR` |
| `ERR 10` | `EMPTY PROGRAM` | `ERR 21` | `VM ERROR` |
| `ERR 11` | `BAD OPCODE` | `ERR 22` | `SOURCE ERROR` |
| `ERR 99` | `INTERNAL ERROR` | | |

Traceback se izpiše v terminal oziroma systemd journal, ne na OLED.

## Primeri in velikosti

Izmerjene velikosti vključujejo PXL1 header, sprite bank in code:

| Primer | Namen | Velikost |
| --- | --- | ---: |
| `animated_sprite.pxla` | animirani vgrajeni sprite | 51 B |
| `cat.pxla` | pet card sprite-ov | 348 B |
| `comet.pxla` | neskončna animacija z `FRAME` | 93 B |
| `fonts.pxla` | vseh pet fontov, scale 1–4 | 96 B |
| `frame_loop.pxla` | končna zanka z `FRAME` | 31 B |
| `heart.pxla` | dvakratni card sprite | 55 B |
| `hello.pxla` | osnovne oblike | 29 B |
| `line.pxla` | črte | 38 B |
| `move.pxla` | premikanje origin z `MOVE` | 47 B |
| `slovenian_text.pxla` | zahtevane slovenske vrstice | 93 B |
| `text.pxla` | osnovni tekst | 63 B |
| `twinkle.pxla` | spremenljivke in naključne pike | 35 B |

## Testi

```bash
.venv/bin/python -m pytest -q
```

Testi ne potrebujejo fizične opreme. Pokrivajo sprite banko, fonte, assembler,
PXL1, validator, VM, preview, display/NFC fake backende, systemd predlogo in
UTF-8 end-to-end pot.

Pred strojno potrditvijo MVP-ja ostajajo ročni testi:

- SSD1309 prikaz in blank prek Waveshare driverja;
- PN532 UART zaznava, NTAG216 write/read/CRC in odstranitev;
- celoten boot → idle → play/error → idle tok;
- systemd zagon po rebootu in OLED cleanup ob `systemctl stop`.
