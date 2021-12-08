from concurrent.futures import ThreadPoolExecutor
import dash



import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from data_functions import *
import numpy as np
import time
import wget
import os
import datetime
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
                #meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1, maximum-scale= 5, minimum-scale=0.4", }])
#app = dash.Dash(index_template='home.html')
app.title = 'COVID-19 Dashboard by CANARY GLOBAL INC.'

server=app.server


def define_variables(df_confirmed, df_vaccinated, df_deaths):
    global df_vac
    global df_con
    global df_dea
    global df_act
    global confirmed
    global vaccinated
    global deaths
    global total_confirmed
    global total_vaccinated
    global total_deaths
    global change_confirmed
    global change_vaccinated
    global change_deaths
    global recovery_rate
    global mortality_rate
    global cases_per_million
    df_confirmed.drop(['Province/State', 'Lat', 'Long'], axis=1, inplace=True)
    df_confirmed.rename(columns={'Country/Region': 'Country'}, inplace=True)
    df_vaccinated.drop(['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Province_State',
                        'Lat', 'Long_', 'Combined_Key', 'Population'], axis=1, inplace=True)
    df_vaccinated.rename(columns={'Country_Region': 'Country'}, inplace=True)
    df_deaths.drop(['Province/State', 'Lat', 'Long'], axis=1, inplace=True)
    df_deaths.rename(columns={'Country/Region': 'Country'}, inplace=True)
    df_vac = merge_countries(df_vaccinated).sort_values(by='Country')  # .drop(['12/13/20'], axis=1)
    df_con = merge_countries(df_confirmed).sort_values(by='Country')  # .drop(['12/13/20'], axis=1)
    df_dea = merge_countries(df_deaths).sort_values(by='Country')  # .drop(['12/13/20'], axis=1)
    df_con.columns = [df_con.columns[0]] + [fix_date(x) for x in df_con.columns[1:]]
    df_dea.columns = [df_dea.columns[0]] + [fix_date(x) for x in df_dea.columns[1:]]

    confirmed = date_wise(df_con.sum(axis=0))
    vaccinated = date_wise(df_vac.sum(axis=0), flag=1)
    deaths = date_wise(df_dea.sum(axis=0))
    total_confirmed = confirmed.Value.iloc[-1]
    total_vaccinated = vaccinated.Value.iloc[-1]
    total_deaths = deaths.Value.iloc[-1]
    change_confirmed = confirmed.Value.iloc[-1] - confirmed.Value.iloc[-2]
    change_vaccinated = vaccinated.Value.iloc[-1] - vaccinated.Value.iloc[-2]
    change_deaths = deaths.Value.iloc[-1] - deaths.Value.iloc[-2]

    if change_confirmed >= 0:
        change_confirmed = f'+{change_confirmed:,}'
    else:
        change_confirmed = f'-{-change_confirmed:,}'
    if change_vaccinated >= 0:
        change_vaccinated = f'+{int(change_vaccinated):,}'
    else:
        change_vaccinated = f'-{-int(change_vaccinated):,}'
    if change_deaths >= 0:
        change_deaths = f'+{change_deaths:,}'
    else:
        change_deaths = f'-{-change_deaths:,}'
    recovery_rate = 100 * total_vaccinated / (total_confirmed)
    mortality_rate = 100 * total_deaths / (total_confirmed)
    cases_per_million = 1e6 * total_confirmed / 7796127694

# getting data periodically
def update_data(period=4):
  while True:
    os.remove('data/time_series_covid19_confirmed_global.csv')
    wget.download('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv','./data')
    global df_confirmed
    df_confirmed = pd.read_csv('data/time_series_covid19_confirmed_global.csv')

    os.remove('data/time_series_covid19_recovered_global.csv')
    wget.download('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv','./data')
    global df_recovered
    df_recovered = pd.read_csv('data/time_series_covid19_recovered_global.csv')

    os.remove('data/time_series_covid19_deaths_global.csv')
    wget.download('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv','./data')
    global df_deaths
    df_deaths = pd.read_csv('data/time_series_covid19_deaths_global.csv')
    time.sleep(period*60*60)
    # print('updating data...')
    os.remove('data/covid-variants.csv')
    wget.download('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/variants/covid-variants.csv', './data')

    define_variables(df_confirmed, df_recovered, df_deaths)


if 'time_series_covid19_confirmed_global.csv' not in os.listdir('./data'):
    wget.download('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv', './data')
if 'time_series_covid19_vaccine_doses_admin_global.csv' not in os.listdir('./data'):
    wget.download('https://raw.githubusercontent.com/govex/COVID-19/master/data_tables/vaccine_data/global_data/time_series_covid19_vaccine_doses_admin_global.csv', './data')
if 'time_series_covid19_deaths_global.csv' not in os.listdir('./data'):
    wget.download('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv', './data')
if 'covid-variants.csv' not in os.listdir('./data'):
    wget.download('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/variants/covid-variants.csv', './data')

# importing data
df_confirmed = pd.read_csv('data/time_series_covid19_confirmed_global.csv')
df_vaccinated = pd.read_csv('data/time_series_covid19_vaccine_doses_admin_global.csv')
df_deaths = pd.read_csv('data/time_series_covid19_deaths_global.csv')
define_variables(df_confirmed, df_vaccinated, df_deaths)


# cards
card_1 = dbc.Card([
        # dbc.CardImg(src="assets/images/confirm.png", top=True),
        dbc.CardBody([
                html.H6("Confirmed", className='card_title'),
                html.H5(f"{change_confirmed}", className='card_changed'),
                html.H5(f"{total_confirmed:,}", className='card_value')
                ], className='card_1_body')], className='card_1')

card_2 = dbc.Card([
        # dbc.CardImg(src="assets/images/recovered.png", top=True),
        dbc.CardBody([
                html.H6("Vaccinated", className='card_title'),
                html.H5(f"{change_vaccinated}", className='card_changed'),
                html.H5(f"{change_vaccinated}", className='card_value')
                ], className='card_2_body')], className='card_2')

card_3 = dbc.Card([
        # dbc.CardImg(src="assets/images/deceased.png", top=True),
        dbc.CardBody([
                html.H6("Deceased", className='card_title'),
                html.H5(f"{change_deaths}", className='card_changed'),
                html.H5(f"{total_deaths:,}", className='card_value')
                ], className='card_3_body')], className='card_3')

# card_4 = dbc.Card([
#         # dbc.CardImg(src="assets/images/recovered.png", top=True),
#         dbc.CardBody([
#                 html.H6("Recovered", className='card_title'),
#                 html.H5(f"{change_vaccinated}", className='card_changed'),
#                 html.H5(f"{change_vaccinated}", className='card_value')
#                 ], className='card_2_body')], className='card_4')

##########################################

files = {'covid': 'data/covid_19_data.csv',
         'covid_line_list': 'data/COVID19_line_list_data.csv',
         'COVID19_open_line_list': 'data/COVID19_open_line_list.csv',
         'global_confirmed': 'data/time_series_covid_19_confirmed.csv',
         'global_deaths': 'data/time_series_covid_19_deaths.csv',
         'global_vaccinated': 'data/time_series_covid19_vaccine_doses_admin_global.csv'}

n = -1
df_top = for_map(df_con, df_vac, df_dea, flag='top')
countries = df_top['Country'].values
countries = np.append(countries, 'Global')
df_top = df_top.sort_values(by='Confirmed', ascending=False).iloc[:n]

################ world-map #################
df_map = for_map(df_con, df_vac, df_dea)
fig_map = create_map(df_map)
fig_map = html.Div(dcc.Graph(figure=fig_map, className='fig_map'), style={'padding':'1.25rem'})
############# Variant-map ##################

df_var = pd.read_csv('data/covid-variants.csv')
dates=df_var['date']
df_var.drop(columns=['date'],inplace=True)
df_var.insert(2,'Dates Till Reported',dates)
df_7=df_var[pd.to_datetime(df_var["Dates Till Reported"]) > datetime.datetime.now() - pd.to_timedelta("7day")]
fig_var = create_var(df_7)
fig_var = html.Div(dcc.Graph(figure=fig_var, className='fig_var'), style={'padding':'1.25rem'})
############# Variant-map ##################


fig_var_all = create_var_all(df_var)
fig_var_all = html.Div(dcc.Graph(figure=fig_var_all, className='fig_var'), style={'padding':'1.25rem'})
################ sunburst plot #############
df_continent = pd.read_csv('https://raw.githubusercontent.com/dbouquin/IS_608/master/NanosatDB_munging/Countries-Continents.csv')
df_continent.replace('Burkina', 'Burkina Faso', inplace=True)
df_continent.replace('Burma (Myanmar)', 'Burma', inplace=True)
df_continent.replace('Congo', 'Congo (Brazzaville)', inplace=True)
df_continent.replace('Congo, Democratic Republic of', 'Congo (Kinshasa)', inplace=True)
df_continent.replace('Russian Federation', 'Russia', inplace=True)

new = pd.DataFrame([['Africa', 'Congo (Brazzaville)'],
                    ['Africa', 'Congo (Kinshasa)'],
                    ['Europe', 'Czechia'],
                    ['Asia', 'Taiwan*'],
                    ['Africa', 'Western Sahara']], columns=df_continent.columns)
df_continent = df_continent.append(new)
df_sunburst = for_map(df_con, df_vac, df_dea, flag='top')
df_sunburst = pd.merge(df_continent, df_sunburst, on='Country')
df_sunburst.replace(0, np.nan, inplace=True)
df_sunburst.dropna(inplace=True)
fig_sunburst_confirmed = create_sunburst(df_sunburst, 'Confirmed')
fig_sunburst_vaccinated = create_sunburst(df_sunburst, 'vaccinated')
fig_sunburst_deaths = create_sunburst(df_sunburst, 'Deaths')

fig_sunburst_confirmed = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(figure=fig_sunburst_confirmed))),
                                             className='figure_confirmed'), className='figure_rows'))

fig_sunburst_vaccinated = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(figure=fig_sunburst_vaccinated))),
                                             className='figure_recovered'), className='figure_rows'))

fig_sunburst_deaths = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(figure=fig_sunburst_deaths))),
                                            className='figure_deceased'), className='figure_rows'))

############################################
# table card
table_card = dbc.Card([
                dbc.Table.from_dataframe(df_top.iloc[:-12], dark=True, bordered=True,
                                 hover=True, responsive=True, size='sm',
                                 className='container', style={'margin': 'auto'})], className='table_card')

############################################
#card container row
card_container_row = dbc.Row(dbc.Col(dbc.Row([
                        dbc.Col(html.Div(card_1), className='cards'),
                        dbc.Col(html.Div(card_2), className='cards'),
                        dbc.Col(html.Div(card_3), className='cards'),
                        # dbc.Col(html.Div(card_4), className='cards'),
                        ], className='cards_inside_row'), className='cards_col'),
    className='cards_row')

############################################
# tab items
dropdown_country = dbc.Card(dbc.CardBody(dbc.Row([
                                        dbc.Col(dbc.Input(placeholder="Search country...", type="text",
                                                      list='list-data', id='_cntry_name', value='India')),
                                        html.Datalist(id='list-data',
                                                      children=[html.Option(value=c) for c in countries])
                                        ]), className='tab_global'), className='tab_global')

dropdown_global = dbc.Card(dbc.CardBody(dbc.Row(dbc.Col(
                            dbc.InputGroup([
                                dbc.InputGroupAddon("Show top", addon_type="prepend", className='addon_text'),

                                dbc.Input(placeholder="10", type="number", min=1, max=180,
                                          step=1, id='_no_of_cntry', value=10),

                                dbc.InputGroupAddon("countries with", addon_type="prepend", className='addon_text'),

                                dbc.Select(id="_hgh_or_lw",
                                    options=[{"label": "lowest", "value": 'lowest'},
                                             {"label": "highest", "value": 'highest'}], value='highest'),

                                dbc.Select(id="_feature",
                                     options=[{"label": "confirmed", "value": 'Confirmed'},
                                              {"label": "vaccinated", "value": 'vaccinated'},
                                              {"label": "deceased", "value": 'Deaths'}], value='Confirmed'),

                                dbc.InputGroupAddon("cases!", addon_type="prepend", className='addon_text'),
                                 ], className='input_group'))), className='tab_global_card'), className='tab_global_card')

#############################################
##Add your info here

###########################################
# tabs
tabs = dbc.Row(dbc.Col([
    dbc.Card(dbc.Tabs(
        [
        dbc.Tab(dropdown_global, label="Global data", className='tab_global', tab_id="tab-1"),
        dbc.Tab(dropdown_country, label="Country wise data", className='tab_country', tab_id="tab-2"),
        ], id="_tabs", active_tab="tab-1"), className='tabs_card'),
    dbc.Button("Get results", color='#AAA', size="sm", className="button", block=True, id='button'),
                        ], className='tabs_column'),
    className='figure_rows')

#############################################
# global data

fig_bar = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_bar'))),
                                  className='figure_global'), className='figure_rows'))

# cdf
# fig_global_confirmed_cdf = confirm_cdf(df_con, 0)
fig_confirmed_cdf = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_confirmed_cdf'))),
                                            className='figure_confirmed'), className='figure_rows'))

# fig_global_recovered_cdf = confirm_cdf(df_rec, 1)
fig_recovered_cdf = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_recovered_cdf'))),
                                            className='figure_recovered'), className='figure_rows'))

# fig_global_deceased_cdf = confirm_cdf(df_dea, 2)
fig_deceased_cdf = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_deceased_cdf'))),
                                           className='figure_deceased'), className='figure_rows'))

# daily
# fig_global_confirmed_daily = confirm_daily(df_con, 0)
fig_confirmed_daily = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_confirmed_daily'))),
                                              className='figure_confirmed'), className='figure_rows'))

# fig_global_recovered_daily = confirm_daily(df_rec, 1)
fig_recovered_daily = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_recovered_daily'))),
                                              className='figure_recovered'), className='figure_rows'))

# fig_global_deceased_daily = confirm_daily(df_dea, 2)
fig_deceased_daily = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_deceased_daily'))),
                                             className='figure_deceased'), className='figure_rows'))

# rate
# fig_global_confirmed_rate = confirm_rate(df_con, 0)
fig_confirmed_rate = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_confirmed_rate'))),
                                             className='figure_confirmed'), className='figure_rows'))

# fig_global_recovered_rate = confirm_rate(df_rec, 1)
fig_recovered_rate = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_recovered_rate'))),
                                             className='figure_recovered'), className='figure_rows'))

# fig_global_deceased_rate = confirm_rate(df_dea, 2)
fig_deceased_rate = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_deceased_rate'))),
                                            className='figure_deceased'), className='figure_rows'))


###### default output ######
[f1,f2,f3,f4,f5,f6,f7,f8,f9,f10] = [
         create_global_bar(df_top),
         confirm_cdf(df_con, c=0), confirm_cdf(df_vac, c=1),
             confirm_cdf(df_dea, c=2),

         confirm_daily(df_con, c=0), confirm_daily(df_vac, c=1),
             confirm_daily(df_dea, c=2),

         confirm_rate(df_con, c=0), confirm_rate(df_vac, c=1),
             confirm_rate(df_dea, c=2)]


@app.callback([
    Output("fig_bar", "figure"),
    Output("fig_confirmed_cdf", "figure"), Output("fig_recovered_cdf", "figure"),
        Output("fig_deceased_cdf", "figure"),
    Output("fig_confirmed_daily", "figure"), Output("fig_recovered_daily", "figure"),
        Output("fig_deceased_daily", "figure"),
    Output("fig_confirmed_rate", "figure"), Output("fig_recovered_rate", "figure"),
        Output("fig_deceased_rate", "figure")],
    [Input('button', 'n_clicks')],
    state = [State("_no_of_cntry", "value"), State("_hgh_or_lw", "value"), State("_feature", "value"),
     State("_cntry_name", "value"), State("_tabs", "active_tab")])

def output_text(n_clicks, _no_of_cntry, _hgh_or_lw, _feature, _cntry_name, _tabs):

    if _tabs == 'tab-1':
        _cntry_name = '#'

    output = [f1, f2, f3, f4, f5,
              f6, f7, f8, f9, f10]

    if n_clicks:
        output = [create_global_bar(df_top, _no_of_cntry, _feature, _hgh_or_lw, _cntry_name),
                  confirm_cdf(df_con, c=0, cntry_name=_cntry_name),
                  confirm_cdf(df_vac, c=1, cntry_name=_cntry_name),
                  confirm_cdf(df_dea, c=2, cntry_name=_cntry_name),

                  confirm_daily(df_con, c=0, cntry_name=_cntry_name),
                  confirm_daily(df_vac, c=1, cntry_name=_cntry_name),
                  confirm_daily(df_dea, c=2, cntry_name=_cntry_name),

                  confirm_rate(df_con, c=0, cntry_name=_cntry_name),
                  confirm_rate(df_vac, c=1, cntry_name=_cntry_name),
                  confirm_rate(df_dea, c=2, cntry_name=_cntry_name)]

        return output

    elif n_clicks==None:
        return output


##########################
# app
company_logo = html.A(dbc.CardImg(src="assets/images/faster_Canary_logo_White-animation.gif", top=True, className='image_link'), href='https://www.canarydetect.com/', target="_blank", className='image_1')
company_logo_footer = html.A(dbc.CardImg(src="assets/images/faster_Canary_logo_White-animation.gif", top=True, className='image_link_footer'), href='https://www.canarydetect.com/', target="_blank", className='image_link_footer')
#kaggle = html.A(dbc.CardImg(src="assets/images/kaggle.svg", top=True, className='image_link'), href='', target="_blank")
#medium = html.A(dbc.CardImg(src="assets/images/medium.png", top=True, className='image_link'), href='', target="_blank")

profile_links_top = dbc.Row([dbc.Col(company_logo, width=20, className='link_col'),
 #                            dbc.Col(linkedin, width=2, className='link_col'),
 #                            dbc.Col(kaggle, width=2, className='link_col'),
  #                           dbc.Col(medium, width=2, className='link_col'),
                            ], className='link_icons')

#profile_links = dbc.Row([dbc.Col(company_logo_footer,width=40, className='link_col'),
                        #dbc.Col(company_logo_footer, width=20, className='link_col'),
      #                   dbc.Col(linkedin, width=2, className='link_col'),
     #                    dbc.Col(kaggle, width=2, className='link_col'),
     #                    dbc.Col(medium, width=2, className='link_col'),
    #                     dbc.Col(width=2, className='link_col')
         #                ], className='link_icons')


heading = html.Div(dbc.Row([dbc.Col(html.H3("Canary Global Covid-19 Dashboard for Deep Analysis ( Compatible with desktop)", className='page_title'), width=8, className='header_col1'),
                            dbc.Col(profile_links_top, width=4, className='header_col2')],
                            className='header_container'))

text_1 = dcc.Markdown('''Johns Hopkins University has made an excellent [dashboard](https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6) 
using the affected cases data. Data is extracted from the google sheets associated and made available [here](https://github.com/CSSEGISandData/COVID-19).''')
text_2 = dcc.Markdown('''From [World Health Organization](https://www.who.int/emergencies/diseases/novel-coronavirus-2019) - On 31 December 2019, WHO was alerted
to several cases of pneumonia in Wuhan City, Hubei Province of China. The virus did not match any other known virus. This raised concern because when a virus is
new, we do not know how it affects people.
So daily level information on the affected people can give some interesting insights when it is made available to the broader data science community.
The purpose of this dashboard is to spread awareness and provide some useful insights on COVID-19 by the means of data.''')
text_3 = dcc.Markdown('''Canary Global Inc. ([Canary](https://www.canarydetect.com/)) is a medical technology company that builds revolutionary diagnostic platforms and services. 
Combined with AI-powered intelligence, Canary’s nano-sensor technology can detect diseases, characterize the nature and location of cancers, and predict 
and monitor responses to therapy.Canary technology is based on robust science derived from decades of published research, cutting-edge digital technology and 
a flexible platform design to enable multiple uses including disease diagnosis and precision medicine''')
text_4 = dcc.Markdown("Our mission is to save lives and help conquer Covid, Cancer and other life-threatening conditions. With our breath and liquid testing platforms,"
                      " we can predict disease risk, identify and characterize presence of disease, and track and monitor responses to therapies and medications.")
text_5 = dcc.Markdown("Our team works with key opinion leaders, clinicians, regulatory experts, data scientists and commercial partners to design the most rigorous"
                      " and fastest pathway to develop the products so patients and their doctors can use them to improve and save lives.Canary Global Inc. wants"
                      " to change healthcare and make safe and accurate rapid testing accessible. ")

text_6 = dcc.Markdown("All viruses, including SARS-CoV-2, the virus that causes COVID-19, change over time. Most changes have little to no impact on the virus’ "
                      "properties. However, some changes may affect the virus’s properties, such as how easily it spreads, the associated disease severity, or "
                      "the performance of vaccines, therapeutic medicines, diagnostic tools, or other public health and social measures")

text_8 = dcc.Markdown(" A [team](https://www.canarydetect.com/about) built around globally-diverse industry experience, sharing a common passion for out the box "
                      "thinking and a drive towards making diagnostic health services widely accessible.  ")
text_9 = dcc.Markdown("For more information about Canary Global Inc.’s products and services or to speak with someone from our team, please "
                      "[contact](https://www.canarydetect.com/contact) us. ")
summary = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
                                    html.Div('About this Medical Company', className='ques'),
                                    html.Div(text_3, className='ans'),
                                    html.Hr(style={'borderColor': 'white', 'border': '1.5'}),
                                    html.Div('Mission', className='ques'),
                                    html.Div(text_4, className='ans'),
                                    html.Hr(style={'borderColor': 'white', 'border': '1.5'}),
                                    html.Div('Our Vision', className='ques'),
                                    html.Div(text_5, className='ans'),
                                    html.Hr(style={'borderColor': 'white', 'border': '1.5'}),
                                    html.Div('Our Team', className='ques'),
                                    html.Div(text_8, className='ans'),
                                    html.Hr(style={'borderColor': 'white', 'border': '1.5'}),
                                    html.Div('About COVID-19 Dashboard BY CANARY GLOBAL INC.', className='ques'),
                                    html.Div(text_2, className='ans'),
                                    html.Hr(style={'borderColor': 'white', 'border': '1.5'}),
                                    html.Div('Source of the COVID-19 data:', className='ques'),
                                    html.Div(text_1, className='ans'),
                                    html.Hr(style={'borderColor': 'white', 'border': '1.5'}),
                                    html.Div('Contact Us', className='ques'),
                                    html.Div(text_9, className='ans'),
                                    html.Hr(style={'borderColor': 'white', 'border': '1.5'}),
                                    ]), className='figure_summary'), className='figure_rows'))

last_time = np.random.randint(6, 24)
last_update = f'This data was last updated {last_time} hours ago.'
data_update = dbc.Row(dbc.Col(html.H6(last_update), className='last_update_1'),
                      className='last_update')

footer = html.Div(dbc.Row([company_logo_footer], className='footer_container'))
footer_1 = html.Div(dbc.Row([dcc.Markdown(" Saving Lives Through Early Disease Detection" ,className='footer_container_line')], className='footer_container'))
app.layout = html.Div(children=[
    heading,
    fig_map,
    fig_var,
    fig_var_all,
    html.Div(dbc.Row([
                dbc.Col([table_card, data_update], className='table_container', width=4),
                dbc.Col([
                    ##ADD OWAIS Plot_Here
                    card_container_row,
                    tabs,
                    fig_bar,
                    fig_confirmed_cdf,
                    fig_recovered_cdf,
                    fig_deceased_cdf,
                    fig_confirmed_daily,
                    fig_recovered_daily,
                    fig_deceased_daily,
                    fig_confirmed_rate,
                    fig_recovered_rate,
                    fig_deceased_rate,
                    fig_sunburst_confirmed,
                    fig_sunburst_vaccinated,
                    fig_sunburst_deaths,
                    summary
                    ], width=8),
                ]), className='table_card_row'),
        footer,
footer_1
        ])

executor = ThreadPoolExecutor(max_workers=1)
executor.submit(update_data)
if __name__ == '__main__':

    app.run_server(debug=True,dev_tools_ui=False,dev_tools_serve_dev_bundles=False,port="8000")




