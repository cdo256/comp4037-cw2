#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import plotly.express as px
import fish
import lca
import survey
import fooddb
import plotly.io as pio


# In[2]:


# Mouse rendering issues
#pio.renderers.default = 'browser'
from IPython.core.display import HTML
HTML("""
<style>
    .js-plotly-plot .plotly .cursor-crosshair {
        cursor: crosshair !important;
    }
    .js-plotly-plot .plotly .cursor-pointer {
        cursor: pointer !important;
    }
</style>
""")


# In[3]:


jp_lca_df = lca.load()
fish_env_info_df, fish_weighting_df, fish_matching_df = fish.load()
products_df, categories_df = fooddb.load()
survey_df = survey.load()


# In[4]:


jp_lca_df.columns


# In[5]:


products_df


# In[6]:


products_df, categories_df, ingredients_df = fooddb.clean(products_df, categories_df)


# In[26]:


survey_df.head(500
            )


# In[8]:


diet_info = pd.DataFrame({
    'diet_group': ['vegan','veggie','fish','meat50','meat','meat100'],
    'rank': [1,2,3,4,5,6],
    'color': ['#7AFF93','#1DB887','#3988C4','#FF7E96','#E9677F','#C25252'],
    'label': ['Vegan','Vegetarian','Fish Eaters','Low Meat Maters','Medium Meat Eaters','High Meat Eaters']
})

diet_color_map = dict(zip(diet_info['diet_group'], diet_info['color']))
diet_label_map = dict(zip(diet_info['diet_group'], diet_info['label']))

diet_info


# In[9]:


#TODO: We want a weighted aggregation, so large groups aren't counted disporoportianately in the average.
#total_participants = survey_df['n_participants'].sum()
#survey_df['weighted_mean_ghgs'] = survey_df['mean_ghgs']# * survey_df['n_participants'] / total_participants
#survey_df['weighted_mean_land'] = survey_df['mean_land'] #* survey_df['n_participants'] / total_participants
#survey_df['weighted_mean_watscar'] = survey_df['mean_watscar'] #* survey_df['n_participants'] / total_participants
#survey_df['weighted_mean_eut'] = survey_df['mean_eut'] #* survey_df['n_participants'] / total_participants
#survey_df['weighted_mean_ghgs_ch4'] = survey_df['mean_ghgs_ch4'] #* survey_df['n_participants'] / total_participants
#survey_df['weighted_mean_watuse'] = survey_df['mean_watuse'] #* survey_df['n_participants'] / total_participants

#survey_df = survey_df.reset_index()
df = pd.merge(survey_df, diet_info, on='diet_group')
print(df.columns)


# In[10]:


from plotly.subplots import make_subplots
import plotly.graph_objects as go

#fig1 = px.box(survey_df, x='diet_group', y='mean_ghgs')
#fig1 = go.Box(x=survey_df['diet_group'], y=survey_df['mean_ghgs'])
 


#grid = go.Figure()
#(rows=1, cols=2, subplot_titles=("mean GHG", "Mean Land Use"))

subcharts = [
    [
        ('mean_ghgs', 'Mean GHG (kg d⁻¹)'),
        ('mean_land', 'Mean Land Use (m² d⁻¹)')
    ],
    [
        ('mean_ghgs_ch4', 'Mean CH4 (kg d⁻¹)'),
        ('mean_watscar', 'Mean Water Scarcity')
    ],
    [
        ('mean_eut', 'Mean Eutrophication (gPO⁴ e d⁻¹)'),
        ('mean_watuse', 'Mean Water Use (m³ d⁻¹)')
    ]
]

titles_joined = [title for row in subcharts for (key, title) in row]

# Citing https://doi.org/10.1038/s43016-023-00795-w -- TODO
grid = make_subplots(row_heights=[600]*3, rows=3, cols=2,
                     subplot_titles=titles_joined,
                     shared_xaxes='rows')
grid.update_layout(title_text='Environmental Impact by Diet',height=900)

for row in range(3):
    for col in range(2):
        #fig = go.Figure()
        #for val, color in zip(survey_df['diet_group'], survey_df['
        grid.add_trace(
            go.Violin(x=df['diet_group'], y=df[subcharts[row][col][0]],
                      points=False, width=1.5), col=col+1, row=row+1)

grid.update_layout(showlegend=False)

grid.show()


# In[11]:


#weighted_sum = lambda x: np.average(x, weights=survey_df.loc[x.index, 'n_participants'])
#
#df = survey_df.groupby('diet_group').agg(
#    weighted_mean_ghgs = ('mean_ghgs', weighted_sum),
#    
#)
diet_group_df = df.groupby('diet_group').agg({
    'mean_ghgs': 'mean',
    'mean_land': 'mean',
    'mean_watscar': 'mean',
    'mean_eut': 'mean',
    'mean_ghgs_ch4': 'mean',
    'mean_watuse': 'mean',
    'n_participants': 'sum',
    'color': 'first',
    'label': 'first',
    'rank': 'first',
    'diet_group': 'first'
}).sort_values('rank')

diet_group_df

#diet_group_df = diet_group_df.reset_index()
#diet_group_df = pd.merge(df, diet_info, on='diet_group')
#df['diet_color'] = df['diet_group'].map(diet_info.set_index('diet_group')['color'])
#df['diet_label'] = df['diet_group'].map(diet_info.set_index('diet_group')['label'])
#df = df.reindex(diet_info['diet_group'])
#df


# In[12]:


cols = [
    'mean_ghgs',
    'mean_land',
    'mean_watscar',
    'mean_eut',
    'mean_ghgs_ch4',
    'mean_watuse'
]

def max_norm(df):
    return df / df.max()

for column in cols:
    diet_group_df[column + '_norm'] = max_norm(diet_group_df[column])
diet_group_df


# In[13]:


col_names = {
    'mean_ghgs': 'Mean GHG',
    'mean_land': 'Mean Land Use',
    'mean_ghgs_ch4': 'Mean CH4',
    'mean_watscar': 'Mean Water Scarcity',
    'mean_eut': 'Mean Eutrophication',
    'mean_watuse': 'Mean Water Use',
}

col_units = {
    'mean_ghgs': 'kg d⁻¹',
    'mean_land': 'm² d⁻¹',
    'mean_ghgs_ch4': 'kg d⁻¹',
    'mean_watscar': 'm³ d⁻¹',
    'mean_eut': 'gPO⁴ e d⁻¹',
    'mean_watuse': 'm³ d⁻¹'
}

col_name_units = {key: f'{col_names[key]}'+(f' ({col_units[key]})' if col_units[key] != '' else '') for key in col_names.keys()}

titles_joined = [title for row in subcharts for (key, title) in row]

# Citing https://doi.org/10.1038/s43016-023-00795-w -- TODO
grid = make_subplots(row_heights=[600]*3, rows=3, cols=2,
                     subplot_titles=titles_joined,
                     shared_xaxes='rows')
grid.update_layout(title_text='Environmental Impact by Diet',height=900)
grid.update_layout(showlegend=False)

def make_cyclic_data(row, cols):
    return list(map(lambda col: row[col].item(), cols))
    #r= []
    #for col in cols:
    #    r.append(row[col].item())
    #r.append(r[0])
    
    # So the lines loop around.
    #theta = list(map(lambda key: col_names[key], cols))
    #theta.append(theta[0])
    #return r, theta

def make_scatter_plot(df, diet):
    row = df[df['diet_group']==diet]
    cols = list(col_names.keys())
    cols.append(cols[0])
    norm_cols = list(map(lambda x: x + '_norm', cols))
    norm_vals = make_cyclic_data(row, norm_cols)
    abs_vals = make_cyclic_data(row, cols)
    #tip_text = list(map(lambda col, val: f'{val} {col_units[col]}', zip(cols, abs_vals)))
    tip_text = [f'{val:.3f} {col_units[col]}' for col, val in zip(cols, abs_vals)]
    print(tip_text)
    return go.Scatterpolar(r=norm_vals, theta=cols, name=row['label'].item(), 
                           line_color=row['color'].item(),
                           hoverinfo='text',
                           text=tip_text,
                           mode='lines+markers', fill='toself')

#fig = go.Scatterpolar(name='Total', r=r, theta=cols, mode='lines', fill='toself')





#fig = go.Scatterpolar(name='Total', r=df[df['diet_group']=='fish'].item()[cols], theta=df[cols])
#fig.show()
#grid.add_trace(fig)

#for row in range(3):
#    for col in range(2):
#        grid.add_trace(
#            go.Violin(x=survey_df['diet_group'], y=survey_df[subcharts[row][col][0]],
#                      points=False, width=1.5), col=col+1, row=row+1)


#grid.show()
diet_group_df
col_name_units


# In[14]:


plot = go.Figure()
plot.update_layout(title_text='Environmental Impact of Meat-Based-Diets Compared to Fish (normalised)',height=900)
fig = make_scatter_plot(diet_group_df, 'meat')
plot.add_trace(fig)
fig = make_scatter_plot(diet_group_df, 'fish')
plot.add_trace(fig)
plot.show()


# In[15]:


plot = go.Figure()
plot.update_layout(title_text='Environmental Impact by Fish Based Diets Against Vegeterain and Vegan Diets (normalised)',height=900)
fig = make_scatter_plot(diet_group_df, 'fish')
plot.add_trace(fig)
fig = make_scatter_plot(diet_group_df, 'veggie')
plot.add_trace(fig)
fig = make_scatter_plot(diet_group_df, 'vegan')
plot.add_trace(fig)
plot.show()


# In[16]:


plot = go.Figure()
plot.update_layout(title_text='Environmental Impact of Various Diets (normalised)',height=900)
fig = make_scatter_plot(diet_group_df, 'meat')
plot.add_trace(fig)
fig = make_scatter_plot(diet_group_df, 'meat100')
plot.add_trace(fig)
fig = make_scatter_plot(diet_group_df, 'meat50')
plot.add_trace(fig)
fig = make_scatter_plot(diet_group_df, 'fish')
plot.add_trace(fig)
fig = make_scatter_plot(diet_group_df, 'veggie')
plot.add_trace(fig)
fig = make_scatter_plot(diet_group_df, 'vegan')
plot.add_trace(fig)
plot.show()


# In[17]:


plot = go.Figure()
plot.update_layout(title_text='Environmental Impact of Vegeterian Diets Against Meat-Based Diets (normalised)',height=900)

#fig = make_scatter_plot(diet_group_df, 'meat100')
#plot.add_trace(fig)
fig = make_scatter_plot(diet_group_df, 'meat')
plot.add_trace(fig)
fig = make_scatter_plot(diet_group_df, 'meat50')
plot.add_trace(fig)
fig = make_scatter_plot(diet_group_df, 'veggie')
plot.add_trace(fig)
plot.show()


# In[104]:


fig = go.Figure()

shuffled_df = df.sample(frac=1).reset_index(drop=True)

# Define diet groups and plot order
diet_order = list(diet_label_map.keys())

for diet_key in diet_order:
    diet_df = shuffled_df[shuffled_df['diet_group'] == diet_key]

    fig.add_trace(go.Scatter(
        x=diet_df['mean_ghgs'],
        y=diet_df['mean_watuse'],
        mode='markers',
        marker=dict(
            size=diet_df['n_participants'],
            color=diet_color_map[diet_key],
            opacity=0.09,
            line=dict(width=0.2)
        ),
        name=diet_label_map[diet_key],
        legendgroup=diet_key,
        showlegend=False,  # We'll add dummy legend markers below
        customdata=diet_df[['n_participants']],
        hovertemplate=(
            f"<b>%{{text}}</b><br>"
            f"GHG Emissions: %{{x}}<br>"
            f"Water Use: %{{y}}<br>"
            f"Participants: %{{customdata[0]}}<extra></extra>"
        ),
        text=diet_df['grouping']
    ))

# Add dummy legend markers
#for diet_key in diet_order:
#    fig.add_trace(go.Scatter(
#        x=[None], y=[None],
#        mode='markers',
#        marker=dict(
#            size=10,
#            color=diet_color_map[diet_key],
#            opacity=1,
#            line=dict(width=0)
#        ),
#        showlegend=True,
#        name=diet_label_map[diet_key],
#        legendgroup=diet_key,
#        hoverinfo='skip'
#    ))

fig.update_layout(
    title='GHG Emissions vs. Water Use by Diet Group',
    xaxis_title=col_name_units['mean_ghgs'],
    yaxis_title=col_name_units['mean_watuse'],
    template='plotly_white',
    height=900
)

fig.show()


# In[96]:


# Rename for clarity
jp_lca_df.columns = ['product_id', 'name','group','id','product_details','country','weight','land','arable_land','pasture_land','biodiversity','ghg','acidification', 'eut', 'watuse', 'watscar','sys']

lca_label_map = {
    'product_id': 'Product id',
    'name': 'Data S2 Name',
    'group': 'Group',
    'id': 'id',
    'product_details': 'Product details',
    'country': 'Country',
    'weight': 'Weight',
    'land': 'Land Use (m^2*year)',
    'arable_land': 'Arable Land Use (m^2 year)',
    'pasture_land': 'Pasture Land Use (m2*year)',
    'biodiversity': 'Biodiversity (sp*yr*10^14)',
    'ghg': 'GHG Emissions (kg CO2eq,<br> incl CC feedbacks)',
    'acidification': 'Acidification (g SO2eq)',
    'eut': 'Eutrophication (g PO43-eq)',
    'watuse': 'Water Use (L)',
    'watscar': 'Scarcity Weighted Water Use (L eq)',
    'sys': 'Sys'
}

lca_impact_cols = ['land','arable_land','pasture_land','biodiversity','ghg','acidification', 'eut', 'watuse', 'watscar']

jp_lca_df


# In[27]:


tree_df = jp_lca_df.copy()

#https://plotly.com/python/treemaps/
tree_df['all'] = 'all'


fig = px.treemap(tree_df, path=['all', 'group', 'name', 'product_details', 'country'], values='land', color='ghg',
                 labels=lca_label_map)
fig.update_traces(root_color='lightgrey')
fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
fig.update_layout(title_text='Land Use by Product, Colored by Green House Emissions',height=900)

fig.show()


# In[80]:


metric = 'mean_land'
diet_groups = diet_info['diet_group']
runs = survey_df['mc_run_id'].sort_values().unique()

fig = go.Figure()

# survey_df['age_group'].unique()
age_map = {
    '20-29': 25,
    '30-39': 35,
    '40-49': 45,
    '50-59': 55,
    '60-69': 65,
    '70-79': 75
}

#survey_df['age_med'] = survey_df['age_group'].map(age_map)

#diet_counts = survey_df.groupby('diet_group')['mc_run_id'].nunique().to_dict()
#max_count = max(diet_counts.values())

visible_diets = ['vegan','fish','meat']

for diet in diet_info['diet_group']:
    for run in runs:
        run_df = survey_df[survey_df['mc_run_id'] == run] #[survey_df['diet_group'] == diet]
        count = diet_counts[diet]
        fig.add_trace(go.Scatter(
            x=run_df['age_med'],
            y=run_df[metric],
            mode='lines',
            line=dict(width=1, color=diet_color_map[diet]),
            opacity=min(1, max_count / count * 0.05),
            showlegend=False,
            legendgroup=diet,
            #visible='legendonly'
        ))
    
    mean_df = survey_df.groupby('diet_group')[metric].mean().reset_index()
    
    fig.add_trace(go.Scatter(
        x=mean_df['diet_group'],
        y=mean_df[metric],
        mode='lines+markers',
        line=dict(width=3, color=diet_color_map[diet]),
        name=diet_label_map[diet],
        legendgroup=diet,
        showlegend=True,
        visible=True
    ))


#fig.update_traces(marker=dict(line=dict(width=0.01)))


fig.update_layout(height=900)
fig.update_layout(
    title=f'Monte Carlo Simulations of {col_names[metric]} by Age Group',
    xaxis_title='Age groups',
    yaxis_title=f'{col_name_units[metric]} (log)',
    yaxis_type='log',
    template='plotly_white',
    legend=dict(groupclick='toggleitem')
)

fig.show()

