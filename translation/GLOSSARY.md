# Sõnastik ja stiilijuhend

Terminid, mis on juba mängu sisse tõlgitud. Dialoogi tõlkides kasuta neid samu
sõnu, muidu ei klapi jutt menüüde ja esemenimedega.

## Põhiterminid

| Inglise | Eesti | Märkus |
|---|---|---|
| Bells | kellad | "100 kella", "10 000 kella" — tuhandeliste vahel tühik |
| turnips | naerid | "10 naerist" |
| town | linn | vt lauseehitus allpool |
| town hall | raekoda | |
| Museum | muuseum | |
| shop / Nook's Cranny | pood / Nooki nurk | poe nimed jäävad: Nook 'n' Go, Nookway, Nookington's |
| Able Sisters (tailor) | rätsep | sildi pilt on veel ingliskeelne |
| Main Gate | peavärav | |
| Happy Room Academy (H.R.A.) | KKA | kirja saatja: "KKA-lt" |
| friend code | sõbrakood | |
| Tag Mode | sildirežiim | |
| Animalese / Bebebese | Loomakeel / Bebebe-keel | kõnestiilid |
| gyroid | güroid | nimed jäävad: dingloid, nebuloid … |
| pansy | kannike | "võõrasema" ei mahu nimevälja |
| exotic (series) | idamaine | sama põhjus |
| design / pattern | kujundus / muster | |
| pic (villager photo) | pilt | "Cyrano pilt" |

## Kirjasaatjad

Kasutame kaanet: **"Tom Nookilt"**, "Muuseumist", "Raekojalt", "Lyle'ilt",
"Reddilt", "Lumememmelt", "Tähelt", "Linnapealt", "Emalt", "Isalt", "KKA-lt".

## Lauseehitus

- **Linna ja mängija nime ei saa käänata**, sest need tulevad muutujast
  (`{04 03 00}` linn, `{04 00 00}` mängija). Kasuta ümbersõnastust:
  "linn nimega {04 03 00}", "linnas nimega {04 03 00}", "Kas sa oled kindel, {04 00 00}?".
- **Artikleid pole:** "a/an/the/some" ridade tõlge on `{-}`, mis teeb rea tühjaks.
- **Kuupäev:** kuud on nimetavas ("juuni"), päevad kujul "5.".
- **Kellaaeg:** 12 tunni süsteem markeritega "e.l." ja "p.l.".
- **Mõõdud** on meetermõõdustikus (tollid ja jalad teisendatud).

## Kõnepruuk

- **Kapp'n** räägib meremehe keeles: "Jarr!", "Jarr harr harr HARR!", "Jo-ho!",
  ja kutsub mängijat kalanimedega ("sa väike makrell", "sa tursk").
- **Elanike kõnepruugid** (`st_npc_habit`) mahuvad 10 märgi sisse, nagu originaalis,
  sest mängija saab neid muuta ja salvestusfail piirab pikkust.

## Piirid, mida tööriistad kontrollivad

| Koht | Piir |
|---|---|
| dialoogikast | 160 px rida, 3-realised leheküljed |
| entsüklopeedia kast | 100 px rida |
| esemenimi | 17 baiti |
| mööblinimi | 16 baiti |
| sarja nimi | 18 baiti |
| mustri nimi | 15 baiti |

Kontrolli käsuga `.venv/bin/python tools/check.py`; ehita `tools/build.py`.
`tools/memory.py` täidab korduvad read juba tõlgitutest ja
`tools/memory.py --report` näitab edenemist kaustade kaupa.
