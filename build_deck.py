"""Build deck/SmartIrrigate_Deck.pptx (7 slides) from results/impact.json and results/*.png.

No number is typed here: every figure comes from impact.json via render_docs.fmt_values.
All results shown are SIMULATED with AquaCrop-OSPy.
"""

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

import config
from render_docs import fmt_values, load_impact, sensitivity_rows

FOREST = RGBColor(0x2C, 0x5F, 0x2D)
MOSS = RGBColor(0x97, 0xBC, 0x62)
INK = RGBColor(0x1F, 0x2A, 0x1F)
MUTED = RGBColor(0x55, 0x63, 0x55)
TINT = RGBColor(0xEE, 0xF4, 0xE8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
PALE = RGBColor(0xD9, 0xE8, 0xCC)
HEAD, BODY = "Cambria", "Calibri"
W, H = Inches(13.333), Inches(7.5)
MARGIN = Inches(0.6)
SIM_TAG = "SIMULATED with AquaCrop-OSPy (FAO AquaCrop model). Not field-measured."


def text(slide, x, y, w, h, runs, size=16, color=INK, font=BODY, bold=False,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, bullets=False, space_after=6):
    """Add a text box. `runs` is a string or a list of paragraphs (strings)."""
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    paras = [runs] if isinstance(runs, str) else runs
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        r = p.add_run()
        r.text = ("•  " + para) if bullets else para
        r.font.size, r.font.color.rgb, r.font.name, r.font.bold = Pt(size), color, font, bold
    return box


def card(slide, x, y, w, h, fill=TINT):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shp.adjustments[0] = 0.06
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def title(slide, t, dark=False):
    text(slide, MARGIN, Inches(0.4), W - 2 * MARGIN, Inches(0.9), t, size=34,
         color=WHITE if dark else FOREST, font=HEAD, bold=True)


def footer(slide, dark=False):
    text(slide, MARGIN, Inches(6.95), W - 2 * MARGIN, Inches(0.4), SIM_TAG, size=11,
         color=PALE if dark else MUTED)


def background(slide, color):
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = color


def stat(slide, x, y, w, value, label, value_size=36):
    card(slide, x, y, w, Inches(1.45))
    text(slide, x + Inches(0.2), y + Inches(0.12), w - Inches(0.4), Inches(0.75), value,
         size=value_size, color=FOREST, font=HEAD, bold=True)
    text(slide, x + Inches(0.2), y + Inches(0.85), w - Inches(0.4), Inches(0.55), label,
         size=13, color=MUTED)


def flow(slide, y, labels, box_w, gap, x0=MARGIN, fill=TINT, size=14):
    for i, label in enumerate(labels):
        x = x0 + i * (box_w + gap)
        shp = card(slide, x, y, box_w, Inches(1.0), fill)
        tf = shp.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = label
        r.font.size, r.font.color.rgb, r.font.name = Pt(size), INK, BODY
        if i < len(labels) - 1:
            arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + box_w + Inches(0.05),
                                           y + Inches(0.38), gap - Inches(0.1), Inches(0.24))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = MOSS
            arrow.line.fill.background()


def build(v: dict, impact: dict) -> Presentation:
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    blank = prs.slide_layouts[6]
    res = config.RESULTS_DIR

    # 1. Title
    s = prs.slides.add_slide(blank)
    background(s, FOREST)
    text(s, MARGIN, Inches(1.6), Inches(11.5), Inches(1.2), "SmartIrrigate", size=54,
         color=WHITE, font=HEAD, bold=True)
    text(s, MARGIN, Inches(2.75), Inches(11.5), Inches(1.0),
         "Soil-moisture-driven irrigation scheduling for water savings: "
         "a simulation study on AquaCrop-OSPy", size=22, color=PALE)
    text(s, MARGIN, Inches(4.1), Inches(11.5), Inches(0.5), f"Team {config.TEAM_NAME}", size=22,
         color=WHITE, bold=True)
    text(s, MARGIN, Inches(4.6), Inches(11.5), Inches(0.5), "  ·  ".join(config.TEAM_MEMBERS),
         size=18, color=WHITE)
    text(s, MARGIN, Inches(5.25), Inches(11.5), Inches(0.5),
         "EcoLogic 1.0 Sustainability Hackathon  |  Theme: Smart Agriculture", size=16, color=PALE)
    text(s, MARGIN, Inches(5.7), Inches(11.5), Inches(0.5), f"Code: {config.REPO_URL}", size=16, color=WHITE)
    footer(s, dark=True)
    s.notes_slide.notes_text_frame.text = "Introduce the team. Say up front: every result in this deck is simulated."

    # 2. Problem
    s = prs.slides.add_slide(blank)
    title(s, "Calendar irrigation wastes water and pump energy")
    text(s, MARGIN, Inches(1.5), Inches(6.4), Inches(4.8), [
        "Many farms irrigate on a fixed calendar: a set depth every few days, whatever the soil or rain.",
        "When rain has already wetted the root zone, the extra water drains past the roots or evaporates.",
        "Every wasted litre was also pumped, so it wastes electricity and adds CO₂.",
        "Goal: irrigate only when the crop needs it, without losing yield.",
    ], size=17, bullets=True, space_after=14)
    stat(s, Inches(7.6), Inches(1.6), Inches(5.1), f"{v['base_mm']} mm",
         f"applied per season by a {v['base_depth']} mm / {v['base_interval']}-day schedule (simulated)")
    stat(s, Inches(7.6), Inches(3.3), Inches(5.1), v["rainfed_pct"],
         "of that schedule's yield reached with no irrigation at all (simulated, sample climate)")
    text(s, Inches(7.6), Inches(4.95), Inches(5.1), Inches(1.4),
         "In our simulation, most of the calendar schedule's water does not turn into extra grain.",
         size=14, color=MUTED)
    footer(s)
    s.notes_slide.notes_text_frame.text = "Numbers are from our simulation, not national statistics."

    # 3. Solution and architecture
    s = prs.slides.add_slide(blank)
    title(s, "One rule: water only when the root zone runs dry")
    text(s, MARGIN, Inches(1.35), Inches(12), Inches(0.5),
         "Simulation pipeline (built, runs in this repository)", size=18, color=FOREST, bold=True)
    flow(s, Inches(1.9), ["Weather, soil, crop inputs", "AquaCrop-OSPy, 8 strategies",
                          "Pre-registered selection rule", "impact.json: L, kWh, ₹, CO₂",
                          "Charts, README, deck"], Inches(2.05), Inches(0.43))
    text(s, MARGIN, Inches(3.4), Inches(12), Inches(0.5),
         "Field deployment concept (not built or tested in this submission)", size=18,
         color=FOREST, bold=True)
    flow(s, Inches(3.95), ["Capacitive soil-moisture probes", "Microcontroller runs the same rule",
                           "Relay on pump or valve", "Water applied only when needed",
                           "Dashboard and logs"], Inches(2.05), Inches(0.43), fill=PALE)
    text(s, MARGIN, Inches(5.3), Inches(12), Inches(1.4), [
        f"Rule: when root-zone water falls below the threshold (selected: {v['scheduler_id']}, "
        "i.e. 40% of available water), refill it; otherwise do nothing.",
        "The controller logic is a few lines and runs offline; per-farm work is sensor calibration.",
    ], size=15, bullets=True, space_after=8)
    footer(s)

    # 4. Method
    s = prs.slides.add_slide(blank)
    title(s, "Method: same seasons and weather, new rule")
    for i, (head, body) in enumerate([
        (f"Baseline: {v['baseline_id']}", [f"{v['base_depth']} mm every {v['base_interval']} days from planting",
                                            "Predefined schedule (AquaCrop method 3)",
                                            "Stylised farmer practice"]),
        ("Scheduler: smt_40 … smt_90", ["Irrigate when root-zone water < 40 … 90% of available",
                                             "Soil-moisture targets (AquaCrop method 1)",
                                             "6 thresholds tested"]),
    ]):
        x = MARGIN + i * Inches(6.2)
        card(s, x, Inches(1.5), Inches(5.9), Inches(2.1))
        text(s, x + Inches(0.25), Inches(1.65), Inches(5.4), Inches(0.5), head, size=20,
             color=FOREST, font=HEAD, bold=True)
        text(s, x + Inches(0.25), Inches(2.2), Inches(5.4), Inches(1.6), body, size=15,
             bullets=True, space_after=4)
    text(s, MARGIN, Inches(4.1), Inches(12), Inches(0.5), "Selection rule, fixed before any results were seen",
         size=18, color=FOREST, bold=True)
    text(s, MARGIN, Inches(4.55), Inches(12), Inches(1.0), v["rule_text"], size=15)
    text(s, MARGIN, Inches(5.6), Inches(12), Inches(1.2), [
        f"Model: FAO AquaCrop via AquaCrop-OSPy. Crop {v['crop']}, soil {v['soil']}, planting 1 October.",
        f"Weather: {v['weather']}; {v['n_seasons']} seasons, {v['first_season']} to {v['last_season']}. Not an Indian site.",
    ], size=14, color=MUTED, space_after=4)
    footer(s)

    # 5. Results
    s = prs.slides.add_slide(blank)
    title(s, f"Result: {v['scheduler_id']} keeps yield with far less water")
    s.shapes.add_picture(str(res / "irrigation_vs_yield.png"), MARGIN, Inches(1.4), width=Inches(7.4))
    x = Inches(8.35)
    stat(s, x, Inches(1.4), Inches(4.4), f"{v['base_mm']} → {v['sched_mm']} mm",
         "mean irrigation per season, baseline → scheduler", value_size=30)
    stat(s, x, Inches(3.0), Inches(4.4), f"{v['base_yield']} → {v['sched_yield']} t/ha",
         f"mean dry yield ({v['yield_diff_pct']})", value_size=30)
    stat(s, x, Inches(4.6), Inches(4.4), f"{v['base_wp']} → {v['sched_wp']}",
         "kg grain per m³ irrigation water (inflated: rain does most of the work)", value_size=30)
    text(s, MARGIN, Inches(6.2), Inches(12.1), Inches(0.7),
         f"Selection rule met: {v['rule_met']}. Less water in {v['paired_less_water']} seasons; "
         f"yield within 2% in {v['paired_within_2pct']} seasons. Rainfed alone reaches {v['rainfed_pct']} "
         "of baseline yield here, so the baseline over-irrigates.", size=14, color=MUTED)
    footer(s)

    # 6. Impact
    s = prs.slides.add_slide(blank)
    title(s, "Impact per hectare per season (simulated)")
    s.shapes.add_picture(str(res / "impact_summary.png"), MARGIN, Inches(1.25), width=W - 2 * MARGIN)
    rows = [("Pump head", "kWh/m³", "kWh saved", "₹ saved", "kg CO₂ saved")] + sensitivity_rows(impact)
    tbl = s.shapes.add_table(len(rows), 5, MARGIN, Inches(4.35), Inches(8.0), Inches(1.9)).table
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.text = val
            run = cell.text_frame.paragraphs[0].runs[0]
            run.font.size, run.font.name = Pt(14), BODY
            run.font.bold = r == 0
            run.font.color.rgb = WHITE if r == 0 else INK
            cell.fill.solid()
            cell.fill.fore_color.rgb = FOREST if r == 0 else (TINT if r % 2 else WHITE)
    text(s, Inches(9.0), Inches(4.35), Inches(3.75), Inches(2.5), [
        "Sensitivity: savings scale with pump head, so we show 15, 30 and 60 m.",
        f"Base case: head {v['head_m']} m, efficiency {v['pump_eff']}, tariff {v['tariff']}/kWh, "
        f"grid {v['grid_ef']} kg CO₂/kWh.",
        "All four are assumptions to verify (docs/ASSUMPTIONS.md).",
    ], size=14, color=MUTED, space_after=8)
    footer(s)

    # 7. Scale, viability, deployment, limitations
    s = prs.slides.add_slide(blank)
    background(s, FOREST)
    title(s, "Path to the field, and what this does not show", dark=True)
    quads = [
        ("Scalability", ["Rule runs on low-cost hardware, offline", "One controller can serve several valves",
                         "Re-run per region with local weather and soil"]),
        ("Commercial viability", ["Saving = water + pump electricity", "Fits pump-solarisation and drip programmes",
                                  "No payback model yet: capex and tariffs unverified"]),
        ("Deployment path", ["Capacitive probes, ESP32-class controller, relay", "Calibrate probes to local soil",
                             "Pilot: one field, control vs treatment plot"]),
        ("Limitations", ["Simulated only; sample climate (Tunis), not local",
                         "Single crop and soil; baseline over-irrigates",
                         "Threshold scheduling is a modest, known idea"]),
    ]
    for i, (head, body) in enumerate(quads):
        x = MARGIN + (i % 2) * Inches(6.15)
        y = Inches(1.45) + (i // 2) * Inches(2.7)
        card(s, x, y, Inches(5.95), Inches(2.45), fill=RGBColor(0x3B, 0x73, 0x3C))
        text(s, x + Inches(0.25), y + Inches(0.15), Inches(5.5), Inches(0.5), head, size=20,
             color=WHITE, font=HEAD, bold=True)
        text(s, x + Inches(0.25), y + Inches(0.75), Inches(5.5), Inches(1.6), body, size=15,
             color=WHITE, bullets=True, space_after=4)
    footer(s, dark=True)
    return prs


def check(path) -> None:
    """Render check: 7 slides, no empty placeholders, team name on slide 1, no leftover team placeholder."""
    prs = Presentation(str(path))
    assert len(prs.slides) == 7, f"expected 7 slides, got {len(prs.slides)}"
    for i, slide in enumerate(prs.slides, start=1):
        for shp in slide.placeholders:
            assert shp.has_text_frame and shp.text_frame.text.strip(), f"empty placeholder on slide {i}"
        texts = " ".join(sh.text_frame.text for sh in slide.shapes if sh.has_text_frame)
        assert "[TEAM NAME]" not in texts and "[MEMBERS]" not in texts, f"leftover placeholder on slide {i}"
        if i == 1:
            assert config.TEAM_NAME in texts, "team name missing from slide 1"
        assert "simulated" in texts.lower(), f"slide {i} lacks the 'simulated' label"
    print(f"Deck check passed: {len(prs.slides)} slides, no empty placeholders, "
          "team name on slide 1, 'simulated' on every slide")


def main() -> None:
    impact = load_impact()
    prs = build(fmt_values(impact), impact)
    config.DECK_PATH.parent.mkdir(exist_ok=True)
    prs.save(str(config.DECK_PATH))
    print(f"Wrote {config.DECK_PATH.relative_to(config.ROOT)}")
    check(config.DECK_PATH)


if __name__ == "__main__":
    main()
