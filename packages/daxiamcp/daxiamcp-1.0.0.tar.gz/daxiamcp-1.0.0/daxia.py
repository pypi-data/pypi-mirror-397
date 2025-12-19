import httpx
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastmcp import FastMCP
import logging

from httpx import Request, AsyncClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticatedHttpClient(AsyncClient):
    
    def __init__(self, base_url: str,
                 token_url: str,
        client_id: str,
        base64_auth: str,):
        super().__init__(base_url=base_url, timeout=30.0) 
        self.token_url = token_url
        self.client_id = client_id
        self.base64_auth = base64_auth

    async def refresh_token(self) -> str:
        logger.info("Refreshing access token...")
        
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'scope': 'waasabi/api'
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.token_url,
                    data=token_data,
                    headers={
                        'Authorization': f'Basic {self.base64_auth}',
                        "Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                
                token_response = response.json()
                
                # Extract token and expiry
                self.current_token = token_response["access_token"]
               
                logger.info(
                    f"Token refreshed successfully."
                )
                return self.current_token
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to refresh token: {e}")
            raise
        except KeyError as e:
            logger.error(f"Invalid token response format: {e}")
            raise ValueError(f"Token response missing required field: {e}")    
    
    async def _get_headers(self,headers) -> Dict[str, str]:
        token = await self.refresh_token()
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
    
    async def send(self, request: Request, **kwargs):
        logger.info(f"Headers before update: {request.headers}")
        await self._get_headers(request.headers)
        logger.info(f">>>>>>>>>>Sending request to {request} : {request.headers}")
        return await super().send(request=request, **kwargs)
    

# Configuration
base_url = os.getenv("API_BASE_URL", "https://api-sandbox.daxiaplatform.com/sandbox/api/v1")
openapi_spec_url = os.getenv("OPENAPI_SPEC_URL", "http://localhost/local/openapi/daXia1.json")
server_name = os.getenv("SERVER_NAME", "Daxia API")
client_id = os.getenv('DAXIA_CLIENT_ID', '')
base64_auth = os.getenv('DAXIA_AUTH_BASIC', '')
auth_url = os.getenv('DAXIA_AUTH_URL','https://auth-sbx.daxiaplatform.com/oauth2/token')



# WRAP THE RUN COMMAND IN A FUNCTION
def main():
    openapi_spec = httpx.get(openapi_spec_url).json()
    logger.info(f"DaXia server is starting...{openapi_spec_url} {base_url}")
    http_client = AuthenticatedHttpClient(base_url=base_url,
                                          token_url=auth_url,
                                          client_id=client_id,
                                          base64_auth=base64_auth)
    mcp =FastMCP.from_openapi(
        openapi_spec=openapi_spec,
        client=http_client,
        name=server_name
    )     
    logger.info("DaXia server started.")
    mcp.run()


if __name__ == "__main__":
        main()
