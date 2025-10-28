# Main Analysis
This section includes the six required analysis tools with embedded visuals.

## 1. Variable Analysis
### 1.1 Univariate
![hist_id_assessment.png](C:\Users\Comma\Desktop\eda_for_all_data\reports\figures\univariate\hist_id_assessment.png)
![hist_id_student.png](C:\Users\Comma\Desktop\eda_for_all_data\reports\figures\univariate\hist_id_student.png)
![hist_date_submitted.png](C:\Users\Comma\Desktop\eda_for_all_data\reports\figures\univariate\hist_date_submitted.png)
![hist_is_banked.png](C:\Users\Comma\Desktop\eda_for_all_data\reports\figures\univariate\hist_is_banked.png)

### 1.2 Summary Statistics
See `outputs/summary_stats.csv` for descriptive metrics.

### 1.3 Bivariate
![Correlation Heatmap](C:\Users\Comma\Desktop\eda_for_all_data\reports\figures\bivariate\corr_heatmap.png)
![Scatter Plot](C:\Users\Comma\Desktop\eda_for_all_data\reports\figures\bivariate\scatter_id_assessment_vs_id_student.png)
![Scatter Plot](C:\Users\Comma\Desktop\eda_for_all_data\reports\figures\bivariate\scatter_id_assessment_vs_date_submitted.png)
![Scatter Plot](C:\Users\Comma\Desktop\eda_for_all_data\reports\figures\bivariate\scatter_id_assessment_vs_is_banked.png)
![2D Density Plot](C:\Users\Comma\Desktop\eda_for_all_data\reports\figures\bivariate\kde2d_id_assessment_vs_id_student.png)

### 1.4 Multivariate
![pca2](C:\Users\Comma\Desktop\eda_for_all_data\reports\figures\multivariate\pca2.png)
![pca13](C:\Users\Comma\Desktop\eda_for_all_data\reports\figures\multivariate\pca13.png)

## 2. Pattern Analysis
### 2.1 Time Series Analysis
Detected time column: **date_submitted**

### 2.2 Pattern Recognition
Outlier counts saved to `outputs/outliers_count.json`.

### 2.3 Segmentation Analysis
Segmentation used quartiles of `id_student`.