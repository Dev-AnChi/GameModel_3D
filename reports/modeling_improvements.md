# Catmosphere — Phase 3.6: Organic Reconstruction

## Kết quả và file

- File làm việc: `Catmosphere_Organic_Master.blend`.
- Sao lưu scene đang mở trước mọi chỉnh sửa: `Catmosphere_PreOrganic.blend`.
- Checkpoint phục hồi trước bước khoét lối đi: `Catmosphere_Organic_PassE_Recovery.blend`.
- So sánh Pass A cùng camera, ánh sáng, độ phân giải: `renders/terrain_before.png`, `renders/terrain_after.png` (1200 × 900).
- Render cuối: `renders/organic_overview.png` (1080 × 1920); `organic_bedroom.png`, `organic_rooftop.png` (1400 × 900).
- Kiểm tra định lượng: `reports/organic_validation.json`.

Tất cả thay đổi scene và render được thực thi bằng Blender MCP trên Blender 5.2.2 LTS, addon 1.8. Không dựng lại scene, không đổi vị trí sáu khu vực. Render bằng EEVEE, 128 samples, AgX; Camera_Overview được khôi phục làm camera active. Ảnh cuối ở frame 75.

## Pass A — Terrain prototype

Chọn tầng sân chơi (Cliff_02 và các Terrace_2_ledge_*). Giữ bản gốc và dữ liệu nguồn; tạo khối mới trên bản sao của đối tượng địa hình.

1. Custom mesh khép kín với các vành địa chất lệch nhau, các mặt lớn, gờ lõm và phần đá nhô không đồng đều.
2. Chỉnh hình bằng trường biến dạng liên tục; không xếp thêm primitive làm khối chính.
3. Hợp nhất có chọn lọc năm mỏm đá bằng voxel remesh cục bộ 0,075 m.
4. Relax hai lượt, decimate 0,28, tính lại normals.

Bản thử đầu còn giống dải ngang; đã chỉnh vai đá lệch và hợp nhất các mỏm rồi render lại. So sánh cùng camera cho thấy khối dưới sân chơi liền hơn và mất vòng đá nhỏ lặp đều. Prototype được chấp nhận sau khi xem render thực tế; chưa áp dụng đồng loạt trước bước này.

Prototype sau remesh có 5.187 vertex / 10.370 triangle. Ảnh terrain_after ghi nhận prototype ở thời điểm Pass A, không phải ảnh của toàn scene cuối. Chất lượng đủ để tiếp tục phương pháp cho các tầng khác; không coi đây là đánh giá hiệu năng trên thiết bị game.

## Pass B — Main terrain

Sáu đối tượng mới:
- Organic primary terrace rock_00 — bến biển.
- Organic primary terrace rock_01 — sân ăn.
- Organic primary terrace rock_02 — sân chơi.
- Organic primary terrace rock_03 — phòng ngủ.
- Organic primary terrace rock_04 — phòng khách.
- Organic primary terrace rock_05 — vườn mái.

Mỗi tầng có khối chính riêng, lệch vai, độ dày và độ nghiêng thay đổi. Các vòng Terrace_*_ledge_* được ẩn; một số mỏm đã hợp nhất vào khối chính. Các mesh Cliff_* cũ và backup được giữ để phục hồi.

Continuous left/right natural cliff buttress và Single sculpted sea island foundation được chỉnh độ liên tục bề mặt bằng subdivision cục bộ mức 2 và displacement nhỏ có kiểm soát; không remesh toàn scene. Lõi phía sau và các cấu trúc cửa có sẵn được giữ.

Chuyển tiếp đá–đất–rêu dùng attribute organic_soil_transition với mask chiều cao, hướng normal và noise. Material đá được giữ làm nền. Không rải thêm hàng loạt object để che vấn đề tạo hình.

## Pass C — Vegetation

- Play shade tree trunk: thay curve đơn giản bằng tám đường Bezier phân nhánh/rễ, bán kính thuôn dần, góc và chiều dài khác nhau.
- Các Shade tree branch cũ được ẩn; tán Shade tree soft crown giảm từ 16 xuống 8 cụm, bố trí theo đầu cành và có khoảng trống.
- Ba mesh dùng chung BeautyBotanical_flowerbed_* được sao lưu và biến dạng chiều cao theo vị trí, giữ thân và hoa liền nhau.
- 21 dây leo Terrace_*_cascading_vine / Pergola trailing vine chuyển thành Bezier mềm và thuôn dần; 315 lá được dịch theo đường dây và xoay nhẹ.
- Tán cây trên đảo xa được chỉnh silhouette bất đối xứng trên mesh hiện có.

Không tăng số lượng lá/object một cách đại trà. Giữ nguyên các bộ botanical mesh dùng chung.

## Pass D — Architecture

- Sofa back, Mattress, Bed padded headboard: thay khối hộp bằng mesh đệm bo và phồng.
- Pillow, Pillow.001 và hai Moon accent pillow: tăng độ phồng có kiểm soát.
- Hai Moon tied curtain: thêm nếp nhỏ và mép vải không đều, dùng subdivision mức 1 và độ dày vải có sẵn.
- Hai Umbrella canopy: điều chỉnh độ võng theo phương bán kính và nếp vải.
- Moon draped soft quilt: thêm nếp mềm nhỏ.

Các cột chịu lực, mộng/chân cột pergola, cửa vòm, lan can và bậc thang giữ cấu trúc hợp lý. Ảnh cận phát hiện đá tầng trên che cửa vòm/sao phòng ngủ: đã chỉnh phần trần trước mỏng hơn và giữ khối dày ở hai bên; render lại xác nhận không gian mở.

## Pass E — Water and clouds

Bốn mesh thác chính được thay topology:
- Waterfall_05.
- Living-to-moon cliff stream.
- Waterfall_03.
- Waterfall_01.

Mỗi thác gồm ba dải cong có bề rộng biến thiên, lệch nhịp và phần đầu nguồn nằm ngang cuộn vào thác. Dùng tám object mới cho đường bọt ngắt quãng và các vùng bọt nguồn/va chạm; các đường bọt thẳng cũ được ẩn.

Ba Master lower sea cliff spill_* được chỉnh độ rộng và hướng cuộn ở chân thác. Không dùng fluid simulation. Hình học nước tĩnh; shader có ba tốc độ cuộn noise khác nhau (0,009 / 0,017 / 0,026 đơn vị tọa độ shader mỗi frame), không phải vận tốc vật lý m/s. Driver được kiểm tra ở frame 76, sau đó khôi phục frame 75 có offset bằng 0, trùng trạng thái render cuối.

Tám Master cloudbank_* giữ nguyên số object; thay bố trí metaball thành cụm nối liền, có các thùy trên lệch nhau và phần đuôi mỏng. Mức màu/phát sáng thay đổi theo nhóm để background nhẹ hơn. Đây là hình học mây stylized, không phải mô phỏng thể tích khí quyển.

## Pass F — Review, repair and validation

Đã xem render overview, prototype trước/sau và các ảnh cận. So sánh với concept tập trung vào khối đá thống nhất, khoảng mở của phòng, tán cây có cấu trúc và đường nước ít thẳng hơn.

Kiểm tra BVH trên geometry evaluated phát hiện đá mới giao với bậc thang và mép nguồn hai thác chạm bậc trên cùng. Đã:
- Khoét vùng lối đi mà không đổi transforms của bậc.
- Khôi phục tầng sân chơi từ checkpoint khi một Boolean theo cả tuyến cho kết quả rỗng.
- Dùng các cutter lồi nhỏ cho vùng khó; remesh cục bộ 0,055 m và decimate 0,22 để sửa topology sau Boolean.
- Xoay phần nước đầu nguồn về phía vách.
- Tính lại normals và kiểm tra lại.

Kết quả cuối:
- Không còn giao nhau bề mặt giữa sáu mesh đá mới / bốn thác chính và 105 bậc thang.
- Không có thay đổi matrix_world của các object cầu thang và sáu Terrace_00..05 so với snapshot đầu.
- Cả sáu mesh đá mới có 0 cạnh non-manifold, 0 mặt suy biến.
- Không thiếu material trên geometry đang bật render.
- PNG được kiểm tra header, kích thước và mở xem; file .blend đã lưu.

| Mesh đá | Triangle nguồn sau sửa topology |
|---|---:|
| rock_00 | 16.300 |
| rock_01 | 10.118 |
| rock_02 | 14.650 |
| rock_03 | 10.330 |
| rock_04 | 15.748 |
| rock_05 | 17.188 |
| Tổng | 84.334 |

Triangle trên là topology nguồn của sáu khối, trước các modifier còn giữ. Toàn scene đang bật render: **1.504.975 triangle evaluated** trên 3.527 object geometry. Tổng object scene 3.900 → 3.915; object bật render 3.707 → 3.547. Các object cũ ẩn vẫn giữ để phục hồi.

## Giới hạn còn lại

- Bố cục sàn và phần lớn tuyến cầu thang vẫn mang hình dáng của map cũ; tổng thể chưa đạt độ phong phú địa chất, mật độ vườn và chất lượng ánh sáng của concept.
- Một số vách/chuyển tiếp vẫn khá trơn; background còn đơn giản, một phần lan can/cầu thang che đồ nội thất từ góc overview.
- Nước chưa có hệ thủy văn liên tục từ hồ tới tất cả đầu thác; các vòng bọt là hiệu ứng tạo hình, không có va chạm chất lỏng.
- Kiểm tra BVH chỉ bao phủ sáu mesh đá mới và bốn thác chính so với bậc thang. Không thay thế kiểm tra va chạm toàn scene, headroom, navmesh hoặc chơi thử trong engine.
- UV và material/modifier của các bộ phận không thay topology được giữ. Voxel remesh thay topology và không bảo toàn UV cũ của khối đá; các khối mới dùng procedural material và attribute. Cần UV/bake riêng khi đưa vào game.
- Đây là bản **High Quality**, chưa có LOD, atlas, batching, bake, profiling Android hay kiểm thử Godot. Không xuất mới GLB; GLB từ phase trước không đại diện cho bản Organic này.
