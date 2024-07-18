import streamlit as st
import pandas as pd
import os
from streamlit_tags import st_tags

# Шаг 1: Загрузка данных
data_file = os.path.join(os.path.dirname(__file__), 'logisticpricebase.xlsx')
df = pd.read_excel(data_file)

# Исправление названия столбца
df.columns = df.columns.str.replace('\n', ' ')

# Функция для поиска похожих адресов и зон
def search_addresses_and_zones(query, df):
    query = query.lower()
    address_results = df[df['Название улиц в зоне'].str.lower().str.contains(query, na=False)]
    zone_results = df[df['Название зоны'].str.lower().str.contains(query, na=False)]
    combined_results = pd.concat([address_results, zone_results]).drop_duplicates()
    return combined_results

# Функция для получения уникальных значений для автозаполнения
def get_unique_values(column_name, df):
    return df[column_name].dropna().unique().tolist()

# Создание вкладок
tabs = st.tabs(["Поиск", "Добавление зоны", "Список зон и адресов"])

# Вкладка поиска
with tabs[0]:
    st.header("Поиск зон доставки")

    options = get_unique_values('Название улиц в зоне', df) + get_unique_values('Название зоны', df)
    query = st_tags(
        label='Введите адрес или зону',
        text='Press enter to add more',
        value='',
        suggestions=options,
        maxtags=1,
        key='1'
    )

    if query:
        query = query[0]
        matching_results = search_addresses_and_zones(query, df)
        if not matching_results.empty:
            st.dataframe(matching_results)

            selected_index = st.selectbox("Выберите строку для отображения деталей", matching_results.index)
            selected_row = matching_results.loc[selected_index]
            st.markdown(f"**Зона:** {selected_row['Название зоны']}")
            st.markdown(f"**ID зоны:** {selected_row['ID зоны']}")
            st.markdown(f"<b>ГАЗель:</b> {selected_row['Стоимость доставки ГАЗель']}", unsafe_allow_html=True)
            st.markdown(f"<b>Валдай/ ГАЗон, ЗиЛ:</b> {selected_row['Стоимость доставки Валдай/ ГАЗон, ЗиЛ']}", unsafe_allow_html=True)
            st.markdown(f"<b>КАМаз:</b> {selected_row['Стоимость доставки КАМаз']}", unsafe_allow_html=True)
            st.markdown(f"**Расстояние от базы:** {selected_row['Ср. расстояние от базы (км)']} км")

# Вкладка добавления новой зоны
with tabs[1]:
    st.header("Добавление новой зоны")
    
    zone_name = st.text_input("Название зоны", "")
    zone_id = st.text_input("ID зоны", "")
    streets = st.text_input("Название улиц в зоне", "")

    col1, col2, col3 = st.columns(3)
    with col1:
        gazel_cost = st.number_input("ГАЗель")
    with col2:
        valday_cost = st.number_input("Валдай/ ГАЗон, ЗиЛ")
    with col3:
        kamaz_cost = st.number_input("КАМаз")

    distance = st.number_input("Ср. расстояние от базы (км)")

    if st.button("Добавить зону"):
        new_data = {
            "Название зоны": zone_name,
            "ID зоны": zone_id,
            "Название улиц в зоне": streets,
            "Стоимость доставки ГАЗель": gazel_cost,
            "Стоимость доставки Валдай/ ГАЗон, ЗиЛ": valday_cost,
            "Стоимость доставки КАМаз": kamaz_cost,
            "Ср. расстояние от базы (км)": distance
        }
        new_df = pd.DataFrame([new_data])
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_excel(data_file, index=False)
        st.success("Данные успешно обновлены")

# Вкладка списка зон и адресов
with tabs[2]:
    st.header("Список зон и адресов")
    edited_df = st.data_editor(df)

    if st.button("Сохранить изменения"):
        edited_df.to_excel(data_file, index=False)
        st.success("Изменения сохранены")