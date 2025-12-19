def anomaly_evaluation_charts(group, group_columns, variable, date_column, eval_periods=None):
    
    group = group.copy()
    
    import plotly.graph_objects as go
    import plotly.express as px
    
    # --------------------------------------------------------------------------------
    # All Models Plot
    # --------------------------------------------------------------------------------
    
    fig = go.Figure()
    
    plot_title = "  --  ".join(list(group[group_columns].values[0])).upper() + "  --  Anomaly Detection Models"
    
    # Actuals
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group[variable],
        mode='lines',
        line=dict(color='seagreen', width=1.5),
        name=variable if variable == variable.upper() else variable.title(),
    ))

    # Evaluation period
    if eval_periods != None:
        fig.add_trace(go.Scatter(
            x=group[date_column][-eval_periods:],
            y=group[variable][-eval_periods:],
            mode='lines',
            line=dict(color='forestgreen', width=1.75),
            name='Evaluation Period',
            hoverinfo='skip',
        ))
    
    # Get colors for each anomaly model
    anom_colors = px.colors.sequential.Magma
    n = len(anom_colors)
    anom_colors_rearr = []
    ptr1 = 0
    ptr_mid = int(np.floor(n/2))
    ptr2 = int(np.floor(n/2))
    while ptr1 <= ptr_mid:
        anom_colors_rearr.append(anom_colors[ptr1])
        ptr1 += 1
        if ptr1 <= ptr_mid:
            anom_colors_rearr.append(anom_colors[ptr2])
            ptr2 += 1
    anom_colors_rearr = list(dict.fromkeys(anom_colors_rearr))    
    anom_sizes = [10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5]
    col_num = 0
    
    # Model anomaly points
    for col in group.columns.to_list():
        if col.startswith('is_') and col.endswith('_anomaly') and col != 'is_anomaly':
            anom_name = col.removeprefix('is_').removesuffix('_anomaly') + ' Anomaly'
            if group[col].sum() >= 1:
                fig.add_trace(go.Scatter(
                    x=group[group[col] == True][date_column],
                    y=group[group[col] == True][variable],
                    mode='markers',
                    marker=dict(color=anom_colors_rearr[col_num], size=anom_sizes[col_num]),
                    name=anom_name,
                    hoverinfo='skip',
                ))
                col_num += 1
    
    # Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_Anomaly'] == True][date_column],
        y=group[group['is_Anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='pink', symbol='cross', line=dict(width=1), size=9),
        name='Anomalies',
        hoverinfo='skip',
    ))
    
    fig.update_layout(
        title=dict(
                text=plot_title,
                y=0.96,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=18, color='black', weight='bold'),
            ),
        height=350,
        width=1200,
        margin=dict(l=50, r=50, t=40, b=30),
        plot_bgcolor='snow',
        paper_bgcolor='whitesmoke',
        xaxis=dict(
            range=[group[date_column].min(), group[date_column].max()],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis=dict(
            range=[group[variable].min()*0.9, group[variable].max()*1.06],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis_title=dict(
            text=variable if variable == variable.upper() else variable.title(),
            font=dict(size=16, weight='bold', color='black')
            ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
        )
    )

    fig.show()
    
    print("\n")
    
    # --------------------------------------------------------------------------------
    # IS ANOMALY Plot
    # --------------------------------------------------------------------------------

    anomaly_cols = []
    for col in group.columns.to_list():
        if col.startswith('is_') and col.endswith('_anomaly') and col != 'is_anomaly':
            anomaly_cols.append(col)
    group['Anomaly Vote Models'] = group.apply(lambda row: [col.removeprefix('is_').removesuffix('_anomaly') for col in anomaly_cols if row[col] == True],
                                               axis=1).apply(sorted)

    group['Anomaly Vote Models'] = group['Anomaly Vote Models'].apply(lambda x: ', '.join(x))

    group['Model Votes'] = group[anomaly_cols].sum(axis=1)
    group['Mean'] = group[variable].mean()
    group['Median'] = group[variable].median()
    
    
    fig = go.Figure()
    
    plot_title = "  --  ".join(list(group[group_columns].values[0])).upper() + "  --  Anomalies"
    
    # Actuals
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group[variable],
        mode='lines',
        line=dict(color='seagreen', width=1.5),
        name=variable if variable == variable.upper() else variable.title(),
        ))
    
    # Mean
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['Mean'],
        mode='lines',
        line=dict(color='maroon', width=0.7, dash='dash'),
        name='Mean',
        showlegend=True,
        hoverinfo='skip',
    ))

    # Median
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['Median'],
        mode='lines',
        line=dict(color='darkblue', width=0.7, dash='dot'),
        name='Median',
        showlegend=True,
        hoverinfo='skip',
    ))
    
    # Evaluation period
    if eval_periods != None:
        fig.add_trace(go.Scatter(
            x=group[date_column][-eval_periods:],
            y=group[variable][-eval_periods:],
            mode='lines',
            line=dict(color='forestgreen', width=1.75),
            name='Evaluation Period'
        ))
    
    # Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_Anomaly'] == True][date_column],
        y=group[group['is_Anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='red', symbol='circle', line=dict(width=1), size=9),
        name='Anomalies',
        customdata=group[group['is_Anomaly'] == True][['Anomaly Vote Models']],
        hovertemplate=(
            f'Date: %{{x|%Y-%m-%d}}<br>' +
            f'{variable if variable == variable.upper() else variable.title()}: %{{y:~.2s}}<br>' +
            'Anomaly Vote Models: %{customdata[0]}<extra></extra>'
            )

        ))
    
    fig.update_layout(
        title=dict(
                text=plot_title,
                y=0.96,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=18, color='black', weight='bold'),
            ),
        height=350,
        width=1200,
        margin=dict(l=50, r=50, t=40, b=30),
        plot_bgcolor='snow',
        paper_bgcolor='whitesmoke',
        xaxis=dict(
            range=[group[date_column].min(), group[date_column].max()],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis=dict(
            range=[group[variable].min()*0.9, group[variable].max()*1.06],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis_title=dict(
            text=variable if variable == variable.upper() else variable.title(),
            font=dict(size=16, weight='bold', color='black')
            ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
        )
    )

    fig.show()

    print("\n")
    
    
    # --------------------------------------------------------------------------------
    # Percentile Model Plot
    # --------------------------------------------------------------------------------
    
    fig = go.Figure()

    plot_title = "  --  ".join(list(group[group_columns].values[0])).upper() + "  --  Percentile Anomaly Detection"

    # Shading above upper line (upper anomaly region)
    fig.add_shape(
        type="rect",
        x0=0, x1=1, xref="paper",
        y0=group['Percentile_high'].values[0], y1=group[variable].max()*1.06,
        yref="y",
        fillcolor="rgba(255, 0, 0, 0.055)",
        line=dict(width=0),
        layer="below"
    )

    # Shading below lower line (lower anomaly region)
    fig.add_shape(
        type="rect",
        x0=0, x1=1, xref="paper",
        y0=0, y1=group['Percentile_low'].values[0],
        yref="y",
        fillcolor="rgba(255, 0, 0, 0.055)",
        line=dict(width=0),
        layer="below"
    )
    
    # Actuals
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group[variable],
        mode='lines',
        line=dict(color='seagreen', width=1.5),
        name=variable if variable == variable.upper() else variable.title(),
        ))

    # Evaluation period
    if eval_periods != None:
        fig.add_trace(go.Scatter(
            x=group[date_column][-eval_periods:],
            y=group[variable][-eval_periods:],
            mode='lines',
            line=dict(color='forestgreen', width=1.75),
            name='Evaluation Period'
        ))

    # Lower Percentile line
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['Percentile_low'],
        mode='lines',
        line=dict(color='orangered', width=1, dash='dashdot'),
        name='Percentile Low',
        showlegend=False
        ))

    # Upper Percentile line
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['Percentile_high'],
        mode='lines',
        line=dict(color='orangered', width=1, dash='dashdot'),
        name='Percentile High',
        showlegend=False
        ))

    # Percentile Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_Percentile_anomaly'] == True][date_column],
        y=group[group['is_Percentile_anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='palevioletred', symbol='circle', line=dict(width=1), size=9),
        name='Percentile Anomalies',
        customdata=group[group['is_Percentile_anomaly'] == True][['Percentile_anomaly']],
        hovertemplate=(
            f'Date: %{{x|%Y-%m-%d}}<br>' +
            f'{variable if variable == variable.upper() else variable.title()}: %{{y:~.2s}}<br>' +
            'Percentile Category: %{customdata[0]}<extra></extra>'
            )

        ))

    # Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_Anomaly'] == True][date_column],
        y=group[group['is_Anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='pink', symbol='cross', line=dict(width=1), size=9),
        name='Anomalies',
        hoverinfo='skip',
        ))

    fig.update_layout(
        title=dict(
                text=plot_title,
                y=0.96,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=18, color='black', weight='bold'),
            ),
        height=350,
        width=1200,
        margin=dict(l=50, r=50, t=40, b=30),
        plot_bgcolor='snow',
        paper_bgcolor='whitesmoke',
        xaxis=dict(
            range=[group[date_column].min(), group[date_column].max()],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis=dict(
            range=[group[variable].min()*0.9, group[variable].max()*1.06],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis_title=dict(
            text=variable if variable == variable.upper() else variable.title(),
            font=dict(size=16, weight='bold', color='black')
            ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
        )
    )

    fig.show()

    print("\n")
    
    # --------------------------------------------------------------------------------
    # SD Model Plot
    # --------------------------------------------------------------------------------
    
    fig = go.Figure()

    plot_title = "  --  ".join(list(group[group_columns].values[0])).upper() + "  --  SD Anomaly Detection"
    
    # Shading above upper line (upper anomaly region)
    fig.add_shape(
        type="rect",
        # Define the X range to span the entire plot width (0 to 1 in paper coordinates)
        x0=0, x1=1, xref="paper",
        # Define the Y range using the data values
        y0=group['SD2_high'].values[0], y1=group[variable].max()*1.06,
        yref="y",
        fillcolor="rgba(255, 0, 0, 0.055)", # Light blue with 30% opacity
        line=dict(width=0), # Hide the rectangle border
        layer="below" # Draw the shading underneath the data line
    )

    # Shading below lower line (lower anomaly region)
    fig.add_shape(
        type="rect",
        # Define the X range to span the entire plot width (0 to 1 in paper coordinates)
        x0=0, x1=1, xref="paper",
        # Define the Y range using the data values
        y0=0, y1=group['SD2_low'].values[0],
        yref="y",
        fillcolor="rgba(255, 0, 0, 0.055)", # Light blue with 30% opacity
        line=dict(width=0), # Hide the rectangle border
        layer="below" # Draw the shading underneath the data line
    )

    # Actuals
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group[variable],
        mode='lines',
        line=dict(color='seagreen', width=1.5),
        name=variable if variable == variable.upper() else variable.title(),
        ))

    # Evaluation period
    if eval_periods != None:
        fig.add_trace(go.Scatter(
            x=group[date_column][-eval_periods:],
            y=group[variable][-eval_periods:],
            mode='lines',
            line=dict(color='forestgreen', width=1.75),
            name='Evaluation Period'
        ))

    # Lower SD line
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['SD2_low'],
        mode='lines',
        line=dict(color='orangered', width=1, dash='dashdot'),
        name='SD Low',
        showlegend=False
        ))

    # Upper SD line
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['SD2_high'],
        mode='lines',
        line=dict(color='orangered', width=1, dash='dashdot'),
        name='SD High',
        showlegend=False
        ))

    # SD Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_SD_anomaly'] == True][date_column],
        y=group[group['is_SD_anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='palevioletred', symbol='circle', line=dict(width=1), size=9),
        name='SD Anomalies',
        customdata=group[group['is_SD_anomaly'] == True][['SD_anomaly']],
        hovertemplate=(
            f'Date: %{{x|%Y-%m-%d}}<br>' +
            f'{variable if variable == variable.upper() else variable.title()}: %{{y:~.2s}}<br>' +
            'SD Category: %{customdata[0]}<extra></extra>'
            )
        ))

    # Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_Anomaly'] == True][date_column],
        y=group[group['is_Anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='pink', symbol='cross', line=dict(width=1), size=9),
        name='Anomalies',
        hoverinfo='skip',
        ))

    fig.update_layout(
        title=dict(
                text=plot_title,
                y=0.96,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=18, color='black', weight='bold'),
            ),
        height=350,
        width=1200,
        margin=dict(l=50, r=50, t=40, b=30),
        plot_bgcolor='snow',
        paper_bgcolor='whitesmoke',
        xaxis=dict(
            range=[group[date_column].min(), group[date_column].max()],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis=dict(
            range=[group[variable].min()*0.9, group[variable].max()*1.06],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis_title=dict(
            text=variable if variable == variable.upper() else variable.title(),
            font=dict(size=16, weight='bold', color='black')
            ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
        )
    )

    fig.show()

    print("\n")


    # --------------------------------------------------------------------------------
    # MAD Model Plot
    # --------------------------------------------------------------------------------
    
    fig = go.Figure()

    plot_title = "  --  ".join(list(group[group_columns].values[0])).upper() + "  --  MAD Anomaly Detection"

    # Shading above upper line (upper anomaly region)
    fig.add_shape(
        type="rect",
        # Define the X range to span the entire plot width (0 to 1 in paper coordinates)
        x0=0, x1=1, xref="paper",
        # Define the Y range using the data values
        y0=group['MAD_high'].values[0], y1=group[variable].max()*1.06,
        yref="y",
        fillcolor="rgba(255, 0, 0, 0.055)",
        line=dict(width=0),
        layer="below"
    )

    # Shading below lower line (lower anomaly region)
    fig.add_shape(
        type="rect",
        # Define the X range to span the entire plot width (0 to 1 in paper coordinates)
        x0=0, x1=1, xref="paper",
        # Define the Y range using the data values
        y0=0, y1=group['MAD_low'].values[0],
        yref="y",
        fillcolor="rgba(255, 0, 0, 0.055)",
        line=dict(width=0),
        layer="below"
    )

    # Actuals
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group[variable],
        mode='lines',
        line=dict(color='seagreen', width=1.5),
        name=variable if variable == variable.upper() else variable.title(),
        ))

    # Evaluation period
    if eval_periods != None:
        fig.add_trace(go.Scatter(
            x=group[date_column][-eval_periods:],
            y=group[variable][-eval_periods:],
            mode='lines',
            line=dict(color='forestgreen', width=1.75),
            name='Evaluation Period'
        ))

    # Lower MAD line
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['MAD_low'],
        mode='lines',
        line=dict(color='orangered', width=1, dash='dashdot'),
        name='MAD Low',
        showlegend=False
        ))

    # Upper MAD line
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['MAD_high'],
        mode='lines',
        line=dict(color='orangered', width=1, dash='dashdot'),
        name='MAD High',
        showlegend=False
        ))

    # MAD Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_MAD_anomaly'] == True][date_column],
        y=group[group['is_MAD_anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='palevioletred', symbol='circle', line=dict(width=1), size=9),
        name='MAD Anomalies',
        customdata=group[group['is_MAD_anomaly'] == True][['MAD_anomaly']],
        hovertemplate=(
            f'Date: %{{x|%Y-%m-%d}}<br>' +
            f'{variable if variable == variable.upper() else variable.title()}: %{{y:~.2s}}<br>' +
            'MAD Category: %{customdata[0]}<extra></extra>'
            )
        ))

    # Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_Anomaly'] == True][date_column],
        y=group[group['is_Anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='pink', symbol='cross', line=dict(width=1), size=9),
        name='Anomalies',
        hoverinfo='skip',
        ))

    fig.update_layout(
        title=dict(
                text=plot_title,
                y=0.96,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=18, color='black', weight='bold'),
            ),
        height=350,
        width=1200,
        margin=dict(l=50, r=50, t=40, b=30),
        plot_bgcolor='snow',
        paper_bgcolor='whitesmoke',
        xaxis=dict(
            range=[group[date_column].min(), group[date_column].max()],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis=dict(
            range=[group[variable].min()*0.9, group[variable].max()*1.06],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis_title=dict(
            text=variable if variable == variable.upper() else variable.title(),
            font=dict(size=16, weight='bold', color='black')
            ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
        )
    )

    fig.show()

    print("\n")

    
    # --------------------------------------------------------------------------------
    # IQR Model Plot
    # --------------------------------------------------------------------------------
    
    fig = go.Figure()

    plot_title = "  --  ".join(list(group[group_columns].values[0])).upper() + "  --  IQR Anomaly Detection"

    # Shading above upper line (upper anomaly region)
    fig.add_shape(
        type="rect",
        # Define the X range to span the entire plot width (0 to 1 in paper coordinates)
        x0=0, x1=1, xref="paper",
        # Define the Y range using the data values
        y0=group['IQR_high'].values[0], y1=group[variable].max()*1.06,
        yref="y",
        fillcolor="rgba(255, 0, 0, 0.055)", # Light blue with 30% opacity
        line=dict(width=0), # Hide the rectangle border
        layer="below" # Draw the shading underneath the data line
    )

    # Shading below lower line (lower anomaly region)
    fig.add_shape(
        type="rect",
        # Define the X range to span the entire plot width (0 to 1 in paper coordinates)
        x0=0, x1=1, xref="paper",
        # Define the Y range using the data values
        y0=0, y1=group['IQR_low'].values[0],
        yref="y",
        fillcolor="rgba(255, 0, 0, 0.055)", # Light blue with 30% opacity
        line=dict(width=0), # Hide the rectangle border
        layer="below" # Draw the shading underneath the data line
    )
    
    # Actuals
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group[variable],
        mode='lines',
        line=dict(color='seagreen', width=1.5),
        name=variable if variable == variable.upper() else variable.title(),
        ))

    # Evaluation period
    if eval_periods != None:
        fig.add_trace(go.Scatter(
            x=group[date_column][-eval_periods:],
            y=group[variable][-eval_periods:],
            mode='lines',
            line=dict(color='forestgreen', width=1.75),
            name='Evaluation Period'
        ))

    # Lower IQR line
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['IQR_low'],
        mode='lines',
        line=dict(color='orangered', width=1, dash='dashdot'),
        name='IQR Low',
        showlegend=False
        ))

    # Upper IQR line
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['IQR_high'],
        mode='lines',
        line=dict(color='orangered', width=1, dash='dashdot'),
        name='IQR High',
        showlegend=False
        ))

    # IQR Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_IQR_anomaly'] == True][date_column],
        y=group[group['is_IQR_anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='palevioletred', symbol='circle', line=dict(width=1), size=9),
        name='IQR Anomalies',
        customdata=group[group['is_IQR_anomaly'] == True][['IQR_anomaly']],
        hovertemplate=(
            f'Date: %{{x|%Y-%m-%d}}<br>' +
            f'{variable if variable == variable.upper() else variable.title()}: %{{y:~.2s}}<br>' +
            'IQR Category: %{customdata[0]}<extra></extra>'
            )
        ))

    # Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_Anomaly'] == True][date_column],
        y=group[group['is_Anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='pink', symbol='cross', line=dict(width=1), size=9),
        name='Anomalies',
        hoverinfo='skip',
        ))

    fig.update_layout(
        title=dict(
                text=plot_title,
                y=0.96,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=18, color='black', weight='bold'),
            ),
        height=350,
        width=1200,
        margin=dict(l=50, r=50, t=40, b=30),
        plot_bgcolor='snow',
        paper_bgcolor='whitesmoke',
        xaxis=dict(
            range=[group[date_column].min(), group[date_column].max()],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis=dict(
            range=[group[variable].min()*0.9, group[variable].max()*1.06],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis_title=dict(
            text=variable if variable == variable.upper() else variable.title(),
            font=dict(size=16, weight='bold', color='black')
            ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
        )
    )

    fig.show()

    print("\n")
    
    
    # --------------------------------------------------------------------------------
    # EWMA Model Plot
    # --------------------------------------------------------------------------------
    
    fig = go.Figure()

    plot_title = "  --  ".join(list(group[group_columns].values[0])).upper() + "  --  EWMA Anomaly Detection"

    # Actuals
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group[variable],
        mode='lines',
        line=dict(color='seagreen', width=1.5),
        name=variable if variable == variable.upper() else variable.title(),
        ))

    # Evaluation period
    if eval_periods != None:
        fig.add_trace(go.Scatter(
            x=group[date_column][-eval_periods:],
            y=group[variable][-eval_periods:],
            mode='lines',
            line=dict(color='forestgreen', width=1.75),
            name='Evaluation Period'
        ))

    # EWMA Forecast
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['EWMA_forecast'],
        mode='lines',
        line=dict(color='slateblue', width=0.5, dash='dashdot'),
        name='EWMA Forecast',
        showlegend=True
        ))

    # EWMA low line
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['EWMA_low'],
        mode='lines',
        line=dict(color='orangered', width=1, dash='dashdot'),
        name='EWMA Low',
        showlegend=False
        ))
    
    # Lower Shading
    fig.add_trace(go.Scatter(
        x=group[group['EWMA_low'].isna()==False][date_column],
        y=[0] * len(group[group['EWMA_low'].isna()==False]),
        mode="lines",
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=False,
        fill="tonexty",
        fillcolor="rgba(255, 0, 0, 0.07)"
    ))
    
    # EWMA high line
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['EWMA_high'],
        mode='lines',
        line=dict(color='orangered', width=1, dash='dashdot'),
        name='EWMA High',
        showlegend=False,
        ))
    
    # Upper Shading
    fig.add_trace(go.Scatter(
        x=group[group['EWMA_high'].isna()==False][date_column],
        y=[group[variable].max() * 1.06] * len(group[group['EWMA_high'].isna()==False]),
        mode="lines",
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=False,
        fill="tonexty",
        fillcolor="rgba(255, 0, 0, 0.07)"
        ))
    
    # EWMA Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_EWMA_anomaly'] == True][date_column],
        y=group[group['is_EWMA_anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='palevioletred', symbol='circle', line=dict(width=1), size=9),
        name='EWMA Anomalies',
        # customdata=group[group['is_EWMA_anomaly'] == True][['IQR_anomaly']],
        # hovertemplate=(
        #     f'Date: %{{x|%Y-%m-%d}}<br>' +
        #     f'{variable if variable == variable.upper() else variable.title()}: %{{y:~.2s}}<br>' +
        #     'IQR Category: %{customdata[0]}<extra></extra>'
        #     )
        ))

    # Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_Anomaly'] == True][date_column],
        y=group[group['is_Anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='pink', symbol='cross', line=dict(width=1), size=9),
        name='Anomalies',
        hoverinfo='skip',
        ))

    fig.update_layout(
        title=dict(
                text=plot_title,
                y=0.96,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=18, color='black', weight='bold'),
            ),
        height=350,
        width=1200,
        margin=dict(l=50, r=50, t=40, b=30),
        plot_bgcolor='snow',
        paper_bgcolor='whitesmoke',
        xaxis=dict(
            range=[group[date_column].min(), group[date_column].max()],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis=dict(
            range=[min(group['EWMA_low'].min(), group[variable].min())*0.9, group[variable].max()*1.06],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis_title=dict(
            text=variable if variable == variable.upper() else variable.title(),
            font=dict(size=16, weight='bold', color='black')
            ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
        )
    )

    fig.show()

    print("\n")

    
    # --------------------------------------------------------------------------------
    # FB Prophet Model Plot
    # --------------------------------------------------------------------------------
    
    fig = go.Figure()

    plot_title = "  --  ".join(list(group[group_columns].values[0])).upper() + "  --  FB Prophet Anomaly Detection"

    # Actuals
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group[variable],
        mode='lines',
        line=dict(color='seagreen', width=1.5),
        name=variable if variable == variable.upper() else variable.title(),
        ))

    # Evaluation period
    if eval_periods != None:
        fig.add_trace(go.Scatter(
            x=group[date_column][-eval_periods:],
            y=group[variable][-eval_periods:],
            mode='lines',
            line=dict(color='forestgreen', width=1.75),
            name='Evaluation Period'
        ))

    # FB Forecast
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['FB_forecast'],
        mode='lines',
        line=dict(color='slateblue', width=0.5, dash='dashdot'),
        name='FB Forecast',
        showlegend=True
        ))

    # Lower FB line
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['FB_low'],
        mode='lines',
        line=dict(color='orangered', width=1, dash='dashdot'),
        name='FB Low',
        showlegend=False
        ))

    # Lower Shading
    fig.add_trace(go.Scatter(
        x=group[group['FB_low'].isna()==False][date_column],
        y=[0] * len(group[group['FB_low'].isna()==False]),
        mode="lines",
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=False,
        fill="tonexty",
        fillcolor="rgba(255, 0, 0, 0.07)"
    ))

    # Upper FB line
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['FB_high'],
        mode='lines',
        line=dict(color='orangered', width=1, dash='dashdot'),
        name='FB High',
        showlegend=False,
        ))
    
    # Upper Shading
    fig.add_trace(go.Scatter(
        x=group[group['FB_high'].isna()==False][date_column],
        y=[group[variable].max() * 1.06] * len(group[group['FB_high'].isna()==False]),
        mode="lines",
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=False,
        fill="tonexty",
        fillcolor="rgba(255, 0, 0, 0.07)"
        ))

    # FB Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_FB_anomaly'] == True][date_column],
        y=group[group['is_FB_anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='palevioletred', symbol='circle', line=dict(width=1), size=9),
        name='FB Anomalies',
        # customdata=group[group['is_FB_anomaly'] == True][['IQR_anomaly']],
        # hovertemplate=(
        #     f'Date: %{{x|%Y-%m-%d}}<br>' +
        #     f'{variable if variable == variable.upper() else variable.title()}: %{{y:~.2s}}<br>' +
        #     'IQR Category: %{customdata[0]}<extra></extra>'
        #     )
        ))

    # Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_Anomaly'] == True][date_column],
        y=group[group['is_Anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='pink', symbol='cross', line=dict(width=1), size=9),
        name='Anomalies',
        hoverinfo='skip',
        ))

    fig.update_layout(
        title=dict(
                text=plot_title,
                y=0.96,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=18, color='black', weight='bold'),
            ),
        height=350,
        width=1200,
        margin=dict(l=50, r=50, t=40, b=30),
        plot_bgcolor='snow',
        paper_bgcolor='whitesmoke',
        xaxis=dict(
            range=[group[date_column].min(), group[date_column].max()],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis=dict(
            range=[min(group['FB_low'].min(), group[variable].min())*0.9, group[variable].max()*1.06],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis_title=dict(
            text=variable if variable == variable.upper() else variable.title(),
            font=dict(size=16, weight='bold', color='black')
            ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
        )
    )

    fig.show()

    print("\n")

    
    # --------------------------------------------------------------------------------
    # DBSCAN Model Plot
    # --------------------------------------------------------------------------------
    
    fig = go.Figure()

    plot_title = "  --  ".join(list(group[group_columns].values[0])).upper() + "  --  DBSCAN Anomaly Detection"

    # Actuals
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group[variable],
        mode='lines',
        # line=dict(color='seagreen', width=1.5),
        line=dict(color='rgba(46, 139, 87, 0.5)', width=1.5),
        name=variable if variable == variable.upper() else variable.title(),
        ))

    # Evaluation period
    if eval_periods != None:
        fig.add_trace(go.Scatter(
            x=group[date_column][-eval_periods:],
            y=group[variable][-eval_periods:],
            mode='lines',
            line=dict(color='forestgreen', width=1.75),
            name='Evaluation Period'
        ))
    
    # DBSCAN Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_DBSCAN_anomaly'] == True][date_column],
        y=group[group['is_DBSCAN_anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='mediumorchid', symbol='circle', line=dict(width=1), size=7),
        name='DBSCAN Anomalies',
        ))

    # DBSCAN Score Threshold
    fig.add_trace(go.Scatter(
        x=group[group['DBSCAN_score'].isna()==False][date_column],
        y=np.zeros(len(group[group['DBSCAN_score'].isna()==False])),
        mode='lines',
        line=dict(color='orangered', width=1, dash='dashdot'),
        name='DBSCAN Score Anomaly Threshold',
        yaxis='y2',
        showlegend=False,
        ))

    # Upper Shading
    fig.add_trace(go.Scatter(
        x=group[group['DBSCAN_score'].isna()==False][date_column],
        y=[max(0.5, group['DBSCAN_score'].max() * 1.1)] * len(group[group['DBSCAN_score'].isna()==False]),
        mode="lines",
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=False,
        fill="tonexty",
        fillcolor="rgba(255, 0, 0, 0.07)",
        yaxis='y2',
        ))

    # DBSCAN Scores
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['DBSCAN_score'],
        mode='lines',
        line=dict(color='midnightblue', width=1.5, shape='vh'),
        name='DBSCAN Scores',
        yaxis='y2',
        ))

    # DBSCAN Anomalies on the DBSCAN_scores line
    fig.add_trace(go.Scatter(
        x=group[group['is_DBSCAN_anomaly'] == True][date_column],
        y=group[group['is_DBSCAN_anomaly'] == True]['DBSCAN_score'],
        mode='markers',
        marker=dict(color='palevioletred', symbol='square', line=dict(width=1), size=9),
        name='DBSCAN Score Anomalies',
        yaxis='y2',
        ))

    # Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_Anomaly'] == True][date_column],
        y=group[group['is_Anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='pink', symbol='cross', line=dict(width=1), size=9),
        name='Anomalies',
        hoverinfo='skip',
        ))

    fig.update_layout(
        title=dict(
                text=plot_title,
                y=0.96,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=18, color='black', weight='bold'),
            ),
        height=350,
        width=1200,
        margin=dict(l=50, r=200, t=40, b=30),
        plot_bgcolor='snow',
        paper_bgcolor='whitesmoke',
        xaxis=dict(
            range=[group[date_column].min(), group[date_column].max()],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis=dict(
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis_title=dict(
            text=variable if variable == variable.upper() else variable.title(),
            font=dict(size=16, weight='bold', color='black')
            ),
        yaxis2=dict(
            range=[group['DBSCAN_score'].min() * 1.1, max(0.5, group['DBSCAN_score'].max() * 1.1)],
            title='DBSCAN Scores',
            overlaying='y',
            side='right',
            showgrid=False,
            zeroline=False,
            linecolor='purple',
            ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.1,
        )
    )

    fig.show()

    print("\n")


    # --------------------------------------------------------------------------------
    # Isolation Forest Model Plot
    # --------------------------------------------------------------------------------
    
    fig = go.Figure()

    plot_title = "  --  ".join(list(group[group_columns].values[0])).upper() + "  --  Isolation Forest Anomaly Detection"

    # Actuals
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group[variable],
        mode='lines',
        # line=dict(color='seagreen', width=1.5),
        line=dict(color='rgba(46, 139, 87, 0.5)', width=1.5),
        name=variable if variable == variable.upper() else variable.title(),
        ))

    # Evaluation period
    if eval_periods != None:
        fig.add_trace(go.Scatter(
            x=group[date_column][-eval_periods:],
            y=group[variable][-eval_periods:],
            mode='lines',
            line=dict(color='forestgreen', width=1.75),
            name='Evaluation Period'
        ))
    
    # Isolation Forest Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_IsolationForest_anomaly'] == True][date_column],
        y=group[group['is_IsolationForest_anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='mediumorchid', symbol='circle', line=dict(width=1), size=7),
        name='Isolation Forest Anomalies',
        ))

    # Isolation Forest Score Threshold
    fig.add_trace(go.Scatter(
        x=group[group['isolation_forest_anomaly_threshold'].isna()==False][date_column],
        y=np.zeros(len(group[group['isolation_forest_anomaly_threshold'].isna()==False])),
        mode='lines',
        line=dict(color='orangered', width=1, dash='dashdot'),
        name='Isolation Forest Score Anomaly Threshold',
        yaxis='y2',
        showlegend=False,
        ))

    # Lower Shading
    fig.add_trace(go.Scatter(
        x=group[group['isolation_forest_score'].isna()==False][date_column],
        y=[min(1.1 * group['isolation_forest_score'].min(), -0.2 * group['isolation_forest_score'].max())] * len(group[group['isolation_forest_score'].isna()==False]),
        mode="lines",
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=False,
        fill="tonexty",
        fillcolor="rgba(255, 0, 0, 0.07)",
        yaxis='y2',
        ))

    # Isolation Forest Scores
    fig.add_trace(go.Scatter(
        x=group[date_column],
        y=group['isolation_forest_score'],
        mode='lines',
        line=dict(color='midnightblue', width=1.5, shape='vh'),
        name='Isolation Foreset Scores',
        yaxis='y2',
        ))

    # Isolation Forest Anomalies on the isolation_forest_score line
    fig.add_trace(go.Scatter(
        x=group[group['is_IsolationForest_anomaly'] == True][date_column],
        y=group[group['is_IsolationForest_anomaly'] == True]['isolation_forest_score'],
        mode='markers',
        marker=dict(color='palevioletred', symbol='square', line=dict(width=1), size=9),
        name='Isolation Forest Score Anomalies',
        yaxis='y2',
        # showlegend=False,
        ))

    # Anomalies
    fig.add_trace(go.Scatter(
        x=group[group['is_Anomaly'] == True][date_column],
        y=group[group['is_Anomaly'] == True][variable],
        mode='markers',
        marker=dict(color='pink', symbol='cross', line=dict(width=1), size=9),
        name='Anomalies',
        hoverinfo='skip',
        ))

    fig.update_layout(
        title=dict(
                text=plot_title,
                y=0.96,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=18, color='black', weight='bold'),
            ),
        height=350,
        width=1200,
        margin=dict(l=50, r=200, t=40, b=30),
        plot_bgcolor='snow',
        paper_bgcolor='whitesmoke',
        xaxis=dict(
            range=[group[date_column].min(), group[date_column].max()],
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis=dict(
            showline=True,
            linewidth=0.5,
            linecolor='orange',
            zeroline=False,
            gridcolor='rgba(255, 165, 0, 0.1)',
            mirror=True
            ),
        yaxis_title=dict(
            text=variable if variable == variable.upper() else variable.title(),
            font=dict(size=16, weight='bold', color='black')
            ),
        yaxis2=dict(
            range=[min(1.1 * group['isolation_forest_score'].min(), -0.2 * group['isolation_forest_score'].max()), group['isolation_forest_score'].max() * 1.1],
            title='Isolation Forest Scores',
            overlaying='y',
            side='right',
            showgrid=False,
            zeroline=False,
            linecolor='purple',
            ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.1,
        )
    )

    fig.show()

    print("\n")
