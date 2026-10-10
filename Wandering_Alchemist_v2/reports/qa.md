# QA — Phase 6.5A

- Blender MCP connected; Blender 5.2.2 LTS protocol 13.
- Source: Wandering_Alchemist_Phase6A_Wood.blend.
- Preserved backup: Blender/Backups/Before_Phase6_5_20261010_152531.blend.
- Downloaded nine maps via official public API manifest URLs: HTTP 200, exact file size, MD5 matches, Pillow decoded all images. Oak/metal 2048²; linen 2048×2052 (native source aspect).
- Base color is sRGB; Roughness and OpenGL Normal are Non-Color. Normals routed through Normal Map nodes.
- Dedicated scene PHASE65A_MATERIAL_TEST rendered in Cycles, neutral light.
- Main scene before/after rendered in Cycles with identical camera, white lights, sample count and resolution.
- One glass shell has actual interior wall and bottom thickness; liquid is separate and top surface is closed. Visual inspection required; no full export/manifold audit claimed.
- No whole-asset integration, export, mobile/game-ready or commercial-ready claim.
- High-detail interior, lanterns, embroidery and remaining potion collection are pending later passes.

## Fabric macro correction

Initial repeat=5 and normal strength=0.22 looked overly smooth. The final trial uses repeat=1, normal strength=0.85 and sheen=0.25. The weave is deliberately coarser for stylized visual readability, not calibrated physical scan scale. linen_macro.png was inspected at 1000×800, 96 samples, denoising off. Board and neutral hero were rerendered after the correction. Material sample board uses 64 samples.
