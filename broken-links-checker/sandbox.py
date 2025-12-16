import os
import logging
from typing import Optional, Generator
from contextlib import contextmanager

# Configure logging
logger = logging.getLogger(__name__)

class SandboxManager:
    """Manages the lifecycle of a browser sandbox."""
    
    def __init__(self, provider: str = "alibaba", region: Optional[str] = None, timeout: int = 10):
        self.provider = provider
        self.region = region
        self.timeout = timeout

    @contextmanager
    def create_browser_sandbox(self) -> Generator:
        """Creates a browser sandbox and manages its lifecycle."""
        try:
            from universal_sandbox import Sandbox
        except ImportError:
            logger.error("universal_sandbox library not installed")
            logger.error("Install with: pip install universal-sandbox")
            raise

        try:
            # Initialize Sandbox with the API token from environment
            sandbox_client = Sandbox(
                token=os.environ.get('SANDBOX_API_TOKEN')
            )
            
            # Prepare arguments for sandbox creation
            args = {"provider": self.provider, "timeout": self.timeout}
            if self.region:
                args["region"] = self.region
            
            logger.info("Creating browser sandbox...")
            
            # Create the browser sandbox
            sbx = sandbox_client.browser.create(**args)
            logger.info(f"✓ Browser sandbox created: {sbx.id}")
            
            try:
                yield sbx
            finally:
                # Clean up the sandbox
                try:
                    sbx.delete()
                    logger.info("Sandbox cleaned up successfully")
                except Exception as e:
                    logger.error(f"Error cleaning up sandbox: {e}")
                    
        except Exception as e:
            logger.error(f"Error in sandbox management: {e}")
            raise
