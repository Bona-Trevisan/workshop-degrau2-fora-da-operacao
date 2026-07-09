#!/usr/bin/env python3
import os
import sys
import json
import time
import base64
import httpx

ENV_PATH = "/opt/steve/.env"
ASSETS_DIR = "/opt/steve/workspace/workshop-degrau2/assets"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-ultra-generate-001:predict"

def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k] = v
    return env

RIGHT_TECH = (
    "RIGHT HALF: dark tech display panel, gradient from black to deep red, "
    "mostly empty negative space reserved for text overlay, subtle faint UI decoration only at edges, "
    "no readable text, no words, no letters, no numbers, no subtitles."
)

PALETTE = (
    "PALETTE: deep red #dc2626 and #991b1b, black #0a0a0a background, cyan accent #22d3ee, "
    "off white highlights, strong neon glow."
)

CAMERA = "CAMERA: medium shot, eye level, 35mm equivalent lens, shallow depth of field, cinematic."

STYLE = (
    "Premium cinematic digital illustration, dramatic lighting, ultra detailed, 16:9 widescreen. "
)

NO_TEXT = "NO TEXT, NO WORDS, NO LETTERS, NO NUMBERS, NO LOGOS, NO SUBTITLES, NO READABLE UI LABELS."

SLIDES = [
    {
        "id": "01",
        "name": "abertura",
        "left": (
            "LEFT HALF: a lone businessman silhouette, generic and non identifiable face, standing "
            "in a dark modern office at night, arms slightly open, looking at a massive wall of floating "
            "holographic red control panels and glowing charts that surround him like a cage, "
            "dramatic red rim light outlining his figure."
        ),
        "env": "ENVIRONMENT: minimalist executive office at night, city lights blurred through a window, floating red digital particles.",
    },
    {
        "id": "02",
        "name": "mapa",
        "left": (
            "LEFT HALF: three glowing holographic panels floating side by side above a sleek desk, "
            "each panel a distinct abstract icon, one showing a coin and graph, one showing a compass "
            "and target, one showing a funnel shape, connected by thin glowing red lines to a small "
            "floating clock icon above them."
        ),
        "env": "ENVIRONMENT: dark tech briefing room, soft cyan rim light, floating particles, sense of a live online session about to start.",
    },
    {
        "id": "03",
        "name": "conceito-chave",
        "left": (
            "LEFT HALF: a large glowing red hourglass shape made of light, the top chamber wide and "
            "full of small chaotic glowing fragments, the narrow neck squeezed tight where a small "
            "silhouette figure stands trapped, symbolizing a business bottleneck concentrated on one person."
        ),
        "env": "ENVIRONMENT: dark void with deep red volumetric light beams, cyan particles drifting, high contrast.",
    },
    {
        "id": "04",
        "name": "slide-ancora",
        "left": None,
        "full": (
            "FULLSCREEN COMPOSITION, no 50/50 split, no side panel. A glowing red core sphere of light "
            "centered in the frame, radiating energy. Around it, three orbiting glowing ring clusters, "
            "each cluster made of abstract holographic icons: one cluster of coin and ascending graph icons, "
            "one cluster of compass and target icons, one cluster of funnel and megaphone icons, connected "
            "to the central core by thin curved glowing red and cyan lines, symmetrical composition, "
            "wide empty dark margins at the very top and bottom of the frame reserved for overlay text."
        ),
        "env": "ENVIRONMENT: infinite dark void, deep red and cyan volumetric glow, fine floating particles, symmetrical epic scale.",
    },
    {
        "id": "05",
        "name": "pilar-financeiro",
        "left": (
            "LEFT HALF: a strong glowing red ascending bar graph made of light rising from a solid "
            "geometric base, next to it a large glowing coin symbol slowly separating into two distinct "
            "stacks, symbolizing separating personal and business finances, sharp clean holographic lines."
        ),
        "env": "ENVIRONMENT: dark minimalist finance control room, floating thin ledger lines of light, cyan grid floor reflection.",
    },
    {
        "id": "06",
        "name": "pilar-estrategico",
        "left": (
            "LEFT HALF: a glowing red compass rose made of light, a single bright beam pointing forward "
            "cutting through a dense cloud of small scattered dim fragments around it, symbolizing one "
            "clear priority cutting through scattered urgent tasks."
        ),
        "env": "ENVIRONMENT: dark strategic war room, faint holographic map grid on the floor, cyan light streaks, particles.",
    },
    {
        "id": "07",
        "name": "pilar-vendas",
        "left": (
            "LEFT HALF: a large glowing red funnel made of light, at the narrow bottom tip a small "
            "silhouette figure straining to hold the entire flow alone, one glowing segment of the "
            "funnel gently detaching and floating away on its own, symbolizing delegating part of the sales process."
        ),
        "env": "ENVIRONMENT: dark tech sales floor, distant floating holographic screens, cyan and red glow, particles.",
    },
    {
        "id": "08",
        "name": "leva-embora",
        "left": (
            "LEFT HALF: a pair of hands holding a glowing translucent tablet of light with three simple "
            "abstract checklist marks glowing on it, soft warm red glow reflecting on the hands, "
            "sense of something tangible being taken away from the session."
        ),
        "env": "ENVIRONMENT: dark cozy home office at night, laptop glow, warm red accent light, subtle bokeh particles.",
    },
    {
        "id": "09",
        "name": "para-quem-e",
        "left": (
            "LEFT HALF: two diverging glowing paths of light on dark ground, one path bright red leading "
            "toward a small glowing open door of light in the distance, the other path dim and fading into "
            "darkness, a single silhouette figure standing at the fork deciding."
        ),
        "env": "ENVIRONMENT: dark abstract landscape, fog, deep red and faint cyan light beams, minimal particles.",
    },
    {
        "id": "10",
        "name": "oferta",
        "left": (
            "LEFT HALF: a glowing translucent ticket or admission card made of red light floating "
            "upright, intricate holographic border patterns, a soft pulsing glow, small floating "
            "seat icons scattered lightly around it suggesting limited seats."
        ),
        "env": "ENVIRONMENT: dark premium event backdrop, subtle spotlight cone from above, floating red particles, elegant.",
    },
    {
        "id": "11",
        "name": "quem-conduz",
        "left": (
            "LEFT HALF: a confident businessman silhouette, generic and non identifiable face, standing "
            "with arms crossed, calm posture, behind him four small distinct glowing holographic building "
            "icons floating in a row representing different industries, an airplane part, a sofa, a "
            "document, a digital screen, all connected to him by thin glowing lines yet he stands relaxed, not overwhelmed."
        ),
        "env": "ENVIRONMENT: dark executive office at night, calm confident atmosphere, soft red and cyan rim light, particles.",
    },
    {
        "id": "12",
        "name": "cta-final",
        "left": (
            "LEFT HALF: a silhouette figure walking calmly through a large glowing red doorway of light "
            "toward a bright open horizon, leaving behind a dim cluttered room full of small fading "
            "holographic panels, strong sense of forward motion and relief."
        ),
        "env": "ENVIRONMENT: dark room transitioning into a bright glowing horizon, dramatic contrast, red and warm light, particles.",
    },
]

def build_prompt(slide):
    if slide.get("full"):
        return (
            f"{STYLE}{slide['full']} {PALETTE} {slide['env']} {CAMERA} {NO_TEXT}"
        )
    return (
        f"{STYLE}{slide['left']} {RIGHT_TECH} {PALETTE} {slide['env']} {CAMERA} {NO_TEXT}"
    )

def generate(api_key, prompt, aspect="16:9"):
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1, "aspectRatio": aspect},
    }
    r = httpx.post(
        f"{ENDPOINT}?key={api_key}",
        json=payload,
        timeout=90,
    )
    r.raise_for_status()
    data = r.json()
    preds = data.get("predictions")
    if not preds:
        raise RuntimeError(f"sem predictions: {data}")
    b64 = preds[0]["bytesBase64Encoded"]
    return base64.b64decode(b64)

def main():
    env = load_env(ENV_PATH)
    api_key = env.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY ausente em /opt/steve/.env", file=sys.stderr)
        sys.exit(1)

    os.makedirs(ASSETS_DIR, exist_ok=True)
    only = sys.argv[1:] if len(sys.argv) > 1 else None

    for slide in SLIDES:
        if only and slide["id"] not in only:
            continue
        out_path = os.path.join(ASSETS_DIR, f"slide-{slide['id']}.png")
        if os.path.exists(out_path) and "--force" not in sys.argv:
            print(f"slide-{slide['id']} ja existe, pulando")
            continue
        prompt = build_prompt(slide)
        print(f"gerando slide-{slide['id']} ({slide['name']})...")
        attempts = 0
        while attempts < 3:
            attempts += 1
            try:
                img_bytes = generate(api_key, prompt)
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
                print(f"  ok: {out_path} ({len(img_bytes)} bytes)")
                break
            except Exception as e:
                print(f"  tentativa {attempts} falhou: {e}", file=sys.stderr)
                if attempts >= 3:
                    print(f"  FALHOU slide-{slide['id']} apos 3 tentativas", file=sys.stderr)
                else:
                    time.sleep(3)

if __name__ == "__main__":
    main()
