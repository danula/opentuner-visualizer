from bokeh.embed import autoload_server
from collections import OrderedDict
from bokeh.plotting import *
from bokeh.models import HoverTool, TapTool, OpenURL, ColumnDataSource, Callback,GlyphRenderer

import pandas as pd
import sqlite3 as lite
import time

con = lite.connect('/home/kasun/projects/opentuner/examples/gccflags/opentuner.db/kasun-Satellite-L755.db')
cur = con.cursor()
   
def get_data():
   cur.execute("SELECT result_id, generation, desired_result.configuration_id, time,requestor,was_new_best "
               +"FROM desired_result INNER JOIN result ON desired_result.result_id = result.id WHERE result.state='OK'")
   rows = cur.fetchall()

   cols = ["result_id", "generation", "configuration_id", "time","requestor","was_new_best"]
   data = pd.DataFrame(rows, columns=cols)

   df = data[["result_id", "time", "was_new_best", "configuration_id"]]
   
   grouped = df.groupby('was_new_best')
   
   colors=["blue" if (val == 0) else "red" for val in df['was_new_best'].values]
   
   return df, colors, grouped.get_group(1)

df, colors,b = get_data()


source = ColumnDataSource(data=dict(
    x = df['result_id'],
    y = df['time'],
    conf_id = df['configuration_id'],
    fill_color = colors
))

source2 = ColumnDataSource(data=dict(
    x = b['result_id'],
    y = b['time'],
    conf_id = b['configuration_id']
))

TOOLS="resize,crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave,tap"

output_server("opentuner2")

p = figure(
tools=TOOLS, title="OpenTuner",
   x_axis_label='Result id', y_axis_label='time'
)


p.circle('x', 'y', conf_id='conf_id', fill_color='fill_color', line_color =None, source=source, size=3)
p.line('x', 'y', conf_id='conf_id', line_color="red", source=source2, size=3)

# q = p.select(dict(type=GlyphRenderer))
# r = r + list(set(q)-set(r))
#third = p.renderers[-1].data_source
# print(r)


callback=Callback(args=dict(source=source), code="""
    var arr = cb_obj.get('selected')['1d'].indices;
    if(arr.length > 0) {
        console.log(cb_obj.get('data')['x'][arr[0]]);
    }
    console.log(cb_obj.get('selected')['1d'].indices);
    /*callfunction(this);*/
""")    

taptool = p.select(dict(type=TapTool))
taptool.action=callback


hover =p.select(dict(type=HoverTool))
hover.tooltips = OrderedDict([
    ("Configuration ID", "@conf_id"),
    ("Result id", "@x"),
    ("Time", "@y")
])

print(autoload_server(p,cursession()))
show(p)

while True:
   df,colors, b = get_data()
   source.data['x'] = df['result_id']
   source.data['y'] = df['time']
   source.data['configuration_id'] = df['configuration_id']
   source.data['fill_color'] =  colors
    
   source2.data['x'] = b['result_id']
   source2.data['y'] = b['time']
   source2.data['configuration_id'] = b['configuration_id']
    
   cursession().store_objects(source)
   time.sleep(.50)
