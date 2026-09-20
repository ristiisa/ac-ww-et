# Text drawn in graphics

These are images, not text, so they must be redrawn to translate.
Tile sheets are rendered to `extracted/gfx/<path>.png` by `tools/gfxsheet.py`
(grayscale 4bpp, palette ignored). Japanese-only sheets are leftovers the US
game never shows and are not listed.

| File | Visible English text | Notes |
|---|---|---|
| `menu/title/bg_us.bch` | "Welcome to Animal Crossing: Wild World" logo, "©2005 Nintendo" | Title screen logo; usually kept as-is |
| `menu/title/bg.bch` | "©2005 Nintendo" | Copyright line, keep |
| `a_mes/a_mes_ttl_bg_ncg.bin` | "START", "TOUCH ..." prompt | Title screen prompt |
| `menu/nin/arr.bch` | "All Rights, including the copyrights of Game, Scenario, Music and Program, reserved by NINTENDO." | Boot legal screen |
| `menu/nin/arrE.bch` | "NOTICE: ESRB ... Game Experience May Change During Online Play" | Boot ESRB notice |
| `menu/staff/logo*.bch` | Credits copyright lines | End credits |
| `a_mes/a_mes_*obj_ncg.bin`, `ab_all/ab_all_obj_ncg.bin` | "MESSAGE 1P..4P", "NAME", "AM" | DS Download Play / multiplayer message screen |
| `menu/bbs/b_bbs.bch`, `menu/chat2/b_bbs.bch` | "MESSAGE" (split tiles) | Bulletin board / chat |
| `menu/han/bg.bch`, `menu/inventory/b_choice.bch`, `b_itm2.bch`, `b_itm_chest.bch`, `b_itm_sell.bch` | "choose 1-4" style labels (split tiles) | Inventory / selection tabs |
| `menu/map/b_map_obj_1.bch` | "NAME", "VILLAGE" | Town map labels |
| `menu/fish/obj0.bch` | "FISH" | Fish/bug encyclopedia |
| `menu/inventory/obj0.bch` | "itm 00-31" | Debug labels, not shown |

## 3D textures (NSBTX)

Rendered to `extracted/tex/` by `tools/texsheet.py <prefix>` (grayscale, palette index).

| File | Visible English text | Notes |
|---|---|---|
| `str/arc/12/str12{s,w}.nsbtx` `fx_tl_do` | "Able Sisters" | Tailor shop sign |
| `str/arc/15/str15{s,w}.nsbtx` `fx_nwU_sd2`, `str15{s,w}_lt` | "Nookway" | Shop sign (upgrade 2) |
| `str/arc/16/str16{s,w}.nsbtx` `fx_nkU_sd`, `str16{s,w}_lt` | "Nookington's" | Shop sign (upgrade 3) |
| `str/arc/30/str30w_lt.nsbtx` `lt_cbs_d` | "NEW YEAR!" | New Year countdown display |
| `roomObj/obj_check_in.nsbtx` `check` | "MUSEUM" | Museum entrance sign |

Checked, no text: `bg/` (terrain), `fg/` (plants), house textures in `str/`.
Not reviewed one by one: `ftr/` furniture textures (1792 files); a few pieces
of furniture may carry small printed words.
