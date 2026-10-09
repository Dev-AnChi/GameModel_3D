# Phase 3.9A — Pass A Waterfall Prototype

## Phạm vi

Chỉ dựng prototype thay thế đoạn `Waterfall_03`. Các thác khác, ocean và rooftop pond chưa nâng cấp. Đây chưa phải bản hoàn tất Phase 3.9A và chưa được duyệt để rollout.

Nguồn: `Catmosphere_Material_Master.blend`. Sao lưu: `Catmosphere_PreWater_20261009.blend`. Bản mới: `Catmosphere_Water_Master.blend`. Không ghi đè các Master cũ.

## Dữ liệu được bảo toàn

Object, mesh, transform và danh sách vật liệu của các object nguồn có chữ ký không thay đổi trong kiểm tra sau khi dựng prototype. Nước và foam cũ của đoạn prototype chỉ ẩn render / viewport, không xóa. Các driver nước cũ giữ nguyên. Scene review dùng hình học môi trường liên kết; không sửa địa hình, kiến trúc, cây hoặc nội thất.

## Cấu trúc chuyển động

Ba dải chính có UV scrolling 17, 23, 29 tile trong 300 frame sau khi hiệu chỉnh tốc độ theo UV scale V = 2.6, với pha ban đầu 0, 0.29, 0.57 để giảm lặp đồng bộ. Với độ cao khoảng 6.37 m, tốc độ chi tiết tương ứng khoảng 4.16, 5.63 và 7.11 m/s. UV tăng trên trục V khiến texture chạy từ đầu nguồn xuống chân thác với UV gốc `v=1-t`. Image Repeat kết hợp chuẩn hóa biên mask bảo đảm các offset trở lại cùng pha sau 300 bước. Các lớp bọt trắng dùng cùng tốc độ của lane tương ứng; không tịnh tiến cả mesh thác.

Splash là các giọt nhỏ có quỹ đạo bật lên rồi rơi xuống, opacity hình học thể hiện bằng scale liên tục. Chu kỳ 60 frame. Bọt dao động nhẹ với chu kỳ 100 frame. Thêm 24 giọt rơi ngoại vi với quỹ đạo tăng tốc và chu kỳ 30, 50, 60 frame. Các chu kỳ đều chia hết 300 frame; giọt thu về scale 0 tại đường nối để tránh bật hiện. Đây là driver hình học nhỏ, không phải fluid simulation.

Thiết lập prototype: 30 FPS, frame 1–300. Frame 301 là điểm kiểm tra trở lại pha frame 1; không đưa frame 301 vào clip để tránh lặp frame tại đường nối.

## Render và trạng thái kiểm tra

`waterfall_before.png` và `waterfall_after.png`: render Blender thật, cùng camera `W39_PrototypeCamera`, rig ánh sáng, frame 75 và độ phân giải 850×1100. `waterfall_before_after.png` chỉ ghép hai render này để so sánh.

Đã điều chỉnh đường nước qua kiểm tra BVH và clearance bề mặt, rồi cắt 59 polygon tại vùng tiếp xúc bị giao cắt. Kiểm tra BVH lần cuối trả về danh sách rỗng giữa các dải chính / nhánh / lớp bọt và nhóm đá, cliff, terrace, stair lân cận được chọn theo không gian. Kiểm tra này không phải chứng nhận toàn bộ map hoặc mọi quỹ đạo giọt nước. Các vị trí đầu nguồn / chân thác giữ cùng vùng và cao độ, nhưng có chỉnh lateral clearance tại mỏm đá; chưa chứng nhận bảo toàn chính xác từng tọa độ endpoint.

Preview MP4 cuối: Blender render thật và đã giải mã đủ 300 frame, 30 FPS, 10.0 giây, H.264, 464×600. Kết quả trong `water_video_validation.json` và strip `water_animation_frames.png` tương ứng clip cuối có sửa biên height, pha lane và mép mềm. Không dùng số đo của clip cũ để chứng nhận bản mới.

Kiểm tra cuối qua MCP: 120 object prototype, 480 object driver hợp lệ, không có shader driver lỗi, chữ ký object nguồn không thay đổi. Matrix của prototype tại frame 1 và 301 có sai khác lớn nhất 0.0. Hai render kiểm tra cùng pha 1/301 có chênh pixel RGB trung bình 0.0453/255; không đòi hỏi dither/antialias cho ảnh hoàn toàn đồng nhất bit.

Đỉnh chênh giữa frame trong MP4 trùng các keyframe H.264 tại 0, 18, 36…288; đã kiểm tra GOP = 18 và giải mã `showinfo`. Vì vậy không tự diễn giải mọi đỉnh sai khác pixel thành giật shader. Clip vẫn có sai số màu / nén so với PNG. Chỉ số cross-correlation ảnh là chẩn đoán, bị ảnh hưởng bởi lớp chồng và phần cảnh tĩnh; không phải chứng nhận vận tốc fluid hay bằng chứng đủ để duyệt mỹ thuật.

Đánh giá tĩnh: đã giảm khối xanh nhựa đặc, có dải nước trong, lớp trắng, normal chuyển động, nhánh ngắn, bọt và splash. Đã áp dụng ảnh thác thật làm chi tiết bọt, tăng tần suất texture và hiệu chỉnh tốc độ. Đã xác nhận trực tiếp UV scale `(1.6, 2.6)` trong node; bản scale cũ không được dùng làm chứng nhận bản cuối. Vertex color `WaterOpacity` làm mềm mép và taper nhánh nhỏ. Shader bổ sung hòa trộn biên tile của ảnh thác không seamless để giảm bước nhảy texture. Dải trắng và các nhánh mảnh vẫn cần duyệt mỹ thuật trong clip; đây là prototype, chưa phải chứng nhận chất lượng để rollout. Chưa dùng volumetric mist.

## Chưa thực hiện

Không có `ocean_after.png`, `pond_after.png` hoặc `water_overview_final.png`: các output này thuộc những Pass sau, không tạo ảnh giả hoặc đổi tên render cũ để thay thế. Cần duyệt chất lượng prototype trước khi triển khai tiếp.
