"""
Tests for RSS downloader functionality
"""
import pytest
from trendspyg import download_google_trends_rss
from trendspyg.exceptions import InvalidParameterError


@pytest.mark.network
class TestRSSBasicFunctionality:
    """Test basic RSS download functionality"""

    def test_rss_returns_data(self):
        """Test that RSS download returns trend data"""
        trends = download_google_trends_rss(geo='US')

        assert isinstance(trends, list)
        assert len(trends) > 0
        assert 'trend' in trends[0]
        assert 'traffic' in trends[0]
        assert 'published' in trends[0]

    def test_rss_with_articles(self):
        """Test RSS download includes news articles"""
        trends = download_google_trends_rss(geo='US', include_articles=True)

        assert 'news_articles' in trends[0]
        assert isinstance(trends[0]['news_articles'], list)

    def test_rss_with_images(self):
        """Test RSS download includes images"""
        trends = download_google_trends_rss(geo='US', include_images=True)

        assert 'image' in trends[0]
        assert 'url' in trends[0]['image']
        assert 'source' in trends[0]['image']

    def test_rss_without_articles(self):
        """Test RSS download without articles"""
        trends = download_google_trends_rss(geo='US', include_articles=False)

        assert 'news_articles' not in trends[0]

    def test_rss_without_images(self):
        """Test RSS download without images"""
        trends = download_google_trends_rss(geo='US', include_images=False)

        assert 'image' not in trends[0]


@pytest.mark.network
class TestRSSOutputFormats:
    """Test different output formats"""

    def test_dict_format(self):
        """Test dict output format (default)"""
        trends = download_google_trends_rss(geo='US', output_format='dict')

        assert isinstance(trends, list)
        assert isinstance(trends[0], dict)

    def test_json_format(self):
        """Test JSON output format"""
        result = download_google_trends_rss(geo='US', output_format='json')

        assert isinstance(result, str)
        assert result.startswith('[')

        # Should be valid JSON
        import json
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_csv_format(self):
        """Test CSV output format"""
        result = download_google_trends_rss(geo='US', output_format='csv')

        assert isinstance(result, str)
        assert 'trend,traffic,published' in result
        lines = result.strip().split('\n')
        assert len(lines) > 1  # Header + at least one data row

    def test_dataframe_format(self):
        """Test DataFrame output format"""
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not installed")

        df = download_google_trends_rss(geo='US', output_format='dataframe')

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'trend' in df.columns
        assert 'traffic' in df.columns


@pytest.mark.network
class TestRSSValidation:
    """Test input validation"""

    def test_invalid_geo_code(self):
        """Test that invalid geo code raises error"""
        with pytest.raises(InvalidParameterError) as exc_info:
            download_google_trends_rss(geo='INVALID')

        assert 'Invalid geo code' in str(exc_info.value)

    def test_invalid_output_format(self):
        """Test that invalid output format raises error"""
        with pytest.raises(InvalidParameterError) as exc_info:
            download_google_trends_rss(geo='US', output_format='xml')

        assert 'Invalid output_format' in str(exc_info.value)

    def test_valid_country_codes(self):
        """Test that valid country codes work"""
        # Test a few country codes
        for geo in ['US', 'GB', 'CA', 'AU']:
            trends = download_google_trends_rss(geo=geo)
            assert len(trends) > 0

    def test_us_state_codes(self):
        """Test that US state codes work"""
        trends = download_google_trends_rss(geo='US-CA')
        assert len(trends) > 0


@pytest.mark.network
class TestRSSDataStructure:
    """Test the structure of returned data"""

    def test_trend_has_required_fields(self):
        """Test that each trend has required fields"""
        trends = download_google_trends_rss(geo='US')

        required_fields = ['trend', 'traffic', 'published', 'explore_link']
        for field in required_fields:
            assert field in trends[0]

    def test_news_article_structure(self):
        """Test news article data structure"""
        trends = download_google_trends_rss(geo='US', include_articles=True)

        if trends[0]['news_articles']:
            article = trends[0]['news_articles'][0]
            assert 'headline' in article
            assert 'url' in article
            assert 'source' in article

    def test_max_articles_limit(self):
        """Test max_articles_per_trend parameter"""
        trends = download_google_trends_rss(
            geo='US',
            include_articles=True,
            max_articles_per_trend=2
        )

        if trends[0]['news_articles']:
            assert len(trends[0]['news_articles']) <= 2


@pytest.mark.network
class TestRSSErrorHandling:
    """Test error handling"""

    def test_case_insensitive_geo(self):
        """Test that geo codes are case-insensitive"""
        trends_upper = download_google_trends_rss(geo='US')
        trends_lower = download_google_trends_rss(geo='us')

        # Both should work (we can't compare exact trends as they change)
        assert len(trends_upper) > 0
        assert len(trends_lower) > 0

    def test_empty_max_articles(self):
        """Test with max_articles_per_trend=0"""
        trends = download_google_trends_rss(
            geo='US',
            include_articles=True,
            max_articles_per_trend=0
        )

        assert len(trends[0]['news_articles']) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
