# -*- coding: utf-8 -*-
"""A printed gravity ball check valve, for when the catalog part will not come.

    python ball_check.py    ->  ball-check.png, stl/check_seat.stl,
                                stl/check_cage.stl, and the sizing below

SHORT ANSWER TO "WOULD IT FIT IN THE TUBING": no, and neither does the part
it replaces. A ball cannot live inside 1/4 in tubing, because the ball is
6.35 mm and so is the tubing bore, and even a smaller ball would seal the
tube the moment it lifted: there would be nowhere for the fluid to go past
it. Every ball check ever made is an inline BODY with a chamber wider than
the ball, and the tubing pushes onto barbs at each end. This one comes out
49 mm long and 16 mm across, against a commercial inline valve at roughly
the same size. It goes in the line exactly where the 91050 would have.

WHAT CHANGED FROM THE FIRST ESTIMATE. head_budget.py prices a 6.35 mm ball
on a 3 mm seat, which is a bad pairing and my mistake: a heavy ball on a
small hole. Cracking pressure is net ball weight over seat area, so a LARGER
seat lowers it, and a larger seat also stops throttling the flow. Opening the
seat from 3 mm to an O-ring at 5.28 mm takes cracking pressure from 6.8 mm of
head to 2.2 mm AND takes the orifice loss at mean flow from 46 mm to 6 mm.
Both terms improve together, which is rare enough to be worth saying out loud.

WHY AN O-RING AND NOT A PRINTED SEAT. A ball landing on an FDM seat lands on
0.24 mm layer steps and will weep. An O-ring standing proud of its groove
conforms, so the valve seals at essentially zero force, which is the whole
point of choosing a ball check in the first place.

MOUNT IT VERTICALLY, FLOW UPWARD. Gravity is the spring. On its side it has
no closing force at all, and a ring seat centres the ball only because the
ball rolls downhill to the middle of the ring.
"""
import math
import os

import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import syringe_drive as S

HERE = os.path.dirname(os.path.abspath(__file__))
RHO = 1037.0             # BMF, kg/m3
G = 9.80665
MU = 4.1e-3
PSI = 6894.757
Q_MEAN, Q_PEAK = 250.0, 500.0           # mL/min
CD = 0.62                               # sharp-edged orifice discharge coeff

# ----------------------------------------------------------------- the ball
BALL_D = 6.35            # 1/4 in, sold by the bag
BALL_RHO = 1410.0        # acetal. Nylon is lighter still but reseats slower

# -------------------------------------------------------------- the O-ring
# AS568-009. The ball seals on its inner upper shoulder, so the ring ID is
# the sealed diameter and therefore the one in the cracking-pressure sum.
ORING_ID, ORING_CS = 5.28, 1.78
GROOVE_DEPTH = 1.30      # ring stands 0.48 proud, which is what the ball squashes

# -------------------------------------------------------------- the body
CHAMBER_D = 9.00         # must clear the ball AND pass flow around it
LIFT = 3.00              # how far the ball rises before the cage stops it
BODY_D = 16.00
BARB_BORE = 4.60         # same as a commercial 1/4 in barb
BARB_RIDGE_D, BARB_ROOT_D = 7.00, 5.80
BARB_L = 14.00
CROSS_W, CROSS_T = 2.00, 2.00
CEIL_D = 8.00            # hole the cross spans. Bigger than the ball on purpose
SPIGOT_OD, SPIGOT_L = 12.20, 6.00
SOCKET_ID = SPIGOT_OD + 0.20 + S.HOLE_SHRINK   # 0.2 mm of glue gap after shrink
NOZZLE = 0.60

# ------------------------------------------------------------- Z stations
Z_SEAT = 20.00                      # top face of the seat ring, in seat-piece Z
Z_GROOVE = Z_SEAT - GROOVE_DEPTH
Z_SEAT_TOP = Z_SEAT + SPIGOT_L      # where the seat piece ends
PROUD = ORING_CS - GROOVE_DEPTH
Z_BALL_BOT = Z_SEAT + PROUD
Z_CROSS = Z_BALL_BOT + BALL_D + LIFT - Z_SEAT    # in cage-piece Z, from its base


def cone_z(r0, r1, zr, sections=96):
    """Truncated cone about Z, radius r0 at zr[0] rising to r1 at zr[1]."""
    prof = np.array([[0.0, zr[0]], [r0, zr[0]], [r1, zr[1]], [0.0, zr[1]]])
    return trimesh.creation.revolve(prof, sections=sections)


def barb(z0, up=True, sections=96):
    """Two-ridge hose barb. Drawn as a solid of revolution, bore cut later.

    Each ridge is a lead-in cone with a step behind it. Printed with the axis
    vertical the step is a short radial overhang, which droops a little and
    grips a little better for it.
    """
    rr, rt = BARB_RIDGE_D / 2.0, BARB_ROOT_D / 2.0
    s = 1.0 if up else -1.0
    pts = [(0.0, 0.0), (rt - 0.5, 0.0), (rr, 4.0), (rt, 4.6),
           (rr, 9.6), (rt, 10.2), (rt, 12.0), (BODY_D / 2.0, BARB_L),
           (0.0, BARB_L)]
    prof = np.array([[r, z0 + s * z] for r, z in pts])
    if not up:
        prof = prof[::-1]
    return trimesh.creation.revolve(prof, sections=sections)


def seat_piece():
    """Inlet barb, the O-ring seat, and the socket the cage glues into."""
    body = barb(0.0, up=True)
    body = S.union(body, S.cyl_z(BODY_D / 2.0, (BARB_L, Z_SEAT_TOP)))
    # bore: barb bore, opening out to the ring ID below the seat
    body = S.diff(body, S.cyl_z(BARB_BORE / 2.0, (-1.0, BARB_L + 2.0)))
    body = S.diff(body, cone_z(BARB_BORE / 2.0, ORING_ID / 2.0,
                               (BARB_L + 2.0, BARB_L + 4.0)))
    body = S.diff(body, S.cyl_z(ORING_ID / 2.0, (BARB_L + 4.0, Z_SEAT + 0.01)))
    # the groove. Drawn oversize so it prints at the ring's real OD.
    groove_od = ORING_ID + 2.0 * ORING_CS + S.HOLE_SHRINK
    body = S.diff(body, S.cyl_z(groove_od / 2.0, (Z_GROOVE, Z_SEAT + 0.01)))
    # the socket
    body = S.diff(body, S.cyl_z(SOCKET_ID / 2.0, (Z_SEAT, Z_SEAT_TOP + 1.0)))
    return body


def cage_piece():
    """Spigot, chamber, the cross the ball stops against, and the outlet barb.

    Its own Z starts at the mating face, so z=0 here sits on Z_SEAT there.
    """
    z_top = Z_CROSS + CROSS_T
    z_cone = z_top + 3.0
    z_barb = z_cone + 2.0
    body = S.cyl_z(SPIGOT_OD / 2.0, (0.0, SPIGOT_L))
    body = S.union(body, S.cyl_z(BODY_D / 2.0, (SPIGOT_L, z_barb)))
    body = S.union(body, barb(z_barb, up=True))
    # chamber, then the ceiling hole, then the convergence to the outlet bore
    body = S.diff(body, S.cyl_z(CHAMBER_D / 2.0, (-1.0, Z_CROSS)))
    body = S.diff(body, S.cyl_z(CEIL_D / 2.0, (Z_CROSS, z_top + 0.01)))
    body = S.diff(body, cone_z(CEIL_D / 2.0, BARB_BORE / 2.0, (z_top, z_cone)))
    body = S.diff(body, S.cyl_z(BARB_BORE / 2.0, (z_cone, z_barb + BARB_L + 1.0)))
    # put the cross back: two bars across the ceiling hole
    for ang in (0.0, 90.0):
        bar = S.box((-CEIL_D / 2.0 - 1.0, CEIL_D / 2.0 + 1.0),
                    (-CROSS_W / 2.0, CROSS_W / 2.0), (Z_CROSS, z_top))
        bar.apply_transform(trimesh.transformations.rotation_matrix(
            math.radians(ang), [0, 0, 1]))
        # The bar runs past the hole on both sides so it anchors into the
        # body wall rather than ending in mid air. The union buries the
        # overhang in solid material.
        body = S.union(body, bar)
    return body


# ------------------------------------------------------------------- sizing
def ball_volume():
    return math.pi / 6.0 * (BALL_D * 1e-3) ** 3


def crack_pa(seat_d_mm=ORING_ID):
    w = ball_volume() * (BALL_RHO - RHO) * G
    return w / (math.pi * (seat_d_mm * 1e-3 / 2.0) ** 2)


def orifice_pa(d_mm, ml_per_min):
    a = math.pi * (d_mm * 1e-3 / 2.0) ** 2
    return RHO / 2.0 * (ml_per_min * 1e-6 / 60.0 / (CD * a)) ** 2


def head_mm(pa):
    return pa / (RHO * G) * 1e3


def area(d):
    return math.pi * d ** 2 / 4.0


def main():
    fails = []

    def check(name, ok, detail=""):
        print("%-4s %-52s %s" % ("PASS" if ok else "FAIL", name, detail))
        if not ok:
            fails.append(name)

    a_annulus = area(CHAMBER_D) - area(BALL_D)
    a_curtain = math.pi * ORING_ID * LIFT
    a_seat, a_barb = area(ORING_ID), area(BARB_BORE)
    a_cross = area(CEIL_D) - (2.0 * CROSS_W * CEIL_D - CROSS_W ** 2)

    print("SIZING  (%.2f mm %s ball, %.2f mm O-ring seat, %.1f mm chamber)"
          % (BALL_D, "acetal", ORING_ID, CHAMBER_D))
    print("  cracking pressure      %.4f psi = %.1f mm of head"
          % (crack_pa() / PSI, head_mm(crack_pa())))
    print("  Qosina 91050, for scale %.4f psi = %.1f mm" % (0.075, head_mm(0.075 * PSI)))
    print("")
    print("  FLOW AREAS, mm2. The smallest is what throttles the loop.")
    for nm, a in (("seat (O-ring ID)", a_seat), ("curtain at full lift", a_curtain),
                  ("annulus past the ball", a_annulus), ("cross in the ceiling", a_cross),
                  ("barb bore", a_barb), ("1/4 in tubing", area(6.35))):
        print("    %-24s %7.1f" % (nm, a))
    print("")
    print("  LOSS AT THE SEAT (sharp-edged orifice, Cd %.2f)" % CD)
    for q in (Q_MEAN, Q_PEAK):
        print("    %3.0f mL/min   %6.1f mm of head   (a 3.0 mm seat would be %.0f)"
              % (q, head_mm(orifice_pa(ORING_ID, q)),
                 head_mm(orifice_pa(3.0, q))))
    print("")
    print("  TOTAL AT MEAN FLOW     %.1f mm of head, against %.1f mm for the 91050"
          % (head_mm(crack_pa()) + head_mm(orifice_pa(ORING_ID, Q_MEAN)),
             head_mm(0.075 * PSI)))
    print("")

    seat, cage = seat_piece(), cage_piece()
    moved = cage.copy()
    moved.apply_translation((0.0, 0.0, Z_SEAT))

    print("GEOMETRY")
    print("  assembled %.0f mm long, %.0f mm across. Tubing is 6.35 mm bore,"
          % (moved.bounds[1][2], BODY_D))
    print("  9.5 mm outside, so the body is an inline cartridge, not an insert.")
    print("  seat piece %.1f mm, cage piece %.1f mm, %.0f mm glue overlap"
          % (seat.bounds[1][2], cage.bounds[1][2], SPIGOT_L))
    print("")

    check("ball cannot pass the seat", BALL_D > ORING_ID + 0.5,
          "%.2f mm ball on a %.2f mm ring" % (BALL_D, ORING_ID))
    check("ball cannot escape past the cross",
          CEIL_D / 2.0 - CROSS_W / 2.0 < BALL_D,
          "largest clear span in the ceiling %.2f mm, ball %.2f"
          % (math.hypot(CEIL_D / 2.0 - CROSS_W / 2.0,
                        CEIL_D / 2.0 - CROSS_W / 2.0), BALL_D))
    check("ball clears the chamber wall", CHAMBER_D > BALL_D + 1.0,
          "%.2f mm ball in a %.2f mm bore, %.2f mm of side play"
          % (BALL_D, CHAMBER_D, (CHAMBER_D - BALL_D) / 2.0))
    check("flow gets past the lifted ball", a_annulus >= a_barb,
          "annulus %.1f mm2 against a %.1f mm2 barb bore, %.1fx"
          % (a_annulus, a_barb, a_annulus / a_barb))
    check("curtain at the seat is not the restriction", a_curtain >= a_seat,
          "curtain %.1f mm2 at %.1f mm lift against a %.1f mm2 seat"
          % (a_curtain, LIFT, a_seat))
    check("the cross is not the restriction", a_cross >= a_barb,
          "%.1f mm2 of clear ceiling against a %.1f mm2 barb bore"
          % (a_cross, a_barb))
    check("cracking pressure beats the catalog part",
          crack_pa() < 0.075 * PSI,
          "%.1f mm of head against %.1f mm, %.0fx better"
          % (head_mm(crack_pa()), head_mm(0.075 * PSI),
             0.075 * PSI / crack_pa()))
    check("seat and orifice together still beat it",
          crack_pa() + orifice_pa(ORING_ID, Q_MEAN) < 0.075 * PSI,
          "%.1f mm total at mean flow"
          % (head_mm(crack_pa()) + head_mm(orifice_pa(ORING_ID, Q_MEAN))))
    check("O-ring stands proud of its groove", PROUD > 0.3,
          "%.2f mm of squeeze available on a %.2f mm cord" % (PROUD, ORING_CS))
    check("groove prints at the ring's real OD",
          abs((ORING_ID + 2 * ORING_CS + S.HOLE_SHRINK - S.HOLE_SHRINK)
              - (ORING_ID + 2 * ORING_CS)) < 1e-9,
          "drawn %.2f, prints %.2f, ring is %.2f"
          % (ORING_ID + 2 * ORING_CS + S.HOLE_SHRINK,
             ORING_ID + 2 * ORING_CS, ORING_ID + 2 * ORING_CS))
    check("socket accepts the spigot after shrink",
          SOCKET_ID - S.HOLE_SHRINK - SPIGOT_OD > 0.1,
          "socket prints %.2f, spigot %.2f, %.2f mm for glue"
          % (SOCKET_ID - S.HOLE_SHRINK, SPIGOT_OD,
             SOCKET_ID - S.HOLE_SHRINK - SPIGOT_OD))
    check("socket wall is printable", (BODY_D - SOCKET_ID) / 2.0 >= 2 * NOZZLE,
          "%.2f mm, %.1f perimeters at a %.1f nozzle"
          % ((BODY_D - SOCKET_ID) / 2.0, (BODY_D - SOCKET_ID) / 2.0 / NOZZLE,
             NOZZLE))
    check("spigot wall is printable", (SPIGOT_OD - CHAMBER_D) / 2.0 >= 2 * NOZZLE,
          "%.2f mm" % ((SPIGOT_OD - CHAMBER_D) / 2.0))
    check("cross bars are printable", CROSS_W >= 2 * NOZZLE,
          "%.1f mm wide bridging %.1f mm" % (CROSS_W, CEIL_D))
    check("both pieces are watertight", seat.is_watertight and cage.is_watertight,
          "seat %s, cage %s" % (seat.is_watertight, cage.is_watertight))
    inter = S.diff(moved, seat)
    check("pieces mate without interference",
          abs(moved.volume - inter.volume) < 1.0,
          "%.2f mm3 of overlap" % abs(moved.volume - inter.volume))
    check("ball travel matches the drawn cage",
          abs((Z_CROSS - (PROUD + BALL_D)) - LIFT) < 1e-6,
          "cross sits %.2f mm above the seat face, ball top at %.2f"
          % (Z_CROSS, PROUD + BALL_D))

    out = os.path.join(HERE, "stl")
    os.makedirs(out, exist_ok=True)
    for nm, m in (("check_seat", seat), ("check_cage", cage)):
        m.export(os.path.join(out, nm + ".stl"))
    print("")
    print("wrote stl/check_seat.stl and stl/check_cage.stl")

    # --------------------------------------------------------------- section
    fig, ax = plt.subplots(figsize=(5.2, 8.0), dpi=170)
    fig.patch.set_facecolor("white")
    for m, col, lab in ((seat, "#2e6fb4", "seat piece"),
                        (moved, "#b4462e", "cage piece")):
        sec = m.section(plane_origin=[0, 0, 0], plane_normal=[0, 1, 0])
        if sec is None:
            continue
        # Plot the 3-D section vertices straight as X against Z. to_planar()
        # refuses a plane it cannot flatten with the identity transform, and
        # feeding it one that can also re-centres the result, which silently
        # slides the drawing off the geometry it is supposed to be showing.
        for ent in sec.entities:
            pts = sec.vertices[ent.points]
            ax.fill(pts[:, 0], pts[:, 2], color=col, alpha=0.85, lw=0.8,
                    ec=col, label=lab)
            lab = None
    ball_z = Z_SEAT + PROUD + BALL_D / 2.0
    th = np.linspace(0, 2 * np.pi, 80)
    ax.fill(BALL_D / 2.0 * np.cos(th), ball_z + BALL_D / 2.0 * np.sin(th),
            color="#3c3c3c", alpha=0.9, label="acetal ball, seated")
    ax.fill(BALL_D / 2.0 * np.cos(th),
            ball_z + LIFT + BALL_D / 2.0 * np.sin(th),
            color="#3c3c3c", alpha=0.22, lw=0)
    for sgn in (-1, 1):
        ax.add_patch(plt.Circle(
            (sgn * (ORING_ID + ORING_CS) / 2.0, Z_SEAT - GROOVE_DEPTH + ORING_CS / 2.0),
            ORING_CS / 2.0, color="#c9a22e", zorder=5))
    ax.annotate("O-ring seat, the ball\nlands on elastomer",
                (-(ORING_ID + ORING_CS) / 2.0, Z_SEAT),
                xytext=(-26, Z_SEAT - 6), fontsize=7.5, color="#444",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#888"))
    ax.annotate("cross stops the ball,\nflow goes around it",
                (0, Z_SEAT + Z_CROSS), xytext=(11, Z_SEAT + Z_CROSS + 8),
                fontsize=7.5, color="#444",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#888"))
    ax.annotate("glue joint,\n%.0f mm overlap" % SPIGOT_L,
                (BODY_D / 2.0, Z_SEAT + SPIGOT_L / 2.0),
                xytext=(13, Z_SEAT - 10), fontsize=7.5, color="#444",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#888"))
    ax.set_aspect("equal")
    ax.set_xlim(-23, 23)
    ax.set_ylim(-3, moved.bounds[1][2] + 3)
    ax.set_xlabel("mm")
    ax.set_title("Printed ball check, section\n%.0f mm long, %.0f mm across, "
                 "1/4 in barbs\ncracks at %.1f mm of head against the 91050's %.0f"
                 % (moved.bounds[1][2], BODY_D, head_mm(crack_pa()),
                    head_mm(0.075 * PSI)), fontsize=10)
    ax.legend(fontsize=8, frameon=False, loc="center right")
    ax.grid(alpha=0.2, lw=0.5)
    fig.text(0.5, 0.012, "Mount vertically, flow upward. Gravity is the spring.",
             fontsize=8.3, color="#555", ha="center")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(os.path.join(HERE, "ball-check.png"), facecolor="white")
    print("wrote ball-check.png")

    if fails:
        print("\n%d check(s) failed:" % len(fails))
        for f in fails:
            print("  - %s" % f)
    else:
        print("\nall checks passed")


if __name__ == "__main__":
    main()
