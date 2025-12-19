import os
from pygenpdf import *
import random

map_rgb = {"color1" : (250, 128, 114),
            "color2" : (255, 228, 196),
            "color3" : (222, 184, 135),
            "color4" : (255, 250, 205),
            "color5" : (127, 255, 0),
            "color6" : (60, 179, 113),
            "color7" : (127, 255, 212),
            "color8" : (206, 231, 255),
            "color9" : (221, 160, 221),
            "color10" : (255, 192, 203),
            "color11" : (250, 235, 215),
            "color12" : (211, 211, 211)}
colors = list(map_rgb.keys())

count_colors = {}
def set_count(color):
    if color not in count_colors:
        count_colors[color] = 1
    else:
        count_colors[color] += 1
def get_color():    
    index_rgb = random.randint(1, len(colors)) - 1
    color = colors[index_rgb]
    rgb = map_rgb[color]
    set_count(color)
    return Color().rgb(rgb[0],rgb[1],rgb[2])

def get_layout_framed():
    color = get_color()
    return VerticalLayout().framed_background(
                                    LineStyle().with_thickness(0.0).with_color(color),
                                    BackgroundStyle().with_color(color)
                                    )
def get_name_color(name):   
    rgb = map_rgb[name]    
    return Color().rgb(rgb[0],rgb[1],rgb[2])

def main():
    doc = Document()
    dir_now = os.path.dirname(os.path.abspath(__file__))
    doc.set_default_font(dir_now + "/liberation", "LiberationSans")
    doc.set_title("report genpdf")
    doc.set_paper_size(Size().A4())
    doc.set_head_page(Paragraph("report genpdf-rs from python").aligned(Alignment.RIGHT).styled(Style().bold().italic().with_font_size(8)))
    doc.set_margins(Margins().trbl(7,10,10,10))
    doc.set_line_spacing(0.9)    
    doc.set_font_size(9)
    
    columns = [1 for i in range(50)]
    
    table_coffe = TableLayout(columns).styled(Style().italic())
    table_coffe.set_cell_decorator(FrameCellDecorator().with_line_style(True, True, True, LineStyle().with_thickness(.1).with_color(Color().greyscale(150))))
    
    for i in range(50):
        row = []
        for j in columns:
            row.append(get_layout_framed().element(Paragraph("")))
        table_coffe.push_row(row)
    
    doc.push(table_coffe)    
    
    doc.push(Break(2))
    order = OrderedList()
    
    for c in count_colors:
        hl = HorizontalLayout([1,20])
        hl.push(VerticalLayout().framed_background(
                                    LineStyle(),
                                    BackgroundStyle().with_color(get_name_color(c))
                                    ).element(Paragraph("")))
        hl.push(Paragraph("   Count  %s"% (str(count_colors[c]))))
        order.push(hl)
        
    doc.push(order)
    
    doc.render_json_file(dir_now + "/background_2_test.pdf")
    
    
if __name__=="__main__":
    main()
