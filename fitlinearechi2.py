from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Circle, CheckboxGroup, FileInput, Button, TextInput, Paragraph,  DataTable, TableColumn
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.tools import LassoSelectTool, TapTool, HoverTool, BoxSelectTool, WheelZoomTool, BoxZoomTool, ResetTool

from bokeh.models.callbacks import CustomJS
from scipy.optimize import curve_fit 

from bokeh.colors import named 

from base64 import b64decode
import pandas as pd
import numpy as np
import io


#### i print vengono stampati a terminale e sono utili in fase di programmazione






p = figure(plot_height=500,  tools='', title="plot con errori")
p.toolbar.logo = None
reset=ResetTool()
box_selection=BoxSelectTool()
lasso_select = LassoSelectTool(select_every_mousemove=False)
box_zoom=BoxZoomTool()
tooltips = [("index", "$index"), ("(time,signal)", "($x, $y)")]
hover1 = HoverTool(tooltips=tooltips)   #hover lo faccio apparire quando faccio il grafico, altrimenti non funziona
tools = ( reset, box_zoom,box_selection)
p.add_tools(*tools)


p1 = figure(plot_height=250, tools='', title="plot dei residui")
p1.toolbar.logo = None
reset=ResetTool()
box_selection=BoxSelectTool()
lasso_select = LassoSelectTool(select_every_mousemove=False)
box_zoom=BoxZoomTool()
tooltips = [("index", "$index"), ("(time,signal)", "($x, $y)")]
hover1 = HoverTool(tooltips=tooltips)   #hover lo faccio apparire quando faccio il grafico, altrimenti non funziona
tools = ( reset, box_zoom,box_selection)
p1.add_tools(*tools)




paragrafo1 = Paragraph(text="Scegliere il file .ods da analizzare:", width=600, height=10)



# funzione che parte quando faccio il load del file: carica i dati
# nota la presenza delle variabili globali, perche i dati servono in funzioni successive
def upload_fit_data(attr, old, new):  # la parentesi ha argomenti perche funzione di callback infatti il file input ha on_change
    # i print sono per controllo! vengon stampati nel pompt
    global nomi, s1, df1
    print("data upload succeeded")
    #to convert the base64 string to what you want and plot the data.
    decoded = b64decode(new)
    f = io.BytesIO(decoded)
    df = pd.read_excel(f, engine="odf")
    nomi=list(df.columns)#estraggo i nomi delle colonne
    df1 = pd.DataFrame(data=df.values,columns=["col1", "col2", "col3"])#rinomino le     colonne per avere un unico programma
#print(df1)
    s1 = ColumnDataSource(data=dict(x=df1.col1, y=df1.col2))    #dati prima e seconda colonna 
file_input = FileInput(accept=".csv,.ods") #se vuo formato diverso da csv devi cambiare la funzione precedente di pandas:new_df = pd.read_csv(f)
file_input.on_change('value', upload_fit_data)





#inizialmente la tabella  vuota
source = ColumnDataSource(dict(x=[], y=[]))
#voglio 3 colonne corrispondenti ai 2 parametri e 1 per i nomi
columns = [
    TableColumn(field="t", title=" "),
    TableColumn(field="x", title="m"),
    TableColumn(field="y", title="q")
]

#widget di bokeh 
spazio1 = Paragraph(text=" ", width=600, height=50)
paragrafo_funzione = Paragraph(text=" ", width=600, height=50)    
table = DataTable(source=source, columns=columns, width=400, height=100, index_position=None)
tau_print = Paragraph(text=" ", width=600, height=50)   # preparo un paragrafo vuoto
spazio2 = Paragraph(text=" ", width=600, height=200)


def fai_grafico():
  p.circle( x='x', y='y', size=10, source=s1, color="black", alpha=1, legend_label="dati acquisiti")  
  p.legend.location = "bottom_right"
  # create the coordinates for the errorbars
  err_xs = []
  err_ys = []
  for a, b, c in zip(df1.col1, df1.col2, df1.col3):
    err_xs.append((a, a))
    err_ys.append((b - c, b + c))

  p.multi_line(err_xs, err_ys, color='black', line_width=2)



  def retta(x, m, q): 
    return m*x+q


  popt, pcov = curve_fit(retta, df1.col1, df1.col2)
# usando gli errori in y come nella riga qui sotto, gli errori sui valori trovati sono piu grandi: strano
#popt, pcov = curve_fit(retta, df1.col1, df1.col2, absolute_sigma=True, sigma = df1.col3)
  sigma = np.sqrt(np.diag(pcov))
  ans=retta(df1.col1, *popt)

  p.line( df1.col1, ans, color="red", alpha=1, legend_label="fit") 
  
  
  p.add_tools(hover1)
  p.xaxis.axis_label = nomi[0]
  p.yaxis.axis_label = nomi[1]
  
  
    #per avere una tabella piu leggibile trasformo i vari param e perr in stringhe formattando i numeri con la notazione esponenziale con 2 cifre dopo la virgola
  table.source.data = dict(t=["Coefficienti", "Std. Dev."], 
      x=["{:.2e}".format(popt[0]), "{:.2e}".format(sigma[0])], 
      y=["{:.2e}".format(popt[1]), "{:.2e}".format(sigma[1])])

  paragrafo_funzione.text="\n\n\nFunzione utilizzata per il fit: y=mx+q" 


  
  
  
  
  
  res = df1.col2 - retta(df1.col1, *popt)
  p1.circle(df1.col1, res, size=10, color="blue")
  p1.add_tools(hover1)
  p1.xaxis.axis_label = nomi[0]
  p1.yaxis.axis_label = nomi[1]
  
  
  
  def chi2(y_measure,y_predict,errors):
    """Calculate the chi squared value given a measurement with errors and prediction"""
    return np.sum( (y_measure - y_predict)**2 / errors**2 )

  def chi2reduced(y_measure, y_predict, errors, number_of_parameters):
    """Calculate the reduced chi squared value given a measurement with errors and prediction,
    and knowing the number of parameters in the model."""
    return chi2(y_measure, y_predict, errors)/(y_measure.size - number_of_parameters)

  chiquadroridotto = chi2reduced(df1.col2,ans,df1.col3,popt.size)
  tau_print.text="Chi2 pari a " +  "{:.2e}".format(chiquadroridotto)
  
  
  
  
  
  
       
grafico_button = Button(label="Clicca per plot e fit", button_type="primary")
grafico_button.on_click(fai_grafico)







#col1=column(paragrafo1, row([file_input,grafico_button]),  p, p1 )
#col2=column(spazio1,paragrafo_funzione, table, tau_print, spazio2,ex_button)
#curdoc().add_root(row([col1, col2]))



col1=column(paragrafo1, file_input, spazio1, grafico_button,  spazio2,paragrafo_funzione, table, tau_print)

col2=column(p, p1 )
curdoc().add_root(row([col1, col2]))
















