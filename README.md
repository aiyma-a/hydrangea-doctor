# 🌸 Hydrangea Doctor

> Now covers 14 garden plants: hydrangea, rose, peony, lilac, tulip, iris, apple, pear, apricot, cherry, plum, grape, raspberry, currant. The app recognises the plant (zero-shot CLIP, ~17/19 on test photos) or the user picks it; each plant has its own trimming calendar in `hydrangea/plants.py`.

Take a photo of a hydrangea → find out if it's healthy, what stage it's in,
and whether (and how far) to trim it, adjusted for your weather and the plant's age.

## How it works

```
photo ──► CLIP (pretrained "eyes") ──► 512 numbers ──┬─► health classifier  ─┐
                                                     └─► stage classifier   ─┤
type + age + month + live weather (Open-Meteo) ──────────────────────────────┼─► trimming rules ─► advice
```

| Part | ML or rules? | File |
|---|---|---|
| Turn a photo into numbers (an *embedding*) | ML, pretrained | `hydrangea/embed.py` |
| Health: healthy / leaf_spot / powdery_mildew / wilting / yellowing | ML | `hydrangea/zeroshot.py`, `hydrangea/train.py` |
| Stage: budding / blooming / fading_blooms / dormant | ML | same |
| Weather: frost coming? hot & dry lately? | free API, no key | `hydrangea/weather.py` |
| Trim now? how far? | rules (gardening knowledge) | `hydrangea/pruning.py` |

**Two ML modes:**
1. **Zero-shot** (works today, no photos needed): compares the photo to sentences
   like *"a hydrangea leaf with brown spots"* (see `config.py`) and picks the closest.
2. **Trained** (after you add photos): a small classifier learns from *your*
   labelled photos on top of CLIP's numbers. This is *transfer learning*, also called a
   *linear probe*. Once `models/<task>.joblib` exists, the app uses it automatically.

`python -m hydrangea.train` measures both on your photos and writes a report, so
you can show exactly how much your own data helped.

## Setup (once)

```bash
python3 -m venv .venv
.venv/bin/pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision
.venv/bin/pip install transformers scikit-learn matplotlib pillow gradio pytest
```
> Running inside the Buzz terminal? Prefix commands with `env -u PYTHONHOME -u PYTHONPATH`.

## Use it

```bash
.venv/bin/python app.py                       # web page at http://127.0.0.1:7860
.venv/bin/python -m hydrangea.predict photo.jpg --species bigleaf --place Bishkek --age 4 --height 120
```

## Phone app (for Mom 📱)

An installable web app (PWA): open the link on the phone → **Add to Home Screen**.
It takes a photo with the camera, uses the phone's GPS for weather, and remembers
the plant's type/age on the phone. The ML runs on the server (`server.py`).

```bash
.venv/bin/uvicorn server:app --port 8080      # local test: http://127.0.0.1:8080
```

| File | What it is |
|---|---|
| `server.py` | API (`POST /api/analyze`) + serves the app |
| `static/` | the phone app: `index.html`, `app.js`, `style.css` |
| `static/manifest.webmanifest`, `static/sw.js` | what makes it installable |
| `Dockerfile` | packages everything for Google Cloud Run |

Install on the phone:
- **iPhone:** open the link in Safari → Share button → *Add to Home Screen*.
- **Android:** open in Chrome → ⋮ menu → *Install app* / *Add to Home screen*.

After retraining, redeploy so the server gets the new `models/*.joblib`.

## Add your photos and train

1. Put each photo in the folder for its label:
   `data/health/<healthy|leaf_spot|powdery_mildew|wilting|yellowing>/`
   `data/stage/<budding|blooming|fading_blooms|dormant>/`
2. **Name files by bush:** `bush1_001.jpg`, `bush2_003.jpg`, … Training keeps
   each bush entirely in either the training or the testing side. Otherwise the
   model "recognises the bush" and the score is fake.
3. Run `.venv/bin/python -m hydrangea.train`
4. Read `reports/health.md` and `reports/stage.md`: accuracy table and *confusion
   matrices* (a grid showing which labels get mixed up).

**Photo tips:** health = close-up of one leaf; stage = whole plant. Daylight, no
flash, mix of sun/shade and times of day. Aim for 30+ per label. Labels you
can't photograph in your garden (e.g. a disease you don't have) can use a few
internet photos.

## Safety rules built in
- If the model is under 50% sure, it says so and won't recommend a big cut.
- Wilting → "water first", never "prune".
- Frost in the next 14 days blocks late-summer/autumn cuts.
- Plants under 3 years get half the usual cut; 6+ years get renewal-pruning advice.

## Tests
```bash
.venv/bin/python -m pytest -q
```
