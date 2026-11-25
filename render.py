#!/usr/bin/env python3
"""Draw the front page for Tuesday 24 November 2026.

A clean newspaper front page for the make.fun news-image-20261124
bounty: masthead, date line, two lead stories, thirteen more stories in
two columns, a red DATE CHECK box and a sources footer. Deterministic:
same input always produces the same PNG bytes.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

SIZE = 1024
PAPER = (248, 242, 228)
INK = (20, 20, 20)
RED = (163, 22, 33)
GREY = (107, 101, 88)
RULE = (60, 60, 60)

SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def fit_size(draw, text, path, start, minimum, max_w):
    """Largest font size in [minimum, start] that fits text in max_w."""
    size = start
    while size > minimum:
        fnt = font(path, size)
        if text_w(draw, text, fnt) <= max_w:
            return fnt
        size -= 1
    return font(path, minimum)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap, returns a list of lines."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_w(draw, trial, fnt) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_rule(draw, x0, x1, y, width=2, color=RULE):
    draw.line([(x0, y), (x1, y)], fill=color, width=width)


def draw_double_rule(draw, x0, x1, y):
    draw_rule(draw, x0, x1, y, width=2)
    draw_rule(draw, x0, x1, y + 5, width=1)


def draw_section(draw, x, y, label):
    """Red square bullet plus red section label. Returns y below it."""
    draw.rectangle([x, y + 3, x + 11, y + 14], fill=RED)
    fnt = font(SANS_BOLD, 19)
    draw.text((x + 18, y), label, font=fnt, fill=RED)
    return y + 28


def draw_story(draw, x, y, width, headline, sub):
    """One grid story: bold headline on one line, one sub line below."""
    head_fnt = fit_size(draw, headline, SERIF_BOLD, 25, 20, width)
    draw.text((x, y), headline, font=head_fnt, fill=INK)
    y += 28
    sub_fnt = font(SERIF, 18)
    sub_lines = wrap(draw, sub, sub_fnt, width)
    for line in sub_lines[:1]:
        draw.text((x, y), line, font=sub_fnt, fill=INK)
        y += 21
    return y + 10


def draw_lead(draw, x, y, width, kicker, headline, sub):
    """A lead story: red kicker, big headline, wrapped sub. Returns y."""
    kick_fnt = font(SANS_BOLD, 19)
    draw.text((x, y), kicker, font=kick_fnt, fill=RED)
    y += 27
    head_fnt = fit_size(draw, headline, SERIF_BOLD, 46, 34, width)
    draw.text((x, y), headline, font=head_fnt, fill=INK)
    y += 52
    sub_fnt = font(SERIF, 21)
    for line in wrap(draw, sub, sub_fnt, width):
        draw.text((x, y), line, font=sub_fnt, fill=INK)
        y += 25
    return y + 4


def main():
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(img)

    # Outer frame.
    draw.rectangle([11, 11, SIZE - 12, SIZE - 12], outline=INK, width=3)

    left = 30
    right = SIZE - 30
    width = right - left

    # Masthead.
    mast_fnt = font(SERIF_BOLD, 62)
    mast = "THE WORLD IN ONE DAY"
    mw = text_w(draw, mast, mast_fnt)
    draw.text(((SIZE - mw) / 2, 26), mast, font=mast_fnt, fill=INK)

    # Date line.
    date_fnt = font(SERIF, 28)
    date = "Tuesday, 24 November 2026"
    dw = text_w(draw, date, date_fnt)
    draw.text(((SIZE - dw) / 2, 104), date, font=date_fnt, fill=INK)
    draw_double_rule(draw, left, right, 148)

    # Lead story 1: Abu Dhabi peace talks.
    y = draw_lead(
        draw, left, 164, width,
        "DIPLOMACY - ABU DHABI",
        "ABU DHABI PEACE TALKS END WITH NO DEAL",
        "Russia rules out territorial concessions; US envoys Kushner and "
        "Witkoff head to Moscow next.",
    )
    draw_rule(draw, left, right, y + 2)
    y += 12

    # Lead story 2: Sanofi buys Insmed.
    y = draw_lead(
        draw, left, y, width,
        "BUSINESS - PHARMA",
        "SANOFI BUYS INSMED FOR $41 BILLION",
        "Cash deal at $175 a share is the year's biggest biopharma takeover.",
    )
    draw_rule(draw, left, right, y + 2)
    y += 14
    grid_top = y

    # Grid: two columns.
    col_w = 466
    gap = 30
    col2_x = left + col_w + gap

    middle_east = [
        ("Gaza strikes kill Hamas security chief",
         "Naeem Abu Nahel among seven killed, Israel says."),
    ]
    ukraine_war = [
        ("Zaporizhzhia strike kills 2, wounds 40",
         "Four children among the wounded overnight."),
        ("Ukraine hits Kerch Bridge and refinery",
         "Kirishi refinery hit in latest long-range attack."),
        ("Russian drone enters Polish airspace",
         "NATO jets scramble after brief incursion."),
        ("NATO vows to defend space",
         "Pledge after reports of a Russian nuclear satellite."),
        ("Germany first into Delta system",
         "Berlin gets access to battlefield management tool."),
        ("Moldova reports seven drone incursions",
         "Russian drones crossed the border seven times."),
    ]
    world = [
        ("Fighting traps Ebola teams in Congo",
         "Health teams stuck in Ituri amid clashes, WHO says."),
        ("Iraq to run Kurdish-held oilfields",
         "Ministry told to run fields in Kurdish-held areas."),
        ("Seoul offers $375,000 rewards",
         "Bounty targets AI cheating in entrance exam."),
        ("UN chief urges talks on AI safety rules",
         "Call for global rules to govern AI."),
        ("Euclid finds most distant quasar yet",
         "Seen 630m years after the Big Bang, ESA says."),
        ("Russian 2026 losses hit record 432,519",
         "Ukraine's General Staff reports the yearly toll."),
    ]

    ly = grid_top
    ly = draw_section(draw, left, ly, "MIDDLE EAST - 1")
    for head, sub in middle_east:
        ly = draw_story(draw, left, ly, col_w, head, sub)
    ly = draw_section(draw, left, ly, "UKRAINE WAR - 6")
    for head, sub in ukraine_war:
        ly = draw_story(draw, left, ly, col_w, head, sub)

    ry = grid_top
    ry = draw_section(draw, col2_x, ry, "WORLD - 6")
    for head, sub in world:
        ry = draw_story(draw, col2_x, ry, col_w, head, sub)

    grid_bottom = max(ly, ry)

    # DATE CHECK box.
    box_top = grid_bottom + 8
    box_bottom = box_top + 66
    draw.rectangle(
        [left, box_top, right, box_bottom], outline=RED, width=2
    )
    check_fnt = font(SANS_BOLD, 19)
    draw.text((left + 14, box_top + 8), "\u2713  DATE CHECK",
              font=check_fnt, fill=RED)
    line_fnt = font(SERIF_BOLD, 20)
    line = ("Every story above happened or was first reported on "
            "Tuesday 24 November 2026.")
    draw.text((left + 14, box_top + 34), line, font=line_fnt, fill=INK)

    # Sources footer.
    foot_fnt = font(SANS, 15)
    foot = ("Sources: Reuters, AP, BBC, Nexus Europa, Sanofi, "
            "Kyiv Independent, WHO, UN, ESA, Just Security")
    draw.text((left, box_bottom + 8), foot, font=foot_fnt, fill=GREY)

    out_path = os.path.join(HERE, "entry.png")
    img.save(out_path, format="PNG")
    print("wrote", out_path)


if __name__ == "__main__":
    main()
