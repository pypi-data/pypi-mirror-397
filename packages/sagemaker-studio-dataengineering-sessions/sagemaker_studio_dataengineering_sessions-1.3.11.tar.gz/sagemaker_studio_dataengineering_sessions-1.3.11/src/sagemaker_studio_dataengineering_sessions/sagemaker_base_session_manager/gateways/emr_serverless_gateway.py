import logging
import boto3

from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.cache import ttl_cache

class EmrServerlessGateway():
    def __init__(self, profile: str | None = None, region: str | None = None):
        self.initialize_clients(profile, region)

    def initialize_clients(self, profile=None, region=None):
        self.emr_serverless_client = self.create_emr_serverless_client(profile, region)
        self.logger = logging.getLogger(__name__)
    
    def ensure_application_started(self, application_id: str):
        """Ensure EMR Serverless application is in STARTED state.
        
        Args:
            application_id: EMR Serverless application ID
            
        Raises:
            RuntimeError: If application is not in STARTED state
        """
        app_state = self.get_emr_serverless_application_state(application_id)
        if app_state != "STARTED":
            raise RuntimeError(f"EMR Serverless application {application_id} is in {app_state} state, expected STARTED")


    def create_emr_serverless_client(self, profile=None, region=None):
        if not region:
            raise ValueError(f"Region must be set.")
        if profile:
            return boto3.Session(profile_name=profile).client(
                "emr-serverless", region_name=region
            )
        else:
            return boto3.Session().client(
                "emr-serverless",
                region_name=region)

    @ttl_cache(ttl_seconds=15)
    def get_emr_serverless_application_state(self, applicationId: str):
        application = self.get_emr_serverless_application(applicationId)
        return application['state']

    def get_emr_serverless_application(self, applicationId: str):
        response = self.emr_serverless_client.get_application(applicationId=applicationId)
        return response['application']

    def start_emr_serverless_application(self, applicationId: str):
        self.emr_serverless_client.start_application(applicationId=applicationId)
        return

    def stop_emr_serverless_application(self, applicationId: str):
        self.emr_serverless_client.stop_application(applicationId=applicationId)
        return
    
    def get_dashboard_for_emr_serverless_application(self, application_id: str, job_run_id: str):
        """Get dashboard URL for EMR Serverless job run.
        
        Args:
            application_id: EMR Serverless application ID
            job_run_id: EMR Serverless job run ID (Spark application ID)
            
        Returns:
            Dashboard response with URL
            
        Raises:
            ValueError: If application_id or job_run_id is None or empty
        """
        if not application_id:
            raise ValueError("application_id is required for dashboard access")
        if not job_run_id:
            raise ValueError("job_run_id is required for dashboard access")
        
        response = self.emr_serverless_client.get_dashboard_for_job_run(
            applicationId=application_id,
            jobRunId=job_run_id,
            accessSystemProfileLogs=False)
        return response
