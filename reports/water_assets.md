# Phase 3.9A — Tài nguyên cho Pass A

## Tài nguyên đã tải và mở thành công

| Tài nguyên | Nguồn / tác giả | Giấy phép | Sử dụng |
|---|---|---|---|
| `textures/water/oga_waterfall_1.png` | [Water Pack 1 — TheDikTatorTot](https://opengameart.org/content/water-pack-1) | CC0, ghi trên trang nguồn | Ảnh tham khảo thác thật; bản tinh chỉnh dùng luminance làm chi tiết bọt. Không phải flow map hoặc animated sprite sheet. |
| `textures/water/wave-normal-map.zip` và thư mục giải nén | [Wave Normal Map — ProcTexture](https://proctexture.com/textures/water/normal-maps/wave-normal-map) | CC0, ghi trên trang nguồn | Normal và height 1024×1024, đã tải, mở trong Blender và pack vào `.blend`. |

Bộ ProcTexture có 5 map: baseColor, normal, height, roughness, ambientOcclusion. Không áp toàn bộ bộ PBR như một vật liệu đặc; chỉ chọn các map phù hợp với lớp nước. Normal và height là dữ liệu Non-Color. Ảnh thác OpenGameArt thực tế mở được ở 512×512; tên download ghi `382px` không phải kích thước đo được. Tệp kiểm chứng kích thước, số byte và SHA-256: `water_asset_validation.json`.

Ảnh thác gốc không seamless. Trang nguồn mô tả bộ wave là tileable, nhưng kiểm tra pixel của height map đo chênh biên trên/dưới trung bình 34.47/255, so với hai hàng kề nhau 1.90/255. Vì vậy không coi height gốc là seamless đã kiểm chứng. Normal map có chênh biên 2.51/255; hai hàng kề nhau 20.60/255.

Shader chuẩn hóa height về giá trị 0.4 tại biên bằng trọng số `sin²(pi*fract(U))*sin²(pi*fract(V))`, rồi hòa ảnh thác vào utility height đã chuẩn hóa bằng cùng kiểu trọng số. Đóng góp dữ liệu không seamless trở về 0 với đạo hàm 0 tại biên tile. Không tuyên bố ảnh gốc là animated waterfall hoặc texture tileable. Không sửa raster gốc; cách xử lý nằm trong shader.

## Tìm kiếm nguồn ưu tiên

Đã kiểm tra Poly Haven, ambientCG, cgbookcase và OpenGameArt trước khi bổ sung shader procedural. OpenGameArt có ảnh thác CC0 sử dụng được. Chưa xác nhận được bộ flow/foam/splash/animated waterfall phù hợp từ ba thư viện PBR ưu tiên; không tuyên bố đã tải những loại map này. ProcTexture là nguồn bổ sung có normal nước tileable và giấy phép rõ ràng.

Không tải một shader thương mại hoặc simulation không rõ giấy phép. Splash được tạo bằng hình học nhỏ và driver; foam kết hợp map ngoài với shader. Không dùng fluid simulation.

## Godot

Node shader Blender không chuyển nguyên vẹn sang Godot. Cần dựng lại scrolling UV, alpha breakup, normal tangent-space, Fresnel với IOR nước 1.333, lớp bọt và driver splash bằng shader / particles của Godot. Giữ CC0 textures, UV mesh và vertex color `WaterOpacity` làm đầu vào. Dùng vertex color để giữ mép mềm và nhánh taper; dựng lại hòa trộn biên ảnh / height không seamless. Cần kiểm tra culling hai mặt, depth và transparency sorting trong Godot. Không coi `.blend` là shader runtime đã hoàn thiện. Scene review và các scene test chỉ phục vụ kiểm chứng, không phải nội dung để xuất vào game.
