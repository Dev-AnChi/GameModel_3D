# Tiến độ hiện tại

File mới nhất: Blender/Wandering_Alchemist_Phase6A_Wood.blend.
Blender MCP xác nhận Blender 5.2.2 LTS / protocol 13. Backup trước Pass A được lưu trong Blender/Backups/Before_Phase6_20261010_151338.blend.

- Silhouette Reference Rebuild giữ nguyên.
- ARCHIVE vẫn ẩn trong viewport/render.
- 176 object gỗ được gắn 5 material PBR khác nhau.
- 20 map PNG 2048 × 2048 tự tạo: BaseColor, Roughness, Normal, Height.
- Height được lưu làm tài nguyên; không nối displacement để tránh biến dạng bề mặt.
- Normal và Roughness nối vào shader thật; BaseColor có variation nhỏ theo object.
- Render trung tính trước/sau và cận cảnh gỗ/bánh/cửa sau đã kiểm tra trực quan.

Chưa hoàn tất: end-grain riêng, wear geometry, UV atlas/texel density, bake variation theo object và kiểm thử glTF. UV hiện phục vụ material gỗ, có thể chồng vùng để tái sử dụng texture; chưa phải UV atlas xuất bán. Các material mái, kính và kim loại chưa được nâng cấp trong Pass A này.


Phase 6.5A: 3 verified CC0 texture sets, 9 maps, four material studies, four selected component trials, neutral before/after renders. Bulk integration and Phase 6.5B–E pending material review.
