# Catmosphere — Hero Environment Beauty Pass

## Phiên bản bàn giao

File mới: `C:/Game/GameModel_3D/Catmosphere_Hero_Environment.blend`.
Các file Organic Master, Water Master và WaterfallRel1 cũ không được ghi đè trong beauty pass này.
Đây là một bản hero reconstruction có thể tiếp tục chỉnh sửa, không phải tuyên bố đã đạt ngang ảnh concept tham chiếu.

## Thay đổi theo phase

- **A — Composition:** camera hero dọc, giữ chuỗi tầng và cầu thang Catmosphere. Giữ các phòng, pergola, nhà kính, nội thất và dock; tầng playground cũ cũng được giữ. Dựng chuỗi hồ và thác ở phía phải để tạo đường dẫn thị giác liên tục.
- **B — Rock:** thay các khối đá platform chính bằng limestone organic, hạ mặt đá dưới sàn gỗ sau review, sửa hướng normal. Thêm bờ đá hồ, vai đá bất quy tắc, buttress treo và chân đảo thuôn. Không xóa kiến trúc nguồn.
- **C — Water:** năm hồ trung gian mới, năm dòng thác nối tầng, hai nhánh phụ và ba dòng tràn khỏi đảo. Thân nước có chiều rộng biến thiên, mép tràn cuộn, độ dày hình học và mask vùng bọt khí. Nước xanh ngọc pha trắng; không dùng alpha thấp đồng nhất phủ toàn thân. Phần cuối ba dòng tràn giảm opacity để hòa vào sương.
- **D — Gardens:** bổ sung 107 cụm foliage/hoa quanh tầng, bờ hồ, pergola, beach và tán cây trái; 39 dây leo/garland có thân và lá riêng. Hoa hồng, ivory và lavender xen lá xanh. Bố trí chủ yếu quanh viền để không lấp trung tâm phòng.
- **E — Materials / atmosphere:** gỗ honey oak và teak có grain, limestone sáng, bảng màu botanical thống nhất; ánh sáng nắng ấm, sky fill lạnh nhẹ và rim vàng. Ba vùng mist cục bộ, nền đảo bay do người dùng cung cấp.
- **F — Polish:** chỉnh đá không che sàn, thêm vai đá phá mép đều, sửa chân đảo, thêm nhánh nâng tán cây, tăng tương phản gỗ/đá và xuất camera cận cảnh riêng.

## Nguồn thực sự được dùng

| Nguồn | Vai trò trong hero scene | Quyền sử dụng |
|---|---|---|
| `textures/water/integration/doodlebuilt_waterfall_fx.png` — [Toon Waterfall, doodlebuilt](https://opengameart.org/content/toon-waterfall) | Pattern dòng chảy / aeration mask trong shader thác mới; UV scrolling. Không import nguyên mô hình | CC0 theo hồ sơ asset đã kiểm tra trong dự án |
| `normal.png` — [ProcTexture Wave Normal Map](https://proctexture.com/de/textures/water/normal-maps/wave-normal-map) | Animated normal map cho thác | CC0 theo hồ sơ nguồn đã kiểm tra |
| `textures/water/integration/Catmosphere_Cloud_Islands_Background.png` | Ảnh nền compositor, từ ảnh “Thung lũng đảo bay giữa mây trời.png” người dùng cung cấp | Tài nguyên do người dùng cung cấp; không suy đoán quyền phân phối/thương mại |
| “Khu vườn nghỉ dưỡng giữa trời mây.png” | Tham khảo bố cục, màu gỗ/đá/nước, mật độ vườn và nhịp thác | Tham khảo do người dùng cung cấp; không dùng ảnh này giả làm render scene |

Shader, mesh đá, hồ/thác mới, lá/hoa/dây leo, foam mask và quỹ đạo splash được dựng trong Blender. Không sao chép nguyên shader Unreal/Unity. Splash gồm 90 giọt mesh nhỏ chạy bằng driver ballistic và 25 arc nhỏ; **không phải mô phỏng fluid vật lý**. Foam gồm các mặt có noise mask và radial falloff, không dùng cầu trắng lớn giả bọt.

Prototype Rel1 cũ được giữ ẩn để bảo toàn lịch sử. Thác HERO hiển thị **không dùng các frame GIF của waterfall_rel1.zip**. ZIP đó không có quyền CC0 đã xác minh; readme không bảo đảm tác giả/quyền của animation gốc. Vì file mới còn giữ dữ liệu prototype cũ, cần loại bỏ dữ liệu Rel1 chưa rõ quyền trước khi phân phối thương mại toàn bộ `.blend`.

## Animation

Scene giữ 300 frame / 30 FPS. Flow texture chạy 7 vòng, normal 19 vòng trong 300 frame; foam có noise animation tuần hoàn, giọt splash dùng nhiều chu kỳ và phase khác nhau. Đây là chuyển động shader/geometry có trong scene, không phải ảnh tĩnh giả animation. Kiểm tra số liệu vòng lặp được lưu riêng trong `catmosphere_hero_validation.json`; không đồng nghĩa đã review toàn bộ 300 frame bằng video. Task beauty pass hiện tại không xuất MP4 mới.

## Render bàn giao

- `renders/catmosphere_hero_final.png`: hero 1080 × 1920, EEVEE 128 samples, frame 75.
- `renders/catmosphere_hero_rooftop.png`, `lounge.png`, `bedroom.png`, `dining.png`, `beach.png` (cùng tiền tố `catmosphere_hero_`): năm close-up 960 × 960, 96 samples.
- `renders/catmosphere_hero_before_after.png`: hai render Blender thật, cùng hero camera, framing và frame 75. Ánh sáng/vật liệu khác nhau vì chúng là một phần beauty pass; không gọi đây là phép so sánh chỉ geometry dưới ánh sáng khóa cố định.
- `renders/catmosphere_hero_level_closeups.png`: tổng hợp năm close-up thực tế.
- Các ảnh Phase A, B/C, beauty review và polish review lưu để đối chiếu quá trình.

## Đánh giá thị giác và giới hạn

Render thực tế cho thấy bố cục nhiều tầng rõ hơn, có hệ hồ/thác liên kết, màu nước xanh ngọc, gỗ ấm và các viền hoa/dây leo phong phú hơn bản nguồn. Các sàn gỗ không còn bị đá mới phủ lên như lần render B/C; phòng ngủ, lounge, dining và cầu thang vẫn đọc được.

Chưa đạt hoàn toàn chất lượng ảnh tham chiếu: foliage còn hình học/lặp lại, đá vẫn có nhịp platform khá đều, nước còn tương đối dạng sheet ở vài đoạn và thiếu sự tan rã tự nhiên của spray. Độ tương phản và cảm giác vật liệu vẫn mềm hơn concept. Đây là bản beauty pass đầu tiên để review, **chưa tự duyệt “premium concept-art final”**. Nền là một ảnh compositor 2D, không phải thế giới đảo bay 3D có parallax. Không tuyên bố đã kiểm tra va chạm mọi object ở mọi frame.
