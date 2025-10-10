import logging
import requests
from typing import Dict, List, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class SupplierAnalysisService:
    """
    Service for communicating with the Supplier Analysis microservice
    """
    def __init__(self):
        self.base_url = settings.SUPPLIER_ANALYSIS_MS_URL
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        self.api_url = f"{self.base_url}api/"
        logger.info(f"Initialized SupplierAnalysisService with base URL: {self.base_url}")

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None,
                     params: Optional[Dict[str, Any]] = None, stream: bool = False) -> Any:
        """
        Make a request to the supplier analysis microservice
        """
        url = f"{self.api_url}{endpoint}"
        
        try:
            logger.debug(f"Making {method} request to {url}")
            if method.lower() == 'get':
                response = requests.get(url, params=params, stream=stream)
            elif method.lower() == 'post':
                response = requests.post(url, json=data, params=params, stream=stream)
            elif method.lower() == 'put':
                response = requests.put(url, json=data, params=params)
            elif method.lower() == 'delete':
                response = requests.delete(url, params=params)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            response.raise_for_status()
            
            if stream:
                return response
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with supplier analysis microservice: {str(e)}")
            return None

    def health_check(self) -> bool:
        """
        Check if the microservice is up and running
        """
        try:
            # Use the specific health endpoint
            response = requests.get(f"{self.api_url}health", timeout=5)
            data = response.json()
            return response.status_code == 200 and data.get("status") == "ok"
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return False

    # Supplier methods
    def get_suppliers(self) -> List[Dict[str, Any]]:
        """
        Get all suppliers from the microservice
        """
        result = self._make_request('get', 'suppliers/')
        return result or []

    def get_supplier(self, supplier_id: int) -> Optional[Dict[str, Any]]:
        """
        Get supplier details by ID
        """
        return self._make_request('get', f'suppliers/{supplier_id}')

    def create_supplier(self, supplier_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new supplier
        """
        return self._make_request('post', 'suppliers/', data=supplier_data)

    def update_supplier(self, supplier_id: int, supplier_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a supplier
        """
        return self._make_request('put', f'suppliers/{supplier_id}', data=supplier_data)

    # Complaint methods
    def create_complaint(self, complaint_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new complaint and update supplier rating
        """
        return self._make_request('post', 'complaints/', data=complaint_data)

    def get_supplier_complaints(self, supplier_id: int) -> List[Dict[str, Any]]:
        """
        Get all complaints for a supplier
        """
        result = self._make_request('get', f'suppliers/{supplier_id}/complaints')
        return result or []

    # Certificate methods
    def create_certificate(self, certificate_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new certificate
        """
        return self._make_request('post', 'certificates/', data=certificate_data)

    def get_supplier_certificates(self, supplier_id: int) -> List[Dict[str, Any]]:
        """
        Get all certificates for a supplier
        """
        result = self._make_request('get', f'suppliers/{supplier_id}/certificates')
        return result or []

    # Analysis methods
    def get_alternative_suppliers(self, material_name: str, min_rating: float = 0.0) -> Dict[str, Any]:
        """
        Get alternative suppliers for a material
        """
        return self._make_request('get', f'analysis/alternative-suppliers/{material_name}', 
                                params={'min_rating': min_rating})

    def get_better_suppliers(self, supplier_id: int, rating_increase: float = 1.0) -> Dict[str, Any]:
        """
        Get better suppliers for a given supplier
        """
        return self._make_request('get', f'analysis/better-suppliers/{supplier_id}', 
                                params={'rating_increase': rating_increase})

    def get_supplier_risk_patterns(self) -> Dict[str, Any]:
        """
        Get supplier risk patterns
        """
        return self._make_request('get', 'analysis/risk-patterns')

    def get_supplier_analytics(self, supplier_id: int) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive analytics for a supplier
        """
        return self._make_request('get', f'analysis/supplier-analytics/{supplier_id}')

    # Report methods
    def get_supplier_report(self, supplier_id: int) -> Optional[bytes]:
        """
        Get a PDF report for a specific supplier
        """
        response = self._make_request('get', f'reports/supplier/{supplier_id}', stream=True)
        if response:
            return response.content
        return None

    def get_supplier_comparison_report(self, supplier_ids: List[int]) -> Optional[bytes]:
        """
        Get a PDF report comparing multiple suppliers
        """
        response = self._make_request('post', 'reports/supplier-comparison', data={'supplier_ids': supplier_ids}, 
                                    stream=True)
        if response:
            return response.content
        return None

    def get_material_suppliers_report(self, material_name: str) -> Optional[bytes]:
        """
        Get a PDF report of all suppliers for a specific material (POST method)
        """
        response = self._make_request('post', 'reports/material', data={'material_name': material_name}, 
                                    stream=True)
        if response:
            return response.content
        return None

    def get_performance_trends_report(self) -> Optional[bytes]:
        """
        Get a comprehensive performance trends report
        """
        response = self._make_request('get', 'reports/performance-trends', stream=True)
        if response:
            return response.content
        return None

    def get_risk_analysis_report(self) -> Optional[bytes]:
        """
        Get a comprehensive risk analysis report
        """
        response = self._make_request('get', 'reports/risk-analysis', stream=True)
        if response:
            return response.content
        return None

    def get_supplier_performance_trends(self) -> Dict[str, Any]:
        """
        Get advanced supplier performance analysis with trends
        """
        return self._make_request('get', 'analysis/supplier-performance-trends')

    def get_material_market_dynamics(self) -> Dict[str, Any]:
        """
        Get material market dynamics analysis
        """
        return self._make_request('get', 'analysis/material-market-dynamics')

    def get_alternative_suppliers_post(self, material_name: str, min_rating: float = 0.0) -> Dict[str, Any]:
        """
        Get alternative suppliers for a material (POST method for UTF-8 support)
        """
        return self._make_request('post', 'analysis/alternative-suppliers', 
                                data={'material_name': material_name, 'min_rating': min_rating})
