#!/usr/bin/env python3
"""
Gemini AI Analysis Engine for Business Intelligence
==================================================

This module integrates Google's Gemini AI to provide intelligent insights
and recommendations for business reports including:

1. Profitability Analysis Insights
2. Performance Trend Analysis  
3. Strategic Recommendations
4. Risk Assessment
5. Market Opportunity Identification

Author: AI Assistant
Date: October 4, 2025
Version: 1.0.0
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AIInsight:
    """Structure for AI-generated insights"""
    category: str  # 'performance', 'risk', 'opportunity', 'recommendation'
    title: str
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    impact: str  # 'financial', 'operational', 'strategic'
    confidence_score: float  # 0.0 to 1.0
    action_required: bool
    timeline: str  # 'immediate', 'short_term', 'long_term'

@dataclass  
class BusinessInsightsReport:
    """Comprehensive AI insights report"""
    analysis_type: str
    generation_timestamp: datetime
    overall_assessment: str
    key_findings: List[str]
    performance_insights: List[AIInsight]
    risk_insights: List[AIInsight]
    opportunity_insights: List[AIInsight]
    strategic_recommendations: List[AIInsight]
    executive_summary: str
    detailed_analysis: str
    confidence_score: float

class GeminiBusinessIntelligence:
    """
    Gemini AI-powered Business Intelligence Engine
    Provides intelligent analysis and insights for business reports
    """
    
    def __init__(self):
        """Initialize Gemini AI with API key"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        logger.info("✅ Gemini AI Business Intelligence Engine initialized")
    
    def analyze_profitability_report(self, profitability_data: Dict[str, Any]) -> BusinessInsightsReport:
        """
        Analyze profitability report data and generate AI insights
        
        Args:
            profitability_data: Dictionary containing profitability analysis results
            
        Returns:
            BusinessInsightsReport with AI-generated insights
        """
        logger.info("🧠 Generating AI insights for profitability analysis...")
        
        try:
            # Prepare data for AI analysis
            analysis_prompt = self._create_profitability_analysis_prompt(profitability_data)
            
            # Generate insights with Gemini
            response = self.model.generate_content(analysis_prompt)
            ai_response = response.text
            
            # Parse AI response into structured insights
            insights_report = self._parse_ai_response_to_insights(ai_response, "Profitability Analysis")
            
            logger.info("✅ AI insights generated successfully")
            return insights_report
            
        except Exception as e:
            logger.error(f"❌ Error generating AI insights: {e}")
            # Return fallback insights
            return self._create_fallback_insights("Profitability Analysis")
    
    def _create_profitability_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Create detailed prompt for profitability analysis"""
        
        # Extract key metrics
        portfolio_value = data.get('summary', {}).get('portfolio_value', 0)
        portfolio_margin = data.get('summary', {}).get('portfolio_margin', 0)
        margin_percentage = data.get('summary', {}).get('portfolio_margin_percentage', 0)
        negative_count = data.get('summary', {}).get('negative_margin_count', 0)
        total_skus = data.get('summary', {}).get('total_skus', 0)
        
        # Top performers
        top_products = data.get('top_5_products', [])
        best_vendors = data.get('best_vendors', [])
        profitable_categories = data.get('profitable_categories', [])
        negative_products = data.get('negative_margin_products', [])
        
        prompt = f"""
As a senior business analyst with 15+ years of experience in retail and inventory management, 
analyze the following profitability report for ABC Book House and provide comprehensive business insights.

COMPANY CONTEXT:
- ABC Book House is a book retail business
- Focus on inventory optimization and profitability enhancement
- Current analysis covers their entire product portfolio

PROFITABILITY ANALYSIS DATA:

PORTFOLIO OVERVIEW:
- Total SKUs Analyzed: {total_skus}
- Portfolio Stock Value: ₹{portfolio_value:,.2f}
- Total Gross Margin: ₹{portfolio_margin:,.2f}
- Overall Margin Percentage: {margin_percentage:.2f}%
- Products with Negative Margins: {negative_count} ({(negative_count/total_skus*100) if total_skus > 0 else 0:.1f}%)

TOP 5 PERFORMING PRODUCTS:
{self._format_products_for_prompt(top_products)}

BEST PERFORMING VENDORS:
{self._format_vendors_for_prompt(best_vendors)}

MOST PROFITABLE CATEGORIES:
{self._format_categories_for_prompt(profitable_categories)}

NEGATIVE MARGIN PRODUCTS (LOSSES):
{self._format_negative_products_for_prompt(negative_products)}

ANALYSIS REQUIREMENTS:
Please provide a comprehensive business intelligence report with the following sections:

1. OVERALL_ASSESSMENT: 2-3 sentence summary of business health
2. KEY_FINDINGS: 5-7 bullet points of most important discoveries
3. PERFORMANCE_INSIGHTS: What's driving profits/losses and why
4. RISK_INSIGHTS: Current and potential risks to profitability
5. OPPORTUNITY_INSIGHTS: Untapped potential and growth areas
6. STRATEGIC_RECOMMENDATIONS: Specific actionable steps with priorities
7. EXECUTIVE_SUMMARY: 2-paragraph summary for senior management
8. DETAILED_ANALYSIS: In-depth analysis with supporting data

For each insight, consider:
- Why this pattern exists (root cause analysis)
- Business impact (financial, operational, strategic)
- Urgency level (immediate, short-term, long-term)
- Confidence level in the assessment
- Specific actions to take

Focus on:
- Margin optimization opportunities
- Vendor relationship management
- Category portfolio balance
- Inventory efficiency
- Pricing strategy recommendations
- Risk mitigation for negative margin products

Provide insights that are:
- Actionable and specific
- Financially quantified where possible
- Prioritized by impact and urgency
- Supportive of strategic decision making

Format your response as structured sections clearly labeled with the section names above.
"""
        
        return prompt
    
    def _format_products_for_prompt(self, products: List[Dict]) -> str:
        """Format product data for AI prompt"""
        if not products:
            return "No data available"
        
        formatted = []
        for i, product in enumerate(products[:5], 1):
            name = product.get('product_name', 'Unknown')[:50]
            margin = product.get('margin_percentage', 0)
            contribution = product.get('contribution', 0)
            formatted.append(f"  {i}. {name} - Margin: {margin:.2f}% - Contribution: ₹{contribution:,.2f}")
        
        return "\n".join(formatted)
    
    def _format_vendors_for_prompt(self, vendors: List[Dict]) -> str:
        """Format vendor data for AI prompt"""
        if not vendors:
            return "No data available"
        
        formatted = []
        for i, vendor in enumerate(vendors[:3], 1):
            name = vendor.get('vendor_name', 'Unknown')
            margin = vendor.get('average_margin', 0)
            total = vendor.get('total_margin', 0)
            formatted.append(f"  {i}. {name} - Avg Margin: {margin:.2f}% - Total: ₹{total:,.2f}")
        
        return "\n".join(formatted)
    
    def _format_categories_for_prompt(self, categories: List[Dict]) -> str:
        """Format category data for AI prompt"""
        if not categories:
            return "No data available"
        
        formatted = []
        for i, category in enumerate(categories[:3], 1):
            name = category.get('category_name', 'Unknown')
            score = category.get('profitability_score', 0)
            margin = category.get('average_margin', 0)
            share = category.get('market_share', 0)
            formatted.append(f"  {i}. {name} - Score: {score:.2f} - Margin: {margin:.2f}% - Share: {share:.1f}%")
        
        return "\n".join(formatted)
    
    def _format_negative_products_for_prompt(self, products: List[Dict]) -> str:
        """Format negative margin products for AI prompt"""
        if not products:
            return "No products with negative margins - Excellent!"
        
        formatted = []
        for i, product in enumerate(products[:5], 1):
            name = product.get('product_name', 'Unknown')[:50]
            vendor = product.get('vendor', 'Unknown')
            margin = product.get('margin_percentage', 0)
            loss = product.get('loss_amount', 0)
            formatted.append(f"  {i}. {name} ({vendor}) - Loss: {margin:.2f}% - Amount: ₹{abs(loss):,.2f}")
        
        if len(products) > 5:
            formatted.append(f"  ... and {len(products) - 5} more products with negative margins")
        
        return "\n".join(formatted)
    
    def _parse_ai_response_to_insights(self, ai_response: str, analysis_type: str) -> BusinessInsightsReport:
        """Parse AI response into structured insights"""
        
        # Initialize collections
        performance_insights = []
        risk_insights = []
        opportunity_insights = []
        strategic_recommendations = []
        
        # Extract sections from AI response
        sections = self._extract_sections_from_response(ai_response)
        
        # Parse different types of insights
        if 'PERFORMANCE_INSIGHTS' in sections:
            performance_insights = self._parse_insights_section(
                sections['PERFORMANCE_INSIGHTS'], 'performance'
            )
        
        if 'RISK_INSIGHTS' in sections:
            risk_insights = self._parse_insights_section(
                sections['RISK_INSIGHTS'], 'risk'
            )
        
        if 'OPPORTUNITY_INSIGHTS' in sections:
            opportunity_insights = self._parse_insights_section(
                sections['OPPORTUNITY_INSIGHTS'], 'opportunity'
            )
        
        if 'STRATEGIC_RECOMMENDATIONS' in sections:
            strategic_recommendations = self._parse_insights_section(
                sections['STRATEGIC_RECOMMENDATIONS'], 'recommendation'
            )
        
        # Create comprehensive report
        report = BusinessInsightsReport(
            analysis_type=analysis_type,
            generation_timestamp=datetime.now(),
            overall_assessment=sections.get('OVERALL_ASSESSMENT', 'Assessment not available'),
            key_findings=self._parse_bullet_points(sections.get('KEY_FINDINGS', '')),
            performance_insights=performance_insights,
            risk_insights=risk_insights,
            opportunity_insights=opportunity_insights,
            strategic_recommendations=strategic_recommendations,
            executive_summary=sections.get('EXECUTIVE_SUMMARY', 'Summary not available'),
            detailed_analysis=sections.get('DETAILED_ANALYSIS', 'Detailed analysis not available'),
            confidence_score=0.85  # Default confidence score
        )
        
        return report
    
    def _extract_sections_from_response(self, response: str) -> Dict[str, str]:
        """Extract structured sections from AI response"""
        sections = {}
        current_section = None
        current_content = []
        
        lines = response.split('\n')
        
        section_markers = [
            'OVERALL_ASSESSMENT', 'KEY_FINDINGS', 'PERFORMANCE_INSIGHTS',
            'RISK_INSIGHTS', 'OPPORTUNITY_INSIGHTS', 'STRATEGIC_RECOMMENDATIONS',
            'EXECUTIVE_SUMMARY', 'DETAILED_ANALYSIS'
        ]
        
        for line in lines:
            line = line.strip()
            
            # Check if this line is a section header
            found_section = None
            for marker in section_markers:
                if marker in line.upper():
                    found_section = marker
                    break
            
            if found_section:
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = found_section
                current_content = []
            else:
                # Add content to current section
                if current_section and line:
                    current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _parse_insights_section(self, section_text: str, category: str) -> List[AIInsight]:
        """Parse a section into individual insights"""
        insights = []
        
        # Split by bullet points or numbered items
        items = []
        for line in section_text.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or 
                        line.startswith('*') or any(line.startswith(f"{i}.") for i in range(1, 20))):
                items.append(line)
        
        for i, item in enumerate(items[:5]):  # Limit to 5 insights per category
            # Clean the item text
            clean_text = item.lstrip('-•*0123456789. ').strip()
            
            if len(clean_text) > 20:  # Only include substantial insights
                # Extract title (first sentence or first 60 chars)
                sentences = clean_text.split('.')
                title = sentences[0][:60] + ('...' if len(sentences[0]) > 60 else '')
                
                # Determine severity and timeline based on category and keywords
                severity = self._determine_severity(clean_text, category)
                timeline = self._determine_timeline(clean_text)
                
                insight = AIInsight(
                    category=category,
                    title=title,
                    description=clean_text,
                    severity=severity,
                    impact='financial' if 'margin' in clean_text.lower() or 'profit' in clean_text.lower() else 'operational',
                    confidence_score=0.8,  # Default confidence
                    action_required=category == 'recommendation' or severity in ['high', 'critical'],
                    timeline=timeline
                )
                
                insights.append(insight)
        
        return insights
    
    def _determine_severity(self, text: str, category: str) -> str:
        """Determine severity based on text content"""
        text_lower = text.lower()
        
        # Critical indicators
        if any(word in text_lower for word in ['urgent', 'critical', 'immediate', 'severe', 'major loss']):
            return 'critical'
        
        # High severity indicators
        if any(word in text_lower for word in ['significant', 'substantial', 'high risk', 'important']):
            return 'high'
        
        # Medium severity
        if any(word in text_lower for word in ['moderate', 'consider', 'review', 'improve']):
            return 'medium'
        
        # Default based on category
        if category == 'risk':
            return 'medium'
        elif category == 'recommendation':
            return 'high'
        else:
            return 'medium'
    
    def _determine_timeline(self, text: str) -> str:  
        """Determine timeline based on text content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['immediate', 'urgent', 'now', 'asap']):
            return 'immediate'
        elif any(word in text_lower for word in ['short', 'month', '30 days', 'quarter']):
            return 'short_term'
        else:
            return 'long_term'
    
    def _parse_bullet_points(self, text: str) -> List[str]:
        """Parse bullet points from text"""
        if not text:
            return []
        
        points = []
        for line in text.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                clean_point = line.lstrip('-•* ').strip()
                if clean_point:
                    points.append(clean_point)
        
        return points[:7]  # Limit to 7 key findings
    
    def _create_fallback_insights(self, analysis_type: str) -> BusinessInsightsReport:
        """Create fallback insights when AI fails"""
        logger.warning("Creating fallback insights due to AI processing error")
        
        return BusinessInsightsReport(
            analysis_type=analysis_type,
            generation_timestamp=datetime.now(),
            overall_assessment="AI analysis temporarily unavailable. Please review the detailed report data.",
            key_findings=[
                "Detailed analysis data is available in the report",
                "Manual review recommended for strategic insights",
                "Contact support if AI insights are consistently unavailable"
            ],
            performance_insights=[],
            risk_insights=[],
            opportunity_insights=[],
            strategic_recommendations=[],
            executive_summary="AI-powered insights are temporarily unavailable. The numerical analysis and report data remain accurate and available for manual review.",
            detailed_analysis="Please refer to the detailed data tables and charts in the main report for comprehensive analysis.",
            confidence_score=0.0
        )
    
    def export_insights_to_dict(self, insights: BusinessInsightsReport) -> Dict[str, Any]:
        """Export insights to dictionary format for API responses"""
        return {
            "analysis_type": insights.analysis_type,
            "timestamp": insights.generation_timestamp.isoformat(),
            "overall_assessment": insights.overall_assessment,
            "key_findings": insights.key_findings,
            "executive_summary": insights.executive_summary,
            "detailed_analysis": insights.detailed_analysis,
            "confidence_score": insights.confidence_score,
            "insights": {
                "performance": [asdict(insight) for insight in insights.performance_insights],
                "risks": [asdict(insight) for insight in insights.risk_insights],
                "opportunities": [asdict(insight) for insight in insights.opportunity_insights],
                "recommendations": [asdict(insight) for insight in insights.strategic_recommendations]
            },
            "summary": {
                "total_insights": (len(insights.performance_insights) + 
                                 len(insights.risk_insights) + 
                                 len(insights.opportunity_insights) + 
                                 len(insights.strategic_recommendations)),
                "high_priority_actions": len([i for i in insights.strategic_recommendations if i.action_required]),
                "critical_issues": len([i for i in insights.risk_insights if i.severity == 'critical'])
            }
        }

# Example usage
if __name__ == "__main__":
    print("🧠 Gemini AI Business Intelligence Engine")
    print("=" * 60)
    
    try:
        # Initialize AI engine
        ai_engine = GeminiBusinessIntelligence()
        
        # Sample profitability data for testing
        sample_data = {
            "summary": {
                "portfolio_value": 1350000,
                "portfolio_margin": 350000,
                "portfolio_margin_percentage": 25.9,
                "negative_margin_count": 3,
                "total_skus": 36
            },
            "top_5_products": [
                {"product_name": "Advanced Python Programming", "margin_percentage": 45.2, "contribution": 35000},
                {"product_name": "Data Science Fundamentals", "margin_percentage": 42.8, "contribution": 28000}
            ],
            "best_vendors": [
                {"vendor_name": "Tech Publications", "average_margin": 38.5, "total_margin": 125000}
            ],
            "profitable_categories": [
                {"category_name": "Programming", "profitability_score": 85.2, "average_margin": 35.4, "market_share": 28.5}
            ],
            "negative_margin_products": [
                {"product_name": "Outdated Tech Manual", "vendor": "Old Publishers", "margin_percentage": -5.2, "loss_amount": -2500}
            ]
        }
        
        # Generate insights
        insights = ai_engine.analyze_profitability_report(sample_data)
        
        # Display results
        print(f"\n📊 AI INSIGHTS GENERATED")
        print(f"Analysis Type: {insights.analysis_type}")
        print(f"Confidence Score: {insights.confidence_score:.2f}")
        print(f"Total Insights: {len(insights.performance_insights + insights.risk_insights + insights.opportunity_insights + insights.strategic_recommendations)}")
        
        print(f"\n🎯 Overall Assessment:")
        print(f"   {insights.overall_assessment}")
        
        print(f"\n🔍 Key Findings:")
        for finding in insights.key_findings:
            print(f"   • {finding}")
        
        print(f"\n📈 Performance Insights: {len(insights.performance_insights)}")
        print(f"⚠️ Risk Insights: {len(insights.risk_insights)}")
        print(f"🚀 Opportunities: {len(insights.opportunity_insights)}")
        print(f"💡 Recommendations: {len(insights.strategic_recommendations)}")
        
        print("\n✅ AI Insights Generation Complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()