"""Web page: upload a hydrangea photo, get health, stage and trimming advice.

Run:  .venv/bin/python app.py     then open http://127.0.0.1:7860
"""
import gradio as gr

from hydrangea import pruning
from hydrangea.config import TASKS
from hydrangea.predict import analyse
from hydrangea.weather import fetch

TRIM_BADGE = {"yes": "✂️ Yes, trim now", "light": "🌿 Light touch only", "no": "✋ Don't trim now"}


def run(image, species_label, place, age, height):
    if image is None:
        return "Upload a photo first.", None, None
    species = next(k for k, v in pruning.SPECIES.items() if v == species_label)
    weather, weather_line = None, ""
    if place and place.strip():
        try:
            weather = fetch(place.strip())
            weather_line = f"\n\n🌦️ {weather.summary()}"
        except Exception as e:  # network down / unknown place: still give advice
            weather_line = f"\n\n⚠️ Couldn't get weather ({e}); advice ignores it."
    r = analyse(image, species, height_cm=height or None, age_years=age or None, weather=weather)
    adv = r["advice"]
    md = [f"## {TRIM_BADGE[adv.trim_now]}", f"**{adv.headline}**"]
    if adv.how_far:
        md.append(f"**How far:** {adv.how_far}")
    md += [f"- {n}" for n in adv.notes]
    md.append(weather_line)
    for task in TASKS:
        t = r[task]
        md.append(f"\n<sub>{task}: **{t.label}** {t.confidence:.0%} via {t.method} model"
                  f"{' (unsure)' if t.unsure else ''}</sub>")
    return "\n\n".join(md), r["health"].probabilities, r["stage"].probabilities


with gr.Blocks(title="Hydrangea Doctor") as demo:
    gr.Markdown("# 🌸 Hydrangea Doctor\nIs my hydrangea healthy, and should I trim it?")
    with gr.Row():
        with gr.Column():
            image = gr.Image(type="pil", label="Photo (leaf close-up or whole plant)")
            species = gr.Dropdown(list(pruning.SPECIES.values()), value=pruning.SPECIES["unknown"], label="Type")
            place = gr.Textbox(label="Town (for weather)", placeholder="e.g. Bishkek")
            with gr.Row():
                age = gr.Number(label="Age (years)", value=None)
                height = gr.Number(label="Height (cm)", value=None)
            btn = gr.Button("Check my hydrangea", variant="primary")
        with gr.Column():
            advice = gr.Markdown()
            health = gr.Label(label="Health", num_top_classes=5)
            stage = gr.Label(label="Stage", num_top_classes=4)
    btn.click(run, [image, species, place, age, height], [advice, health, stage])

if __name__ == "__main__":
    demo.launch()
