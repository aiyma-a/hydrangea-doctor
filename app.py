"""Laptop demo page (Gradio): upload photos, get health, stage and trimming advice.

Run:  .venv/bin/python app.py     then open http://127.0.0.1:7860
(The phone app is server.py + static/.)
"""
import gradio as gr

from hydrangea import pruning
from hydrangea.config import PLANTS
from hydrangea.embed import open_image
from hydrangea.i18n import LANGS, t
from hydrangea.predict import analyse
from hydrangea.weather import fetch

TRIM_BADGE = {"yes": "✂️", "light": "🌿", "no": "✋"}


def run(files, plant, species_label, place, age, height, lang):
    if not files:
        return "Upload a photo first.", None, None
    species = next(s for s in pruning.SPECIES if t(f"species.{s}") == species_label)
    weather, weather_line = None, ""
    if place and place.strip():
        try:
            weather = fetch(place.strip())
            weather_line = f"\n\n🌦️ {weather.summary(lang)}"
        except Exception as e:  # network down / unknown place: still give advice
            weather_line = f"\n\n⚠️ {e}"
    images = [open_image(f if isinstance(f, str) else f.name) for f in files]
    r = analyse(images, species, height_cm=height or None, age_years=age or None, weather=weather, plant=plant)
    adv = r["advice"].render(lang)
    md = [f"## {TRIM_BADGE[adv['trim_now']]} {adv['headline']}"]
    if adv["how_far"]:
        md.append(adv["how_far"])
    md += [f"- {n}" for n in adv["notes"]]
    md.append(weather_line)
    md.append(f"\n<sub>plant: **{t(f'plant.{r['plant_key']}', lang)}** {r['plant'].confidence:.0%} via {r['plant'].method}</sub>")
    for task in ("health", "stage"):
        res = r[task]
        md.append(f"\n<sub>{task}: **{t(f'label.{res.label}', lang)}** {res.confidence:.0%} via {res.method}</sub>")
    return "\n\n".join(md), r["health"].probabilities, r["stage"].probabilities


with gr.Blocks(title="Hydrangea Doctor") as demo:
    gr.Markdown("# 🌸 Hydrangea Doctor\nIs my hydrangea healthy, and should I trim it?")
    with gr.Row():
        with gr.Column():
            files = gr.File(file_count="multiple", file_types=["image"], label="Photos of one plant")
            plant = gr.Dropdown(["auto", *PLANTS], value="auto", label="Plant")
            species = gr.Dropdown([t(f"species.{s}") for s in pruning.SPECIES], value=t("species.unknown"), label="Type")
            place = gr.Textbox(label="Town (for weather)", placeholder="e.g. Bishkek")
            with gr.Row():
                age = gr.Number(label="Age (years)", value=None)
                height = gr.Number(label="Height (cm)", value=None)
            lang = gr.Radio(list(LANGS), value="en", label="Language")
            btn = gr.Button("Check my hydrangea", variant="primary")
        with gr.Column():
            advice = gr.Markdown()
            health = gr.Label(label="Health", num_top_classes=5)
            stage = gr.Label(label="Stage", num_top_classes=4)
    btn.click(run, [files, plant, species, place, age, height, lang], [advice, health, stage])

if __name__ == "__main__":
    demo.launch()
