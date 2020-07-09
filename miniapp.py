from flask import Flask, render_template, flash, request
from flask_table import Table, Col, LinkCol
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from bs4 import BeautifulSoup
import requests

Location = "minneapolis" #Change to set search location

#App config
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


class ItemTable(Table):
    tabname = Col('Name')
    tabprice = Col('Price')
    tablink = LinkCol('Name', 'static', anchor_attrs={'class': 'myclass'})


class Item(object):
    def __init__(self, tabname, tabprice, tablink):
        self.tabname = tabname
        self.tabprice = tabprice
        self.tablink = tablink
 
class ReusableForm(Form):
    make = TextField('Make:', validators=[validators.required()])
    model = TextField('Model:', validators=[validators.required()])
    minprice = TextField('Minimum Price:', validators=[validators.required()])
    maxprice = TextField('Maximum Price:', validators=[validators.required()])
 
 

def Saabscrape(make, model, sorttype, minprice, maxprice):
    if sorttype == 'new':
        sort = 'date'
    elif sorttype == 'old':
        sort = 'rel'
    elif sorttype == 'high':
        sort = 'pricedsc'
    elif sorttype == 'low':
        sort = 'priceasc'

        
    if minprice == '':
        minprice = '0'
    if maxprice == '':
        maxprice = '0'

    currentpage = 0
    
    cardata = []
    while currentpage < 3: #Set number of max pages here
        url1 = 'https://' + Location + '.craigslist.org/search/sss?'
        urlpage = 's=' + str(currentpage*120)
        urlquer = '&query='
        url2 = '&sort=' + sort + '&srchType=T'
        url3 = '&min_price=' + minprice + '&max_price=' + maxprice
        url = url1 + urlpage + urlquer + make +  '+' + model + url2 + url3
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        totalentries = soup.find(class_='totalcount').text
        if int(totalentries) > 120:
            currentpage += 1
        else:
            currentpage = 3 #set max page count here
        for result in soup.find_all(class_='result-info'):
            carname = result.find(class_='result-title')
            price = result.find(class_='result-price')
            link = result.find('a', href=True)
            linktext = link['href']
            if price != None:
                cardata.append(Item(carname.text, price.text, linktext))
    return cardata

@app.route("/", methods=['GET', 'POST'])
def main():
    form = ReusableForm(request.form)

    table = ''
    sorttype = ''
    print(form.errors)
    if request.method == 'POST':
        make=request.form['make']
        model=request.form['model']
        minprice = request.form['minprice']
        maxprice = request.form['maxprice']
        sorttype = request.form.get('sorting')
        results = Saabscrape(make, model, sorttype, minprice, maxprice)
        table = ItemTable(results)
 
    return render_template('main.html', form=form, table=table)
 
if __name__ == "__main__":
    app.run()

