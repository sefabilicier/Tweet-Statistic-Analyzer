import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
import json

class TweetStatisticsCalculator:
    """Calculate comprehensive summary statistics for tweet data"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare data for analysis"""
        if 'date' in self.df.columns and not pd.api.types.is_datetime64_any_dtype(self.df['date']):
            self.df['date'] = pd.to_datetime(self.df['date'])
        
        if 'word_count' not in self.df.columns and 'content' in self.df.columns:
            self.df['word_count'] = self.df['content'].apply(
                lambda x: len(str(x).split()) if pd.notna(x) else 0
            )
        
        if 'date' in self.df.columns:
            self.df['year'] = self.df['date'].dt.year
            self.df['month'] = self.df['date'].dt.month
            self.df['quarter'] = self.df['date'].dt.quarter
            self.df['weekday'] = self.df['date'].dt.dayofweek
            self.df['hour'] = self.df['date'].dt.hour
        
        if 'word_count' in self.df.columns:
            self.df_clean = self.df[self.df['word_count'] <= 100].copy()
        else:
            self.df_clean = self.df.copy()
    
    def calculate_basic_stats(self, data: pd.Series) -> Dict:
        """Calculate basic summary statistics for a numeric series"""
        stats_dict = {
            'count': int(len(data)),
            'mean': round(float(data.mean()), 2),
            'median': float(data.median()),
            'mode': data.mode()[0] if not data.mode().empty else None,
            'std': round(float(data.std()), 2),
            'var': round(float(data.var()), 2),
            'min': float(data.min()),
            'max': float(data.max()),
            'range': float(data.max() - data.min()),
            'q1': float(data.quantile(0.25)),
            'q3': float(data.quantile(0.75)),
            'iqr': float(data.quantile(0.75) - data.quantile(0.25)),
            'skewness': round(float(data.skew()), 3),
            'kurtosis': round(float(data.kurtosis()), 3),
            'cv': round(float(data.std() / data.mean() * 100), 2) if data.mean() != 0 else 0
        }
        return stats_dict
    
    def yearly_summary_stats(self) -> pd.DataFrame:
        """Calculate summary statistics grouped by year"""
        if 'year' not in self.df_clean.columns or 'word_count' not in self.df_clean.columns:
            return pd.DataFrame()
        
        yearly_stats = []
        
        for year in sorted(self.df_clean['year'].unique()):
            year_data = self.df_clean[self.df_clean['year'] == year]['word_count']
            
            if len(year_data) > 0:
                stats_dict = self.calculate_basic_stats(year_data)
                stats_dict['year'] = year
                stats_dict['tweet_count'] = len(year_data)
                yearly_stats.append(stats_dict)
        
        return pd.DataFrame(yearly_stats)
    
    def monthly_summary_stats(self) -> pd.DataFrame:
        """Calculate monthly summary statistics"""
        if 'year' not in self.df_clean.columns or 'month' not in self.df_clean.columns:
            return pd.DataFrame()
        
        self.df_clean['year_month'] = self.df_clean['date'].dt.to_period('M')
        monthly_stats = []
        
        for period, group in self.df_clean.groupby('year_month'):
            if len(group) >= 5:
                word_counts = group['word_count']
                stats_dict = self.calculate_basic_stats(word_counts)
                stats_dict['year_month'] = str(period)
                stats_dict['tweet_count'] = len(group)
                monthly_stats.append(stats_dict)
        
        return pd.DataFrame(monthly_stats)
    
    def user_comparison_stats(self) -> pd.DataFrame:
        """Compare statistics across different users"""
        if 'username' not in self.df_clean.columns:
            return pd.DataFrame()
        
        user_stats = []
        
        for username, group in self.df_clean.groupby('username'):
            word_counts = group['word_count']
            
            stats_dict = {
                'username': username,
                'displayname': group['displayname'].iloc[0] if 'displayname' in group.columns else username,
                'tweet_count': len(group),
                'mean_words': round(word_counts.mean(), 2),
                'median_words': word_counts.median(),
                'std_words': round(word_counts.std(), 2),
                'min_words': word_counts.min(),
                'max_words': word_counts.max(),
                'total_engagement': group['like_count'].sum() + group['retweet_count'].sum() if 'like_count' in group.columns else 0
            }
            
            if 'industry' in group.columns:
                stats_dict['industry'] = group['industry'].iloc[0]
            
            user_stats.append(stats_dict)
        
        return pd.DataFrame(user_stats)
    
    def detect_trends(self) -> Dict:
        """Detect significant trends in tweet length over time"""
        yearly_df = self.yearly_summary_stats()
        
        if len(yearly_df) < 2:
            return {"message": "Insufficient years for trend detection"}
        
        trends = {
            'mean_trend': None,
            'volatility_trend': None,
            'significant_change': False,
            'description': []
        }
        
        yearly_df = yearly_df.sort_values('year')
        yearly_df['mean_change'] = yearly_df['mean'].diff()
        yearly_df['std_change'] = yearly_df['std'].diff()
        
        first_year = yearly_df.iloc[0]
        last_year = yearly_df.iloc[-1]
        
        mean_change_pct = ((last_year['mean'] - first_year['mean']) / first_year['mean']) * 100
        trends['mean_trend'] = round(mean_change_pct, 1)
        
        std_change_pct = ((last_year['std'] - first_year['std']) / first_year['std']) * 100
        trends['volatility_trend'] = round(std_change_pct, 1)
        
        first_data = self.df_clean[self.df_clean['year'] == first_year['year']]['word_count']
        last_data = self.df_clean[self.df_clean['year'] == last_year['year']]['word_count']
        
        if len(first_data) > 10 and len(last_data) > 10:
            t_stat, p_value = stats.ttest_ind(first_data, last_data)
            trends['significant_change'] = p_value < 0.05
            trends['p_value'] = round(p_value, 4)
        
        if abs(mean_change_pct) > 10:
            direction = "increased" if mean_change_pct > 0 else "decreased"
            trends['description'].append(
                f"Average tweet length has {direction} by {abs(mean_change_pct):.1f}%"
            )
        
        if abs(std_change_pct) > 20:
            direction = "more variable" if std_change_pct > 0 else "more consistent"
            trends['description'].append(
                f"Tweeting has become {direction} (volatility {direction})"
            )
        
        return trends
    
    def get_distribution_stats(self) -> Dict:
        """Get distribution characteristics"""
        if 'word_count' not in self.df_clean.columns:
            return {}
        
        all_words = self.df_clean['word_count']
        
        skewness = all_words.skew()
        kurtosis = all_words.kurtosis()
        
        distribution_type = "Normal" if abs(skewness) < 0.5 and abs(kurtosis) < 1 else "Skewed"
        
        percentiles = {
            'p1': float(all_words.quantile(0.01)),
            'p5': float(all_words.quantile(0.05)),
            'p10': float(all_words.quantile(0.10)),
            'p25': float(all_words.quantile(0.25)),
            'p50': float(all_words.quantile(0.50)),
            'p75': float(all_words.quantile(0.75)),
            'p90': float(all_words.quantile(0.90)),
            'p95': float(all_words.quantile(0.95)),
            'p99': float(all_words.quantile(0.99))
        }
        
        return {
            'distribution_type': distribution_type,
            'skewness': round(skewness, 3),
            'kurtosis': round(kurtosis, 3),
            'percentiles': percentiles
        }
    
    def get_engagement_correlation(self) -> Dict:
        """Calculate correlation between word count and engagement"""
        if all(col in self.df_clean.columns for col in ['word_count', 'like_count', 'retweet_count']):
            correlations = {}
            
            for metric in ['like_count', 'retweet_count', 'reply_count']:
                if metric in self.df_clean.columns:
                    corr = self.df_clean['word_count'].corr(self.df_clean[metric])
                    correlations[metric] = round(corr, 3)
            
            return correlations
        
        return {}
    
    def generate_full_report(self) -> Dict:
        """Generate a complete statistical report"""
        report = {
            'dataset_info': {
                'total_tweets': len(self.df),
                'clean_tweets': len(self.df_clean),
                'date_range': {
                    'start': str(self.df['date'].min()) if 'date' in self.df.columns else None,
                    'end': str(self.df['date'].max()) if 'date' in self.df.columns else None
                },
                'unique_users': self.df['username'].nunique() if 'username' in self.df.columns else 1
            },
            'overall_stats': self.calculate_basic_stats(self.df_clean['word_count']) if 'word_count' in self.df_clean.columns else {},
            'yearly_stats': self.yearly_summary_stats().to_dict('records') if not self.yearly_summary_stats().empty else [],
            'trends': self.detect_trends(),
            'distribution': self.get_distribution_stats(),
            'engagement': self.get_engagement_correlation(),
            'user_comparison': self.user_comparison_stats().to_dict('records') if not self.user_comparison_stats().empty else []
        }
        
        return report

if __name__ == "__main__":
    from collect_tweets import TwitterDataCollector
    
    collector = TwitterDataCollector()
    sample_df = collector.load_sample_data()
    
    calculator = TweetStatisticsCalculator(sample_df)
    
    print("=" * 60)
    print("SUMMARY STATISTICS REPORT")
    print("=" * 60)
    
    report = calculator.generate_full_report()
    
    print(f"\n📊 Dataset Overview:")
    print(f"  - Total Tweets: {report['dataset_info']['total_tweets']:,}")
    print(f"  - Clean Tweets: {report['dataset_info']['clean_tweets']:,}")
    print(f"  - Date Range: {report['dataset_info']['date_range']['start']} to {report['dataset_info']['date_range']['end']}")
    print(f"  - Unique Users: {report['dataset_info']['unique_users']}")
    
    print(f"\n📈 Overall Tweet Statistics:")
    stats = report['overall_stats']
    print(f"  - Mean: {stats.get('mean', 'N/A')} words")
    print(f"  - Median: {stats.get('median', 'N/A')} words")
    print(f"  - Std Dev: {stats.get('std', 'N/A')} words")
    print(f"  - Range: {stats.get('min', 'N/A')} - {stats.get('max', 'N/A')} words")
    print(f"  - Skewness: {stats.get('skewness', 'N/A')}")
    
    print(f"\n📉 Trends:")
    trends = report['trends']
    if 'description' in trends:
        for desc in trends['description']:
            print(f"  - {desc}")
    if 'p_value' in trends:
        print(f"  - Statistical significance: p={trends['p_value']} (p<0.05: {trends['significant_change']})")
    
    print("\n" + "=" * 60)