## ##          ##    ## ## ##     ####  ##      ##
##  ##       ##  ##     ##      ##      ##      ##
##   ##    ##      ##   ##    ##        ##      ##
##  ##     ## #### ##   ##    ##        ## #### ##
##    ##   ##      ##   ##    ##        ##      ##
##     ##  ##      ##   ##    ##        ##      ##
##    ##   ##      ##   ##      ##      ##      ##
##  ##     ##      ##   ##        ####  ##      ##



def batch_process_all_directories(base_slicedir, methods=None, auto_select_peaks=[1, 2, 3, 4, 5], 
                                       connect_all=True, export_data=True, save_plots=True):
    """
    Process all directories in base_slicedir automatically using the new auto-save functions.
    """
    
    if methods is None:
        methods = ["FFT_DUAL"]
    
    # Get all subdirectories
    all_directories = [d.name for d in Path(base_slicedir).iterdir() 
                  if d.is_dir()]
    all_directories = natsorted(all_directories)
    
    print(f"Found {len(all_directories)} directories to process:")
    for i, dirname in enumerate(all_directories[:5]):
        print(f"  {i}: {dirname}")
    if len(all_directories) > 5:
        print(f"  ... and {len(all_directories) - 5} more")
    
    # Create output directory for batch results
    daily_dir = jelfun.make_daily_directory()
    batch_output_dir = os.path.join(daily_dir, f"batch_analysis_{jelfun.get_timestamp()}")
    os.makedirs(batch_output_dir, exist_ok=True)
    
    batch_results = []
    
    for dir_idx, dirname in enumerate(all_directories):
        dir_path = Path(base_slicedir) / dirname
        
        try:
            print(f"\n=== batch_process_all_directories: Processing directory {dir_idx + 1}/{len(all_directories)}: {dirname} ===")
            
            # Select files
            selected_files = select_audio_files(
                dir_path,
                range_start=0,
                range_end=2,  # Adjust as needed
                verbose=False
            )
            
            if len(selected_files) == 0:
                print(f"  No audio files found in {dirname}, skipping...")
                batch_results.append({
                    'directory': dirname,
                    'status': 'error',
                    'error': 'No audio files found',
                    'files_processed': 0,
                    'plots_generated': 0,
                    'total_pairs': 0
                })
                continue
            
            print(f"  Processing {len(selected_files)} files...")
            
            # Use new auto-save function instead of the old method
            html_path, png_path, plots = auto_save_after_analysis(
                audio_directory=dir_path,
                methods=methods,
                selected_files=selected_files,
                save_png=save_plots,
                save_html=export_data,  # Generate HTML if we want data export
                auto_select_peaks=auto_select_peaks
            )
            
            if plots is None or len(plots) == 0:
                print(f"  Analysis failed for {dirname}, skipping...")
                batch_results.append({
                    'directory': dirname,
                    'status': 'error',
                    'error': 'Analysis failed',
                    'files_processed': len(selected_files),
                    'plots_generated': 0,
                    'total_pairs': 0
                })
                continue
            
            # Count pairs from the processed plots
            total_pairs = 0
            for plot in plots:
                if hasattr(plot, 'pairs'):
                    total_pairs += len(plot.pairs)
            
            # Export additional data if requested
            if export_data:
                print(f"  📊 Exporting additional data formats...")
                
                # CSV export - NEED TO FIX!!!!!
                csv_data = []
                
                # JSON export
                json_data = {
                    'directory': dirname,
                    'timestamp': jelfun.get_timestamp(),
                    'methods': methods,
                    'auto_selected_peaks': auto_select_peaks,
                    'plots': []
                }
                
                for plot_idx, plot in enumerate(plots):
                    plot_data = {
                        'plot_index': plot_idx,
                        'filename': getattr(plot, 'filename', f'Plot_{plot_idx}'),
                        'selected_peaks': getattr(plot, 'selected_peaks', []),
                        'pairs': getattr(plot, 'pairs', [])
                    }
                    json_data['plots'].append(plot_data)
                
                json_filename = f"{dirname}_analysis_data.json"
                json_path = os.path.join(batch_output_dir, json_filename)
                with open(json_path, 'w') as f:
                    json.dump(json_data, f, indent=2)
                print(f"    Saved JSON: {json_filename}")
            
            # Store results for summary
            batch_results.append({
                'directory': dirname,
                'status': 'success',
                'files_processed': len(selected_files),
                'plots_generated': len(plots),
                'total_pairs': total_pairs,
                'html_path': html_path,
                'png_path': png_path
            })
            
            print(f"  ✅ Success: {len(plots)} plots, {total_pairs} pairs total")

        except Exception as e:
            print(f"  ❌ ERROR processing {dirname}: {e}")
            batch_results.append({
                'directory': dirname,
                'status': 'error',
                'error': str(e),
                'files_processed': 0,
                'plots_generated': 0,
                'total_pairs': 0
            })
            continue

    # Save batch summary
    summary_data = {
        'batch_timestamp': jelfun.get_timestamp(),
        'total_directories': len(all_directories),
        'successful': len([r for r in batch_results if r['status'] == 'success']),
        'failed': len([r for r in batch_results if r['status'] == 'error']),
        'methods_used': methods,
        'auto_selected_peaks': auto_select_peaks,
        'total_files_processed': sum(r['files_processed'] for r in batch_results),
        'total_plots_generated': sum(r['plots_generated'] for r in batch_results),
        'total_pairs_created': sum(r['total_pairs'] for r in batch_results),
        'results': batch_results
    }
    
    summary_path = os.path.join(batch_output_dir, 'batch_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"\n=== BATCH PROCESSING COMPLETE ===")
    print(f"Output directory: {batch_output_dir}")
    print(f"Successful: {summary_data['successful']}")
    print(f"Failed: {summary_data['failed']}")
    print(f"Total files processed: {summary_data['total_files_processed']}")
    print(f"Total plots generated: {summary_data['total_plots_generated']}")
    print(f"Total pairs created: {summary_data['total_pairs_created']}")
    print(f"Summary saved to: {summary_path}")
    
    return batch_output_dir, batch_results

def run_batch_analysis():
    """Run batch analysis using the updated functions"""
    
    #existing directory setup
    main_slicedir = all_slicedirs[65]  # Or whichever base directory you want
    
    # Get parent directory containing all slice directories
    slice_parent = main_slicedir.parent  # This should contain all 70 subdirectories
    
    print(f"Running fixed batch analysis on: {slice_parent}")
    print(f"Looking for subdirectories in: {slice_parent}")
    
    # Run updated batch processing
    output_dir, results = batch_process_all_directories_fixed(
        base_slicedir=str(slice_parent),
        methods=["FFT_DUAL"],
        auto_select_peaks=[1, 2, 3, 4, 5],
        connect_all=True,
        export_data=True,
        save_plots=True
    )
    
    print(f"Fixed batch processing complete! Results in: {output_dir}")
    
    return output_dir, results

def batch_auto_select_and_connect_peaks(plots, auto_select_peaks=[1, 2, 3, 4, 5], connect_all=True):
    """
    Automatically select and connect peaks for batch processing.
    This modifies the plots in-place before HTML generation.
    """
    for plot in plots:
        if not hasattr(plot, 'peak_freqs') or len(plot.peak_freqs) == 0:
            continue
        
        # Get detected peaks and powers
        detectedPeaks = plot.peak_freqs
        detectedPowers = plot.peak_powers
        
        # Create array of peak-power pairs and sort by power descending
        peak_power_pairs = list(zip(detectedPeaks, detectedPowers))
        peak_power_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Initialize selection structures if they don't exist
        if not hasattr(plot, 'selected_peaks'):
            plot.selected_peaks = []
        if not hasattr(plot, 'pairs'):
            plot.pairs = []
        if not hasattr(plot, 'colors'):
            plot.colors = ['red', 'green', 'purple', 'orange', 'brown', 'cyan', 'magenta']
        
        # Select the specified peaks
        selected_freqs = []
        for peak_num in auto_select_peaks:
            if peak_num <= len(peak_power_pairs):
                freq_to_select = peak_power_pairs[peak_num - 1][0]  # -1 for 0-indexing
                plot.selected_peaks.append(freq_to_select)
                selected_freqs.append(freq_to_select)
        
        # Connect all selected peaks if requested
        if connect_all and len(selected_freqs) >= 2:
            plot.pairs = []  # Clear existing pairs
            selected_sorted = sorted(selected_freqs)
            
            # Create all possible pairs
            pair_index = 0
            for i in range(len(selected_sorted)):
                for j in range(i + 1, len(selected_sorted)):
                    f0 = selected_sorted[i]
                    f1 = selected_sorted[j]
                    ratio = f1 / f0
                    color = plot.colors[pair_index % len(plot.colors)]
                    
                    pair = {
                        'f0': f0,
                        'f1': f1, 
                        'ratio': ratio,
                        'color': color
                    }
                    plot.pairs.append(pair)
                    pair_index += 1
        
        print(f"    📍 {plot.filename}: Selected {len(selected_freqs)} peaks, created {len(plot.pairs)} pairs")

def generate_png_with_plotly_static(plots, dir_name, output_directory, auto_select_peaks=[1, 2, 3, 4, 5], connect_all=True):
    """
    Generate PNG that exactly replicates the HTML Plotly layout with spectrograms + PSD overlays.
    """
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        import plotly.io as pio
        
        print(f"  📊 Creating static Plotly figure matching HTML layout...")
        
        # Auto-select peaks in plots (modify plots in-place)
        # batch_auto_select_and_connect_peaks(plots, auto_select_peaks, connect_all)
        
        # Only auto-select peaks if they haven't been selected yet
        if not hasattr(plots[0], 'selected_peaks') or not plots[0].selected_peaks:
            batch_auto_select_and_connect_peaks(plots, auto_select_peaks, connect_all)

        # Calculate grid dimensions (same as HTML template)
        unique_files = set()
        unique_methods = set()
        for plot in plots:
            base_name = plot.filename.split(' (')[0] if ' (' in plot.filename else plot.filename
            unique_files.add(base_name)
            if hasattr(plot, 'method_name'):
                unique_methods.add(plot.method_name)
        
        n_files = len(unique_files)
        n_methods = len(unique_methods) if unique_methods else 1
        n_rows = n_files
        n_cols = n_methods
        
        print(f"  📐 Grid: {n_rows} rows × {n_cols} cols = {len(plots)} plots")
        
        # Calculate vertical spacing (same as template)
        if n_rows > 1:
            v_spacing = min(0.15, 0.2 / (n_rows - 1))
        else:
            v_spacing = 0.15
        
        # Create subplot figure (exact same parameters as template)
        fig = make_subplots(
            rows=n_rows, 
            cols=n_cols,
            subplot_titles=[getattr(plot, 'filename', f'Plot {i+1}') for i, plot in enumerate(plots)],
            vertical_spacing=v_spacing,
            horizontal_spacing=0.08
        )
        
        # Process each plot (replicating template logic)
        for i, plot in enumerate(plots):
            row = i // n_cols + 1
            col = i % n_cols + 1
            
            print(f"  🎨 Processing plot {i+1}: {getattr(plot, 'filename', 'Unknown')}")
            
            # Get current scale data (matching template logic)
            use_db_scale = False  # template uses linear scale by default
            frequencies = plot.frequencies
            
            if use_db_scale:
                current_psd = plot.psd_db if hasattr(plot, 'psd_db') else plot.psd_linear
                y_label = "PSD (dB)"
            else:
                current_psd = plot.psd_linear if hasattr(plot, 'psd_linear') else plot.psd_db
                y_label = "PSD (linear)"
            
            # 1. ADD SPECTROGRAM AS BACKGROUND (if available)
            if (hasattr(plot, 'has_spectrogram') and plot.has_spectrogram and 
                hasattr(plot, 'spectrogram_linear') and plot.spectrogram_linear is not None):
                
                print(f"    🌈 Adding spectrogram background for plot {i}")
                
                # Scale time to PSD range (exact same logic as template)
                psd_min = np.min(current_psd)
                psd_max = np.max(current_psd)
                time_min = np.min(plot.times)
                time_max = np.max(plot.times)
                
                # Scale times to use 50% of PSD range at the top (  exact logic)
                psd_range = psd_max - psd_min
                scaled_times = []
                for t in plot.times:
                    normalized_time = (t - time_min) / (time_max - time_min)  # 0 to 1
                    scaled_time = psd_max - (psd_range * 0.5) + (normalized_time * psd_range * 0.5)
                    scaled_times.append(scaled_time)
                
                # Use dB version of spectrogram (  template uses spectrogram_db)
                spec_array = plot.spectrogram_db
                spec_array_transposed = spec_array.T
                
                # Add spectrogram heatmap (exact same as template)
                fig.add_trace(
                    go.Heatmap(
                        x=frequencies,
                        y=scaled_times,
                        z=spec_array_transposed.tolist(),
                        colorscale='magma',
                        opacity=1.0,
                        showscale=False,
                        name=f"spectrogram_{i}",
                        hovertemplate='Freq: %{x:.1f} Hz<br>Time: %{y:.3f} s<br>Power: %{z:.2f}<extra></extra>',
                        zmin=np.min(spec_array),
                        zmax=np.max(spec_array),
                    ),
                    row=row, col=col
                )
            
            # 2. ADD MAIN PSD LINE (exact same as template)
            fig.add_trace(
                go.Scatter(
                    x=frequencies,
                    y=current_psd,
                    mode='lines',
                    name=f"psd_{i}",
                    line=dict(color='black', width=2),
                    showlegend=False
                ),
                row=row, col=col
            )
            
            # 3. ADD DETECTED PEAK MARKERS (gray dots, exact same as template)
            if hasattr(plot, 'peak_freqs') and hasattr(plot, 'peak_powers'):
                # Calculate peak powers for current scale
                peak_powers_current = []
                for peak_freq in plot.peak_freqs:
                    freq_idx = np.argmin(np.abs(plot.frequencies - peak_freq))
                    if use_db_scale:
                        peak_powers_current.append(plot.psd_db[freq_idx])
                    else:
                        peak_powers_current.append(plot.psd_linear[freq_idx])
                
                fig.add_trace(
                    go.Scatter(
                        x=plot.peak_freqs,
                        y=peak_powers_current,
                        mode='markers',
                        name=f"peaks_{i}",
                        marker=dict(color='gray', size=5, opacity=0.7),
                        showlegend=False
                    ),
                    row=row, col=col
                )
            
            # 4. ADD SELECTED PEAKS (blue markers with labels)
            if hasattr(plot, 'selected_peaks') and plot.selected_peaks:
                print(f"    🎯 Adding {len(plot.selected_peaks)} selected peaks")
                
                selected_powers = []
                for freq in plot.selected_peaks:
                    freq_idx = np.argmin(np.abs(plot.frequencies - freq))
                    if use_db_scale:
                        selected_powers.append(plot.psd_db[freq_idx])
                    else:
                        selected_powers.append(plot.psd_linear[freq_idx])
                
                fig.add_trace(
                    go.Scatter(
                        x=plot.selected_peaks,
                        y=selected_powers,
                        mode='markers+text',
                        marker=dict(color='blue', size=10, line=dict(color='black', width=1)),
                        text=[f"{f:.0f}" for f in plot.selected_peaks],
                        textposition='top center',
                        textfont=dict(color='blue', size=10),
                        name=f"selected_{i}",
                        showlegend=False
                    ),
                    row=row, col=col
                )
            
            # 5. ADD CONNECTING LINES FOR PAIRS
            if hasattr(plot, 'pairs') and plot.pairs:
                print(f"    🔗 Adding {len(plot.pairs)} connecting lines")
                
                for pair_idx, pair in enumerate(plot.pairs):
                    # Get powers for paired frequencies
                    f0_idx = np.argmin(np.abs(plot.frequencies - pair['f0']))
                    f1_idx = np.argmin(np.abs(plot.frequencies - pair['f1']))
                    
                    if use_db_scale:
                        f0_power = plot.psd_db[f0_idx]
                        f1_power = plot.psd_db[f1_idx]
                    else:
                        f0_power = plot.psd_linear[f0_idx]
                        f1_power = plot.psd_linear[f1_idx]
                    
                    # Connecting line
                    fig.add_trace(
                        go.Scatter(
                            x=[pair['f0'], pair['f1']],
                            y=[f0_power, f1_power],
                            mode='lines+markers',
                            line=dict(color=pair['color'], width=2),
                            marker=dict(color='blue', size=10, line=dict(color='black', width=1)),
                            name=f"pair_{i}_{pair_idx}",
                            showlegend=False
                        ),
                        row=row, col=col
                    )
            
            # 6. ADD SPECTRAL RIDGES (if available, cyan lines)
            if (hasattr(plot, 'has_spectrogram') and plot.has_spectrogram and 
                hasattr(plot, 'spectrogram_linear') and plot.spectrogram_linear is not None):
                
                try:
                    # Calculate ridge data (same as Python code)
                    ridge_times, ridge_freqs = find_max_energy_ridge(
                        plot.spectrogram_linear, plot.frequencies, plot.times
                    )
                    
                    # Scale ridge times same as spectrogram
                    psd_min = np.min(current_psd)
                    psd_max = np.max(current_psd)
                    time_min = np.min(plot.times)
                    time_max = np.max(plot.times)
                    psd_range = psd_max - psd_min
                    
                    scaled_ridge_times = []
                    for t in ridge_times:
                        normalized_time = (t - time_min) / (time_max - time_min)
                        scaled_time = psd_max - (psd_range * 0.5) + (normalized_time * psd_range * 0.5)
                        scaled_ridge_times.append(scaled_time)
                    
                    fig.add_trace(
                        go.Scatter(
                            x=ridge_freqs,
                            y=scaled_ridge_times,
                            mode='lines',
                            line=dict(color='cyan', width=3, dash='solid'),
                            name=f"ridge_{i}",
                            showlegend=False
                        ),
                        row=row, col=col
                    )
                    print(f"    🌊 Added spectral ridge")
                except Exception as e:
                    print(f"    ⚠️ Ridge calculation failed: {e}")
            
            # Set axis properties (same range as plots)
            if hasattr(plot, 'plot_fmin') and hasattr(plot, 'plot_fmax'):
                fig.update_xaxes(range=[plot.plot_fmin, plot.plot_fmax], row=row, col=col)
            fig.update_xaxes(title_text="Frequency (Hz)", row=row, col=col)
            fig.update_yaxes(title_text=y_label, row=row, col=col)


            # 7. ADD SPECTRAL VEINS (if available)
            if (hasattr(plot, 'has_spectrogram') and plot.has_spectrogram and 
                hasattr(plot, 'spectrogram_linear') and plot.spectrogram_linear is not None):
                
                try:
                    # Calculate spectral veins
                    veins = find_spectral_veins(
                        plot.spectrogram_linear, plot.frequencies, plot.times, 
                        num_veins=getattr(plot, 'num_veins', 6)
                    )
                    
                    vein_colors = ['coral', 'yellow', 'magenta', 'lime', 'orange', 'teal']
                    
                    for vein_idx, vein in enumerate(veins[:len(vein_colors)]):
                        if len(vein['freqs']) > 0:
                            # Scale vein times same as ridge times
                            psd_min = np.min(current_psd)
                            psd_max = np.max(current_psd)
                            time_min = np.min(plot.times)
                            time_max = np.max(plot.times)
                            psd_range = psd_max - psd_min
                            
                            scaled_vein_times = []
                            for t in vein['times']:
                                normalized_time = (t - time_min) / (time_max - time_min)
                                scaled_time = psd_max - (psd_range * 0.5) + (normalized_time * psd_range * 0.5)
                                scaled_vein_times.append(scaled_time)
                            
                            fig.add_trace(
                                go.Scatter(
                                    x=vein['freqs'],
                                    y=scaled_vein_times,
                                    mode='lines',
                                    line=dict(color=vein_colors[vein_idx], width=2, dash='dash'),
                                    name=f"vein_{i}_{vein_idx}",
                                    showlegend=False
                                ),
                                row=row, col=col
                            )
                    
                    print(f"    🔗 Added {len(veins)} spectral veins")
                except Exception as e:
                    print(f"    ⚠️ Vein calculation failed: {e}")



        # Update layout (matching template dimensions)
        fig.update_layout(
            title=f"Interactive Spectral Analysis - Dir: {dir_name} - generate_png_with_plotly_static",
            height=max(600, 500 * n_rows),
            width=max(800, 300 * n_cols),
            template="plotly_white",
            margin=dict(l=50, r=50, t=100, b=50),
            font=dict(size=10)
        )
        
        # Save as PNG
        png_filename = f"{dir_name}_staticplot.png"
        png_path = os.path.join(output_directory, png_filename)
        os.makedirs(output_directory, exist_ok=True)

        
        print(f"  💾 Saving complete analysis PNG: {png_filename}")
        pio.write_image(fig, png_path, format='png', width=fig.layout.width, height=fig.layout.height, scale=2)
        print(f"  ✅ Complete analysis PNG saved successfully")
        print(f"  ✅ {png_path}")
        
        return png_path
        
    except ImportError:
        print(f"  ❌ kaleido not installed. Run: pip install kaleido")
        return None
    except Exception as e:
        print(f"  ❌ Static PNG generation error: {e}")
        import traceback
        traceback.print_exc()
        return None
