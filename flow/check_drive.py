# -*- coding: utf-8 -*-
"""Interference checks and a shaded view of the syringe drive.

    python check_drive.py     ->  syringe-drive.png  + pass/fail table
"""
import os
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import syringe_drive as S

HERE = os.path.dirname(os.path.abspath(__file__))
LIGHT = np.array([0.45, -0.75, 0.55])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
fails = []


def check(name, ok, detail=""):
    print("%-4s %-50s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        fails.append(name)


def eye(elev, azim):
    e, a = np.radians(elev), np.radians(azim)
    return np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])


def shade(ax, mesh, base, view, alpha=1.0, zbias=0.0):
    keep = mesh.face_normals @ view > 0.0
    tri, nrm = mesh.triangles[keep], mesh.face_normals[keep]
    lam = 0.35 + 0.65 * np.clip(nrm @ LIGHT, 0.0, 1.0)
    rgb = np.clip(np.array(base)[None, :] * lam[:, None], 0, 1)
    order = np.argsort(tri.mean(axis=1) @ view)
    col = Poly3DCollection(tri[order], facecolors=rgb[order], alpha=alpha,
                           edgecolors=rgb[order], linewidths=0.3, shade=False)
    col.set_sort_zpos(zbias)
    ax.add_collection3d(col)


parts = S.build()
frame, carr = parts["frame"], parts["carriage"]

for n, m in sorted(parts.items()):
    check("watertight and positive volume: %s" % n,
          m.is_watertight and m.volume > 0, "%.1f mL" % (m.volume / 1000.0))

# Carriage must clear the frame everywhere in its travel.
sweep = trimesh.util.concatenate([
    carr.copy().apply_translation((x, 0, 0))
    for x in np.linspace(S.X_CARR_MIN, S.X_CARR_MAX, 36)])
sweep = trimesh.boolean.union([sweep], engine="manifold")
clash = trimesh.boolean.intersection([frame, sweep], engine="manifold")
check("carriage clears the frame through full travel",
      clash.volume < 5.0, "swept overlap %.2f mm3" % clash.volume)

# Rod bores must line up between the two parts.
cb = carr.bounds
check("carriage spans both rods",
      cb[0][1] < -S.ROD_SPACING / 2 and cb[1][1] > S.ROD_SPACING / 2,
      "carriage y %.1f..%.1f, rods at %.1f" % (cb[0][1], cb[1][1], S.ROD_SPACING / 2))

# Screw supported at both ends: motor at one, 608 at the other.
span = S.SCREW_SPAN
nc = 4.76e6 * S.SCREW_ROOT_D / (span ** 2)
check("screw critical speed exceeds the piston's peak", nc > S.PEAK_RPM * 1.5,
      "%.0f rpm over a %.0f mm span" % (nc, span))

# The carriage cannot drive the plunger fully home, because its own front wall
# meets the end rib first. What is left is dead volume, and it must stay small.
# Dead volume is what the piston cannot expel, because the carriage's own
# front wall meets the end rib before the plunger bottoms. Judge it as a
# FRACTION of the barrel, not in mL: the same geometry gives 13% on a 3 mL
# barrel and 15% on a 5 mL one, and an absolute threshold tuned on the 3 mL
# would fail the 5 mL for no physical reason. It is dead LIQUID, which is
# harmless. Dead air would not be, which is why the syringe mounts tip up:
# bubbles rise to the tip, and the tip is the outlet, so flow carries them out.
dead_mL = S.DEAD_MM * S.BORE_A / 1000.0
check("dead volume is a small fraction of the barrel",
      dead_mL / S.SYR_CAPACITY_ML < 0.20,
      "%.1f mm = %.2f mL of %.1f mL, %.0f%%. Mount TIP UP so it purges"
      % (S.DEAD_MM, dead_mL, S.SYR_CAPACITY_ML,
         dead_mL / S.SYR_CAPACITY_ML * 100.0))

# The frame's mechanical travel is longer than the barrel can take. That is
# safe only as long as software knows it.
check("frame travel is not the binding limit, software is",
      S.SOFT_TRAVEL < S.TRAVEL,
      "retract at most %.1f mm of the %.0f mm available"
      % (S.SOFT_TRAVEL, S.TRAVEL))
check("soft limit still leaves room for the beat plus priming",
      S.SOFT_TRAVEL > S.BEAT_MM * 3.0,
      "%.1f mm soft limit against a %.2f mm beat, %.1fx"
      % (S.SOFT_TRAVEL, S.BEAT_MM, S.SOFT_TRAVEL / S.BEAT_MM))

# The whole point of the offset: screw and syringe must not share space.
# The envelope is the collar, not the barrel, since the collar is what the
# frame actually holds and it is the larger of the two.
sep = S.SYR_H - S.SCREW_H - (S.SADDLE_BORE / 2 + S.BEAR_OD / 2)
check("collar clears the screw bearing", sep > 0.0,
      "%.1f mm between the %.1f mm collar OD and the 608 OD"
      % (sep, S.SADDLE_BORE))

# Collar: the part that absorbs the one syringe dimension that could have
# scrapped the frame. It has to be printable and it has to fit both ways.
# Where the straps fall, and therefore where the collars sit. Defined once,
# here, because several checks below need it.
STRAP_X = (S.X_RIB_BACK + 8.0, S.X_SADDLE_END - 16.0)
COLLAR_X = tuple(xs + 2.0 - S.COLLAR_L / 2.0 for xs in STRAP_X)

_bore_drawn = S.SYR_BARREL_D - S.COLLAR_GRIP + S.HOLE_SHRINK
wall = (S.SADDLE_BORE - _bore_drawn) / 2.0
check("collar wall is printable", wall >= S.COLLAR_WALL_MIN,
      "%.2f mm wall, drawn bore %.2f inside a %.1f mm OD, two perimeters at "
      "%.2f mm" % (wall, _bore_drawn, S.SADDLE_BORE, wall / 2.0))

# The collar is the one part whose fit is deliberately an interference, so the
# shrink that every other hole has to defeat is being used on purpose here.
# Both bounds matter: too little and the collar falls off the barrel while the
# syringe is handled, too much and the slit will not close under the strap.
_bore_printed = _bore_drawn - S.HOLE_SHRINK
_grip = S.SYR_BARREL_D - _bore_printed
check("collar snaps onto the barrel rather than sliding",
      0.05 <= _grip <= 0.25,
      "drawn %.2f prints about %.2f on a %.1f mm barrel, %.2f mm interference"
      % (_bore_drawn, _bore_printed, S.SYR_BARREL_D, _grip))

check("collar still fits the saddle the frame actually has",
      S.SADDLE_BORE / 2.0 <= S.SADDLE_BORE / 2.0 + S.FIT,
      "collar OD %.1f in a channel cut at %.1f, %.2f mm radial room"
      % (S.SADDLE_BORE, S.SADDLE_BORE + 2 * S.FIT, S.FIT))

# A slit that stops short of the OD is a ring with a groove in it, and it has
# none of the compliance the split was added for. Sweep a thin probe through
# the full wall thickness at the top, on the bore axis, and require the collar
# to contain none of it. Containment by ray casting would need rtree, which is
# not installed, so this asks the boolean engine the model is already built
# with: the answer has to be exactly zero, not merely small.
_slit_probe = S.box((2.0, S.COLLAR_L - 2.0), (-0.5, 0.5),
                    (_bore_drawn / 2.0, S.SADDLE_BORE / 2.0))
_left = trimesh.boolean.intersection([parts["collar"], _slit_probe],
                                     engine="manifold")
check("collar slit runs right through the wall at the top",
      _left.volume < 1e-6,
      "%.6f mm3 of material across the full %.2f mm wall on the bore axis, "
      "so the C can close" % (_left.volume, wall))

# The frame is printed and the saddle bore can no longer be changed, so it has
# to admit every barrel we might plausibly move to. A 5 mL barrel halves the
# screw speed, which is the single biggest lever on the whole motor problem,
# and it would be lost for good to a 14 mm bore.
#
# The 5 mL entry was an ESTIMATE of 12.5 mm when the frame was committed. It
# measured 14.0 on 2026-11-10, so the estimate was 1.5 mm light and a saddle
# sized to it would have rejected the real part. The measured value replaces
# it here rather than sitting beside it, because leaving a refuted estimate in
# a table of constraints is how it gets believed a second time.
FUTURE_BARRELS = (("3 mL", 10.5), ("5 mL measured", 14.0))
blocked = [n for n, od in FUTURE_BARRELS
           if (S.SADDLE_BORE - od) / 2.0 < S.COLLAR_WALL_MIN]
check("saddle bore keeps the plausible syringe sizes open", not blocked,
      "bore %.1f admits %s%s" % (
          S.SADDLE_BORE,
          ", ".join(n for n, od in FUTURE_BARRELS if n not in blocked),
          ("  BLOCKED: " + ", ".join(blocked)) if blocked else ""))

# The frame is the print that cannot be redone cheaply, so everything that
# could still change has to be shown not to reach it. The barrel OD is already
# tested above. The remaining exposure is barrel LENGTH, which sets where the
# saddle straps fall: too short a barrel and the far collar hangs off the end
# of it with nothing inside to grip.
min_barrel = (STRAP_X[1] + 2.0 + S.COLLAR_L / 2.0) - S.X_RIB_BACK
check("frame works for any barrel longer than the far strap",
      S.SYR_BARREL_L >= min_barrel,
      "far collar ends %.0f mm past the flange, so any barrel over %.0f mm "
      "works. The measured barrel is %.0f"
      % (min_barrel, min_barrel, S.SYR_BARREL_L))

# This is the one that matters now, because the frame is no longer a drawing.
# It was printed to a GUESSED 56 mm barrel and the real one measured 66. Both
# collars still have to land on barrel, with the extra length simply hanging
# past the saddle. Checking SYR_BARREL_L against the model's own saddle would
# be circular once FRAME_SADDLE_L is pinned, so this asks the question the
# other way round: take the saddle that exists, and put the real barrel in it.
for i, xs in enumerate(STRAP_X):
    c0 = xs + 2.0 - S.COLLAR_L / 2.0
    check("printed frame: collar %d grips the measured barrel" % (i + 1),
          c0 >= S.X_RIB_BACK and c0 + S.COLLAR_L <= S.X_TIP,
          "collar X %.1f..%.1f inside a barrel running X %.1f..%.1f"
          % (c0, c0 + S.COLLAR_L, S.X_RIB_BACK, S.X_TIP))

_sad_end = S.X_SADDLE_END - 6.0
check("barrel overhang past the saddle is clearance, not interference",
      S.X_TIP > _sad_end and S.X_TIP > S.X_END,
      "tip stands %.1f mm past the saddle and %.1f mm past the end of the "
      "plate, so the luer and its tubing are in free air"
      % (S.X_TIP - _sad_end, S.X_TIP - S.X_END))

# Both motors have to bolt to the same plate, because which one ends up
# driving it is still open and the plate is on the frame.
check("motor plate takes a standard NEMA 17 face",
      abs(S.MOTOR_SQ - 42.3) < 0.5 and abs(S.MOTOR_BC - 31.0) < 0.5,
      "%.1f mm square, %.1f mm bolt circle, %.1f mm boss. Fits the 23 mm "
      "pancake and the 48 mm alike, since only the body length differs"
      % (S.MOTOR_SQ, S.MOTOR_BC, S.MOTOR_BOSS_D))

# Each collar is centred under a strap slot, which is what clamps it. The
# straps are the only thing locating the barrel axially, so the collar has to
# actually be under one, and inside the saddle at both ends.
sad_lo, sad_hi = S.X_RIB_BACK + 3.0, S.X_SADDLE_END - 6.0
check("collars sit inside the saddle under the straps",
      all(x >= sad_lo - 0.01 and x + S.COLLAR_L <= sad_hi + 0.01
          for x in COLLAR_X),
      "collars at %s span %.0f mm, saddle is X %.0f..%.0f"
      % (", ".join("%.0f" % x for x in COLLAR_X), S.COLLAR_L, sad_lo, sad_hi))

# No syringe dimension may reach the frame except the two benign ones. This is
# the claim the print order rests on, so it gets tested rather than asserted:
# perturb the barrel OD and the frame must come out unchanged.
_saved = S.SYR_BARREL_D
S.SYR_BARREL_D = _saved + 1.5
try:
    frame_perturbed = S.frame()
finally:
    S.SYR_BARREL_D = _saved
check("frame is independent of the barrel OD",
      abs(frame_perturbed.volume - frame.volume) < 1e-6,
      "barrel OD +1.5 mm changed the frame by %.6f mm3"
      % abs(frame_perturbed.volume - frame.volume))

# Electronics shelf holes must miss the carriage sweep, which covers the whole
# width with only 10 mm of air beneath it.
sweep_lo, sweep_hi = S.X_CARR_MIN, S.X_CARR_MAX + S.CARRIAGE_L
clear = all(x < sweep_lo - 2.0 or x > sweep_hi + 2.0 for x in S.TRAY_HOLES_X)
check("shelf holes miss the carriage sweep", clear,
      "holes at %s, sweep X %.0f..%.0f"
      % (", ".join("%.0f" % x for x in S.TRAY_HOLES_X), sweep_lo, sweep_hi))

# And they must stand off the strap slots and the existing mounting holes in X.
# The straps sit at |y| 11.5 and the shelf holes at y 35, so nothing actually
# touches, but a zip-tie tail needs somewhere to go and the test is free.
others = [S.X_MOTOR_BACK + 14.0, S.X_END - 16.0,
          S.X_RIB_BACK + 8.0, S.X_SADDLE_END - 16.0]
gap = min(abs(a - b) for a in S.TRAY_HOLES_X for b in others)
check("shelf holes stand off the straps and mounting holes", gap > 5.0,
      "nearest other feature is %.1f mm away in X" % gap)

# Both rods must be gripped at BOTH ends. For several revisions they were not:
# the motor plate was only as wide as the NEMA 17 face, 42.3 mm, while the rods
# sit 56 mm apart, so the rods passed through the end rib and nothing else and
# cantilevered the length of the frame. Nothing in the geometry complained,
# because a hole cut through empty space is not an error.
rod_y = S.ROD_SPACING / 2.0 + S.ROD_D / 2.0
for label, xs in (("motor end", S.X_MOTOR_FACE + S.WALL_T / 2.0),
                  ("rib end", S.X_RIB + S.RIB_T / 2.0)):
    probe = S.box((xs - 0.4, xs + 0.4),
                  (S.ROD_SPACING / 2 - 0.4, S.ROD_SPACING / 2 + 0.4),
                  (S.SCREW_H - 8.0, S.SCREW_H - 5.0))
    hit = trimesh.boolean.intersection([frame, probe], engine="manifold")
    check("rod is carried at the %s" % label, hit.volume > 0.1,
          "material under the rod bore at X %.0f, y %.0f" % (xs, S.ROD_SPACING / 2))

# Printed, not drawn: what the rod bore and the bearing pocket will actually
# measure once the press takes its 0.24 mm out of them. The rod bore must not
# end up larger than the rod, or nothing holds the rods; the bearing pocket
# must not end up larger than the bearing, or it falls out.
rod_printed = (S.ROD_D + 0.24) - S.HOLE_SHRINK
pocket_printed = (S.BEAR_OD + 0.2) - S.HOLE_SHRINK
check("rod bore prints to a press fit, not a clearance fit",
      rod_printed <= S.ROD_D + 0.02,
      "drawn %.2f, prints about %.2f on an %.2f mm rod"
      % (S.ROD_D + 0.24, rod_printed, S.ROD_D))
check("608 pocket prints to a press fit",
      pocket_printed <= S.BEAR_OD,
      "drawn %.2f, prints about %.2f on a %.2f mm bearing"
      % (S.BEAR_OD + 0.2, pocket_printed, S.BEAR_OD))

# A 608 is 7 mm wide and the rib must be thicker than that, or the pocket is
# a through hole and nothing seats the bearing but the luck of the print.
seat = S.RIB_T - S.BEAR_W
check("608 has a shoulder to seat against", seat >= 1.5,
      "%.1f mm of rib behind a %.1f mm bearing in a %.1f mm rib"
      % (seat, S.BEAR_W, S.RIB_T))

# The coupon only means something if it prints the same features the frame
# does, at the same thickness and the same orientation.
cp = parts["fit_coupon"]
# Measure the WALL, not the bounding box: the coupon has a foot so it does not
# tip over on the bed, and the foot is deliberately wider than the wall.
above = cp.vertices[cp.vertices[:, 2] > S.BASE_T + 1.0]
wall_t = above[:, 0].max() - above[:, 0].min()
check("fit coupon wall matches the rib it stands in for",
      abs(wall_t - S.RIB_T) < 0.05,
      "coupon wall %.1f mm, rib %.1f mm, same 608 pocket, shoulder and rod bore"
      % (wall_t, S.RIB_T))

# The end rib is a full-width wall, so a vertical hole there would pierce it.
check("shelf holes miss the end rib",
      all(x < S.X_RIB - 1.0 or x > S.X_RIB_BACK + 1.0 for x in S.TRAY_HOLES_X),
      "rib wall spans X %.0f..%.0f" % (S.X_RIB, S.X_RIB_BACK))

# The syringe is fixed, so check the carriage where the two actually meet:
# fully extended, with the disc seated in its pocket. Any overlap at all is a
# clearance error, most likely the plunger rod slot not reaching below the axis.
syr = S.syringe()
hit = trimesh.boolean.intersection(
    [syr, carr.copy().apply_translation((S.X_CARR_MAX, 0, 0))], engine="manifold")
check("carriage clears the plunger rod, disc and flange",
      hit.volume < 1.0, "overlap %.2f mm3 at full extension" % hit.volume)

# And the frame must not foul the syringe either.
hitf = trimesh.boolean.intersection([syr, frame], engine="manifold")
check("frame clears the syringe barrel and flange",
      hitf.volume < 1.0, "overlap %.2f mm3" % hitf.volume)

# Retract hard stop must not crush the coupler.
coup = S.X_CARR_MIN - (S.X_MOTOR_BACK + S.COUPLER_L)
check("retracted carriage clears the coupler", coup > 0.5, "%.1f mm" % coup)

# Beat stroke must sit inside the travel with priming headroom.
check("travel covers the beat stroke plus priming",
      S.TRAVEL > S.BEAT_MM * 3, "%.1f mm travel, %.2f mL prime"
      % (S.TRAVEL, S.TRAVEL * S.BORE_A / 1000.0))

# Carriage must stop short of the end rib at full extension.
ext = carr.copy().apply_translation((S.X_CARR_MAX, 0, 0))
check("carriage stops short of the syringe finger flange",
      ext.bounds[1][0] <= S.X_RIB - S.SYR_FLANGE_T + 0.01,
      "carriage ends at %.1f, flange face at %.1f"
      % (ext.bounds[1][0], S.X_RIB - S.SYR_FLANGE_T))

# ---- the rod clamp, and the pocket it made unnecessary to measure ----
# The disc pocket used to be a fit. It is now a swallow: anything in the
# declared range must drop in with clearance, and nothing in that range may
# jam. Jamming is the expensive failure, because it is discovered after the
# 95 minute print.
_pocket = S.DISC_T_MAX + 0.3 - S.HOLE_SHRINK
check("disc pocket swallows the whole declared disc range",
      _pocket > S.DISC_T_MAX and S.DISC_T_MIN >= 1.5,
      "pocket prints %.2f mm, accepts %.1f to %.1f mm. The micrometer says "
      "%.2f" % (_pocket, S.DISC_T_MIN, S.DISC_T_MAX, S.DISC_T))

check("measured disc is inside the range the pocket was built for",
      S.DISC_T_MIN <= S.DISC_T <= S.DISC_T_MAX,
      "%.2f mm sits %.2f mm above the floor and %.2f mm below the ceiling"
      % (S.DISC_T, S.DISC_T - S.DISC_T_MIN, S.DISC_T_MAX - S.DISC_T))

# The clamp only works if the tongue reaches the rod BEFORE the bar lands on
# the carriage. If the bar bottoms out first the bolts tighten against the
# carriage and the rod stays loose, which would look assembled and do nothing.
_gap = S.DISC_D / 2.0 + 3.0 - S.PLUNGER_ROD_D / 2.0
check("clamp tongue reaches the rod before the bar bottoms out",
      S.CLAMP_TONGUE > _gap,
      "tongue %.2f mm into a %.2f mm gap, so the bar stands %.2f mm proud on "
      "the measured rod and the bolts do the clamping"
      % (S.CLAMP_TONGUE, _gap, S.CLAMP_TONGUE - _gap))

check("clamp still reaches a rod at the bottom of the declared range",
      S.CLAMP_TONGUE > S.DISC_D / 2.0 + 3.0 - S.ROD_D_MIN / 2.0,
      "reaches a %.1f mm rod with %.2f mm to spare"
      % (S.ROD_D_MIN,
         S.CLAMP_TONGUE - (S.DISC_D / 2.0 + 3.0 - S.ROD_D_MIN / 2.0)))

_tongue_half = S.PLUNGER_ROD_D / 2.0 + 0.2
_slot_half = S.PLUNGER_ROD_D / 2.0 + 0.6
check("clamp tongue enters the rod slot without binding",
      _tongue_half + S.HOLE_SHRINK / 2.0 < _slot_half,
      "tongue %.1f mm wide in a slot that prints %.1f mm, %.2f mm total "
      "clearance" % (2 * _tongue_half, 2 * _slot_half - S.HOLE_SHRINK,
                     2 * (_slot_half - _tongue_half) - S.HOLE_SHRINK))

check("clamp bolts miss the rod slot and stay inside the carriage",
      S.CLAMP_Y - S.M3 / 2.0 > S.PLUNGER_ROD_D / 2.0 + 0.6
      and S.CLAMP_W / 2.0 < S.HALF_W - 2.0,
      "bolts at %.1f leave %.2f mm of wall to the slot edge, bar %.0f mm wide "
      "inside a %.0f mm carriage"
      % (S.CLAMP_Y, S.CLAMP_Y - S.M3 / 2.0 - (S.PLUNGER_ROD_D / 2.0 + 0.6),
         S.CLAMP_W, 2 * (S.HALF_W - 2.0)))

check("clamp does not foul the carriage, the frame or the saddle",
      trimesh.boolean.intersection(
          [parts["rod_clamp"], parts["carriage"]], engine="manifold").volume
      < 1e-6,
      "0 mm3 of overlap with the carriage it bolts to")

# ---- the motor, which is about to be swapped for the team's ----
# VREF is not a property of the driver. 0.556 V on the pot was derived for the
# pancake, and the same setting on a different motor can be anywhere between
# fine and over its rated current. These run against whichever motor MOTOR
# names, so a swap re-answers them instead of inheriting the old answer.
_mp = S.MOTORS[S.MOTOR]
check("phase current is within the fitted motor's rating",
      S.SET_I <= _mp["i"],
      "%.3f A set against a %.1f A motor, %.0f%% of rated"
      % (S.SET_I, _mp["i"], 100 * S.SET_I / _mp["i"]))

_kt = _mp["th"] / (2.0 ** 0.5 * _mp["i"])
_ceiling = S.DRIVE_V / _kt * 60.0 / (2 * 3.14159265)
check("fitted motor can reach the speed the piston needs",
      _ceiling > S.PEAK_RPM * 1.5,
      "%s ceiling %.0f rpm at %.0f V, piston needs %.0f, margin %.1fx"
      % (S.MOTOR, _ceiling, S.DRIVE_V, S.PEAK_RPM, _ceiling / S.PEAK_RPM))

_w = S.PEAK_RPM * 2 * 3.14159265 / 60.0
_head = S.DRIVE_V - S.SET_I * _mp["r"] - _kt * _w
_trev = 2.0 * _mp["l"] * S.SET_I / _head if _head > 0 else 9e9
_budget = 1.0 / (2 * S.PEAK_RPM / 60.0 * 50)
check("phase reverses inside the beat on the fitted motor",
      _trev < _budget / 2.0,
      "%.2f ms to reverse against a %.2f ms budget, margin %.1fx"
      % (_trev * 1e3, _budget * 1e3, _budget / _trev))

check("every motor in the table is either complete or deliberately blank",
      all(all(v is None for k, v in m.items() if k != "note")
          or all(v is not None for k, v in m.items() if k != "note")
          for m in S.MOTORS.values()),
      "%d motors listed, %d with full nameplates"
      % (len(S.MOTORS),
         sum(1 for m in S.MOTORS.values() if m["th"] is not None)))

# The tally used to print here, which put it AHEAD of the checks appended
# below it, so a failure in those was printed as FAIL and then tallied as
# "all checks passed" on the same run. A summary that is not last is not a
# summary. It now runs at the end of the file.

# ------------------------------------------------------------------ render
fig = plt.figure(figsize=(13.0, 5.6), dpi=170)
fig.patch.set_facecolor("white")
for i, (elev, azim, title, xoff) in enumerate((
        (26, -62, "Retracted (syringe full, homing stop)", S.X_CARR_MIN),
        (26, -62, "Extended (plunger at the flange)", S.X_CARR_MAX))):
    ax = fig.add_subplot(1, 2, i + 1, projection="3d", computed_zorder=False)
    view = eye(elev, azim)
    shade(ax, frame, (0.80, 0.76, 0.72), view, zbias=0)
    shade(ax, syr, (0.86, 0.88, 0.90), view, alpha=0.85, zbias=40)
    # Collars, drawn where the straps land. They are the only thing touching
    # the barrel, so a render without them hides the whole support scheme.
    for xc in COLLAR_X:
        c = S.collar()
        c.apply_translation((xc, 0.0, S.SYR_H))
        shade(ax, c, (0.55, 0.42, 0.30), view, zbias=50)
    shade(ax, carr.copy().apply_translation((xoff, 0, 0)), (0.30, 0.46, 0.60),
          view, zbias=60)
    # screw and rods, drawn for context
    scr = S.cyl_x(4.0, (S.X_MOTOR_BACK, S.X_RIB_BACK), z=S.SCREW_H)
    shade(ax, scr, (0.72, 0.60, 0.25), view, zbias=100)
    for dy in (-S.ROD_SPACING / 2, S.ROD_SPACING / 2):
        rod = S.cyl_x(S.ROD_D / 2, (S.X_MOTOR_FACE, S.X_RIB_BACK), y=dy, z=S.SCREW_H)
        shade(ax, rod, (0.55, 0.57, 0.60), view, zbias=90)
    ax.set_box_aspect((S.X_END, 2 * S.HALF_W, 70))
    ax.set_xlim(0, S.X_END)
    ax.set_ylim(-S.HALF_W - 2, S.HALF_W + 2)
    ax.set_zlim(0, 70)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title, fontsize=10.5, color="#1b1b1b", fontweight="semibold", y=0.96)

fig.text(0.5, 0.045,
         "NEMA 17 at left, Tr8x8 screw low into a 608 in the end rib, syringe offset "
         "%.0f mm above it, carriage bridging the two." % (S.SYR_H - S.SCREW_H),
         fontsize=8.3, color="#555", ha="center")
fig.text(0.5, 0.015,
         "Travel %.0f mm. The beat uses only 8.5 mm of it; the rest is priming headroom."
         % S.TRAVEL, fontsize=8.3, color="#555", ha="center")
fig.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.09, wspace=0.0)
fig.savefig(os.path.join(HERE, "syringe-drive.png"), facecolor="white")
print("wrote syringe-drive.png")


# The rib was printed for a guessed 2.5 mm flange and the real one is 2.0.
# Slack behind the flange is harmless, because the piston's reaction pushes
# the barrel forward into the rib and the straps hold it. A flange THICKER
# than the as-built guess is the opposite case: the barrel would not seat
# against the rib at all and the whole pulse would go into moving the syringe.
check("printed frame: the measured flange still seats against the rib",
      S.SYR_FLANGE_T <= S.FRAME_FLANGE_T,
      "rib placed for %.1f mm, flange measures %.1f mm, %.1f mm of axial "
      "slack taken up by the straps"
      % (S.FRAME_FLANGE_T, S.SYR_FLANGE_T, S.FRAME_FLANGE_T - S.SYR_FLANGE_T))


# ------------------------------------------------------- the T8 nut interface
# The nut bolts the screw to the carriage, so its mounting face carries every
# newton the piston makes, and the bolt circle is the one dimension that
# cannot be drawn loose: brass T8 flange nuts are 16 mm and POM ones are sold
# at 18, and at 16 against 18 the M3 centres land 1 mm apart radially, so the
# two sets merge into slots and the face is scrap.
#
# So the carriage no longer cuts them. It cuts a pocket sized to swallow the
# range, and the nut becomes its own drilling jig afterwards. That turns an
# unrecoverable gamble into four shallow pilot holes, which is why this gate
# now asks about the POCKET and not about the nut.
_nut = S.NUTS[S.NUT]
check("the carriage does not commit to a bolt circle it cannot know",
      not S.NUT_HOLES_CUT,
      "holes deferred, pocket is %.1f dia x %.1f deep with a %.1f bore. "
      "Mark through the nut on the lead screw, pilot 4 mm, drive M3 "
      "thread-formers" % (S.NUT_POCKET_D, S.NUT_POCKET_T, S.NUT_BORE_D))

_bs = S.NUTS["brass-std"]
check("the pocket swallows the nut we can actually name",
      S.NUT_POCKET_D > 22.0 and S.NUT_POCKET_T > _bs["flange_t"]
      and S.NUT_BORE_D > _bs["body_d"],
      "brass-std is %.1f flange / %.1f thick / %.1f body and the pocket is "
      "%.1f / %.1f / %.1f, so there is room above every one"
      % (22.0, _bs["flange_t"], _bs["body_d"],
         S.NUT_POCKET_D, S.NUT_POCKET_T, S.NUT_BORE_D))

check("the nut pocket clears the bearing bores",
      S.ROD_SPACING / 2 - S.NUT_POCKET_D / 2 - (S.LM_OD / 2 + 0.15) > 3.0,
      "%.1f mm of wall between the pocket and each LM8UU bore"
      % (S.ROD_SPACING / 2 - S.NUT_POCKET_D / 2 - (S.LM_OD / 2 + 0.15)))

# Lead is the one nut number the listing does state, and the only one the
# firmware depends on. A "T8" sold with a 2 mm lead instead of 8 would deliver
# a quarter of every commanded volume, and nothing on a scope would look wrong
# because the step train would be exactly as asked for.
check("ordered nut's lead matches what the firmware is scaled to",
      S.SCREW_LEAD == 8.0,
      "8 mm lead, 2 mm pitch, 4 start on the ordered part; 1600 microsteps "
      "per rev over %.0f mm is %.0f steps/mm"
      % (S.SCREW_LEAD, 1600.0 / S.SCREW_LEAD))

# These two only run once the nut is in hand. The gate above is what fails
# while they cannot run, so nothing passes by being unmeasurable.
if _nut["body_d"] is not None:
    check("nut body clears the carriage bore",
          _nut["body_d"] <= S.NUT_BODY_D + 2 * S.FIT,
          "body %.1f mm into a %.1f mm bore"
          % (_nut["body_d"], S.NUT_BODY_D + 2 * S.FIT))
if _nut["spring_od"] is not None:
    # The spring is what makes it anti-backlash, and it has to live somewhere.
    # Inside the carriage it needs the body bore; outside it eats travel.
    check("nut spring clears the carriage bore, or is outboard",
          _nut["spring_od"] <= S.NUT_BODY_D + 2 * S.FIT,
          "spring OD %.1f mm against a %.1f mm bore; if it fouls, the spring "
          "stack mounts on the motor side and costs that much travel"
          % (_nut["spring_od"], S.NUT_BODY_D + 2 * S.FIT))
if _nut["flange_t"] is not None:
    check("nut flange seats in its counterbore",
          _nut["flange_t"] <= S.NUT_FLANGE_T + S.FIT,
          "flange %.1f mm into a %.2f mm counterbore"
          % (_nut["flange_t"], S.NUT_FLANGE_T + S.FIT))

# Registered with atexit rather than written at the bottom of the file. This
# summary has now printed BEFORE later checks twice, because this file grows
# by appending and anything "at the end" stops being at the end the next time
# somebody adds a section. atexit cannot be outrun by an append.
import atexit


@atexit.register
def _summary():
    if fails:
        print("\n%d check(s) failed:" % len(fails))
        for f in fails:
            print("  - %s" % f)
    else:
        print("\nall checks passed")


# ------------------------------------------------------------ the material
# Every press and slip fit in this model rests on HOLE_SHRINK, and that is a
# property of the FILAMENT, not of the printer. The 0.24 mm was measured in
# PLA. ABS shrinks about 0.7 percent on cooling against PLA's 0.3, so it adds
# a term proportional to the hole on top of the fixed extrusion encroachment
# that dominated in PLA: roughly 0.06 mm more on a 15 mm LM8UU bore, which is
# a quarter of the whole PLA figure and lands on a SLIDING fit.
_m = S.MATERIALS[S.MATERIAL]
check("hole shrink is measured in the filament actually loaded",
      not S.MATERIAL_UNKNOWN,
      "%s is unmeasured. Reprint fit_coupon in it and measure the 608 "
      "pocket and both rod bores. Until then every fitted part is drawn "
      "against PLA's %.2f mm" % (S.MATERIAL, 0.24)
      if S.MATERIAL_UNKNOWN else
      "%s, fixed %.2f mm plus %.4f mm per mm of bore"
      % (S.MATERIAL, _m["fixed"], _m["per_mm"]))

# The frame is PLA and already on the bench. Parts printed in ABS have to
# mate with it, so the cross-material joints are the ones to watch: the
# collar sits in the frame's 16.0 mm saddle, and the carriage rides rods the
# frame holds. Those are clearances, which is the forgiving direction.
check("cross-material joints are clearances, not interference",
      S.SADDLE_BORE >= S.SYR_BARREL_D,
      "collar OD %.1f into a PLA saddle bored %.1f, zip-tied not pressed. "
      "An ABS collar printing small is loose, which the ties take up"
      % (S.SADDLE_BORE, S.SADDLE_BORE))

check("every material in the table is complete or deliberately blank",
      all(m["fixed"] is None or m["per_mm"] is not None
          for m in S.MATERIALS.values()),
      "%d materials listed, %d measured"
      % (len(S.MATERIALS),
         sum(1 for m in S.MATERIALS.values() if m["fixed"] is not None)))


# ------------------------------------------------- the frame is not reprinted
# Decided 2026-11-11. The PLA frame stays, so its geometry stopped being a
# design choice. ROD_SPACING is the dangerous one: the carriage's two LM8UU
# bores sit on it, and changing it while designing the carriage gives a part
# that verifies perfectly against the model and will not go on the rods.
_drift = S.frame_drift()
check("nothing has moved under the frame that is already printed",
      not _drift,
      "; ".join("%s was %s, model now says %s" % d for d in _drift)
      if _drift else
      "%d constants pinned to the %s frame"
      % (len(S.FRAME_AS_BUILT) - 1, S.FRAME_AS_BUILT["printed"]))

# PLA frame, ABS everything else. Worth a check because the two materials
# will not shrink alike and the joints have to be the forgiving direction.
check("the mixed-material joints all run the forgiving way",
      S.MATERIAL != S.FRAME_AS_BUILT["printed"].split(",")[0],
      "frame is %s, new parts are %s. The collar is zip-tied into the "
      "saddle rather than pressed, and the carriage rides steel rods, so "
      "nothing presses ABS into PLA"
      % (S.FRAME_AS_BUILT["printed"].split(",")[0], S.MATERIAL))


# --------------------------------------------------------------- the rods
# Nothing retains the rods but friction in the printed bores. The bore runs
# clean through both the motor plate and the rib, so there is no shoulder,
# no circlip and nowhere for a shaft collar: the rib's back face is 3 mm
# from the saddle and a collar is about ten.
_grip = S.WALL_T + S.RIB_T
check("the rods have enough printed bore to grip",
      _grip >= 2.0 * S.ROD_D,
      "%.0f mm of grip on an %.0f mm rod, %.0f in the motor plate and %.0f "
      "in the rib. The bore is line-to-line, so the coupon decides whether "
      "that is a press or a slip" % (_grip, S.ROD_D, S.WALL_T, S.RIB_T))

# I claimed on 2026-11-10 that the motor blocked forward travel and that
# this halved the problem. It does not. The rods sit at y = +/- 28 and a
# NEMA17 is 42.3 square, so the rod passes 6.85 mm OUTSIDE the motor body
# and sails right by it. Both directions were open the whole time, which
# makes the lock necessary rather than tidy.
_clear = S.ROD_SPACING / 2 - S.MOTOR_SQ / 2
check("the motor does NOT retain the rods, contrary to the old note",
      _clear > 0.0,
      "rod centre y=%.0f against a motor half width of %.2f, so the rod "
      "clears it by %.2f mm and the motor stops nothing"
      % (S.ROD_SPACING / 2, S.MOTOR_SQ / 2, _clear))

# What does retain them.
check("something actually fixes the rods in both directions",
      hasattr(S, "rod_lock"),
      "rod_lock() clamps the rod and bolts to the rib, so the rod is fixed "
      "to the frame. A plain collar would stop one direction only")

_free_rib = S.X_RIB - (S.X_CARR_MIN + S.TRAVEL + S.CARRIAGE_L)
check("a pair of plain collars would NOT have fitted",
      _free_rib < 10.0,
      "only %.0f mm of rod is free inboard of the rib once the carriage has "
      "swept, and a collar is about 10. That is why the lock bolts to the "
      "rib instead of just gripping the rod" % _free_rib)

check("the rod lock clears the barrel saddle",
      S.ROD_SPACING / 2 - S.LOCK_HALF > 13.0,
      "lock inner edge y=%.0f against a saddle that spans y +/- 13"
      % (S.ROD_SPACING / 2 - S.LOCK_HALF))

check("the rod lock bore is a clamp fit, not a press fit",
      0.08 <= (S.ROD_D + 0.15 + S.HOLE_SHRINK) - S.HOLE_SHRINK - S.ROD_D <= 0.30,
      "prints %.2f on an %.2f rod. It has to SLIDE on so the screw can do "
      "the holding, which is the opposite of the frame's bores"
      % (S.ROD_D + 0.15, S.ROD_D))


# ------------------------------------------- what the ABS coupon bought us
# Measured 2026-11-11. The two fits that had almost nothing in them, re-run
# against the real number rather than the estimate.
_sh = S.MATERIALS[S.MATERIAL]["fixed"]
_lm_clear = (S.LM_OD + 0.30) - _sh - S.LM_OD
check("the LM8UU still slides into an ABS carriage",
      _lm_clear >= 0.04,
      "bore prints %.2f on a %.2f bearing, %+.2f mm clearance. The estimate "
      "had this at 0.00 and the coupon says it is fine"
      % ((S.LM_OD + 0.30) - _sh, S.LM_OD, _lm_clear))

_grip = S.SYR_BARREL_D - ((S.SYR_BARREL_D - S.COLLAR_GRIP + S.HOLE_SHRINK) - _sh)
check("the collar still grips the barrel",
      0.05 <= _grip <= 0.30,
      "%.2f mm of interference, designed for %.2f. It is a split ring under "
      "zip ties, so this range is all usable" % (_grip, S.COLLAR_GRIP))


# ------------------------------------------------- the registry is the list
# rod_lock() existed, printed, rendered and passed its own checks while being
# absent from build(), so print_plate crashed and the BOM would have shipped
# a part nothing could slice. A function is not a part until the registry
# says so, and nothing was watching the gap between the two.
import print_plate as _PP
_built = set(S.build())
_oriented = set(n for n, _a, _c in _PP.ORIENT)
check("every part in build() can be oriented for printing",
      _oriented >= _built - {"fit_coupon"},
      "missing from print_plate.ORIENT: %s"
      % ", ".join(sorted(_built - {"fit_coupon"} - _oriented))
      if _built - {"fit_coupon"} - _oriented else
      "%d parts, all with a print orientation" % len(_oriented))
check("every part print_plate orients actually exists",
      _built >= _oriented,
      "in ORIENT but not in build(): %s"
      % ", ".join(sorted(_oriented - _built))
      if _oriented - _built else "no orphans")

# The same gap, one layer out: rod_lock was in build() and in ORIENT, and
# still missing from the 3-D model, which is the only place the students
# ever look. Being printable is not the same as being in the assembly.
import assembly as _AS
_assembled = set(n for n, _m, _c, _e, _t in _AS.parts())
_PRINTED_IN_ASSY = {"frame": "frame", "carriage": "carriage",
                    "saddle_cap": "saddle cap + ties", "collar":
                    "split collars x2", "rod_clamp": "rod clamp",
                    "rod_lock": "rod lock x2", "rod_stop": "rod stop x2"}
check("every printed part is in the 3-D assembly",
      set(_PRINTED_IN_ASSY) == _built - {"fit_coupon"},
      "missing from the assembly map: %s"
      % ", ".join(sorted(_built - {"fit_coupon"} - set(_PRINTED_IN_ASSY)))
      if _built - {"fit_coupon"} - set(_PRINTED_IN_ASSY) else
      "%d printed parts, all placed" % len(_PRINTED_IN_ASSY))
check("the assembly names match what it actually draws",
      set(_PRINTED_IN_ASSY.values()) <= _assembled,
      "named but not drawn: %s"
      % ", ".join(sorted(set(_PRINTED_IN_ASSY.values()) - _assembled))
      if set(_PRINTED_IN_ASSY.values()) - _assembled else
      "%d steps in the build, printed and bought" % len(_assembled))

# The rods have to reach the lock, or the lock clamps air.
check("the shafts in the assembly are as long as the BOM buys",
      abs(_AS.parts()[5][1].bounds[1][0] - (S.X_RIB_BACK + S.LOCK_T)) < 1e-6,
      "drawn to X=%.1f, and the BOM cuts them at %.0f mm"
      % (_AS.parts()[5][1].bounds[1][0], S.X_RIB_BACK + S.LOCK_T))

# ------------------------------------------- which way the lock is loaded
# Kevin asked whether the lock just travels with the rod. Half right, and
# the half that is right is the half I had not taken in compression.
#
#   rod creeps BACK toward the motor -> lock is driven into the rib's back
#       face. Compression on a printed wall. Nothing to fail.
#   rod creeps FORWARD toward the syringe -> lock lifts off that face and
#       hangs on two M3 in thread pullout. This is the real load path.
#
# The right answer would be a second lock outboard of the motor plate, so
# that direction is compression too. It does not fit: the lock spans y 17
# to 39 and the NEMA 17 body reaches y 21.15, so a same-shape lock would
# foul the motor by 4.15 mm. Worth knowing, not worth building, because the
# weak direction is still four orders of magnitude clear.
_eng = S.LOCK_SCREW_L - S.LOCK_T
check("the rib screws actually reach the rib",
      _eng >= 6.0,
      "M3 x %.0f spends %.0f mm crossing the lock and engages %.0f mm of "
      "rib. An x16 would engage 4" % (S.LOCK_SCREW_L, S.LOCK_T, _eng))
check("the rib screws do NOT come out the far side",
      _eng < S.RIB_T,
      "%.0f mm of thread in a %.0f mm rib, %.0f mm spare. Beyond the rib is "
      "the gap the carriage sweeps into, so breaking through is a crash"
      % (_eng, S.RIB_T, S.RIB_T - _eng))

# Pullout against the thing it is actually resisting. The drag that walks a
# rod is the bush sliding on it, not the piston load: the piston pushes the
# CARRIAGE along the rod, it does not push the rod.
_W = (S.build()["carriage"].volume / 1000.0 * 1.04 + 55.0) / 1000.0 * 9.81
_walk = 0.005 * (_W + 20.0)              # 20 N of misalignment preload, generous
_pull = 2 * (3.14159 * 3.0 * _eng * 0.6) * 25.0      # 2x M3 form in ABS
check("the weak direction still wins by a wide margin",
      _pull / _walk > 1000.0,
      "%.0f N of thread pullout against %.2f N of bush drag, a margin of "
      "%.0fx. The screws are not what to worry about here"
      % (_pull, _walk, _pull / _walk))

_motor_foul = S.MOTOR_SQ / 2 - (S.ROD_SPACING / 2 - S.LOCK_HALF)
check("a second lock at the motor end would NOT fit as drawn",
      _motor_foul > 0.0,
      "the lock reaches y=%.0f and the NEMA 17 body reaches y=%.2f, so it "
      "would foul the motor by %.2f mm. That is why forward is the pullout "
      "direction and not a second compression face"
      % (S.ROD_SPACING / 2 - S.LOCK_HALF, S.MOTOR_SQ / 2, _motor_foul))

# --------------------------------------- the forward stop, and what it costs
# The rib lock takes travel toward the motor in compression and travel toward
# the syringe in thread pullout. rod_stop() makes the second one compression
# too, by sitting inboard of the rib. The pair sandwich the rib.
check("the stop lands on solid rib face",
      S.ROD_SPACING / 2 - S.LOCK_HALF > S.BEAR_OD / 2 + 0.1,
      "stop inner edge y=%.0f against a 608 pocket reaching y %.1f, and the "
      "saddle cut does not start until z %.1f"
      % (S.ROD_SPACING / 2 - S.LOCK_HALF, S.BEAR_OD / 2 + 0.1,
         S.SYR_H - S.SADDLE_BORE / 2 - S.FIT))

_lost = S.STOP_T - (S.X_RIB - S.X_CARR_FRONT)
check("the stop eats forward travel, and the amount is affordable",
      0.0 < _lost <= 6.0,
      "%.0f mm of the %.0f mm stop sits in the gap that already existed, so "
      "the sweep loses %.0f mm = %.2f mL. The beat is %.2f mL and there is "
      "%.1f mL of priming headroom, so this is %.0f%% of the slack"
      % (S.X_RIB - S.X_CARR_FRONT, S.STOP_T, _lost,
         _lost * S.BORE_A / 1000.0, S.BEAT_ML,
         (S.TRAVEL - S.BEAT_MM) * S.BORE_A / 1000.0,
         100.0 * _lost / (S.TRAVEL - S.BEAT_MM)))

check("the carriage can no longer reach the rib, which is the point",
      S.X_STOP < S.X_CARR_FRONT,
      "the carriage used to sweep to X=%.0f with the rib at %.0f. The stop "
      "now occupies X %.0f to %.0f, so X=%.0f is the forward limit and a "
      "crash lands on the rod and the rib, not on the carriage face"
      % (S.X_CARR_FRONT, S.X_RIB, S.X_STOP, S.X_RIB, S.X_STOP))

check("the stop is thick enough for its own pinch screw",
      S.STOP_T - S.M3_TAP >= 4.0,
      "%.1f mm body around a %.1f mm tapped hole leaves %.1f mm of wall each "
      "side. A 4 mm stop, which is all the old gap allowed, would leave %.1f"
      % (S.STOP_T, S.M3_TAP, (S.STOP_T - S.M3_TAP) / 2.0,
         (4.0 - S.M3_TAP) / 2.0))

check("the rib is sandwiched, so the rod is pinned both ways in compression",
      abs(S.X_RIB_BACK - S.X_RIB - S.RIB_T) < 1e-9,
      "stop on the front face at X=%.0f, lock on the back face at X=%.0f, "
      "%.0f mm of printed wall between them and the rod clamped to both"
      % (S.X_RIB, S.X_RIB_BACK, S.RIB_T))

# What the carriage actually transmits into a rod, which is the whole premise.
_F_piston = 20.0                        # seal stiction dominates; 120 mmHg is 1.9 N
_axial = 0.005 * (_W + 20.0)
check("a ball bush does not transmit the piston load into the rod",
      _axial < _F_piston / 50.0,
      "the piston's %.0f N goes plunger -> carriage -> nut -> screw -> 608. "
      "What reaches the rod is mu times the bush's radial load, %.2f N, "
      "which is %.0fx smaller. Even a fully seized bush at %.0f N is %.0fx "
      "inside the stop's grip"
      % (_F_piston, _axial, _F_piston / _axial, _F_piston, 300.0 / _F_piston))

# ------------------------------------------- the two firmware files agree
# P1 and P2 go on the Pico that is ALREADY in the rig, because it is the
# only board where the pressure samples and the step counter share a clock,
# and telling a bad P2 from a bad piston is the whole reason P1 exists. That
# only works if the sensor pins and the stepper pins are disjoint, and those
# two facts live in two files that nothing was comparing.
import re as _re
import io as _io
_cfg = _io.open("pico/config.py", encoding="utf-8").read()
_prs = _io.open("pico/pressure.py", encoding="utf-8").read()
_step = [int(n) for n in _re.search(
    r"STEP_PIN, DIR_PIN, EN_PIN = ([\d, ]+)", _cfg).group(1).split(",")]
_sense = [int(n) for n in _re.search(
    r"P1_PIN, P2_PIN = ([\d, ]+)", _prs).group(1).split(",")]
check("the sensor pins do not collide with the stepper",
      not (set(_step) & set(_sense)),
      "stepper on GP%s, sensors on GP%s. One Pico runs both, so the pressure "
      "trace and the step count share a clock"
      % ("/".join(map(str, _step)), "/".join(map(str, _sense))))
check("the sensor pins are actually ADC pins",
      all(26 <= p <= 28 for p in _sense),
      "GP%s. Only GP26, 27 and 28 reach the RP2350's ADC, so a plausible "
      "looking number on any other pin reads nothing"
      % "/".join(map(str, _sense)))
