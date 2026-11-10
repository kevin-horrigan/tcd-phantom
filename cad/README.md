# Phantom block model, rev A

Parametric solid model of the Group 1 phantom block, built to K. Horrigan's 2026-10-30 sizing: 60 mm ear to eye, 40 mm tall, 100 mm deep, with the 60 mm face as the temporal window, slightly rounded, and the skull window sliding in and out of it.

```
python phantom_block.py     # writes stl/ and prints the build report
python verify.py            # fit, clearance and assembly checks
python drawing.py           # dimensioned sheet, png + svg
python iso.py               # shaded isometric, assembled and exploded
```

Needs `numpy`, `trimesh`, `manifold3d`, `matplotlib`. Everything is driven by the constants at the top of `phantom_block.py`, so changing a number and re-running regenerates the STL, the checks and the drawings together.

## Coordinates

Origin at the crown of the window face, mid height. `+x` anterior, ear to eye. `+y` medial, into the head, which is also the beam axis. `+z` superior.

## What the model decides, and why

These are my choices filling in what the sizing did not specify. Each is a parameter, so any of them can be changed in one line.

**The window face is a vertical-axis cylinder, R80.** That is a temple-like curvature that falls back 5.84 mm at the ear and eye edges and 3.08 mm at the pocket edges. It gives the probe something to rock on for the insertion-loss-versus-angle sweep, which is acceptance criterion 6 on the materials team's list. The 100 mm depth is measured crown to back, so the block is 94.2 mm deep at its edges.

**The plate slides vertically, down from the top face.** This follows from the curved face. A plate that slid along the 60 mm direction would have to travel around the arc, which makes the pocket a curved sweep and the plate something that cannot be cast between two parallel mold faces. Sliding along the vertical axis is pure translation of a constant cross-section, so the plate stays a simple part and the pocket stays a straight channel. The plate bottoms out on a 4 mm seat, so it registers at a repeatable depth every time.

**The pocket floor is concentric with the face, R70.** A flat floor under a curved face would make the plate 10 mm thick at the center and 13.1 mm at the edges. Since plate thickness is the variable the whole window set exists to study, the floor has to follow the face. The plate is then a uniform 10 mm arc shell, verified uniform to 0.006 mm in `verify.py`.

**Every plate has the same 10 mm envelope.** The bone analog of thickness t sits on the probe side and the rest is backed with the brain formulation. The window face and the probe-to-vessel distance therefore do not move when the plate is swapped, so an insertion loss difference between two plates is attributable to the bone layer rather than to a change in geometry. The alternative, plates of differing thickness, moves the vessel depth by up to 8 mm across the set.

**The lumen runs bottom to top at 30 degrees off the beam axis**, in the x = 0 plane, 55 mm deep at mid height. Three things follow:

- 30 degrees rather than Soloukey's 25. The block is only 40 mm tall, so the angle and the end clearances trade directly against each other. At 25 degrees the inlet ends up 2 mm behind the pocket floor, which is not enough material to anchor a connector. 30 degrees puts both ends 10 mm clear. The cost is a Doppler cosine of 0.866 instead of 0.906.
- 23 mm of lumen lies between 45 and 65 mm depth, which is both the clinical M1 insonation depth and, near enough, the 22 to 27 mm length of the real M1 segment.
- Inlet at the bottom, outlet at the top, so the loop fills upward and gas sweeps out rather than collecting. The interface control document asks for exactly this.

**15 mm of buried connector length is reserved at each end.** The nearest free surface to a connector tip at that depth is 7.5 mm.

## Open items this model does not settle

- **The pocket has to be wetted.** Any air film between plate and floor is a total reflector at 2 MHz. Gel the pocket before the plate goes in, or load it submerged. There is no geometry in the model that enforces this.
- **Plate retention.** Gravity and the seat hold the plate down, nothing holds it in. A clip, a strap or a cover plate is a build detail, not modeled.
- **Scalp layer.** Not modeled. It can be a pad over the window face or a second shallow pocket, and it needs a decision before the mold is cut.
- **The connector itself.** Interface control document specs 7 and 8 are still open and they gate the mold. The model reserves the burial length but assumes nothing about the part.
- **Mold, not block.** This is the finished part. The mold is its inverse plus draft, vents and a mandrel fixture, and it has to survive 130 C.

## Output

`stl/block.stl` is the cast part. `stl/plate_*_bone.stl` and `stl/plate_*_backing.stl` are the window set, two solids per plate. `stl/lumen_mandrel.stl` is the rod that forms the wall-less channel, drawn with stub length past both faces.
