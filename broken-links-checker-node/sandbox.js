import { SandboxClient } from '@universal-sandbox/sdk';
import { chromium } from 'playwright';
import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

/**
 * Manages the lifecycle of a browser sandbox.
 */
export class SandboxManager {
  constructor(provider = 'alibaba', region = null, timeout = 10) {
    this.provider = provider;
    this.region = region;
    this.timeout = timeout;
  }

  /**
   * Creates a browser sandbox and manages its lifecycle.
   * @returns {Promise<Object>} An object containing the sandbox instance, playwright browser, and cleanup function
   */
  async createBrowserSandbox() {
    let sandboxClient;
    let sandboxResponse;
    let browser;

    try {
      // Initialize SandboxClient with the API token from environment
      sandboxClient = new SandboxClient({
        token: process.env.SANDBOX_API_TOKEN
      });

      // Prepare arguments for sandbox creation
      const args = {
        provider: this.provider,
        timeout: this.timeout
      };

      if (this.region) {
        args.region = this.region;
      }

      console.log('Creating browser sandbox...');

      // Create the browser sandbox
      sandboxResponse = await sandboxClient.browser.create(args);
      console.log(`✓ Browser sandbox created: ${sandboxResponse.id}`);

      // Connect Playwright to the sandbox via WebSocket
      if (!sandboxResponse.urls?.wss_url) {
        throw new Error('Sandbox WebSocket URL not available');
      }

      console.log('Connecting Playwright to sandbox...');
      browser = await chromium.connectOverCDP(sandboxResponse.urls.wss_url);
      console.log('✓ Playwright connected');

      // Return sandbox with cleanup function
      return {
        sandbox: sandboxResponse,
        browser: browser,
        cleanup: async () => {
          try {
            // Close the browser connection
            if (browser) {
              await browser.close();
              console.log('Browser connection closed');
            }
            // Delete the sandbox
            if (sandboxClient && sandboxResponse) {
              await sandboxClient.sandboxes.delete(sandboxResponse.id);
              console.log('Sandbox cleaned up successfully');
            }
          } catch (error) {
            console.error(`Error cleaning up sandbox: ${error.message}`);
          }
        }
      };
    } catch (error) {
      // Clean up on error
      try {
        if (browser) {
          await browser.close();
        }
        if (sandboxClient && sandboxResponse) {
          await sandboxClient.sandboxes.delete(sandboxResponse.id);
        }
      } catch (cleanupError) {
        console.error(`Error during error cleanup: ${cleanupError.message}`);
      }
      console.error(`Error in sandbox management: ${error.message}`);
      throw error;
    }
  }
}
