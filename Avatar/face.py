COLOR_FACE = "#000000"

class FaceMixin:
    def _draw_brow(self, draw, cx, cy, length, thickness, slope, inner_left):
        half = length / 2
        if inner_left:
            x_inner = cx + half
            x_outer = cx - half
        else:
            x_inner = cx - half
            x_outer = cx + half

        y_inner = cy + slope
        y_outer = cy

        t_inner = thickness * 1.0
        t_mid = thickness * 0.75
        t_outer = thickness * 0.25

        arch = thickness * 0.4
        x_mid = (x_inner + x_outer) / 2
        y_mid = (y_inner + y_outer) / 2 - arch

        top_inner = y_inner - t_inner / 2
        top_mid = y_mid - t_mid / 2
        top_outer = y_outer - t_outer / 2

        bot_outer = y_outer + t_outer / 2
        bot_mid = y_mid + t_mid / 2
        bot_inner = y_inner + t_inner / 2

        x_q1 = x_inner + (x_mid - x_inner) * 0.5
        x_q3 = x_mid + (x_outer - x_mid) * 0.5

        pts = [
            (x_inner, top_inner),
            (x_q1, top_inner + (top_mid - top_inner) * 0.6),
            (x_mid, top_mid),
            (x_q3, top_mid + (top_outer - top_mid) * 0.5),
            (x_outer, top_outer),
            (x_outer, bot_outer),
            (x_q3, bot_mid + (bot_outer - bot_mid) * 0.5),
            (x_mid, bot_mid),
            (x_q1, bot_inner + (bot_mid - bot_inner) * 0.6),
            (x_inner, bot_inner),
        ]

        draw.polygon(pts, fill=COLOR_FACE)

    def _draw_eye(self, draw, cx, cy, width, height, pupil_dx, pupil_dy, closed=False):
        half_w = width / 2
        half_h = height / 2

        if closed:
            draw.line(
                [(cx - half_w, cy), (cx + half_w, cy)],
                fill=COLOR_FACE,
                width=2,
            )
            return

        pupil_r_x = max(1, int(half_w * 0.35))
        pupil_r_y = max(1, int(half_h * 0.6))
        pcx = cx + pupil_dx
        pcy = cy + pupil_dy
        
        draw.ellipse(
            [pcx - pupil_r_x, pcy - pupil_r_y, pcx + pupil_r_x, pcy + pupil_r_y],
            fill=COLOR_FACE,
        )