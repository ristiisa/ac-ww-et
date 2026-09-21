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
| Happy Room Academy (H.R.A.) | Kauni Kodu Akadeemia | kirja saatja: "KKA-lt" |
| friend code | sõbrakood | |
| Tag Mode | sildirežiim | |
| Animalese / Bebebese | Loomakeel / Bebebe-keel | kõnestiilid |
| gyroid | güroid | nimed jäävad: dingloid, nebuloid … |
| pansy | kannike | "võõrasema" ei mahu nimevälja |
| exotic (series) | idamaine | sama põhjus |
| design / pattern | kujundus / muster | |
| pic (villager photo) | pilt | "Cyrano pilt" |
| observatory / telescope | observatoorium / teleskoop | tähtkuju = constellation |
| Shampoodle | Šampuudel | Harriet: "kullake", "musike" |
| Crazy Redd's | Hullu Reddi pood | klient = "nõbu" |
| Point System | punktisüsteem | Tom Nooki oma |
| lost and found | leidude hoiukoht | peavärava juures |
| acorn / Cornimer | tõru / Cornimer | mängijale "tõrukene" |
| snowman | lumememm | |
| Flower Fest / Green Thumb | lillepidu / rohenäpp | |
| Fishing Tourney | kalapüügivõistlus | |
| Fireworks Show | ilutulestikushow | |
| Acorn Festival | tõrupidu | |
| Yay Day | kiidupäev | kind words = **kiidusõnad** |
| New Year's Eve Countdown | aastavahetuse loendus | |
| Flea Market | kirbuturg | |
| party popper | paugutid | aastavahetus |
| Gulliver / Porpoise 5000 | nimed jäävad | "osad" = parts |
| Bug-Off | putukavõistlus | võitja saab **karika** |
| La-Di-Day | laulupäev | parim laul = **linna viis** (town tune) |
| Bright Nights | valgusööd | kaunistusvõistlus |
| Bright Star | säratäht | valgusööde võitja |
| mayor (Tortimer) | linnapea | |

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

## Kõnepruugid (erikujud)

- **Resetti**: toores, lühikesed laused, "semu", "nolk", "pole higi",
  "käid mulle närvidele" (*bustin' my chops*).
- **Lyle**: "Pauk!" (*Bang!*), telegrammistiil, "eks?", "muidugi".
- **Redd**: "Hihihii!", "HUUUULL!" (*CRAAAZY*), kutsub mängijat "nõbuks".
- **Saharah**: katkendlik, iga lause lõpus "jah?".
- **Joan** (naerimüüja): "mu väike redis".
- **Tortimer**: "võsuke", naerab "HOORF!".
- **Blathers/Celeste**: "huhh-huu!" (*hootie-toot*).
- **Sable**: vaikne, "Ohhh...", "Emmm...".
- **Booker** (värav): kogeleb, "ee", "vist".
- **Timmy & Tommy**: noorem kordab lause lõppu ("...aitäh!").

## Elanike isiksusekaustad (`message/<kaust>/`)

| Kaust | Isiksus | Eesti kõnetoon |
| --- | --- | --- |
| `bo` | laisk poiss (*lazy*) | rahulik, söögist ja unest, "nämm" |
| `ha` | sportlik poiss (*jock*) | "jou", "semu", trenn, "lihased" |
| `ko` | torssis poiss (*cranky*) | pahur, otsekohene, "kasi", "tola" |
| `ge` | elavaloomuline tüdruk (*peppy*) | "täiesti", "nagu", "JEE!", hüüumärgid |
| `ta` | ülbe tüdruk (*snooty*) | peen, üleolev, "hihii", meik, moeteemad |
| `fu` | tavaline tüdruk (*normal*) | viisakas, soe, pehme, "kullake" |

Sama faili nimi eri kaustades tähendab sama olukorda, aga tekst on igal
isiksusel erinev — tõlgitut ei saa kaustade vahel kopeerida
(`tools/memory.py` leiab need üksikud read, mis tõesti kattuvad).

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
