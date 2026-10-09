# Waterfall_03 — Pass A Refined

Trạng thái: prototype chờ duyệt bằng hình ảnh và video. Không triển khai cho thác khác.

## Phạm vi và bảo toàn

- File mới: `Catmosphere_Water_Refined.blend`.
- File Pass A `Catmosphere_Water_Master.blend` được giữ nguyên. SHA-256: `76b05e384b7a307b6bd9e2fc5c49ece58b1368ef677f848926a6194ac0fb4a72`.
- Chỉ thay phần hiển thị Waterfall_03 và foam liên quan bằng collection `R39 | Waterfall_03 Refined`. Bản original và Pass A vẫn được giữ trong file để đối chiếu.
- Không sửa hình học, vị trí hoặc gán vật liệu của các object có sẵn. Không sửa các thác khác, hồ, biển, đá, cây hoặc cầu thang.

## Sửa lỗi và thay đổi

Phát hiện lỗi lấy mẫu trong Pass A: mỗi lane nguồn có 585 vertex, tương ứng 65 hàng × 9 vertex, không phải 612 vertex/68 hàng. Việc đọc lẫn đầu lane kế tiếp đã tạo các mặt nối ngược từ chân lên đầu thác. Đường chảy mới dùng đúng topology nguồn.

Thân chính được dựng bằng tiết diện có chiều sâu, thay cho các lớp alpha phẳng. Mật độ aerated flow được điều khiển bằng mask dòng nước, có vùng trắng đục, vùng tối trong hơn và các dòng mép ngắn, taper, uốn cong. Không dùng một giá trị alpha thấp đồng nhất cho toàn bộ thác.

Đầu dòng được uốn trực tiếp từ tràn ngang sang rơi dọc. Các phương án nối rời và streak foam lơ lửng đã được tắt. Chân dòng và foam được điều chỉnh theo bề mặt đá tại điểm va chạm, thay cho một mảng bọt nằm trên mặt phẳng nổi.

Splash gồm các tia nhỏ và giọt nhỏ với pha khác nhau. Các tia dư được tắt để giảm cảm giác mạng lưới cung tròn. Ripple là các cung không khép kín, có mở rộng và fade. Không dùng cầu trắng lớn hoặc mist để che lỗi.

## Animation và kiểm tra

- Timeline 1–300, 30 FPS, thời lượng 10 giây.
- UV flow đi từ trên xuống; các material chính, thứ cấp và dòng mép có tốc độ khác nhau.
- Mask ảnh được crossfade giữa hai offset để tránh đường nối texture khi cuộn. Normal animation và các pha hình học dùng chu kỳ nguyên trong 300 frame.
- Splash có các chu kỳ 30, 50, 60, 75 và 100 frame, với phase offset.
- Kiểm tra giao cắt của hình học evaluated tại frame 1, 26, 51, 76, 101, 126, 151, 176, 201, 226, 251, 276 và 301: lần kiểm tra cuối không có giao cắt với 199 obstacle lân cận. Đây là kiểm tra lấy mẫu, không phải chứng nhận mô phỏng collision liên tục.
- Hai ảnh frame 1/301 và video xuất thực tế được dùng để kiểm tra vòng lặp. Kết quả decode nằm trong `water_refined_video_validation.json` sau khi video hoàn tất.
- Kết quả cuối: video H.264 464 × 600, decode đủ 300 frame, 30 FPS, 10,0 giây. Sai khác vị trí vertex evaluated frame 1/301 bằng 0; sai khác trung bình hai ảnh loop khoảng 0,046/255 trên mỗi kênh màu. Không có driver object lỗi. Hash Pass A được xác nhận lại, không đổi.

## Render đối chiếu

Ba render toàn thác dùng cùng camera `W39_PrototypeCamera`, frame 75, ánh sáng, world, exposure và kích thước 850 × 1100:

- `waterfall_original_refine_compare.png`
- `waterfall_pass_a_refine_compare.png`
- `waterfall_refined.png`

Close-up đầu, giữa và chân thác nằm trong `waterfall_refined_closeup_top.png`, `waterfall_refined_closeup_middle.png`, `waterfall_refined_closeup_base.png`.

Preview thực tế: `waterfall_refined_animation_preview.mp4`, không phải nội suy từ ảnh tĩnh. Scene review riêng dùng các context object của scene preview trước; các phần nước ngoài prototype được giữ đứng yên trong scene review, không thay animation của chúng trong main scene.

## Đánh giá hình ảnh

Render cho thấy khối nước trắng rõ hơn Pass A, giảm màu xanh nhựa của original và tăng sự phân biệt với các dòng mép trong. Foam nhỏ hơn, không còn cụm cầu trắng lớn. Các frame lấy từ clip tại 1, 76, 151, 226 và 300 cho thấy mask bọt khí và hình dáng dòng thay đổi, với context ngoài prototype đứng yên. Đây là bằng chứng chuyển động, không tự chứng minh nước đã realistic.

Không đánh dấu đạt đủ tám tiêu chí: hình dáng vẫn có mức stylized và các nếp flow còn gợi cảm giác dải vật liệu ở close-up. Foam đã bám bề mặt va chạm nhưng còn nhỏ và tương đối phẳng; splash ở camera toàn cảnh khá tinh tế, cần duyệt độ thuyết phục khi xem clip. Chưa đề nghị duyệt realistic hoàn toàn hoặc nhân rộng khi prototype chưa được duyệt.
