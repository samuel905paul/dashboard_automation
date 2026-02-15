"""
Executive Dashboard Automation Suite - Main Pipeline
Author: T Samuel Paul
Description: Orchestrates end-to-end dashboard automation workflow
"""

import argparse
import sys
import logging
from datetime import datetime
from typing import List, Dict
import pandas as pd

from src.extractors.sql_extractor import SQLExtractor
from src.transformers.data_cleaner import DataCleaner
from src.transformers.aggregator import MetricsAggregator
from src.loaders.sql_loader import WarehouseLoader
from src.powerbi.dataset_manager import PowerBIManager
from src.notification.email_sender import EmailSender
from config import CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/pipeline_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class DashboardPipeline:
    """Main pipeline orchestrator for dashboard automation."""
    
    def __init__(self, dashboard_name: str = None):
        """
        Initialize pipeline for specific dashboard or all dashboards.
        
        Args:
            dashboard_name: Name of specific dashboard to process
        """
        self.dashboard_name = dashboard_name
        self.config = CONFIG
        self.extractor = SQLExtractor(self.config['database'])
        self.cleaner = DataCleaner()
        self.aggregator = MetricsAggregator()
        self.loader = WarehouseLoader(self.config['warehouse'])
        self.powerbi = PowerBIManager(self.config['powerbi'])
        self.email_sender = EmailSender(self.config['email'])
        self.execution_summary = {
            'start_time': datetime.now(),
            'dashboards_processed': [],
            'errors': []
        }
        
    def get_dashboards_to_process(self) -> List[str]:
        """Get list of dashboards to process."""
        if self.dashboard_name:
            return [self.dashboard_name]
        return list(self.config['dashboards'].keys())
    
    def extract_data(self, dashboard: str) -> Dict[str, pd.DataFrame]:
        """
        Extract data for specific dashboard.
        
        Args:
            dashboard: Dashboard name
            
        Returns:
            Dictionary of DataFrames by data source
        """
        logger.info(f"="*60)
        logger.info(f"EXTRACTING DATA FOR: {dashboard.upper()}")
        logger.info(f"="*60)
        
        dashboard_config = self.config['dashboards'][dashboard]
        data_sources = dashboard_config['data_sources']
        extracted_data = {}
        
        for source in data_sources:
            try:
                logger.info(f"Extracting from: {source}")
                df = self.extractor.extract(source)
                extracted_data[source] = df
                logger.info(f"✓ Extracted {len(df):,} records from {source}")
            except Exception as e:
                logger.error(f"✗ Failed to extract from {source}: {e}")
                self.execution_summary['errors'].append({
                    'dashboard': dashboard,
                    'step': 'extraction',
                    'source': source,
                    'error': str(e)
                })
                raise
        
        return extracted_data
    
    def transform_data(self, dashboard: str, raw_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Transform and aggregate data for dashboard.
        
        Args:
            dashboard: Dashboard name
            raw_data: Dictionary of raw DataFrames
            
        Returns:
            Transformed DataFrame ready for loading
        """
        logger.info(f"="*60)
        logger.info(f"TRANSFORMING DATA FOR: {dashboard.upper()}")
        logger.info(f"="*60)
        
        try:
            # Clean data
            cleaned_data = {}
            for source, df in raw_data.items():
                logger.info(f"Cleaning data from {source}")
                cleaned_df = self.cleaner.clean(df)
                cleaned_data[source] = cleaned_df
                logger.info(f"✓ Cleaned {source}: {len(cleaned_df):,} records")
            
            # Aggregate metrics
            logger.info(f"Aggregating metrics for {dashboard}")
            dashboard_config = self.config['dashboards'][dashboard]
            final_df = self.aggregator.aggregate(
                cleaned_data,
                dashboard_config['metrics']
            )
            logger.info(f"✓ Created final dataset: {len(final_df):,} records")
            
            return final_df
            
        except Exception as e:
            logger.error(f"✗ Transformation failed: {e}")
            self.execution_summary['errors'].append({
                'dashboard': dashboard,
                'step': 'transformation',
                'error': str(e)
            })
            raise
    
    def load_data(self, dashboard: str, data: pd.DataFrame) -> bool:
        """
        Load transformed data to warehouse.
        
        Args:
            dashboard: Dashboard name
            data: Transformed DataFrame
            
        Returns:
            Success status
        """
        logger.info(f"="*60)
        logger.info(f"LOADING DATA FOR: {dashboard.upper()}")
        logger.info(f"="*60)
        
        try:
            dashboard_config = self.config['dashboards'][dashboard]
            target_table = dashboard_config['warehouse_table']
            
            logger.info(f"Loading to table: {target_table}")
            self.loader.load(data, target_table)
            logger.info(f"✓ Successfully loaded {len(data):,} records")
            return True
            
        except Exception as e:
            logger.error(f"✗ Load failed: {e}")
            self.execution_summary['errors'].append({
                'dashboard': dashboard,
                'step': 'loading',
                'error': str(e)
            })
            return False
    
    def refresh_powerbi(self, dashboard: str) -> bool:
        """
        Refresh Power BI dataset.
        
        Args:
            dashboard: Dashboard name
            
        Returns:
            Success status
        """
        logger.info(f"="*60)
        logger.info(f"REFRESHING POWER BI: {dashboard.upper()}")
        logger.info(f"="*60)
        
        try:
            dashboard_config = self.config['dashboards'][dashboard]
            dataset_id = dashboard_config['powerbi_dataset_id']
            
            logger.info(f"Triggering refresh for dataset: {dataset_id}")
            success = self.powerbi.refresh_dataset(dataset_id)
            
            if success:
                logger.info("✓ Power BI refresh triggered successfully")
                
                # Wait for refresh to complete
                logger.info("Waiting for refresh to complete...")
                completed = self.powerbi.wait_for_refresh(dataset_id, timeout=600)
                
                if completed:
                    logger.info("✓ Power BI refresh completed")
                    return True
                else:
                    logger.warning("⚠ Refresh timeout - check Power BI Service")
                    return False
            else:
                logger.error("✗ Failed to trigger refresh")
                return False
                
        except Exception as e:
            logger.error(f"✗ Power BI refresh failed: {e}")
            self.execution_summary['errors'].append({
                'dashboard': dashboard,
                'step': 'powerbi_refresh',
                'error': str(e)
            })
            return False
    
    def send_email_report(self, dashboard: str) -> bool:
        """
        Send email report to stakeholders.
        
        Args:
            dashboard: Dashboard name
            
        Returns:
            Success status
        """
        logger.info(f"="*60)
        logger.info(f"SENDING EMAIL REPORT: {dashboard.upper()}")
        logger.info(f"="*60)
        
        try:
            dashboard_config = self.config['dashboards'][dashboard]
            
            # Get email template and recipients
            template = dashboard_config['email_template']
            recipients = dashboard_config['email_recipients']
            
            # Get latest metrics for email
            metrics = self.get_dashboard_metrics(dashboard)
            
            logger.info(f"Sending to {len(recipients)} recipients")
            success = self.email_sender.send_dashboard_report(
                template=template,
                recipients=recipients,
                metrics=metrics,
                dashboard_link=dashboard_config['powerbi_link']
            )
            
            if success:
                logger.info(f"✓ Email sent successfully to {len(recipients)} recipients")
                return True
            else:
                logger.error("✗ Email sending failed")
                return False
                
        except Exception as e:
            logger.error(f"✗ Email distribution failed: {e}")
            self.execution_summary['errors'].append({
                'dashboard': dashboard,
                'step': 'email',
                'error': str(e)
            })
            return False
    
    def get_dashboard_metrics(self, dashboard: str) -> Dict:
        """
        Retrieve current dashboard metrics for email report.
        
        Args:
            dashboard: Dashboard name
            
        Returns:
            Dictionary of metric values
        """
        dashboard_config = self.config['dashboards'][dashboard]
        metrics_query = dashboard_config['metrics_query']
        
        metrics_df = self.extractor.execute_query(metrics_query)
        return metrics_df.iloc[0].to_dict()
    
    def run_full_pipeline(self, dashboard: str) -> bool:
        """
        Run complete pipeline for a dashboard.
        
        Args:
            dashboard: Dashboard name
            
        Returns:
            Success status
        """
        logger.info("\n" + "="*80)
        logger.info(f"STARTING PIPELINE FOR: {dashboard.upper()}")
        logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80 + "\n")
        
        try:
            # Extract
            raw_data = self.extract_data(dashboard)
            
            # Transform
            transformed_data = self.transform_data(dashboard, raw_data)
            
            # Load
            load_success = self.load_data(dashboard, transformed_data)
            if not load_success:
                return False
            
            # Refresh Power BI
            refresh_success = self.refresh_powerbi(dashboard)
            if not refresh_success:
                logger.warning("Power BI refresh failed, but data is loaded")
            
            # Mark as successfully processed
            self.execution_summary['dashboards_processed'].append({
                'name': dashboard,
                'status': 'SUCCESS',
                'records_processed': len(transformed_data),
                'timestamp': datetime.now()
            })
            
            logger.info(f"\n✅ PIPELINE COMPLETED SUCCESSFULLY FOR: {dashboard.upper()}\n")
            return True
            
        except Exception as e:
            logger.error(f"\n❌ PIPELINE FAILED FOR: {dashboard.upper()}")
            logger.error(f"Error: {e}\n")
            self.execution_summary['dashboards_processed'].append({
                'name': dashboard,
                'status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now()
            })
            return False
    
    def print_execution_summary(self) -> None:
        """Print pipeline execution summary."""
        end_time = datetime.now()
        duration = (end_time - self.execution_summary['start_time']).total_seconds()
        
        print("\n" + "="*80)
        print("PIPELINE EXECUTION SUMMARY")
        print("="*80)
        print(f"Start Time:  {self.execution_summary['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End Time:    {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration:    {duration:.1f} seconds")
        print(f"\nDashboards Processed: {len(self.execution_summary['dashboards_processed'])}")
        
        successful = sum(1 for d in self.execution_summary['dashboards_processed'] 
                        if d['status'] == 'SUCCESS')
        failed = len(self.execution_summary['dashboards_processed']) - successful
        
        print(f"  ✓ Successful: {successful}")
        print(f"  ✗ Failed:     {failed}")
        
        if self.execution_summary['errors']:
            print(f"\nErrors Encountered: {len(self.execution_summary['errors'])}")
            for error in self.execution_summary['errors']:
                print(f"  - {error['dashboard']} ({error['step']}): {error['error']}")
        
        print("="*80 + "\n")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Dashboard Automation Pipeline')
    parser.add_argument('--mode',
                       choices=['full', 'extract', 'transform', 'refresh', 'distribute'],
                       default='full',
                       help='Pipeline mode')
    parser.add_argument('--dashboard',
                       type=str,
                       default=None,
                       help='Specific dashboard to process')
    parser.add_argument('--email',
                       action='store_true',
                       help='Send email reports')
    
    args = parser.parse_args()
    
    try:
        # Initialize pipeline
        pipeline = DashboardPipeline(args.dashboard)
        dashboards = pipeline.get_dashboards_to_process()
        
        logger.info(f"Processing {len(dashboards)} dashboard(s)")
        
        # Process each dashboard
        for dashboard in dashboards:
            if args.mode == 'full':
                pipeline.run_full_pipeline(dashboard)
                if args.email:
                    pipeline.send_email_report(dashboard)
            elif args.mode == 'extract':
                pipeline.extract_data(dashboard)
            elif args.mode == 'refresh':
                pipeline.refresh_powerbi(dashboard)
            elif args.mode == 'distribute':
                pipeline.send_email_report(dashboard)
        
        # Print summary
        pipeline.print_execution_summary()
        
        # Exit with appropriate code
        failed = sum(1 for d in pipeline.execution_summary['dashboards_processed']
                    if d['status'] == 'FAILED')
        sys.exit(0 if failed == 0 else 1)
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
