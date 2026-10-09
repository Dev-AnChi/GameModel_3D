# Catmosphere — Texture Sources, Phase 3.7

Nguồn thực tế đã được tải qua Blender MCP, không phải texture giả lập. Toàn bộ ảnh được pack trong file Material Master; thư viện texture rock/wood riêng cũng được giữ trong `Catmosphere_CC0_Material_Library.blend`.

| Tài nguyên | Tác giả | Độ phân giải | Giấy phép | Sử dụng thực tế |
|---|---|---|---|---|
| [Rock Face 03](https://polyhaven.com/a/rock_face_03) | Dario Barresi, Rico Cilliers | 2K, 2048 × 2048; scan rộng 2.7 m | CC0 | Diffuse lấy chi tiết khoáng để phối với cream-gray grading; Rough điều khiển roughness; Displacement tạo bump normal. Box projection, không displacement mesh. |
| [Oak Wood Planks](https://polyhaven.com/a/oak_wood_planks) | Dimitrios Savva | 2K, 2048 × 2048; scan rộng 1.2 m | CC0 | Rough phối với roughness theo vân. Color, directional grain, edge wear, normal và lệch pha từng tấm là procedural để giữ stylized honey wood và tránh thêm đường nối ván giả lên geometry có sẵn. |
| [Monochrome Studio 03](https://polyhaven.com/a/monochrome_studio_03) | Grzegorz Wronkowski | HDR 1K | CC0 | Neutral lookdev world trong ba scene prototype và scene M37_Neutral_Map_TextureCheck, strength 0.3. Beauty scene giữ rig Sun và world của Organic Master. |

Giấy phép được đối chiếu ở [Poly Haven Asset License](https://polyhaven.com/license). Poly Haven công bố các asset tải về theo CC0. Trang web, logo và ảnh preview không được coi là asset CC0; không dùng chúng làm texture.

## Color space và packing

Diffuse: sRGB. Rough, Displacement, nor_gl: Non-Color. HDRI: Linear Rec.709. Chín image datablock đã được pack, gồm hai bộ bốn maps và một HDRI; `reports/material_validation.json` kiểm chứng resolution, packing và color space.

`nor_gl` của hai bộ scan đã tải/pack nhưng không được cắm vào shader box-projected: tangent-space normal cần tiếp tuyến UV hoặc normal reprojection đúng. Đá dùng scan height qua Bump để tạo normal trong hệ mapping hiện có. Oak Diffuse/Displacement/nor_gl được giữ trong thư viện nhưng không sử dụng ở shader rollout. Không tuyên bố mọi map đã được dùng. Không có AO map riêng được tải; không nhân AO thiếu kiểm chứng lên albedo. Bóng/cavity hiện đến từ ánh sáng và Eevee.

## Vật liệu procedural / hybrid đã tạo

- Rock: hybrid CC0 scan + layered mineral tone, distorted strata, sparse fine fissures, moss mask theo normal hướng lên và noise. Height tạo normal; không tăng số lượng mesh.
- Wood/bark: directional 3D grain, honey palette, tint và phase khác giữa object, subtle edge wear từ smooth/face normal, grain bump, roughness phối CC0. Local mapping bù physical object scale và chọn X/Y/Z theo chiều dài.
- Fabric/rope/seams: dye variation, fine crossed weave pha irregular fibers, micro-bump, sheen và roughness mềm. Không dùng cloth texture tải ngoài.
- Leaves/flowers: botanical root-to-tip palette, roughness theo từng loại, fine bump, subsurface nhẹ. Đây là Eevee subsurface approximation, không leaf transmission shader vật lý đầy đủ.
- Ground/soil/terracotta/ceramics/books: noise màu và roughness vừa phải, micro-bump; ceramic có coat. Không có texture ngoài cho các nhóm này.
- Metal: bronze dùng metallic 0.8, variation roughness và fine surface response.
- Glass: greenhouse giữ thiết lập transparency/render method từ nguồn, IOR 1.45, transmission/roughness phù hợp hơn. Amber lamp glass phát sáng giữ nguyên graph nguồn.
- Water: turquoise grade, IOR 1.333, roughness và ripple normal; depth là proxy/gradient nghệ thuật. Ba animated Organic flow graphs được copy trọn để giữ nguyên driver chuyển động; không có fluid simulation hoặc scene-depth absorption thật.
- Sky/cloud/backdrop và emission lamps: giữ material Organic cho beauty; được ghi nhãn Blender Beauty Only.

## Godot

Hybrid/procedural surface materials cần bake UV maps trước khi giữ đầy đủ bề mặt qua glTF. Animated water cần shader Godot tương đương. Texture pack trong Blender không tự động làm procedural graph tương thích glTF. Phase này không bake hoặc xuất GLB mới; danh sách nhãn từng material nằm trong `material_audit.md` và `material_validation.json`.
