import asyncio
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import os
from dotenv import load_dotenv

# Add the parent directory to the Python path so we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import your models and database connection
from database import DATABASE_URL
from models import KiteSchool
from sqlalchemy import select, create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

# Load environment variables
load_dotenv()

async def fetch_data_from_db():
    """Fetch kiteschool data from the database"""
    # Create async engine
    engine = create_async_engine(DATABASE_URL)
    
    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Query all kiteschools
        result = await session.execute(select(KiteSchool))
        schools = result.scalars().all()
        
        # Convert to list of dictionaries
        data = []
        for school in schools:
            data.append({
                "id": school.id,
                "company_name": school.company_name,
                "location": school.location,
                "country": school.country,
                "google_review_score": school.google_review_score,
                "owner_name": school.owner_name,
                "website_url": school.website_url,
                "course_pricing": school.course_pricing,
                "created_at": school.created_at
            })
    
    # Close engine
    await engine.dispose()
    
    return data

def analyze_kiteschools(df):
    """Analyze kiteschool data from DataFrame"""
    print(f"Total kiteschools: {len(df)}")
    
    # Country distribution
    country_counts = df['country'].value_counts()
    print("\nTop 10 countries by number of kiteschools:")
    print(country_counts.head(10))
    
    # Google review score analysis
    # Convert to numeric, ignoring errors (non-numeric values become NaN)
    df['google_review_score'] = pd.to_numeric(df['google_review_score'], errors='coerce')
    
    print("\nGoogle Review Score statistics:")
    print(df['google_review_score'].describe())
    
    # Pricing analysis (this is more complex as pricing is in text format)
    print("\nSample of course pricing:")
    print(df['course_pricing'].sample(5))
    
    # Create output directory for charts
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create some visualizations
    plt.figure(figsize=(12, 6))
    
    # Plot top 10 countries
    country_counts.head(10).plot(kind='bar')
    plt.title('Top 10 Countries by Number of Kiteschools')
    plt.xlabel('Country')
    plt.ylabel('Number of Kiteschools')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'kiteschools_by_country.png'))
    print(f"\nSaved chart to {output_dir}/kiteschools_by_country.png")
    
    # Plot review score distribution
    plt.figure(figsize=(10, 6))
    df['google_review_score'].hist(bins=20)
    plt.title('Distribution of Google Review Scores')
    plt.xlabel('Review Score')
    plt.ylabel('Number of Kiteschools')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'kiteschools_review_scores.png'))
    print(f"Saved chart to {output_dir}/kiteschools_review_scores.png")
    
    # Additional analysis: Website availability
    # Add a new column for website availability
    df['has_website'] = df['website_url'].notna() & (df['website_url'] != '')
    website_percent = df['has_website'].mean() * 100
    print(f"\nPercentage of kiteschools with website: {website_percent:.1f}%")
    
    # Plot website availability by country
    plt.figure(figsize=(12, 6))
    # Group by country and calculate the percentage with websites
    website_by_country = df.groupby('country')['has_website'].mean() * 100
    website_by_country.sort_values(ascending=False).head(10).plot(kind='bar')
    plt.title('Top 10 Countries by Website Availability (%)')
    plt.xlabel('Country')
    plt.ylabel('Percentage with Website')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'kiteschools_website_by_country.png'))
    print(f"Saved chart to {output_dir}/kiteschools_website_by_country.png")
    
    # Location analysis
    print("\nTop 10 locations by number of kiteschools:")
    location_counts = df['location'].value_counts()
    print(location_counts.head(10))
    
    # Additional analysis: Course pricing patterns
    print("\nAnalyzing course pricing patterns...")
    # Count occurrences of common pricing patterns
    pricing_patterns = {
        'hourly_rate': df['course_pricing'].str.contains('hour', case=False, na=False).sum(),
        'lesson_based': df['course_pricing'].str.contains('lesson', case=False, na=False).sum(),
        'course_based': df['course_pricing'].str.contains('course', case=False, na=False).sum(),
        'package': df['course_pricing'].str.contains('package', case=False, na=False).sum(),
        'not_available': df['course_pricing'].str.contains('not available', case=False, na=False).sum()
    }
    print("Pricing patterns found:")
    for pattern, count in pricing_patterns.items():
        print(f"- {pattern.replace('_', ' ').title()}: {count} schools ({count/len(df)*100:.1f}%)")
    
    # Plot pricing patterns
    plt.figure(figsize=(10, 6))
    pd.Series(pricing_patterns).plot(kind='bar')
    plt.title('Kiteschool Pricing Patterns')
    plt.xlabel('Pricing Pattern')
    plt.ylabel('Number of Schools')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'kiteschools_pricing_patterns.png'))
    print(f"Saved chart to {output_dir}/kiteschools_pricing_patterns.png")
    
    return df

async def main():
    # Fetch data from database
    print("Fetching data from database...")
    data = await fetch_data_from_db()
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    if len(df) == 0:
        print("No data found in the database. Have you imported the kiteschools data?")
        return
    
    # Analyze data
    print("\nAnalyzing kiteschool data...")
    analyze_kiteschools(df)
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    asyncio.run(main())