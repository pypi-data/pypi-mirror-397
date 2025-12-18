# trill_metrics.py

# Analyzes sequential audio data. 
# Extracts syllable count, bout duration, and repetition rate using annotation files. 
# Performs statistical tests (ANOVA/Kruskal-Wallis), and generates summary tables. 
# Multivariate methods (PCA, clustering, distance-based ordering) show pair-level patterns. 
# Outputs statistical summaries and visualizations in multiple formats. 

import os
import pandas as pd
import librosa
from pathlib import Path
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import kruskal, f_oneway
import scikit_posthocs as sp

def get_bout_info_from_annotations(xlsx_path):
    """Get syllable count and bout duration from annotation file"""
    try:
        df = pd.read_excel(xlsx_path)
        
        # Search for start/stop time columns (common names)
        start_cols = [col for col in df.columns if 'start' in col.lower() or 'begin' in col.lower()]
        stop_cols = [col for col in df.columns if 'stop' in col.lower() or 'end' in col.lower()]
        
        if start_cols and stop_cols:
            clean_df = df.dropna(subset=[start_cols[0], stop_cols[0]])
            if len(clean_df) > 0:
                syllable_count = len(clean_df)
                first_start = float(clean_df[start_cols[0]].min())
                last_stop = float(clean_df[stop_cols[0]].max())
                bout_duration = last_stop - first_start
                return syllable_count, bout_duration
    except Exception as e:
        print(f"Error processing {xlsx_path}: {e}")
    
    return 0, 0

def analyze_syllable_distribution(base_dir):
    """Analyze syllable distribution across bouts and pairs"""
    ano_dir = Path(base_dir) / 'ano'
    syllable_data = defaultdict(list)
    
    # Process each annotation file
    for xlsx_file in ano_dir.glob('*.xlsx'):
        file_id = xlsx_file.stem
        pair_id = int(file_id[:2])  # First two digits
        
        syllable_count, bout_duration = get_bout_info_from_annotations(xlsx_file)
        
        if bout_duration > 0:
            syllable_data[pair_id].append({
                'bout_id': file_id,
                'pair_id': pair_id,
                'syllables': syllable_count,
                'duration': bout_duration,
                'syllables_per_sec': syllable_count / bout_duration
            })
    
    # Flatten data for analysis
    all_data = []
    for pair_id, bout_data in syllable_data.items():
        all_data.extend(bout_data)
    
    return pd.DataFrame(all_data), syllable_data

def test_pair_associations(df):
    """Test statistical associations between pair ID and acoustic metrics"""
    print("\nStatistical Tests for Pair Effects")
    print("=" * 50)
    
    # Group data by pair
    pairs = [group['syllables'].values for name, group in df.groupby('pair_id')]
    durations = [group['duration'].values for name, group in df.groupby('pair_id')]
    rates = [group['syllables_per_sec'].values for name, group in df.groupby('pair_id')]
    
    # Test for normality (Shapiro-Wilk test on residuals)
    print("Normality tests (Shapiro-Wilk on residuals):")
    for metric, data in [('syllables', df['syllables']), 
                        ('duration', df['duration']), 
                        ('rate', df['syllables_per_sec'])]:
        # Calculate residuals from overall mean
        residuals = data - data.mean()
        stat, p = stats.shapiro(residuals)
        print(f"  {metric}: W = {stat:.4f}, p = {p:.4f}")
    
    # Test homogeneity of variance (Levene's test)
    print("\nHomogeneity of variance tests (Levene's):")
    syll_levene = stats.levene(*pairs)
    dur_levene = stats.levene(*durations)
    rate_levene = stats.levene(*rates)
    
    print(f"  Syllables: W = {syll_levene.statistic:.4f}, p = {syll_levene.pvalue:.4f}")
    print(f"  Duration: W = {dur_levene.statistic:.4f}, p = {dur_levene.pvalue:.4f}")
    print(f"  Rate: W = {rate_levene.statistic:.4f}, p = {rate_levene.pvalue:.4f}")
    
    # Choose appropriate tests based on assumptions
    print("\nPrimary statistical tests:")
    
    # Test 1: Syllables per bout
    if syll_levene.pvalue > 0.05:  # Equal variances
        f_stat, f_p = f_oneway(*pairs)
        test_used = "One-way ANOVA"
    else:
        f_stat, f_p = kruskal(*pairs)
        test_used = "Kruskal-Wallis"
    
    print(f"A. Syllables per bout ({test_used}):")
    print(f"   Statistic = {f_stat:.4f}, p = {f_p:.4f}")
    
    # Test 2: Bout duration
    if dur_levene.pvalue > 0.05:  # Equal variances
        f_stat2, f_p2 = f_oneway(*durations)
        test_used2 = "One-way ANOVA"
    else:
        f_stat2, f_p2 = kruskal(*durations)
        test_used2 = "Kruskal-Wallis"
    
    print(f"B. Bout duration ({test_used2}):")
    print(f"   Statistic = {f_stat2:.4f}, p = {f_p2:.4f}")
    
    # Test 3: Syllable rate
    if rate_levene.pvalue > 0.05:  # Equal variances
        f_stat3, f_p3 = f_oneway(*rates)
        test_used3 = "One-way ANOVA"
    else:
        f_stat3, f_p3 = kruskal(*rates)
        test_used3 = "Kruskal-Wallis"
    
    print(f"C. Syllable rate ({test_used3}):")
    print(f"   Statistic = {f_stat3:.4f}, p = {f_p3:.4f}")
    
    # Post-hoc tests if significant
    alpha = 0.05
    print(f"\nPost-hoc comparisons (α = {alpha}):")
    
    if f_p < alpha:
        print("Syllables per bout - Significant pair effect detected")
        if test_used == "One-way ANOVA":
            posthoc = sp.posthoc_tukey(df, val_col='syllables', group_col='pair_id')
        else:
            posthoc = sp.posthoc_dunn(df, val_col='syllables', group_col='pair_id')
        print(f"Post-hoc test results:\n{posthoc.round(4)}")
    else:
        print("Syllables per bout - No significant pair effect")
    
    if f_p2 < alpha:
        print("Bout duration - Significant pair effect detected")
        if test_used2 == "One-way ANOVA":
            posthoc2 = sp.posthoc_tukey(df, val_col='duration', group_col='pair_id')
        else:
            posthoc2 = sp.posthoc_dunn(df, val_col='duration', group_col='pair_id')
        print(f"Post-hoc test results:\n{posthoc2.round(4)}")
    else:
        print("Bout duration - No significant pair effect")
    
    if f_p3 < alpha:
        print("Syllable rate - Significant pair effect detected")
        if test_used3 == "One-way ANOVA":
            posthoc3 = sp.posthoc_tukey(df, val_col='syllables_per_sec', group_col='pair_id')
        else:
            posthoc3 = sp.posthoc_dunn(df, val_col='syllables_per_sec', group_col='pair_id')
        print(f"Post-hoc test results:\n{posthoc3.round(4)}")
    else:
        print("Syllable rate - No significant pair effect")
    
    # Effect sizes (eta-squared for ANOVA, epsilon-squared for Kruskal-Wallis)
    print(f"\nEffect sizes:")
    
    # For syllables
    if test_used == "One-way ANOVA":
        ss_between = sum([len(group) * (group.mean() - df['syllables'].mean())**2 
                         for group in pairs])
        ss_total = sum([(x - df['syllables'].mean())**2 for x in df['syllables']])
        eta_sq = ss_between / ss_total
        print(f"  Syllables per bout: η² = {eta_sq:.4f}")
    
    # Summary interpretation
    print(f"\nInterpretation:")
    significant_effects = []
    if f_p < alpha: significant_effects.append("syllable count")
    if f_p2 < alpha: significant_effects.append("bout duration") 
    if f_p3 < alpha: significant_effects.append("syllable rate")
    
    if significant_effects:
        print(f"  Breeding pairs differ significantly in: {', '.join(significant_effects)}")
    else:
        print("  No significant differences between breeding pairs detected")

def create_summary_table(df):
    """Create publication-ready summary table"""
    summary_stats = df.groupby('pair_id').agg({
        'syllables': ['count', 'mean', 'std'],
        'duration': ['mean', 'std'],
        'syllables_per_sec': ['mean', 'std']
    }).round(2)
    
    # Flatten column names
    summary_stats.columns = ['n_bouts', 'syllables_mean', 'syllables_std', 
                           'duration_mean', 'duration_std', 'rate_mean', 'rate_std']
    
    # Add overall row
    overall = pd.DataFrame({
        'n_bouts': [len(df)],
        'syllables_mean': [df['syllables'].mean()],
        'syllables_std': [df['syllables'].std()],
        'duration_mean': [df['duration'].mean()],
        'duration_std': [df['duration'].std()],
        'rate_mean': [df['syllables_per_sec'].mean()],
        'rate_std': [df['syllables_per_sec'].std()]
    }, index=['Overall']).round(2)
    
    summary_table = pd.concat([summary_stats, overall])
    
    # Format for publication
    summary_table['Syllables per bout'] = summary_table['syllables_mean'].astype(str) + ' ± ' + summary_table['syllables_std'].astype(str)
    summary_table['Bout duration (ms)'] = summary_table['duration_mean'].astype(str) + ' ± ' + summary_table['duration_std'].astype(str)
    summary_table['Syllable rate (Hz)'] = summary_table['rate_mean'].astype(str) + ' ± ' + summary_table['rate_std'].astype(str)
    
    final_table = summary_table[['n_bouts', 'Syllables per bout', 'Bout duration (ms)', 'Syllable rate (Hz)']]
    final_table.columns = ['N bouts', 'Syllables per bout', 'Bout duration (ms)', 'Syllable rate (Hz)']
    
    return final_table



# Run analysis
print("Trill Bout Analysis: Lonchura oryzivora Vocal Metrics")
print("=" * 60)

df, syllable_data = analyze_syllable_distribution(r'D:\anvo\buncho\zhang\all_mod')

# Convert duration from seconds to milliseconds
df['duration'] = df['duration'] * 1000

# Create summary table
summary_table = create_summary_table(df)
print("\nTable 1. Trill bout characteristics in Java Sparrow breeding pairs")
print("-" * 80)
print(summary_table.to_string())

# Run statistical tests
test_pair_associations(df)

# Save table as CSV for easy import
summary_table.to_csv('java_sparrow_trill_metrics.csv')
print(f"\nTable saved as: java_sparrow_trill_metrics.csv")



# Additional descriptive statistics
print("\n\nStudy Summary:")
print("=" * 50)
print(f"Species: Lonchura oryzivora (Java Sparrow)")
print(f"Total trill bouts analyzed: {len(df)}")
print(f"Number of breeding pairs: {df['pair_id'].nunique()}")
print(f"Bouts per pair: {len(df)/df['pair_id'].nunique():.1f} ± {df.groupby('pair_id').size().std():.1f}")
print(f"Overall syllable rate: {df['syllables_per_sec'].mean():.1f} ± {df['syllables_per_sec'].std():.1f} Hz")


def find_optimal_pair_ordering(df):
    """Find statistically significant ways to order pairs using multiple criteria"""
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
    from scipy.spatial.distance import pdist
    
    print("\nOptimal Pair Ordering Analysis")
    print("=" * 40)
    
    # Calculate pair-level means for all metrics
    pair_data = df.groupby('pair_id').agg({
        'syllables': 'mean',
        'duration': 'mean', 
        'syllables_per_sec': 'mean'
    })
    
    print("Pair-level data:")
    print(pair_data.round(3))
    
    # Method 1: Principal Component Analysis
    print(f"\n1. Principal Component Analysis:")
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(pair_data)
    
    pca = PCA()
    pca_scores = pca.fit_transform(scaled_data)
    
    print(f"   PC1 explains {pca.explained_variance_ratio_[0]:.3f} of variance")
    print(f"   PC1 loadings: syllables={pca.components_[0,0]:.3f}, duration={pca.components_[0,1]:.3f}, rate={pca.components_[0,2]:.3f}")
    
    # Order pairs by PC1
    pc1_order = pair_data.index[np.argsort(pca_scores[:, 0])]
    print(f"   PC1 ordering: {list(pc1_order)}")
    
    # Method 2: Hierarchical clustering
    print(f"\n2. Hierarchical Clustering:")
    linkage_matrix = linkage(scaled_data, method='ward')
    clusters = fcluster(linkage_matrix, t=3, criterion='maxclust')  # 3 clusters
    
    cluster_df = pd.DataFrame({'pair_id': pair_data.index, 'cluster': clusters})
    cluster_df = cluster_df.sort_values('cluster')
    print("   Cluster assignments:")
    for cluster in sorted(clusters):
        pairs_in_cluster = cluster_df[cluster_df['cluster'] == cluster]['pair_id'].tolist()
        print(f"   Cluster {cluster}: {pairs_in_cluster}")
    
    # Method 3: Distance-based ordering (traveling salesman-like)
    print(f"\n3. Distance-based Sequential Ordering:")
    distances = pdist(scaled_data, metric='euclidean')
    
    # Greedy nearest-neighbor ordering
    n_pairs = len(pair_data)
    visited = [False] * n_pairs
    order = [0]  # Start with first pair
    visited[0] = True
    
    for _ in range(n_pairs - 1):
        current = order[-1]
        min_dist = float('inf')
        next_pair = -1
        
        for j in range(n_pairs):
            if not visited[j]:
                if current < j:
                    dist_idx = n_pairs * current + j - ((current + 2) * (current + 1)) // 2
                else:
                    dist_idx = n_pairs * j + current - ((j + 2) * (j + 1)) // 2
                
                if distances[dist_idx] < min_dist:
                    min_dist = distances[dist_idx]
                    next_pair = j
        
        order.append(next_pair)
        visited[next_pair] = True
    
    distance_order = [pair_data.index[i] for i in order]
    print(f"   Distance-based ordering: {distance_order}")
    
    return {
        'pc1_order': pc1_order,
        'cluster_order': cluster_df['pair_id'].tolist(),
        'distance_order': distance_order,
        'pca_scores': pca_scores,
        'clusters': clusters,
        'pca': pca
    }

def plot_optimal_orderings(df, ordering_results, plot_style='boxplot'):
    """Plot pairs using different optimal orderings
    
    Parameters:
    plot_style: str, one of 'boxplot', 'heatmap', 'line', 'radar', 'parallel'
    """
    # Helper functions
    def plot_heatmap_ordering(df, pair_order, metrics, ax):
        pair_means = df.groupby('pair_id')[metrics].mean()
        ordered_means = pair_means.reindex(pair_order)
        sns.heatmap(ordered_means.T, annot=True, cmap='viridis', ax=ax, cbar=False)
        ax.set_xticklabels([f'P{pid}' for pid in pair_order])

    def plot_line_ordering(df, pair_order, metric, ax):
        pair_means = df.groupby('pair_id')[metric].mean()
        ordered_values = [pair_means[pid] for pid in pair_order]
        ax.plot(range(len(ordered_values)), ordered_values, 'o-', linewidth=2, markersize=8)
        ax.set_xticks(range(len(pair_order)))
        ax.set_xticklabels([f'P{pid}' for pid in pair_order])

    def plot_radar_ordering(df, pair_order, metrics, ax, pair_colors):
        from math import pi
        angles = [n / len(metrics) * 2 * pi for n in range(len(metrics))]
        angles += angles[:1]
        
        for pair_id in pair_order:
            values = [df[df['pair_id']==pair_id][m].mean() for m in metrics]
            values += values[:1]
            color = pair_colors[pair_id]
            ax.plot(angles, values, 'o-', linewidth=1, label=f'P{pair_id}', color=color)
            ax.fill(angles, values, alpha=0.1, color=color)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(['Syllable Count', 'Bout Duration', 'Repetition Rate'])
        ax.set_ylabel('Z-score')
        ax.legend(bbox_to_anchor=(1.1, 1.1))

    def plot_parallel_ordering(df, pair_order, metrics, ax):
        from pandas.plotting import parallel_coordinates
        pair_data = df.groupby('pair_id')[metrics].mean().reset_index()
        pair_data = pair_data.set_index('pair_id').reindex(pair_order).reset_index()
        parallel_coordinates(pair_data, 'pair_id', ax=ax, colormap='viridis')
        ax.legend(bbox_to_anchor=(1.05, 1))

    # Main plotting logic
    if plot_style == 'radar':
        fig, axes = plt.subplots(1, 4, figsize=(24, 6))
        axes = axes.reshape(1, -1)  # Make it 2D for consistent indexing
    elif plot_style == 'parallel':
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        axes = axes.reshape(1, -1)
    else:
        fig, axes = plt.subplots(3, 4, figsize=(24, 15))
    
    method_descriptions = {
        'boxplot': 'Box-and-Whisker Visualization',
        'line': 'Line Plot Visualization', 
        'heatmap': 'Heatmap Visualization',
        'radar': 'Radar Plot Visualization',
        'parallel': 'Parallel Coordinates Visualization'
    }

    fig.suptitle(f'Multivariate Acoustic Phenotype Orderings: Lonchura oryzivora Pairs\n{method_descriptions[plot_style]}', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    orderings = {
        'PC1 Ordering': ordering_results['pc1_order'],
        'Cluster Ordering': ordering_results['cluster_order'], 
        'Distance Ordering': ordering_results['distance_order']
    }
    
    metrics = ['syllables', 'duration', 'syllables_per_sec']
    metric_names = ['Syllables per Bout', 'Bout Duration (ms)', 'Syllable Rate (Hz)']
    
    # Create consistent color mapping for all pairs
    all_pairs = sorted(df['pair_id'].unique())
    n_pairs = len(all_pairs)

    # Generate distinct colors using multiple colormaps if needed
    if n_pairs <= 20:
        colors = plt.cm.tab20(np.linspace(0, 1, n_pairs))
    else:
        # Combine multiple colormaps for more unique colors
        colors1 = plt.cm.tab20(np.linspace(0, 1, 20))
        colors2 = plt.cm.Set3(np.linspace(0, 1, min(12, n_pairs-20)))
        if n_pairs > 32:
            colors3 = plt.cm.Pastel1(np.linspace(0, 1, min(9, n_pairs-32)))
            colors = np.vstack([colors1, colors2, colors3])[:n_pairs]
        else:
            colors = np.vstack([colors1, colors2])[:n_pairs]
    pair_colors = dict(zip(all_pairs, colors))

    if plot_style in ['radar', 'parallel']:
        # Special layouts for radar and parallel plots
        for col, (order_name, pair_order) in enumerate(orderings.items()):
            if plot_style == 'radar':
                plot_radar_ordering(df, pair_order, metrics, axes[0, col], pair_colors)
                axes[0, col].set_title(f'{order_name}')
            elif plot_style == 'parallel':
                plot_parallel_ordering(df, pair_order, metrics, axes[0, col])
                axes[0, col].set_title(f'{order_name}')

        # Add syllables vs duration plot for radar
        if plot_style == 'radar':
            ax_scatter = axes[0, 3]
            for pair_id in df['pair_id'].unique():
                pair_data = df[df['pair_id'] == pair_id]
                ax_scatter.scatter(pair_data['duration'], pair_data['syllables'], 
                                color=pair_colors[pair_id], label=f'P{pair_id}', alpha=0.7)
            ax_scatter.set_xlabel('Bout Duration (ms) (Z-score)')
            ax_scatter.set_ylabel('Syllable Count per Bout (Z-score)')
            ax_scatter.set_title('Syllables vs Duration')
            ax_scatter.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)


    else:
        # Standard 3x3 layout for other plot types
        for row, (order_name, pair_order) in enumerate(orderings.items()):
            for col, (metric, metric_name) in enumerate(zip(metrics, metric_names)):
                df_ordered = df.copy()
                df_ordered['order_rank'] = df_ordered['pair_id'].map(
                    {pair_id: rank for rank, pair_id in enumerate(pair_order)}
                )
                df_ordered = df_ordered.sort_values('order_rank')
                
                # Choose plot type
                if plot_style == 'boxplot':
                    sns.boxplot(data=df_ordered, x='order_rank', y=metric, ax=axes[row, col])
                    # Add trend line
                    pair_means = df.groupby('pair_id')[metric].mean()
                    ordered_means = [pair_means[pair_id] for pair_id in pair_order]
                    axes[row, col].plot(range(len(ordered_means)), ordered_means, 
                                       'r-', linewidth=2, alpha=0.7)
                elif plot_style == 'heatmap':
                    plot_heatmap_ordering(df, pair_order, [metric], axes[row, col])
                elif plot_style == 'line':
                    plot_line_ordering(df, pair_order, metric, axes[row, col])
                
                # Customize labels
                if plot_style != 'heatmap':
                    pair_labels = [f"P{pid}" for pid in pair_order]
                    axes[row, col].set_xticklabels(pair_labels, rotation=45)
                    axes[row, col].set_xlabel('Pair Ordering')
                
                axes[row, col].set_ylabel(f'{metric_name} (Z-score)')
                axes[row, col].set_title(f'{order_name}: {metric_name}')
    

            # Add 4th column: Syllable Count vs Bout Duration scatter plot
            ax_scatter = axes[row, 3]
            for pair_id in pair_order:
                pair_data = df[df['pair_id'] == pair_id]
                ax_scatter.scatter(pair_data['duration'], pair_data['syllables'], 
                                #label=f'P{pair_id}', alpha=0.7)
                                color=pair_colors[pair_id], label=f'P{pair_id}', alpha=0.7)
            
            ax_scatter.set_xlabel('Bout Duration (ms) (Z-score)')
            ax_scatter.set_ylabel('Syllable Count per Bout (Z-score)')
            ax_scatter.set_title(f'{order_name}: Syllables vs Duration')
            ax_scatter.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)


    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    return fig

# Usage examples:
ordering_results = find_optimal_pair_ordering(df)

# Boxplot (default)
fig1 = plot_optimal_orderings(df, ordering_results, plot_style='boxplot')

# Line plots
fig2 = plot_optimal_orderings(df, ordering_results, plot_style='line')

# Heatmap
fig3 = plot_optimal_orderings(df, ordering_results, plot_style='heatmap')

# Radar plots
fig4 = plot_optimal_orderings(df, ordering_results, plot_style='radar')

# Parallel coordinates
fig5 = plot_optimal_orderings(df, ordering_results, plot_style='parallel')