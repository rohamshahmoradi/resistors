import streamlit as st
from itertools import combinations
import pandas as pd

try:
    # Set page configuration
    st.set_page_config(page_title="Resistor Combination Calculator", layout="wide")

    # About us


    @st.dialog("About us")
    def vote():
        st.write("_Developed by **_Amin Fallah_** & **_Roham Shahmoradi_**_")
        st.write(
            "_If you have any suggestions or criticisms, contact us in **telegram**:_")
        st.write("**_@FallahAmin_**")
        st.write("**_@rohamshahmoradi_**")
        if st.button("Got it"):
            st.rerun()


    # Title and description
    st.title("Resistor Combination Calculator")
    st.write("Calculate series and parallel resistor combinations to match a target value.")
    if st.button("About us"):
        vote()
    # Input Section
    st.header("Input Parameters")
    col1, col2, col3 = st.columns(3)
    with col1:
        target = st.text_input('Your target resistance:',
                            placeholder="e.g., 10k, 1M, ...")
    with col2:
        tolerance = st.number_input(
            'Maximum tolerance (in %):', min_value=0.01, max_value=100.0, value=5.0) / 100
    with col3:
        num_combinations = st.number_input(
            'Number of combinations to calculate:', min_value=1, max_value=1000, value=10)

    # Standard resistor values
    n1 = [10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82]
    n = [j * 10**i for i in range(6) for j in n1]

    # Process input target resistance
    if target and not target[-1].isdigit():
        order = target[-1]
        number = float(target[:-1])
    else:
        order = ""
        number = float(target) if target else 0

    ordrs = {"": 1, "k": 10**3, "M": 10**6}
    target_val = number * ordrs[order]

    # Color bands for resistors (three colors for each resistor)
    color_codes = {0: 'black', 1: 'brown', 2: 'red', 3: 'orange',
                4: 'yellow', 5: 'green', 6: 'blue', 7: 'purple', 8: 'gray', 9: 'white'}


    def resistor_colors(value):
        a = '%E' % value
        a = a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]
        a = a.split('E+')
        digits = [int(n) for n in a[0] if n != '.']
        digits.append(int(a[-1]))
        if len(digits) == 2:
            digits.insert(1, 0)
            digits[-1] -= 1
        else:
            digits[-1] -= 1
        colors = [color_codes[d] for d in digits[:3]]
        return colors


    def color_bands_html(colors):
        return "".join([f'<span style="background-color:{c};width:7px;height:40px;display:inline-block;border:1px solid #000;margin:1px;"></span>' for c in colors])

    # Helper functions


    def search(n, target):
        if target > n[-1]:
            return -1
        for i, j in enumerate(n):
            if j > target:
                return i


    def seriesok(args, target, tol):
        return abs(sum(args) - target) / target < tol


    def paraok(args, target, tol):
        return abs(1 / sum([1 / x for x in args]) - target) / target < tol


    def series_algo(n, max_n, target, tol):
        n = n[:search(n, target)]
        series_list = []
        n = n * 3
        for i in range(1, min(max_n, len(n)) + 1):
            series_list += list(combinations(n, i))
        series_list = list(set(series_list))
        return [i for i in series_list if seriesok([x for x in i], target=target, tol=tol)]


    def para_algo(n, max_n, target, tol):
        para_list = []
        n = n * 3
        for i in range(1, min(max_n, len(n)) + 1):
            para_list += list(combinations(n, i))
        para_list = list(set(para_list))
        return [i for i in para_list if paraok([x for x in i], target=target, tol=tol)]


    def khoshgelization(n):
        if len(str(n)) == 7:
            return str(n / 10**6) + "MΩ"
        elif 4 <= len(str(n)) <= 6:
            return str(n / 10**3) + "kΩ"
        else:
            return str(n) + "Ω"


    def ans(mode, args):
        if mode == 'para':
            return int(1 / sum([1 / x for x in args]))
        elif mode == 'series':
            return sum([x for x in args])


    def closest_result(results, target, mode, num_combinations):
        closest = sorted(results, key=lambda x: abs(
            ans(mode, x) - target))[:num_combinations]
        return closest, abs(ans(mode, closest[0]) - target) / target * 100

    # Add radio buttons for sorting method
    sort_method = st.radio("Sort by:", ('Error',
                                        'Number of Resistors'), index=0, horizontal=True)

    # Calculation and display results

    if st.button('Calculate'):
        with st.spinner("Processing..."):
            para_results, error_para = closest_result(
                para_algo(n, 3, target_val, tolerance), target_val, 'para', num_combinations)
            series_results, error_series = closest_result(series_algo(
                n, 3, target_val, tolerance), target_val, 'series', num_combinations)

        if error_para == 0:
            st.success(f"**Closest parallel combination error:** Exact match")
        else:
            st.warning(
                f"**Closest parallel combination error:** {error_para:.2f}%")

        if error_series == 0:
            st.success(f"**Closest series combination error:** Exact match")
        else:
            st.warning(
                f"**Closest series combination error:** {error_series:.2f}%")
        # Sorting based on selected method

        def sort_results(results, mode, method):
            if method == 'Number of Resistors':
                return sorted(results, key=lambda x: (len(x), abs(ans(mode, x) - target_val)))
            else:
                return sorted(results, key=lambda x: (abs(ans(mode, x) - target_val), len(x)))

        para_results = sort_results(para_results, 'para', sort_method)
        series_results = sort_results(series_results, 'series', sort_method)

        col1, col2 = st.columns(2)

        col1.subheader('Parallel Resistors:')
        para_table = []
        for j in para_results:
            combination = " || ".join([khoshgelization(k) for k in j])
            colors_html = " , ".join([color_bands_html(resistor_colors(k))
                                      for k in j])
            result = khoshgelization(ans('para', j))
            error = f"{abs(ans('para', j) - target_val) / target_val * 100:.2f}"
            para_table.append([combination, colors_html, result, error])
        para_df = pd.DataFrame(para_table, columns=[
            "Combination", "Colors", "Result", "Error (%)"])
        para_df.index += 1  # Start index from 1
        para_df = para_df.style.set_table_styles(
            [{'selector': 'th', 'props': [('text-align', 'center')]}])
        col1.markdown(para_df.to_html(escape=False), unsafe_allow_html=True)

        col2.subheader('Series Resistors:')
        series_table = []
        for j in series_results:
            combination = " + ".join([khoshgelization(k) for k in j])
            colors_html = " , ".join([color_bands_html(resistor_colors(k))
                                      for k in j])
            result = khoshgelization(ans('series', j))
            error = f"{abs(ans('series', j) - target_val) / target_val * 100:.2f}"
            series_table.append([combination, colors_html, result, error])
        series_df = pd.DataFrame(series_table, columns=[
            "Combination", "Colors", "Result", "Error (%)"])
        series_df.index += 1  # Start index from 1
        series_df = series_df.style.set_table_styles(
            [{'selector': 'th', 'props': [('text-align', 'center')]}])
        col2.markdown(series_df.to_html(escape=False), unsafe_allow_html=True)

except Exception as e:
    st.error("An error occurred")
