# Catmosphere — Material Audit Phase 3.7

Nguồn: Catmosphere_Organic_Master.blend, được người dùng chọn rõ trong chat. Blender 5.2.2 LTS, Eevee, addon 1.8/protocol 13.
Bản gốc được giữ nguyên; backup live scene: Catmosphere_Organic_PreMaterial_20261009.blend. Bản World Detailed mở lúc đầu được lưu riêng: Catmosphere_PreMaterial_20261009.blend.

Audit nguồn: 57 material được tham chiếu (bao gồm object cũ đang ẩn), 3915 object. 30 màu hằng, 56 không có roughness thay đổi trên bề mặt, 30 thiếu normal/bump. Wood có roughness khác nhau giữa object nhưng đồng đều trên mỗi object.

## Phân loại và lỗi ban đầu

| Material | Nhóm | Object tham chiếu | Màu hằng | Roughness bề mặt đều | Thiếu normal | Mapping ban đầu |
|---|---|---:|---|---|---|---|
| Book spine 0 | Decorative materials | 5 | True | True | True |  |
| Book spine 1 | Decorative materials | 5 | True | True | True |  |
| Book spine 2 | Decorative materials | 6 | True | True | True |  |
| Book spine 3 | Decorative materials | 4 | True | True | True |  |
| Botanical / cliff moss | Leaves | 18 | True | True | True |  |
| Botanical / deep vine stems | Leaves | 208 | True | True | True |  |
| Botanical / textured warm bark | Wood | 6 | False | True | False | Generated |
| Botanical / waxy pond lily pads | Leaves | 3 | True | True | True |  |
| Detail / mellow bronze | Metal | 4 | True | True | True |  |
| Detail / quiet gold embroidery | Fabric | 4 | True | True | True |  |
| Detail / sage ceramic glaze | Decorative materials | 3 | True | True | True |  |
| Detail / warm linen seams | Fabric | 25 | True | True | True |  |
| Environment / clear pastel sky | Decorative materials | 1 | False | False | False | Generated |
| Environment / hazy distant rock | Decorative materials | 16 | True | True | True |  |
| Environment / hazy island foliage | Decorative materials | 16 | True | True | True |  |
| Environment / pearl cloud | Decorative materials | 56 | True | True | True |  |
| Fabric / lavender blue | Fabric | 3 | False | True | False | Generated |
| Fabric / lilac folded curtains | Fabric | 2 | False | True | False | Generated |
| Fabric / quiet sage umbrella panels | Fabric | 2 | True | True | True |  |
| Fabric / sage linen | Fabric | 5 | False | True | False | Generated |
| Fabric / soft moon quilt | Fabric | 3 | False | True | False | Generated |
| Fabric / warm ivory | Fabric | 29 | False | True | False | Generated |
| Flower golden heart | Flowers | 285 | True | True | True |  |
| Greenhouse soft glass | Glass | 5 | True | True | True |  |
| Ground / pale beach sand | Ground | 1 | False | True | False | Generated |
| Ivory blossoms | Flowers | 397 | True | True | True |  |
| Leaf / fresh green | Leaves | 601 | False | True | False | Generated |
| Leaf / golden tips | Leaves | 589 | False | True | False | Generated |
| Leaf / jade | Leaves | 740 | False | True | False | Generated |
| Master / warm amber lantern glass | Glass | 13 | True | True | True |  |
| Moon lamp warm glow | Decorative materials | 4 | True | True | True |  |
| Natural rope | Fabric | 12 | True | True | True |  |
| Organic / cloud depth 0 | Decorative materials | 3 | True | True | True |  |
| Organic / cloud depth 1 | Decorative materials | 3 | True | True | True |  |
| Organic / cloud depth 2 | Decorative materials | 2 | True | True | True |  |
| Organic / flowing water lane 0 | Water | 4 | False | True | False | Generated |
| Organic / flowing water lane 1 | Water | 4 | False | True | False | Generated |
| Organic / flowing water lane 2 | Water | 4 | False | True | False | Generated |
| Organic / rock with crevice soil and moss | Rock | 3 | False | True | False | Generated |
| Organic / rock with crevice soil and moss.001 | Rock | 3 | False | True | False | Generated |
| Pastel pink blossoms | Flowers | 543 | True | True | True |  |
| Pot dark soil | Ground | 21 | True | True | True |  |
| Stone / recessed fine fissure | Rock | 17 | True | True | True |  |
| Stone / warm limestone 0 | Rock | 214 | False | True | False | Generated |
| Stone / warm limestone 1 | Rock | 217 | False | True | False | Generated |
| Stone / warm limestone 2 | Rock | 220 | False | True | False | Generated |
| Stone / warm limestone 3 | Rock | 214 | False | True | False | Generated |
| Structure / greenhouse sage | Decorative materials | 15 | False | True | False | Generated |
| Terracotta plant pots | Decorative materials | 42 | True | True | True |  |
| Terracotta playhouse roof | Decorative materials | 10 | True | True | True |  |
| Water / rooftop pond | Water | 1 | False | True | False | Generated |
| Water / translucent waterfall | Water | 4 | False | True | False | Generated |
| Water / turquoise sea | Water | 1 | False | True | False | Generated |
| Water / warm white foam | Water | 127 | True | True | True |  |
| Wood / golden edge trim | Wood | 243 | False | True | False | Generated |
| Wood / honey structural | Wood | 412 | False | True | False | Generated |
| Wood / warm floorboards | Wood | 115 | False | True | False | Generated |

## Mapping, repetition và màu sắc

Generated 0–1 khiến hạt noise/vân không có kích thước vật lý đồng nhất trên mesh lớn/nhỏ. Không có image texture trong nguồn nên không phát hiện tiled bitmap; repetition chủ yếu đến từ generic noise cùng hệ số trên các object/mesh giống nhau. Wood quá đều trên mỗi tấm; rock/cloth nhiều vùng thiếu phản ứng bề mặt. Bronze dùng Metallic 0 trong nguồn nên chưa có phản ứng kim loại.
Material mới dùng Position theo mét cho rock/fabric/ground và box projection cho scan đá. Wood dùng Position chuyển WORLD → OBJECT và bù scale thực theo object, chọn chiều dài bbox làm hướng vân; Object Info Random lệch pha giữa tấm để giảm lặp. Không chỉnh UV, geometry, bố cục hoặc animation gốc. Leaf/petal giữ Generated cho gradient cục bộ nhưng micro-normal dùng mét. Rock phủ scan 2.7 m và thêm noise rộng để giảm repetition; oak roughness 1.2 m.
Palette giữ honey wood, cream-gray limestone, botanical greens, hoa pink/yellow/ivory, sofa cream và bedroom lavender-blue. Water có IOR 1.333, turquoise, normal hai tần số và roughness thấp. Không dùng metallic để tạo nước phản chiếu.

## Prototype và đánh giá

Ba scene độc lập gồm bản sao Organic primary terrace rock_03, nhóm Zone_4_floorboard_08–14 và sofa/phụ kiện. Camera, hai area light trắng, HDRI studio, exposure 0, geometry và resolution 1000 × 750 được giữ nguyên giữa before/after. Có render thật bằng Eevee và kiểm tra ảnh. Camera test được sửa trước khi xuất bộ before/after cuối; ảnh trống trong lần kiểm tra đầu đã được thay bằng render hợp lệ.
Lần 1: đá chưa đủ lớp khoáng, vải có sọc. Lần 2: thêm scan height, lớp strata và fissure nhỏ, moss mềm; giảm độ nổi weave vải, pha irregular fibers. Wood có vân liên tục và roughness theo thớ. Chỉ rollout sau khi xem ba cặp ảnh này. Kiểm tra cận thêm trên cushion (fabric_detail_before/final) rồi hạ tần số weave để sợi đọc rõ hơn mà giảm aliasing; cùng camera và HDRI. Sofa thay đổi có chủ ý nhỏ hơn đá/gỗ để tránh bề mặt thô cứng. Water được chỉnh sáng thêm sau full-scene review vì bản đầu quá tối; beauty renders được cập nhật lại.

## Lighting và kiểm thử

Neutral: ba scene studio trắng và HDRI CC0 Monochrome Studio 03, strength 0.3, exposure 0. Scene M37_Neutral_Map_TextureCheck liên kết geometry/material của bản đồ và dùng bản sao Sun/key/fill màu trắng + HDRI, exposure 0; render overview_material_neutral.png. Beauty: scene Scene giữ rig Organic với Sun chính, soft key/front fill, ánh vàng living và xanh tím bedroom; AgX Medium High Contrast và exposure 0.1. Không tăng exposure để che lỗi bề mặt. Beauty world và background geometry vốn có được giữ.
Render trước/sau toàn scene dùng cùng Camera_LivingRoom, M37_Camera_OrganicCliff, Camera_Rooftop, Camera_Bedroom và Camera_Overview, cùng rig beauty. Các shader mới đã được kiểm tra bằng actual Eevee renders. Rock scan dùng height để tạo normal bump trên box projection; nor_gl đã pack nhưng không cắm tangent-space normal vào box projection để tránh sai hệ tiếp tuyến. Oak chỉ dùng scan roughness; màu/vân wood và cloth micro-normal procedural.
Texture stretching được kiểm bằng metrical mapping và render mẫu/cận; không có UV unwrap hay displacement hình học. Đây là kiểm tra hình ảnh và density theo mét, không phải chứng nhận mọi UV trong scene hoàn hảo. Wood bù scale và chia X/Y/Z; các thanh cong liên tục không có UV dọc đường cong chuyên dụng. Ba Organic flowing water lane giữ nguyên graph Generated và driver chuyển dòng gốc, đồng thời thêm micro-normal theo mét; nhãn material_animation_checks kiểm chứng driver expression/path/index.

## Godot / glTF

| Nhãn | Ý nghĩa |
|---|---|
| DIRECT_GLTF_PRINCIPLED_CONSTANTS | Các material legacy dạng Principled hằng; chỉ các thuộc tính được glTF hỗ trợ. |
| BAKE_REQUIRED | Noise, color ramp, box mapping, bump, moss, vân và cloth cần bake UV textures trước khi giữ chất lượng qua glTF. |
| GODOT_SHADER_REWRITE | Nước có ripple/depth proxy và phản xạ phụ thuộc renderer; cần Godot shader/thiết lập equivalent. |
| BLENDER_BEAUTY_ONLY | Sky, clouds, backdrop và các vật liệu phát sáng được giữ để beauty render; ánh sáng không được xuất như texture. |

Không bake, không xuất GLB mới và không kiểm thử Godot trong Phase 3.7. Không tuyên bố shader procedural xuất trực tiếp hoặc chất lượng tương đương ở Godot. Depth water là gradient nghệ thuật, chưa lấy độ sâu scene thật; không phải fluid simulation.

## Validation

Object gốc: 3915. Object gốc mất: 0. Geometry/transform/modifier/action thay đổi: 0. Camera mới: M37_Camera_OrganicCliff.
Texture ảnh pack: 9. Shader output lỗi: 0. Chi tiết: material_validation.json. Hidden legacy object/material được giữ để khôi phục; không purge.

## Material cuối và nhãn tương thích

| Material | Nhóm | Object visible | Godot |
|---|---|---:|---|
| Botanical / deep vine stems | Leaves | 0 | DIRECT_GLTF_PRINCIPLED_CONSTANTS |
| Botanical / textured warm bark | Wood | 0 | BAKE_REQUIRED |
| Environment / clear pastel sky | Decorative materials | 1 | BLENDER_BEAUTY_ONLY |
| Environment / hazy distant rock | Decorative materials | 16 | BLENDER_BEAUTY_ONLY |
| Environment / hazy island foliage | Decorative materials | 16 | BLENDER_BEAUTY_ONLY |
| Environment / pearl cloud | Decorative materials | 0 | BLENDER_BEAUTY_ONLY |
| Flower golden heart | Flowers | 0 | DIRECT_GLTF_PRINCIPLED_CONSTANTS |
| Ivory blossoms | Flowers | 0 | DIRECT_GLTF_PRINCIPLED_CONSTANTS |
| Leaf / fresh green | Leaves | 0 | BAKE_REQUIRED |
| Leaf / golden tips | Leaves | 0 | BAKE_REQUIRED |
| Leaf / jade | Leaves | 0 | BAKE_REQUIRED |
| M37 / Book spine 0 | Decorative materials | 5 | BAKE_REQUIRED |
| M37 / Book spine 1 | Decorative materials | 5 | BAKE_REQUIRED |
| M37 / Book spine 2 | Decorative materials | 6 | BAKE_REQUIRED |
| M37 / Book spine 3 | Decorative materials | 4 | BAKE_REQUIRED |
| M37 / Botanical / cliff moss | Leaves | 18 | BAKE_REQUIRED |
| M37 / Botanical / deep vine stems | Leaves | 200 | BAKE_REQUIRED |
| M37 / Botanical / textured warm bark / axis 2 | Wood | 3 | BAKE_REQUIRED |
| M37 / Botanical / waxy pond lily pads | Leaves | 3 | BAKE_REQUIRED |
| M37 / Detail / mellow bronze | Metal | 4 | BAKE_REQUIRED |
| M37 / Detail / quiet gold embroidery | Fabric | 4 | BAKE_REQUIRED |
| M37 / Detail / sage ceramic glaze | Decorative materials | 3 | BAKE_REQUIRED |
| M37 / Detail / warm linen seams.003 | Fabric | 25 | BAKE_REQUIRED |
| M37 / Fabric / lavender blue | Fabric | 3 | BAKE_REQUIRED |
| M37 / Fabric / lilac folded curtains | Fabric | 2 | BAKE_REQUIRED |
| M37 / Fabric / quiet sage umbrella panels | Fabric | 2 | BAKE_REQUIRED |
| M37 / Fabric / sage linen.003 | Fabric | 5 | BAKE_REQUIRED |
| M37 / Fabric / soft moon quilt | Fabric | 3 | BAKE_REQUIRED |
| M37 / Fabric / warm ivory.003 | Fabric | 29 | BAKE_REQUIRED |
| M37 / Flower golden heart | Flowers | 277 | BAKE_REQUIRED |
| M37 / Greenhouse soft glass | Glass | 5 | BAKE_REQUIRED |
| M37 / Ground / pale beach sand | Ground | 1 | BAKE_REQUIRED |
| M37 / Ivory blossoms | Flowers | 389 | BAKE_REQUIRED |
| M37 / Leaf / fresh green | Leaves | 587 | BAKE_REQUIRED |
| M37 / Leaf / golden tips | Leaves | 577 | BAKE_REQUIRED |
| M37 / Leaf / jade | Leaves | 724 | BAKE_REQUIRED |
| M37 / Natural rope | Fabric | 12 | BAKE_REQUIRED |
| M37 / Organic / flowing water lane 0.001 | Water | 4 | GODOT_SHADER_REWRITE |
| M37 / Organic / flowing water lane 1.001 | Water | 4 | GODOT_SHADER_REWRITE |
| M37 / Organic / flowing water lane 2.001 | Water | 4 | GODOT_SHADER_REWRITE |
| M37 / Organic / rock with crevice soil and moss.003 | Rock | 3 | BAKE_REQUIRED |
| M37 / Organic / rock with crevice soil and moss.004 | Rock | 3 | BAKE_REQUIRED |
| M37 / Pastel pink blossoms | Flowers | 535 | BAKE_REQUIRED |
| M37 / Pot dark soil | Ground | 21 | BAKE_REQUIRED |
| M37 / Stone / recessed fine fissure | Rock | 17 | BAKE_REQUIRED |
| M37 / Stone / warm limestone 0 | Rock | 48 | BAKE_REQUIRED |
| M37 / Stone / warm limestone 1 | Rock | 50 | BAKE_REQUIRED |
| M37 / Stone / warm limestone 2 | Rock | 50 | BAKE_REQUIRED |
| M37 / Stone / warm limestone 3 | Rock | 47 | BAKE_REQUIRED |
| M37 / Structure / greenhouse sage | Decorative materials | 15 | BAKE_REQUIRED |
| M37 / Terracotta plant pots | Decorative materials | 42 | BAKE_REQUIRED |
| M37 / Terracotta playhouse roof | Decorative materials | 10 | BAKE_REQUIRED |
| M37 / Water / rooftop pond | Water | 1 | GODOT_SHADER_REWRITE |
| M37 / Water / translucent waterfall | Water | 3 | GODOT_SHADER_REWRITE |
| M37 / Water / turquoise sea | Water | 1 | GODOT_SHADER_REWRITE |
| M37 / Wood / golden edge trim / axis 0 | Wood | 95 | BAKE_REQUIRED |
| M37 / Wood / golden edge trim / axis 1 | Wood | 36 | BAKE_REQUIRED |
| M37 / Wood / golden edge trim / axis 2 | Wood | 112 | BAKE_REQUIRED |
| M37 / Wood / honey structural / axis 0 | Wood | 153 | BAKE_REQUIRED |
| M37 / Wood / honey structural / axis 0.001 | Wood | 3 | BAKE_REQUIRED |
| M37 / Wood / honey structural / axis 1 | Wood | 28 | BAKE_REQUIRED |
| M37 / Wood / honey structural / axis 1.001 | Wood | 2 | BAKE_REQUIRED |
| M37 / Wood / honey structural / axis 1.002 | Wood | 1 | BAKE_REQUIRED |
| M37 / Wood / honey structural / axis 2 | Wood | 221 | BAKE_REQUIRED |
| M37 / Wood / honey structural / axis 2.001 | Wood | 4 | BAKE_REQUIRED |
| M37 / Wood / warm floorboards / axis 0.003 | Wood | 115 | BAKE_REQUIRED |
| Master / warm amber lantern glass | Glass | 13 | BLENDER_BEAUTY_ONLY |
| Moon lamp warm glow | Decorative materials | 4 | BLENDER_BEAUTY_ONLY |
| Organic / cloud depth 0 | Decorative materials | 3 | BLENDER_BEAUTY_ONLY |
| Organic / cloud depth 1 | Decorative materials | 3 | BLENDER_BEAUTY_ONLY |
| Organic / cloud depth 2 | Decorative materials | 2 | BLENDER_BEAUTY_ONLY |
| Pastel pink blossoms | Flowers | 0 | DIRECT_GLTF_PRINCIPLED_CONSTANTS |
| Stone / warm limestone 0 | Rock | 0 | BAKE_REQUIRED |
| Stone / warm limestone 1 | Rock | 0 | BAKE_REQUIRED |
| Stone / warm limestone 2 | Rock | 0 | BAKE_REQUIRED |
| Stone / warm limestone 3 | Rock | 0 | BAKE_REQUIRED |
| Water / translucent waterfall | Water | 0 | BAKE_REQUIRED |
| Water / warm white foam | Water | 44 | BLENDER_BEAUTY_ONLY |
