"""Member B: expense category pie chart (Python standard library only).

Commands:
    py pie_chart.py           # real data from expenses.db
    py pie_chart.py --demo    # example chart, no database changes
"""

from contextlib import closing
from html import escape
from math import cos, pi, sin
from pathlib import Path
import sqlite3
import sys

FOLDER = Path(__file__).resolve().parent
DB_FILE = FOLDER / "expenses.db"
COLORS = [
    "#4F46E5", "#06B6D4", "#F59E0B", "#10B981", "#EC4899",
    "#8B5CF6", "#F97316", "#84CC16", "#64748B", "#EF4444",
]


def read_expenses():
    """Read category totals without modifying A's SQLite database."""
    if not DB_FILE.is_file():
        raise FileNotFoundError(f"找不到 {DB_FILE}，請先確認資料庫在同一資料夾。")
    with closing(sqlite3.connect(str(DB_FILE))) as conn:
        return conn.execute(
            """
            SELECT COALESCE(NULLIF(TRIM(category), ''), '其他') AS name,
                   SUM(amount) AS total
            FROM expenses
            WHERE amount > 0
            GROUP BY name
            ORDER BY total DESC
            """
        ).fetchall()


def build_svg(data):
    total = sum(float(value) for _, value in data)
    width, height = 1000, max(560, 160 + 40 * len(data))
    cx, cy, radius = 255, 300, 178

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        '<style>text{font-family:"Microsoft JhengHei","Noto Sans TC",sans-serif;fill:#172033}</style>',
        '<text x="60" y="62" font-size="32" font-weight="700">支出分類圓餅圖</text>',
        f'<text x="60" y="100" font-size="19" fill="#475569">總支出：NT$ {total:,.2f}</text>',
        '<text x="495" y="151" font-size="22" font-weight="700">分類明細</text>',
    ]

    current = -pi / 2
    for i, (category, value) in enumerate(data):
        amount = float(value)
        portion = amount / total
        angle = 2 * pi * portion
        color = COLORS[i % len(COLORS)]
        category_xml = escape(str(category))

        if len(data) == 1:
            shape = f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{color}"/>'
        else:
            x1, y1 = cx + radius * cos(current), cy + radius * sin(current)
            x2, y2 = cx + radius * cos(current + angle), cy + radius * sin(current + angle)
            large = int(angle > pi)
            shape = (
                f'<path d="M {cx} {cy} L {x1:.3f} {y1:.3f} '
                f'A {radius} {radius} 0 {large} 1 {x2:.3f} {y2:.3f} Z" '
                f'fill="{color}" stroke="white" stroke-width="2"/>'
            )
        parts.append(f'<g><title>{category_xml}: NT$ {amount:,.2f} ({portion:.1%})</title>{shape}</g>')

        if portion >= 0.07:
            center_angle = current + angle / 2
            tx = cx + radius * 0.63 * cos(center_angle)
            ty = cy + radius * 0.63 * sin(center_angle)
            parts.append(
                f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="18" '
                f'font-weight="700" fill="white" text-anchor="middle" '
                f'style="fill:white">{portion:.1%}</text>'
            )
        current += angle

        legend_y = 200 + i * 40
        display_name = str(category) if len(str(category)) <= 19 else str(category)[:18] + "…"
        parts.append(f'<rect x="495" y="{legend_y - 18}" width="19" height="19" rx="4" fill="{color}"/>')
        parts.append(
            f'<text x="530" y="{legend_y - 2}" font-size="17">'
            f'{escape(display_name)}：NT$ {amount:,.2f}（{portion:.1%}）</text>'
        )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    demo = len(sys.argv) > 1 and sys.argv[1] == "--demo"
    if demo:
        rows = [("食物", 400.0), ("娛樂", 200.0), ("交通", 50.0)]
        output = FOLDER / "pie_chart_demo.svg"
    else:
        try:
            rows = read_expenses()
        except (OSError, sqlite3.Error) as exc:
            print(f"資料庫讀取失敗：{exc}")
            return 1
        if not rows:
            print("資料庫沒有支出紀錄。請先執行 py v1_0.py 新增支出。")
            return 1
        output = FOLDER / "pie_chart.svg"

    output.write_text(build_svg(rows), encoding="utf-8")
    print(f"圓餅圖已產生：{output}")
    print(f"開啟方式：start {output.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
