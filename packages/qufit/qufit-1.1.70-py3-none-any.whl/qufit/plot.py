import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from plotly.subplots import make_subplots

rows = 1
vertical_spacing=0.2/rows
colorbar_= True

def subplots2D(image,height=400,width=900,sharex=False,sharey=False,x_title=None,y_title=None,
               colorbar=True,title='',layout={},col_w=None,cols=2):
    
    global rows, vertical_spacing, colorbar_
    colorbar_ = colorbar

    num = len(image)
    rows = num // cols if num % cols == 0 else num // cols + 1
    vertical_spacing=0.2/rows
    height = height if rows<2 else 200
    
    cols_, column_widths = (cols * 2,[0.9/cols,0.1/cols]*cols) if colorbar else (cols,[1/cols]*cols)
    print(f'{column_widths=}')
    column_widths = column_widths if col_w is None else col_w
    fig = go.Figure(layout=go.Layout(height=height*rows, width=width))
    fig = make_subplots(rows=rows,cols=cols_,shared_xaxes=sharex,
                        shared_yaxes=sharey,
                       column_widths=column_widths,
                       row_heights=[1/rows]*rows,
                       vertical_spacing=vertical_spacing,
                       horizontal_spacing=0.04,
                       x_title=x_title,
                       y_title=y_title,
                       figure=fig)
    print(rows,cols)
    for i,trace in enumerate(image):
        if colorbar:
            r, c = (i//cols+1,2*(i%cols)+1) #if i%2==0 else (i//cols+1,3)
#             print(i,r,c)
        else:
            r, c = (i//cols+1,i%cols+1) #if i%2==0 else (i//2+1,2)
        
        for tr in trace:
            fig.add_trace(tr,row=r,col=c)
            try:
                yanchor = 1-(i//2*2+1)/2/rows*(1-vertical_spacing*(rows-1)) - vertical_spacing*(i//2)
                x_bar, y_bar = (0.39,yanchor) if i%2==0 else (0.91,yanchor)
                name = tr.name
                if name[:2] == 'cb':
                    fig.update_traces(colorbar=dict(x=x_bar,y=y_bar,len=0.8/rows,title=name[2:],
                                                    nticks=5),row=r,col=c)
            except:
                pass
            
    legend=dict(
#         x=1,
#         y=1,
        # traceorder="reversed",
        title_font_family="Times New Roman",
        font=dict(
            family="Courier",
            size=12,
            color="black"
        ),
#         bgcolor="LightSteelBlue",
#         bordercolor="Black",
        borderwidth=1
    )
    fig.update_layout(margin=dict(r=0,t=30,b=55,l=80),showlegend=True,legend=legend,title=title,**layout)#,xaxis=dict(fixedrange=True),yaxis=dict(fixedrange=True))

    return fig

def add_plot(fig,tr,row=0,col=0):
    global rows, vertical_spacing, colorbar_
    if colorbar_:
        r, c = (row,2*col+1)#(row,1) if col==1 else (row,3)
    else:
        r, c = (row,col)#(row,1) if col==1 else (row,2)
    fig.add_trace(tr,row=r,col=c)
    try:
        name = tr.name
        yanchor = 1-(r*2-1)/2/rows*(1-vertical_spacing*(rows-1)) - vertical_spacing*(r-1)
        x_bar, y_bar = (0.39,yanchor) if c==1 else (0.91,yanchor)
        if name[:2] == 'cb':
            fig.update_traces(colorbar=dict(x=x_bar,y=y_bar,len=0.8/rows,title=name[2:],
                                                            nticks=5),row=r,col=c)
    except:
        pass
    
def add_title(fig,title):
    name = fig.layout.title.text
    name += f'{title}'
    fig.update_layout(title=name)
    
def set_title(fig,title):
    name = f'{title}'
    fig.update_layout(title=name)