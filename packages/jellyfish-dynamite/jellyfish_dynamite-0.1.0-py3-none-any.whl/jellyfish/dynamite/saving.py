
# ==================== SAVE FUNCTIONS ====================

def save_figure_with_timestamp(fig, plots, base_filename="psd_anal", output_directory=None):
    """Save a figure with timestamp as part of the filename for versioning."""
    if output_directory is None:
        daily_dir = jelfun.make_daily_directory()
        output_directory = f"{daily_dir}/jellyfish_dynamite_plots"
    
    # Create directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Save figure with timestamp
    fig_filename = f"{base_filename}_{jelfun.get_timestamp()}_fig.png"
    fig_path = os.path.join(output_directory, fig_filename)
    
    # Save the figure
    fig.savefig(fig_path, bbox_inches='tight', dpi=200)
    
    # Save pair data as JSON
    data_filename = f"{base_filename}_{jelfun.get_timestamp()}_pairdata.json"
    data_path = os.path.join(output_directory, data_filename)
    
    # Export data
    export_data = []
    for plot in plots:
        file_data = {
            'filename': plot.filename,
            'pairs': []
        }
        for pair in plot.pairs:
            file_data['pairs'].append({
                'f0': float(pair['f0']),
                'f1': float(pair['f1']),
                'f1_f0_ratio': float(pair['f1'] / pair['f0'])
            })
        export_data.append(file_data)
    
    # Save the data
    with open(data_path, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"Figure saved to {fig_path}")
    print(f"Data saved to {data_path}")

    return fig_path, data_path

def save_jellyfish_jinja(template_vars, template_name, base_filename="psd_analysis", output_directory=None, **kwargs):
    """Agnostic Jinja templating function - works with any template and data."""
    
    # Custom JSON encoder for NumPy types
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.number):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)
    
    # Use daily_dir as default if none provided
    if output_directory is None:
        try:
            daily_dir = jelfun.make_daily_directory()
            output_directory = f"{daily_dir}/jellyfish_dynamite_html"
        except:
            output_directory = "html_output"
    
    # Create directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Load template file
    if not os.path.exists(template_name):
        print(f"Template not found: {template_name}")
        print(f"Current directory: {os.getcwd()}")
        return None, None, None
    
    with open(template_name, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Create Jinja2 template and render
    template = Template(template_content)
    html_str = template.render(**template_vars)
    
    # Define file paths
    html_filename = f"{base_filename}_{jelfun.get_timestamp()}.html"
    html_path = os.path.join(output_directory, html_filename)
    
    # Save HTML file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_str)
    
    print(f"HTML saved to: {html_path}")
    
    try:
        # webbrowser.open(f'file://{os.path.abspath(html_path)}')
        print(f"Opening HTML file in browser...")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print(f"Please open manually: {html_path}")
    
    return html_path

def prepare_plotly_template_vars(plots, methods=None, dir_name=None, use_db_scale=True, output_directory=None, pagination_info=None, **kwargs):
    """Prepare template variables specifically for Plotly templates with dual scale support."""

    # Custom JSON encoder for NumPy types
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.number):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    # Calculate grid dimensions from plots
    total_plots = len(plots)
    filenames = set()
    methods_set = set()
    for plot in plots:
        base_name = plot.filename.split(' (')[0] if ' (' in plot.filename else plot.filename
        filenames.add(base_name)
        if hasattr(plot, 'method_name'):
            methods_set.add(plot.method_name)

    n_files = len(filenames)
    n_methods = len(methods_set) if methods_set else total_plots
    n_rows = n_files
    n_cols = n_methods

    # Calculate vertical spacing
    if n_rows > 1:
        v_spacing = min(0.15, 0.2 / (n_rows - 1))
    else:
        v_spacing = 0.15

    # Create plotly figure with subplots
    plotly_fig = make_subplots(
        rows=n_rows, 
        cols=n_cols,
        subplot_titles=[getattr(plot, 'filename', f"Plot {i+1}") for i, plot in enumerate(plots)],
        vertical_spacing=v_spacing,
        horizontal_spacing=0.08, 
        #specs=[[{"secondary_y": True} for _ in range(n_cols)] for _ in range(n_rows)]  # ADD THIS
    )

    # Helper function to safely convert arrays
    def safe_tolist(arr):
        if hasattr(arr, 'tolist'):
            return arr.tolist()
        elif isinstance(arr, (list, tuple)):
            return list(arr)
        else:
            return arr

    # Process each plot
    for i, plot in enumerate(plots):

        print(f"\n=== PROCESSING PLOT {i} ===")
        print(f"Plot filename: {getattr(plot, 'filename', 'Unknown')}")
        print(f"Plot method: {getattr(plot, 'method_name', 'Unknown')}")
        
        file_idx = i // n_methods
        method_idx = i % n_methods
        row = file_idx + 1
        col = method_idx + 1
                
        frequencies = safe_tolist(plot.frequencies)        
        
        # Get both linear and dB versions of the data
        linear_psd = safe_tolist(plot.original_psd if hasattr(plot, 'original_psd') else plot.psd)
        db_psd = safe_tolist(plot.psd_db)
        
        # Also get peak data in both scales
        peak_freqs = safe_tolist(plot.peak_freqs)

        # Calculate peak powers for both scales
        peak_powers_linear = []
        peak_powers_db = []
        for peak_freq in plot.peak_freqs:
            freq_idx = np.argmin(np.abs(plot.frequencies - peak_freq))
            peak_powers_linear.append(float(plot.psd_linear[freq_idx]))
            peak_powers_db.append(float(plot.psd_db[freq_idx]))

        # Use the scale parameter to determine starting data
        starting_psd = db_psd if use_db_scale else linear_psd
        starting_peak_powers = peak_powers_db if use_db_scale else peak_powers_linear

        # Calculate and add spectral ridge and vein data
        ridge_data = None
        veins_data = None

        # BEFORE adding spectrogram to Plotly:
        # Check if this plot has spectrogram data (FFT_DUAL method)
        if (hasattr(plot, 'has_spectrogram') and plot.has_spectrogram and 
            hasattr(plot, 'spectrogram_linear') and plot.spectrogram_linear is not None):
            try:
                # Calculate spectral ridge
                ridge_times, ridge_freqs = find_max_energy_ridge(
                    plot.spectrogram_linear, plot.frequencies, plot.times
                )
                ridge_data = {
                    'times': safe_tolist(ridge_times),
                    'freqs': safe_tolist(ridge_freqs)
                }
                
                # Calculate spectral veins
                veins = find_spectral_veins(
                    plot.spectrogram_linear, plot.frequencies, plot.times, 
                    num_veins=getattr(plot, 'num_veins', 6)
                )
                veins_data = []
                for vein in veins:
                    veins_data.append({
                        'times': safe_tolist(vein['times']),
                        'freqs': safe_tolist(vein['freqs']),
                        'center_freq': float(vein['center_freq']),
                        'rank': int(vein['rank'])
                    })
                    
                print(f"SUCCESS: Calculated ridge/veins for plot {i} - Ridge points: {len(ridge_data['freqs'])}, Veins: {len(veins_data)}")
                    
            except Exception as e:
                print(f"ERROR calculating ridge/veins for plot {i}: {e}")
                ridge_data = None
                veins_data = None

            # DEBUG 
            # Check if data was calculated
            print(f"RIDGE/VEIN DEBUG plot {i}: ridge_data={ridge_data is not None}, veins_data={veins_data is not None}")
            if ridge_data:
                print(f"  Ridge has {len(ridge_data['freqs'])} points")
            if veins_data:
                print(f"  Veins has {len(veins_data)} veins")

            # DEBUG
            print(f"PYTHON DEBUG for plot {i}:")
            print(f"  ridge_data exists: {ridge_data is not None}")
            print(f"  veins_data exists: {veins_data is not None}")
            if ridge_data:
                print(f"  ridge_data keys: {ridge_data.keys()}")
                print(f"  ridge freqs length: {len(ridge_data['freqs'])}")
                print(f"  ridge times length: {len(ridge_data['times'])}")
            if veins_data:
                print(f"  veins_data length: {len(veins_data)}")
                print(f"  first vein sample: {veins_data[0] if veins_data else 'None'}")

            times = safe_tolist(plot.times)

        # S P E C T R O G R A M !!!!!
        # remember - only the fft has this for now, wil fail for CQT etc. 
        # BEFORE adding spectrogram to Plotly:
        if hasattr(plot, 'has_spectrogram') and plot.has_spectrogram:
            times = safe_tolist(plot.times)
            
            # Scale time to PSD range**
            psd_min = np.min(starting_psd)
            psd_max = np.max(starting_psd)
            time_min = np.min(plot.times)
            time_max = np.max(plot.times)

            # Scale times to use 50% of PSD range at the top
            psd_range = psd_max - psd_min
            scaled_times = []
            for t in plot.times:
                # Map time to top 50% of PSD range
                normalized_time = (t - time_min) / (time_max - time_min)  # 0 to 1
                scaled_time = psd_max - (psd_range * 0.5) + (normalized_time * psd_range * 0.5)
                scaled_times.append(scaled_time)            

            # Right before the problematic line:
            print(f"About to check spectrogram for plot {i}")
            print(f"plot.spectrogram_db type: {type(getattr(plot, 'spectrogram_db', 'MISSING'))}")
            
            # Keep as numpy array until the last moment
            spec_array = plot.spectrogram_db  # Already numpy array
            spec_array_transposed = spec_array.T  # Transpose the numpy array
            
            # Convert to list only for Plotly
            spectrogram_data = spec_array_transposed.tolist()
            
            # Add as background heatmap (same axes as PSD)
            plotly_fig.add_trace(
                go.Heatmap(
                    x=frequencies,  # X-axis: frequency (matches PSD)
                    y=scaled_times,        # Y-axis: time (will be scaled to fit PSD y-range)
                    z=spectrogram_data,  # converted to list from transposed numpy aray
                    colorscale='magma', #'viridis', 'magma', 'plasma', 'hot', 'turbo', 'jet'
                    opacity=1.0,  # Low opacity for background effect
                    showscale=False, # Remove sidebar for gradient legend
                    name=f"spectrogram_{i}",
                    hovertemplate='Freq: %{x:.1f} Hz<br>Time: %{y:.3f} s<br>Power: %{z:.2f}<extra></extra>',
                    zmin=np.min(spec_array),
                    zmax=np.max(spec_array),
                ),
                row=row, col=col,
                #secondary_y=True  # Put on secondary Y-axis
            )

        # Add main PSD curve with both scales stored on primary Y-axis
        plotly_fig.add_trace(
            go.Scatter(
                x=frequencies,
                y=starting_psd,
                mode='lines',
                name=f"psd_{i}",
                line=dict(color='black', width=2),
                showlegend=False,
                # Store both scales in customdata/meta
                meta={
                    'linear_psd': linear_psd,
                    'db_psd': db_psd,
                    'scale_type': 'main_trace',
                    # Add spectrogram meta if available
                    'has_spectrogram': hasattr(plot, 'has_spectrogram') and plot.has_spectrogram,
                    'spectrogram_linear': safe_tolist(plot.spectrogram_linear) if hasattr(plot, 'spectrogram_linear') else None,
                    'spectrogram_db': safe_tolist(plot.spectrogram_db) if hasattr(plot, 'spectrogram_db') else None,
                    'times': times if hasattr(plot, 'has_spectrogram') and plot.has_spectrogram else None,
                    # Add veins and ridges
                    'ridge_data': ridge_data,
                    'veins_data': veins_data
                }
            ),
            row=row, col=col,
        )
        
        # Add detected peaks with both scales stored on primary Y-axis  
        plotly_fig.add_trace(
            go.Scatter(
                x=peak_freqs,
                y=starting_peak_powers,
                mode='markers',
                name=f"peaks_{i}",
                marker=dict(color='gray', size=5, opacity=0.7),
                showlegend=False,
                meta={
                    'linear_powers': peak_powers_linear,
                    'db_powers': peak_powers_db,
                    'scale_type': 'peak_trace'
                }
            ),
            row=row, col=col,
            secondary_y=False  # Optional but clear
        )
        
        # Add spectral ridge if available!!
        if ridge_data is not None:
            plotly_fig.add_trace(
                go.Scatter(
                    x=ridge_data['freqs'],
                    y=ridge_data['times'],
                    mode='lines',
                    name=f"ridge_{i}",
                    line=dict(color='cyan', width=2.5),
                    showlegend=False,
                    visible=False,  # toggle visibility with 'e' key
                    meta={
                        'scale_type': 'ridge_trace'
                    }
                ),
                row=row, col=col
            )

        # Set axis properties
        if hasattr(plot, 'plot_fmin') and hasattr(plot, 'plot_fmax'):
            plotly_fig.update_xaxes(range=[plot.plot_fmin, plot.plot_fmax], row=row, col=col)
        plotly_fig.update_xaxes(title_text="Frequency (Hz)", row=row, col=col)
        plotly_fig.update_yaxes(title_text="PSD (dB)", row=row, col=col, secondary_y=False)  # Primary Y
        plotly_fig.update_yaxes(title_text="Time (s)", row=row, col=col, secondary_y=True)   # Secondary Y


    # Update main layout
    plotly_fig.update_layout(
        title=f"Interactive Spectral Analysis - Dir: {dir_name} - prepare_plotly_template_vars",
        height=max(600, 500 * n_rows),
        width=max(800, 300 * n_cols),
        template="plotly_white",
        margin=dict(l=50, r=50, t=100, b=50)
    )

    # Convert to JSON
    fig_json = plotly_fig.to_json()
    fig_dict = json.loads(fig_json)

    subplot_titles = [getattr(plot, 'filename', f"Plot {i+1}") for i, plot in enumerate(plots)]

    # Audio source path calculation for browser access
    audio_source_path = ""
    if 'audio_directory' in kwargs and kwargs['audio_directory']:
        try:
            audio_dir = Path(kwargs['audio_directory'])

            # For Flask uploads, use the session directory structure
            if 'temp_uploads' in str(audio_dir):
                # Extract session ID from path like "temp_uploads/0f6c2775"
                parts = audio_dir.parts
                if 'temp_uploads' in parts:
                    session_idx = parts.index('temp_uploads')
                    if len(parts) > session_idx + 1:
                        session_id = parts[session_idx + 1]
                        audio_source_path = f"temp_uploads/{session_id}"
                        print(f"🎵 Flask session audio path: {audio_source_path}")

            # Original logic for direct audio directories
            else:    
                # Extract the relative path from code/ directory
                # e.g., if audio_directory is "/Users/me/code/tranche/slices/2556"
                # we want "tranche/slices/2556"
                audio_dir_str = str(audio_dir).replace('\\', '/')
                
                if 'code/' in audio_dir_str:
                    # Split on 'code/' and take the part after it
                    audio_source_path = '/' + audio_dir_str.split('code/')[-1] # leading slash looks in server root
                else:
                    # Fallback: try to construct relative path
                    # Look for tranche/slices pattern
                    parts = audio_dir.parts
                    try:
                        tranche_idx = parts.index('tranche')
                        audio_source_path = '/'.join(parts[tranche_idx:])
                    except ValueError:
                        # Last resort: use directory name
                        audio_source_path = audio_dir.name
                
            print(f"🎵 Audio source path calculated: {audio_source_path}")
            
            # Debug info
            print(f"🔍 DEBUG AUDIO PATHS:")
            print(f"  Original audio directory: {audio_dir}")
            print(f"  Calculated source path: {audio_source_path}")
            
        except Exception as e:
            print(f"⚠️  Could not calculate audio path: {e}")
            audio_source_path = ""


    # Return template variables for Plotly
    return {
        # Audio configuration
        'AUDIO_SOURCE_PATH': audio_source_path,
        
        # Plot display stuff
        'PLOT_ID': f"plot_{jelfun.get_timestamp()}",
        'PLOT_HEIGHT': max(600, 500 * n_rows),
        'PLOT_WIDTH': max(800, 300 * n_cols),
        'PLOT_DATA': json.dumps(fig_dict['data']),
        'LAYOUT_DATA': json.dumps(fig_dict['layout']),
        'SUBPLOT_TITLES': json.dumps(subplot_titles), 
        'DIR_NAME': dir_name, 
        'USE_DB_SCALE': 'true' if use_db_scale else 'false',
        'N_ROWS': n_rows,
        'N_COLS': n_cols,
        'TOTAL_PLOTS': len(plots), 
        
        # Spectral resolution params
        'PSD_N_FFT': kwargs.get('psd_n_fft', 1024),
        'SPEC_N_FFT': kwargs.get('spec_n_fft', 512), 
        'PSD_HOP_LENGTH': kwargs.get('psd_hop_length', 512),
        'SPEC_HOP_LENGTH': kwargs.get('spec_hop_length', 512), 

        # Pagination stuff for loading large html files, validation
        'PAGINATION_INFO': json.dumps(pagination_info) if pagination_info else 'null',
        'CURRENT_PAGE': pagination_info['current_page'] if pagination_info else 1,
        'TOTAL_PAGES': pagination_info['total_pages'] if pagination_info else 1,
    }

def save_spectrogram_images(plots, output_directory):
    """Save spectrograms as PNG images for HTML background use."""
    print(f"DEBUG: save_spectrogram_images called with {len(plots)} plots")
    print(f"DEBUG: output_directory = {output_directory}")

    spectrogram_paths = []

    for i, plot in enumerate(plots):
        print(f"DEBUG: Plot {i} - has_spectrogram: {hasattr(plot, 'has_spectrogram')}")
        if hasattr(plot, 'has_spectrogram'):
            print(f"DEBUG: Plot {i} - has_spectrogram value: {plot.has_spectrogram}")
        
        if hasattr(plot, 'has_spectrogram') and plot.has_spectrogram:
            print(f"DEBUG: Processing spectrogram for plot {i}")
            try:
                # Create matplotlib figure for spectrogram
                fig_spec, ax_spec = plt.subplots(figsize=(8, 6))
                
                # FIXED: Use imshow instead of pcolormesh for easier handling
                im = ax_spec.imshow(
                    plot.spectrogram_db,
                    aspect='auto',
                    origin='lower',
                    cmap='magma',
                    alpha=0.7,
                    extent=[
                        plot.frequencies[0], plot.frequencies[-1],  # X range (frequency)
                        plot.times[0], plot.times[-1]              # Y range (time)
                    ]
                )
                
                ax_spec.set_xlim(plot.plot_fmin, plot.plot_fmax)
                ax_spec.set_xlabel('Frequency (Hz)')
                ax_spec.set_ylabel('Time (s)')
                ax_spec.set_title(f'Spectrogram - {plot.filename}')
                
                # Save as PNG - FIXED VARIABLE NAME
                spec_filename = f"spectrogram_{i}_{jelfun.get_timestamp()}.png"
                spec_path = os.path.join(output_directory, spec_filename)  # ADD THIS LINE
                fig_spec.savefig(spec_path, bbox_inches='tight', dpi=150, transparent=True)
                plt.close(fig_spec)
                
                print(f"DEBUG: Saved spectrogram to: {spec_path}")
                print(f"DEBUG: File exists: {os.path.exists(spec_path)}")
                spectrogram_paths.append(spec_filename)
                
            except Exception as e:
                print(f"ERROR saving spectrogram for plot {i}: {e}")
                import traceback
                traceback.print_exc()  # This will show the full error
                spectrogram_paths.append(None)
        else:
            print(f"DEBUG: Plot {i} has no spectrogram")
            spectrogram_paths.append(None)

    print(f"DEBUG: Final spectrogram_paths: {spectrogram_paths}")
    return spectrogram_paths


def save_jellyfish_plotly(plots, 
                        base_filename="psd_analysis_plotly", 
                        output_directory=None,
                        methods=None, 
                        dir_name=None, 
                        use_db_scale=True,  
                        pagination_info=None,
                        **kwargs):
    """Convenience wrapper for saving Plotly plots using Jinja templates."""
    n_fft = kwargs.get('n_fft')
    nfft_suffix = f"_nfft{n_fft}" if n_fft else ""

    # Set up output directory FIRST
    if output_directory is None:
        daily_dir = jelfun.make_daily_directory()
        output_directory = f"{daily_dir}/jellyfish_dynamite_html"
    os.makedirs(output_directory, exist_ok=True)

    # Generate spectrogram images with proper output directory 
    spectrogram_images = save_spectrogram_images(plots, output_directory)

    # Prepare template variables including audio source path
    template_vars = prepare_plotly_template_vars(
        plots, methods, dir_name, use_db_scale, 
        output_directory=output_directory, 
        audio_directory=kwargs.get('audio_directory')
    )

    # ADD SPECTROGRAM DATA TO TEMPLATE VARS
    template_vars['SPECTROGRAM_IMAGES'] = json.dumps(spectrogram_images)
    template_vars['HAS_SPECTROGRAMS'] = any(img is not None for img in spectrogram_images)

    # FIX THE GRID CALCULATION
    # Get unique filenames (files) and methods
    unique_files = set()
    unique_methods = set()

    for plot in plots:
        # Extract base filename without method suffix
        base_name = plot.filename.split(' (')[0] if ' (' in plot.filename else plot.filename
        unique_files.add(base_name)
        
        # Get method name
        if hasattr(plot, 'method_name'):
            unique_methods.add(plot.method_name)

    n_files = len(unique_files)
    n_methods = len(unique_methods) if unique_methods else 1

    # In the grid: rows = files, cols = methods
    template_vars['N_ROWS'] = n_files
    template_vars['N_COLS'] = n_methods
    template_vars['TOTAL_PLOTS'] = len(plots)

    print(f"DEBUG: Grid dimensions - {n_files} files × {n_methods} methods = {len(plots)} total plots")

    # Use the Plotly template
    #template_name = "jellyfish_dynamite_plotly.html"
    template_name = "dynamo.html"

    # Call the agnostic Jinja function
    html_path = save_jellyfish_jinja(template_vars, template_name, base_filename, output_directory)

    # Save pair and graph data (existing code from original function)
    data_filename = f"{dir_name}_{base_filename}{nfft_suffix}_{jelfun.get_timestamp()}_pairdata.json"
    data_path = os.path.join(output_directory, data_filename)

    export_data = []
    for plot in plots:
        file_data = {
            'filename': getattr(plot, 'filename', 'Untitled'),
            'method': getattr(plot, 'method_name', 'Unknown'),
            'pairs': []
        }
        if hasattr(plot, 'pairs'):
            for pair in plot.pairs:
                if 'f0' in pair and 'f1' in pair:
                    file_data['pairs'].append({
                        'f0': float(pair['f0']),
                        'f1': float(pair['f1']),
                        'ratio': float(pair['f1'] / pair['f0'])
                    })
        export_data.append(file_data)

    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2)

    # Save graph data
    graph_filename = f"{dir_name}_{base_filename}{nfft_suffix}_{jelfun.get_timestamp()}_graphdata.json"
    graph_path = os.path.join(output_directory, graph_filename)

    graph_export_data = []
    for plot in plots:
        graph_data = {'nodes': [], 'edges': []}
        if hasattr(plot, 'get_graph_data'):
            try:
                raw_graph = plot.get_graph_data()
                if 'nodes' in raw_graph:
                    for node in raw_graph['nodes']:
                        safe_node = {}
                        for key, value in node.items():
                            if hasattr(value, 'item'):
                                safe_node[key] = value.item()
                            elif isinstance(value, (np.ndarray, np.number)):
                                safe_node[key] = float(value)
                            else:
                                safe_node[key] = value
                        graph_data['nodes'].append(safe_node)
                
                if 'edges' in raw_graph:
                    for edge in raw_graph['edges']:
                        safe_edge = {}
                        for key, value in edge.items():
                            if hasattr(value, 'item'):
                                safe_edge[key] = value.item()
                            elif isinstance(value, (np.ndarray, np.number)):
                                safe_edge[key] = float(value)
                            else:
                                safe_edge[key] = value
                        graph_data['edges'].append(safe_edge)
            except Exception as e:
                print(f"Error processing graph data: {e}")
        
        file_data = {
            'filename': getattr(plot, 'filename', 'Untitled'),
            'method': getattr(plot, 'method_name', 'Unknown'),
            'graph': graph_data
        }
        graph_export_data.append(file_data)

    with open(graph_path, 'w', encoding='utf-8') as f:
        json.dump(graph_export_data, f, indent=2)

    print(f"Data saved to: {data_path}")
    print(f"Graph data saved to: {graph_path}")

    # # Start simple web server for audio compatibility
    print(f"🎵 Starting web server for audio compatibility...")
    serve_html_with_audio(html_path)

    return html_path, data_path, graph_path


