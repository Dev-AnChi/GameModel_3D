# Waterfall_03 — Waterfall Rel1 integration

## Phạm vi

Chỉ chỉnh Waterfall_03. Không rollout, không đổi ocean, rooftop pond, bố cục, kiến trúc hoặc cây. Nền Sky gradient backdrop được ẩn khi render để dùng ảnh đảo bay do người dùng cung cấp; ánh sáng World và đèn không đổi. File mới: `Catmosphere_Water_WaterfallRel1.blend`. File Water Master cũ giữ nguyên SHA-256 `76B05E384B7A307B6BD9E2FC5C49ECE58B1368EF677F848926A6194AC0FB4A72`.

## Kiểm tra ZIP thực tế

Nguồn: `C:/Users/Admin/Downloads/waterfall_rel1.zip`, 555.418 byte. Đã giải nén vào `textures/water/waterfall_rel1`, đọc toàn bộ readme và mở được tất cả ảnh bằng Pillow. Chi tiết checksum từng file nằm trong `inspection.json` cùng thư mục.

| Thành phần | Nội dung thực tế | Sử dụng |
|---|---|---|
| waterfall_tex0.jpg–waterfall_tex10.jpg | 11 frame RGB, 256 × 256; readme hướng dẫn add blending | Đóng atlas không vẽ lại, nội suy hai frame trong Blender Shader Nodes; dùng làm mask bọt khí, không dùng Add trực tiếp lên toàn thân |
| waves_concent_tex1.png–waves_concent_tex6.png | 6 frame RGB, 256 × 256; không có alpha channel dù readme mô tả fade-to-transparent | Atlas ripple; lấy luminance làm mask, không giả định PNG có alpha |
| foam_particle.png | RGBA, 256 × 256 | Mask foam ở vùng impact và các mặt foam cong nhỏ |
| waterfall_behind.png | RGBA, 220 × 210 | Không dùng: không thay đá và bố cục Catmosphere |
| waterfall.b3d | BB3D v1; một mesh, 100 vertex, 162 triangle, một UV set và vertex color | Không dùng nguyên mesh. Blender hiện tại không có importer B3D sẵn; không cài hoặc chạy converter không rõ nguồn |
| readme.txt | Dieter Marfurt, 2022 | Đã đọc đầy đủ; cảnh báo bản quyền bên dưới |

Asset không có normal map, không có foam flipbook riêng và không ghi FPS gốc. Không gọi 11 frame nguồn là animation 300 frame nguyên gốc. Preview 300 frame được tạo bởi shader nội suy và chuyển động bổ sung trong Blender.

## Giấy phép — chưa đủ cơ sở cho phát hành thương mại

Readme nói animation được trích từ GIF trên nhiều nền tảng, truy được tới Tumblr năm 2013 nhưng không tìm được tác giả gốc. Public-domain status chỉ là giả định và không được bảo đảm. Đây **không phải asset CC0 đã xác minh**. Dieter Marfurt là người xử lý/masking, không được xem là người sở hữu animation gốc. Prototype này chỉ phục vụ thử nghiệm nội bộ theo yêu cầu; cần thay nguồn hoặc có xác nhận quyền trước khi phát hành thương mại. Không đóng gói ZIP nguồn thành một gói asset để phân phối lại.

Trang nguồn: [Free Asset Waterfall Animation](https://jfkeo1010etc.itch.io/free-asset-waterfall-animation). Readme tải thực tế là bằng chứng quan trọng hơn suy đoán từ tên “free”.

## Phần dùng thực tế và phần bổ sung

- Thực tế dùng toàn bộ 11 frame flow, 6 frame ripple, foam_particle.png; ảnh nền do người dùng cung cấp được pack vào Blender.
- Normal map `normal.png` có sẵn trong project, nguồn ProcTexture Wave Normal Map, CC0; không nằm trong ZIP Rel1.
- Geometry kế thừa đường chảy an toàn của Refined, sao chép thành collection REL1 riêng rồi làm mượt silhouette, rộng thân chính, thu hẹp vùng cuối dòng, giữ hai strand ngắn và mép tràn cong. Thân phụ bị tắt sau review để giảm chồng lớp. Không đổi geometry nguồn.
- Shader tự xây trong Blender: nội suy frame, retint xanh ngọc/trắng, density mask, flow breakup, normal UV scrolling, relief nhỏ từ luminance của animation nguồn, vùng trong/đục khác nhau. Không sao chép shader Unity/Unreal.
- Splash gồm 52 giọt mesh nhỏ có quỹ đạo ballistic, phase và fade riêng, cùng splash fingers; không phải mô phỏng fluid hoặc particle emitter vật lý. Các driver và shape key đều lưu trong file.
- Foam bổ sung bằng hai mặt bám đá có mask alpha × luminance của ảnh, không dùng cầu trắng lớn để giả bọt. Năm mặt thử nghiệm còn lại bị tắt sau review. Ripple dùng texture animation nguồn, không dùng ảnh tĩnh thay animation.
- Toon Waterfall CC0 của doodlebuilt không dùng trong shader hoặc geometry hiển thị của phiên bản REL1; asset inspection còn lưu riêng từ nghiên cứu trước. Không báo asset đó là nguồn chính của bản này.

## Animation và kiểm tra

300 frame / 30 FPS / 10 giây. Flow và ripple chạy 7 chu kỳ trong 300 frame, có nội suy. Normal chạy 19 vòng; breakup dùng 4D noise theo pha sine/cosine, 5 chu kỳ tuần hoàn liên tục. Các splash có phase riêng. Vòng lặp hình học frame 1/301: sai lệch tối đa 0.0 sau sửa pivot và geometry cuối. File `waterfall_rel1_loop.json` ghi dữ liệu thực tế. Preview 464 × 600, EEVEE 24 samples; ảnh tĩnh 850 × 1100, 128 samples. Preview là render scene review có context liên kết và animation ngoài prototype được giữ tĩnh, không phải full-map cinematic.

Ba bản so sánh dùng cùng camera W39_PrototypeCamera, frame 75, ánh sáng và nền mới. Original là geometry/shader gốc Waterfall_03; Refined current là baseline R39; New là collection REL1. Close-up dùng các camera top/middle/base cố định.

Kiểm tra BVH với 199 object context tại frame 1, 75, 151, 226 sau sửa điểm kết thúc: không còn giao cắt được phát hiện trên các object prototype đang render. Đây là kiểm tra theo mẫu, không phải chứng minh không va chạm ở mọi frame. Snapshot geometry, material assignment và transform của 4.127 object nguồn không đổi (`protected_changes: []`). Chi tiết trong `waterfall_rel1_geometry_validation.json`.

MP4 bàn giao đã được giải mã độc lập bằng FFmpeg: H.264, 464 × 600, **300 frame, 30.0 FPS, 10.0 giây**, 1.322.578 byte. Sai khác RGB trung bình giữa frame liền kề trong vùng thác là 1,059/255; các ảnh frame 1/76/151/226/300 được trích từ chính MP4 để review chuyển động. Chỉ số này xác nhận ảnh có thay đổi, không chứng minh chất lượng thẩm mỹ.

Ảnh render frame 1 và 301 sau sửa cuối có sai khác RGB trung bình toàn ảnh 0,047/255, rất nhỏ nhưng không byte-identical do sampling/độ chính xác số. Hình học khớp 0.0; các clock shader đều tuần hoàn. Metadata đầy đủ ở `waterfall_rel1_video_validation.json`.

## Đánh giá hình ảnh

Bản mới có lõi xanh ngọc rõ hơn và ít trắng phủ toàn thân hơn Refined. Silhouette sạch hơn, vùng bọt khí và flow texture đã chạy thực sự. Tuy nhiên close-up còn có cảm giác bề mặt kéo dài/ribbon, foam cần thêm kiểm tra về độ mềm và tiếp xúc đá. **Chưa duyệt “stylized premium” và không rollout.** Độ phân giải 256 px và nguồn GIF khiến asset phù hợp làm base/mask thử nghiệm hơn là nguồn texture chất lượng cao cuối cùng.

Một lỗi pivot trên mặt foam được phát hiện khi review close-up: scale theo trục Z áp vào vertex world-space gây foam nổi cao. Đã chuyển vertex sang local-space quanh pivot và đưa mặt foam về tiếp xúc đá trước xuất cuối. Preview ban đầu được giữ riêng dưới tên `waterfall_rel1_animation_initial_unreviewed.mp4`, không phải bản bàn giao.

Kiểm tra cuối còn phát hiện vài mặt ở đoạn cuối dòng đi vào đá. Đã nâng/cắt hai hàng cuối theo raycast mặt đá, giữ đầu/cuối gần vị trí nguồn, rồi render lại clip. `waterfall_rel1_animation_contact_review.mp4` là clip trước sửa va chạm này, không phải bản bàn giao. File bàn giao duy nhất là `waterfall_rel1_animation_preview.mp4`.
