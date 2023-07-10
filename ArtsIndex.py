import pandas as pd
import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import st_folium

def set_page_config():
    """Sets the page configuration.
    """
    st.set_page_config(
        page_title="Data Gallery for Arts Vibrancy in Korea",
        layout="wide",
    )
set_page_config()

# loads arts_vib_index data & geodata
# df_test = pd.read_csv('data/arts_index.csv')

busan_df = pd.read_csv('data/Busan_arts_index_indetail.csv')
seoul_df = pd.read_csv('data/Seoul_arts_index_indetail.csv')
filename_geodata = 'hangjeongdong_merge_last.geojson'
admin_gdf = gpd.read_file(filename_geodata)

merged_seoul_df = pd.merge(seoul_df, admin_gdf, left_on='구', right_on='sggnm', how='inner')
merged_busan_df = pd.merge(busan_df, admin_gdf, left_on='구', right_on='sggnm', how='inner')

merged_df = pd.concat([merged_seoul_df, merged_busan_df])
# merged_df_all = pd.merge(merged_busan_df, merged_seoul_df, how='outer')
merged_df = merged_df.drop_duplicates(subset=['sidonm', 'sggnm'])
merged_gdf = gpd.GeoDataFrame(merged_df, geometry="geometry")

# global variables
center = [37.541, 126.986]
m = folium.Map(location = center, zoom_start = 10)

def get_top_communities(n):
  '''
    예술활력지수가 높은 N개의 커뮤니티를 반환
    @n : TOP-N
  '''
  # top = df_test['arts_index'].sort_values(ascending=False).iloc[0:n]
  # df_top = df_test.iloc[top.index]

  top_communities_df = merged_gdf.nlargest(n, '예술활력지수')
  return top_communities_df
  # print(top_communities_df)
  
  # result = []
  # for i in range(n):
  #   if df_top.index[i] > 15:
  #     jiyeok = "서울"
  #   else:
  #     jiyeok = "부산"

  #   geo = jiyeok + " " + df_top['구'].values.tolist()[i]
  #   crd = geocoding(geo)
  #   result.append([crd['lat'], crd['lng']])

  # return (result, df_top)


def add_circle_area(n):
  '''
    예술활력지수가 높은 상위 커뮤니티 추출
    @n : TOP-N
  '''
  top_communities_df = get_top_communities(n)

  if n == 10:
    radius, color = 700, 'crimson'
  else:
    radius, color = 1000, 'pink'

  for index, row in top_communities_df.iterrows():
    centroid = [ row['geometry'].centroid.y, row['geometry'].centroid.x ]
    messages = f" {row['구']} + 예술활력지수: {int(row['예술활력지수']) }"
    popup = folium.Popup(messages, max_width=300)

    folium.Circle(
        location = centroid,
        radius = radius,
        popup= popup,
        color = color,
        fill = True,
        fill_color = color,
        fill_opacity=100,
    ).add_to(m)
    
  # if n == 10:
  #   df_top = df_top.iloc[0:n]
  #   top = top[0:n]
  #   radius = 700
  #   color = 'crimson'
  # else:
  #   radius = 1000
  #   color = 'pink'

  # for i in range(n):
  #   folium.Circle(
  #       location=top[i],
  #       radius = radius,
  #       popup= df_top['구'].values.tolist()[i],
  #       color = color,
  #       fill = True,
  #       fill_color = color,
  #       fill_opacity=100,
  #   ).add_to(m)

def select_top_communities(cmd):
    '''
      상위 커뮤니티 선택
      @ cmd: Top 10 or Top 5
    '''
    st.session_state.marker = cmd
    if cmd == "Top 10":
        add_circle_area(10)
    elif cmd == "Top 5":
        add_circle_area(5)


'''
  Arts Vibrancy Index WebApp
'''
def main():
  # initialize
  st.sidebar.title("Data Gallery")
  st.sidebar.header("지역커뮤니티의 예술 활력을 탐험하기")
  
  ## main content
  st.title("Art Vibrancy Index Map")

  # add layer: Choropleth
  folium.Choropleth(
      geo_data = filename_geodata,
      data = merged_gdf,
      columns = ('sggnm', '예술활력지수'),
      key_on = 'feature.properties.sggnm',
      fill_color = 'BuPu',
      legend_name = 'Arts Vibrancy Index',
  ).add_to(m)

  # add layer: carto
  tiles = "CartoDB positron"
  folium.TileLayer(tiles=tiles).add_to(m)

  st.sidebar.title("The Arts Vibrancy in Busan & Seoul")
    
  with st.sidebar:
      if st.sidebar.checkbox('Top 10 Large Communities'):
          select_top_communities("Top 10")
      if st.checkbox('Top 5 Large Communities'):
          select_top_communities("Top 5")
      
  # map
  st_data = st_folium(m, width=1500, height=800)

  # process returned objects by user action
  if st_data['last_clicked'] is not None:
    if 'last_active_drawing' in st_data:
      clicked_sggnm = st_data['last_active_drawing']['properties']['sggnm']
      clicked_sidonm = st_data['last_active_drawing']['properties']['sidonm']
      # print(st_data['last_active_drawing']['properties']['sggnm'])

      # extract sub-dataframe
      condition = (merged_gdf['sggnm'] == clicked_sggnm) & (merged_gdf['sidonm'] == clicked_sidonm) 
      filtered_df = merged_gdf[condition].iloc[:, 0:70].transpose()
      filtered_df.rename(columns=filtered_df.iloc[0],inplace=True)
      filtered_df = filtered_df.drop(filtered_df.index[0])
      creation = filtered_df.iloc[[4, 0, 1, 2, 3]]
      finance = filtered_df.iloc[[11, 5, 6, 7, 8, 9, 10]]
      facilities = filtered_df.iloc[[17, 12, 13, 14, 15, 16]]
      enjoyment = filtered_df.iloc[[26, 18, 19, 20, 21, 22, 23, 24, 25]]
      achievement = filtered_df.iloc[[34, 27, 28, 29, 30, 31, 32, 33]]
      # print(filtered_df)
    
      # st.sidebar.table(filtered_df)
    
      # write sub-indices
      st.sidebar.write(f"**{clicked_sidonm}**  **{clicked_sggnm}**")
      
      st.sidebar.table(creation)
      st.sidebar.table(finance)
      st.sidebar.table(facilities)
      st.sidebar.table(enjoyment)
      st.sidebar.table(achievement)

      

if __name__ == '__main__':
    main()
