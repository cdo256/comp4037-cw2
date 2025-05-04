#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import lca
import survey
from math import pi


# In[2]:


jp_lca_df = lca.load()
survey_df = survey.load()


# In[3]:


diet_info = pd.DataFrame({
    'diet_group': ['vegan','veggie','fish','meat50','meat','meat100'],
    'rank': [1,2,3,4,5,6],
    'color': ['#7AFF93','#1DB887','#3988C4','#FF7E96','#E9677F','#C25252'],
    'label': ['Vegan','Vegetarian','Fish Eaters','Low Meat Eaters','Medium Meat Eaters','High Meat Eaters']
})

diet_color_map = dict(zip(diet_info['diet_group'], diet_info['color']))
diet_label_map = dict(zip(diet_info['diet_group'], diet_info['label']))

diet_info


# In[4]:


#weighted_sum = lambda x: np.average(x, weights=survey_df.loc[x.index, 'n_participants'])
#
#df = survey_df.groupby('diet_group').agg(
#    weighted_mean_ghgs = ('mean_ghgs', weighted_sum),
#    
#)
diet_group_df = survey_df.groupby('diet_group').agg({
    'mean_ghgs': 'mean',
    'mean_land': 'mean',
    'mean_watscar': 'mean',
    'mean_eut': 'mean',
    'mean_ghgs_ch4': 'mean',
    'mean_watuse': 'mean',
    'n_participants': 'sum'
}).merge(diet_info, on='diet_group').sort_values('rank').reset_index(drop=True)

diet_group_df

#diet_group_df = diet_group_df.reset_index()
#diet_group_df = pd.merge(df, diet_info, on='diet_group')
#df['diet_color'] = df['diet_group'].map(diet_info.set_index('diet_group')['color'])
#df['diet_label'] = df['diet_group'].map(diet_info.set_index('diet_group')['label'])
#df = df.reindex(diet_info['diet_group'])
#df


# In[5]:


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


# In[6]:


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


# In[14]:


fig = go.Figure()

#TEMP: Drop 90% elements for performance
shuffled_df = survey_df.merge(diet_info, on='diet_group').sample(frac=1).reset_index(drop=True)

diet_order = list(diet_label_map.keys())

fig = px.scatter(
    shuffled_df,
    x='mean_ghgs',
    y='mean_watuse',
    color='diet_group',
    color_discrete_map=diet_color_map,
    size='n_participants',
    hover_name='grouping',
    title='GHG Emissions vs. Water Use by Diet Group',
    marginal_x='violin',
    marginal_y='violin',
    labels={'diet_group': 'Diet Group', 'n_participants': '# participants'} | col_name_units | diet_label_map,
    category_orders={'diet_group': list(diet_label_map.keys())},
    hover_data={
        'mean_ghgs': ':.3f',
        'mean_watuse': ':.3f',
        'n_participants': True,
        'diet_group': False  # hide duplicate legend info
    }
)

fig.update_layout(height=900)

# Make bubbles semi-transparent
fig.update_traces(marker=dict(opacity=0.01, line=dict(width=0.1)))

# Refine violin appearance and legend deduplication
legend_shown = set()
for trace in fig.data:
    if trace.type == 'violin':
        trace.side = 'positive'
        trace.width = 2.1
        trace.points = False
        trace.hoverinfo = 'skip'
        trace.hovertemplate = '%{y:.3f}<extra></extra>' if trace.orientation == 'v' else '%{x:.3f}<extra></extra>'
    elif trace.type in ['scatter', 'scattergl']:
        diet_label = diet_label_map.get(trace.name, trace.name)
        trace.name = diet_label
        #if diet_label in legend_shown:
        #    trace.showlegend = False
        #else:
        #    legend_shown.add(diet_label)
        #    trace.showlegend = True

fig.show()

